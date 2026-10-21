# -*- coding: utf-8 -*-

import json
import os
import threading

import ResMgr
from helpers import getClientLanguage

from .utils import logger


class TranslationManager(object):
    def __init__(self):
        self._defaultTranslationsMap = {}
        self._translationsMap = {}
        self._currentLanguage = None
        self._translationCache = {}
        self._cacheLock = threading.Lock()
        self._translationsLoaded = False
        self.fallbackLanguage = 'en'
        self.translationPathTemplate = 'mods/under_pressure.wn8withoutxvm/{}.json'

    def _safeJsonLoad(self, content, language):
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return json.loads(content)
        except (ValueError, TypeError, UnicodeDecodeError) as e:
            logger.error('[TranslationManager] Failed to parse JSON for language %s: %s', language, e)
            return None

    def _loadLanguageFile(self, language):
        try:
            translationPath = self.translationPathTemplate.format(language)
            translationsRes = ResMgr.openSection(translationPath)
            if translationsRes is None:
                logger.debug('[TranslationManager] Translation file not found for language: %s', language)
                return None
            content = translationsRes.asBinary
            if not content:
                logger.debug('[TranslationManager] Empty translation file for language: %s', language)
                return None
            return self._safeJsonLoad(content, language)
        except Exception as e:
            logger.error('[TranslationManager] Error loading translation file for %s: %s', language, e)
            return None

    def _validateTranslations(self, translations, language):
        if not isinstance(translations, dict):
            logger.error('[TranslationManager] Invalid translation format for %s: expected dict', language)
            return False
        return True

    def loadTranslations(self, forceReload=False):
        if self._translationsLoaded and not forceReload:
            return True
        try:
            defaultTranslations = self._loadLanguageFile(self.fallbackLanguage)
            if defaultTranslations is None:
                self._defaultTranslationsMap = self._getHardcodedDefaults()
                self._translationsMap = self._defaultTranslationsMap.copy()
                self._translationsLoaded = True
                return True
            if not self._validateTranslations(defaultTranslations, self.fallbackLanguage):
                return False
            self._defaultTranslationsMap = defaultTranslations
            try:
                clientLanguage = getClientLanguage()
            except Exception:
                clientLanguage = self.fallbackLanguage
            self._currentLanguage = clientLanguage
            if clientLanguage != self.fallbackLanguage:
                clientTranslations = self._loadLanguageFile(clientLanguage)
                if clientTranslations is not None and self._validateTranslations(clientTranslations, clientLanguage):
                    self._translationsMap = clientTranslations
                else:
                    self._translationsMap = defaultTranslations.copy()
            else:
                self._translationsMap = defaultTranslations.copy()
            self._clearCache()
            self._translationsLoaded = True
            return True
        except Exception as e:
            logger.error('[TranslationManager] Critical error during translation loading: %s', e)
            self._defaultTranslationsMap = self._getHardcodedDefaults()
            self._translationsMap = self._defaultTranslationsMap.copy()
            self._translationsLoaded = True
            return True

    def _getHardcodedDefaults(self):
        return {
            'section.battleResults': 'Battle Results',
            'battleResultsDeanonimize.header': 'De-anonymize players in Battle Results',
            'battleResultsDeanonimize.body': 'Show real player names instead of anonymized names in Battle Results',
            'panelWinrateFontSize.header': 'Player-panel statistic font size',
            'panelWinrateFontSize.body': 'Adjust the font size of the statistic shown near the vehicle icon',
            'panelHorizontalOffset.header': 'Statistics horizontal offset',
            'panelHorizontalOffset.body': 'Move player-panel statistics horizontally from their default position (0-250 px)',
            'panelValueFormat.header': 'Player-panel value format',
            'panelValueFormat.body': 'Show the win rate with decimals or as a whole number',
            'panelValueFormat.exact': 'Exact (49.31%)',
            'panelValueFormat.whole': 'Whole (49%)',
            'winratePosition.beforeNickname': 'Next to nickname',
            'modname': 'WN8 Without XVM',
            'checked': 'enabled',
            'unchecked': 'disabled',
            'defaultValue': 'default',
            'showWn8.header': 'Show WN8 in TAB',
            'showWn8.body': 'Display WN8 rating in TAB',
            'showWinrate.header': 'Show win rate in TAB',
            'showWinrate.body': 'Display win rate percentage in TAB',
            'showBattles.header': 'Show battles in TAB',
            'showBattles.body': 'Display number of battles in TAB',
            'panelDisplayMode.header': 'Player-panel display mode',
            'panelDisplayMode.body': 'Show the player-panel statistic and coloring always or only while Alt is held',
            'panelDisplayMode.always': 'Always',
            'panelDisplayMode.alt': 'On Alt',
            'panelWinratePosition.header': 'Player-panel statistic position',
            'panelWinratePosition.body': 'Where to show the selected statistic in player panels',
            'panelMetric.header': 'What to show in player panels',
            'panelMetric.body': 'Choose win rate or WN8 for player panels',
            'panelMetric.winrate': 'Win rate',
            'panelMetric.wn8': 'WN8 rating',
            'ratingMode.header': 'Rating mode',
            'ratingMode.body': 'Choose overall statistics or statistics for the last 1000 battles',
            'ratingMode.recentWn8': 'Last 1000 battles',
            'ratingMode.overallWn8': 'Overall',
            'winratePosition.nearIcon': 'Near vehicle icon',
            'winratePosition.beforeVehicle': 'Before vehicle name',
            'winratePosition.none': "Don't show",
            'wgApiRegion.header': 'WG API Region',
            'wgApiRegion.body': 'Server region used for WG Public API requests',
            'region.eu': 'Europe',
            'region.na': 'North America',
            'region.asia': 'Asia',
            'colorizePanelText.header': 'Colorize nicknames and vehicle names in player panels',
            'colorizePanelText.body': 'Colorize stock nicknames and vehicle names in player panels using the selected color metric',
            'panelTextColorMetric.header': 'Colorize by',
            'panelTextColorMetric.body': 'Choose the statistic whose color is used for nicknames and vehicle names',
            'panelTextColorMetric.wn8': 'WN8',
            'panelTextColorMetric.winrate': 'Win rate',
            'showAnonymizerIcon.header': 'Show anonymizer icon',
            'showAnonymizerIcon.body': 'Show the anonymizer icon for players whose statistics are unavailable'
        }

    def _clearCache(self):
        with self._cacheLock:
            self._translationCache.clear()

    def getCurrentLanguage(self):
        return self._currentLanguage or self.fallbackLanguage

    def initialize(self):
        try:
            self.loadTranslations()
        except Exception as e:
            logger.error('[TranslationManager] Critical error initializing translations: %s', e)


g_translationManager = TranslationManager()
g_translationManager.initialize()


class TranslationElement(object):
    def __init__(self, tokenName, manager=None):
        self._tokenName = tokenName
        self._cachedValue = None
        self._manager = manager or g_translationManager

    def __get__(self, instance, owner=None):
        if self._cachedValue is None:
            self._cachedValue = self._generateTranslation()
        return self._cachedValue

    def _generateTranslation(self):
        if not self._manager._translationsLoaded:
            self._manager.loadTranslations()
        cached = self._manager._translationCache.get(self._tokenName)
        if cached is not None:
            return cached
        if self._tokenName in self._manager._translationsMap:
            translation = self._manager._translationsMap[self._tokenName]
        elif self._tokenName in self._manager._defaultTranslationsMap:
            translation = self._manager._defaultTranslationsMap[self._tokenName]
        else:
            translation = self._tokenName.replace('.', ' ').replace('_', ' ').title()
        with self._manager._cacheLock:
            self._manager._translationCache[self._tokenName] = translation
        return translation


class Translator(object):
    MOD_NAME = TranslationElement('modname')
    CHECKED = TranslationElement('checked')
    UNCHECKED = TranslationElement('unchecked')
    DEFAULT_VALUE = TranslationElement('defaultValue')
    SHOW_WN8_HEADER = TranslationElement('showWn8.header')
    SHOW_WN8_BODY = TranslationElement('showWn8.body')
    SHOW_WINRATE_HEADER = TranslationElement('showWinrate.header')
    SHOW_WINRATE_BODY = TranslationElement('showWinrate.body')
    SHOW_BATTLES_HEADER = TranslationElement('showBattles.header')
    SHOW_BATTLES_BODY = TranslationElement('showBattles.body')
    PANEL_DISPLAY_MODE_HEADER = TranslationElement('panelDisplayMode.header')
    PANEL_DISPLAY_MODE_BODY = TranslationElement('panelDisplayMode.body')
    PANEL_DISPLAY_MODE_ALWAYS = TranslationElement('panelDisplayMode.always')
    PANEL_DISPLAY_MODE_ALT = TranslationElement('panelDisplayMode.alt')
    PANEL_WINRATE_POSITION_HEADER = TranslationElement('panelWinratePosition.header')
    PANEL_WINRATE_POSITION_BODY = TranslationElement('panelWinratePosition.body')
    PANEL_METRIC_HEADER = TranslationElement('panelMetric.header')
    PANEL_METRIC_BODY = TranslationElement('panelMetric.body')
    PANEL_METRIC_WINRATE = TranslationElement('panelMetric.winrate')
    PANEL_METRIC_WN8 = TranslationElement('panelMetric.wn8')
    PANEL_WINRATE_FONT_SIZE_HEADER = TranslationElement('panelWinrateFontSize.header')
    PANEL_WINRATE_FONT_SIZE_BODY = TranslationElement('panelWinrateFontSize.body')
    PANEL_HORIZONTAL_OFFSET_HEADER = TranslationElement('panelHorizontalOffset.header')
    PANEL_HORIZONTAL_OFFSET_BODY = TranslationElement('panelHorizontalOffset.body')
    PANEL_VALUE_FORMAT_HEADER = TranslationElement('panelValueFormat.header')
    PANEL_VALUE_FORMAT_BODY = TranslationElement('panelValueFormat.body')
    PANEL_VALUE_FORMAT_EXACT = TranslationElement('panelValueFormat.exact')
    PANEL_VALUE_FORMAT_WHOLE = TranslationElement('panelValueFormat.whole')
    RATING_MODE_HEADER = TranslationElement('ratingMode.header')
    RATING_MODE_BODY = TranslationElement('ratingMode.body')
    RATING_RECENT_WN8 = TranslationElement('ratingMode.recentWn8')
    RATING_OVERALL_WN8 = TranslationElement('ratingMode.overallWn8')
    WINRATE_NEAR_ICON = TranslationElement('winratePosition.nearIcon')
    WINRATE_BEFORE_VEHICLE = TranslationElement('winratePosition.beforeVehicle')
    WINRATE_BEFORE_NICKNAME = TranslationElement('winratePosition.beforeNickname')
    WINRATE_NONE = TranslationElement('winratePosition.none')
    WG_API_REGION_HEADER = TranslationElement('wgApiRegion.header')
    WG_API_REGION_BODY = TranslationElement('wgApiRegion.body')
    REGION_EU = TranslationElement('region.eu')
    REGION_NA = TranslationElement('region.na')
    REGION_ASIA = TranslationElement('region.asia')
    PANEL_TEXT_COLOR_WN8 = TranslationElement('panelTextColorMetric.wn8')
    PANEL_TEXT_COLOR_WINRATE = TranslationElement('panelTextColorMetric.winrate')


def getTranslation(key):
    if not g_translationManager._translationsLoaded:
        g_translationManager.loadTranslations()
    if key in g_translationManager._translationsMap:
        return g_translationManager._translationsMap[key]
    if key in g_translationManager._defaultTranslationsMap:
        return g_translationManager._defaultTranslationsMap[key]
    return key.replace('.', ' ').replace('_', ' ').title()


PARAM_REGISTRY = {}


def toJson(obj):
    return json.dumps(obj, ensure_ascii=False)


def toBool(value):
    return str(value).lower() == 'true'


def clamp(minValue, value, maxValue):
    if minValue is not None:
        value = max(minValue, value)
    if maxValue is not None:
        value = min(value, maxValue)
    return value


def createTooltip(header=None, body=None, note=None, attention=None):
    resStr = ''
    if header is not None:
        resStr += '{HEADER}%s{/HEADER}' % header
    if body is not None:
        resStr += '{BODY}%s{/BODY}' % body
    if note is not None:
        resStr += '{NOTE}%s{/NOTE}' % note
    if attention is not None:
        resStr += '{ATTENTION}%s{/ATTENTION}' % attention
    return resStr


class BaseParameter(object):
    def __init__(self, path, defaultValue, disabledValue=None):
        self.name = path[-1]
        self.path = path
        self.tokenName = '-'.join(self.path)
        self.value = defaultValue
        self.defaultValue = defaultValue
        self.disabledValue = disabledValue if disabledValue is not None else defaultValue
        PARAM_REGISTRY[self.tokenName] = self

    def __call__(self):
        config = globals().get('g_config')
        if config is not None and hasattr(config, 'configParams') and hasattr(config.configParams, 'enabled'):
            if not config.configParams.enabled.value:
                return self.disabledValue
        return self.value

    @property
    def jsonValue(self):
        return self.toJsonValue(self.value)

    @jsonValue.setter
    def jsonValue(self, jsonValue):
        try:
            self.value = self.fromJsonValue(jsonValue)
        except Exception as e:
            logger.error('Error saving parameter %s with jsonValue %s: %s', self.tokenName, jsonValue, str(e))

    @property
    def msaValue(self):
        return self.toMsaValue(self.value)

    @msaValue.setter
    def msaValue(self, msaValue):
        try:
            self.value = self.fromMsaValue(msaValue)
        except Exception as e:
            logger.error('Error saving parameter %s with msaValue %s: %s', self.tokenName, msaValue, str(e))

    @property
    def defaultMsaValue(self):
        return self.toMsaValue(self.defaultValue)

    @property
    def defaultJsonValue(self):
        return self.toJsonValue(self.defaultValue)

    def toMsaValue(self, value):
        raise NotImplementedError()

    def fromMsaValue(self, msaValue):
        raise NotImplementedError()

    def toJsonValue(self, value):
        raise NotImplementedError()

    def fromJsonValue(self, jsonValue):
        raise NotImplementedError()

    def renderParam(self, header, body=None, note=None, attention=None):
        raise NotImplementedError()


class CheckboxParameter(BaseParameter):
    def toMsaValue(self, value):
        return value

    def fromMsaValue(self, msaValue):
        return msaValue

    def toJsonValue(self, value):
        return toJson(value)

    def fromJsonValue(self, jsonValue):
        return toBool(jsonValue)

    def renderParam(self, header, body=None, note=None, attention=None):
        return {
            'type': 'CheckBox', 'text': header, 'varName': self.tokenName,
            'value': self.toMsaValue(self.value),
            'tooltip': createTooltip(
                header='{} ({}: {})'.format(header, Translator.DEFAULT_VALUE, Translator.CHECKED if self.defaultValue else Translator.UNCHECKED),
                body=body, note=note, attention=attention)
        }


class SliderParameter(BaseParameter):
    def __init__(self, path, defaultValue, minimum, maximum, step=1, disabledValue=None):
        super(SliderParameter, self).__init__(path, defaultValue, disabledValue)
        self.minimum = minimum
        self.maximum = maximum
        self.step = step

    def _normalize(self, value):
        try:
            value = int(round(float(value)))
        except (ValueError, TypeError):
            value = int(self.defaultValue)
        return int(clamp(self.minimum, value, self.maximum))

    def toMsaValue(self, value): return self._normalize(value)
    def fromMsaValue(self, msaValue): return self._normalize(msaValue)
    def toJsonValue(self, value): return toJson(self._normalize(value))
    def fromJsonValue(self, jsonValue): return self._normalize(jsonValue)

    def renderParam(self, header, body=None, note=None, attention=None):
        return {
            'type': 'Slider', 'text': header, 'varName': self.tokenName,
            'value': self.toMsaValue(self.value), 'minimum': self.minimum,
            'maximum': self.maximum, 'snapInterval': self.step, 'format': '{value}', 'width': 250,
            'tooltip': createTooltip(header='{} ({}: {})'.format(header, Translator.DEFAULT_VALUE, self.defaultValue), body=body, note=note, attention=attention)
        }


class OptionItem(object):
    def __init__(self, value, msaValue, displayName):
        self.value = value
        self.msaValue = msaValue
        self.displayName = displayName


class DropdownParameter(BaseParameter):
    def __init__(self, path, options, defaultValue, disabledValue=None):
        super(DropdownParameter, self).__init__(path, defaultValue, disabledValue)
        self.options = options

    def toMsaValue(self, value):
        for i, option in enumerate(self.options):
            if option.value == value:
                return i
        return 0

    def fromMsaValue(self, msaValue):
        try:
            index = int(msaValue)
            if 0 <= index < len(self.options):
                return self.options[index].value
        except (ValueError, TypeError):
            pass
        return self.defaultValue

    def toJsonValue(self, value): return toJson(value)

    def fromJsonValue(self, jsonValue):
        option = self.getOptionByValue(jsonValue)
        if option is None:
            raise Exception('Invalid value {} for config param {}'.format(jsonValue, self.tokenName))
        return option.value

    def getOptionByValue(self, value):
        foundOptions = [option for option in self.options if option.value == value]
        return foundOptions[0] if foundOptions else None

    def getOptionByMsaValue(self, msaValue):
        try:
            index = int(msaValue)
            if 0 <= index < len(self.options):
                return self.options[index]
        except (ValueError, TypeError):
            pass
        return self.getOptionByValue(self.defaultValue)

    def renderParam(self, header, body=None, note=None, attention=None):
        return {
            'type': 'Dropdown', 'text': header, 'varName': self.tokenName,
            'value': self.toMsaValue(self.value),
            'options': [{'label': option.displayName} for option in self.options],
            'tooltip': createTooltip(header='{} ({}: {})'.format(header, Translator.DEFAULT_VALUE, self.getOptionByValue(self.defaultValue).displayName), body=body, note=note, attention=attention),
            'width': 200
        }


class TextInputParameter(BaseParameter):
    def __init__(self, path, defaultValue='', disabledValue=None):
        super(TextInputParameter, self).__init__(path, defaultValue, disabledValue)

    def toMsaValue(self, value): return value if value is not None else ''
    def fromMsaValue(self, msaValue): return self.defaultValue if msaValue is None else str(msaValue)
    def toJsonValue(self, value): return toJson(value)
    def fromJsonValue(self, jsonValue): return jsonValue if jsonValue is not None else self.defaultValue

    def renderParam(self, header, body=None, note=None, attention=None):
        return {
            'type': 'TextInput', 'text': header, 'varName': self.tokenName,
            'value': self.toMsaValue(self.value),
            'tooltip': createTooltip(header='{} ({}: {})'.format(header, Translator.DEFAULT_VALUE, self.defaultValue or "''"), body=body, note=note, attention=attention),
            'width': 250
        }


class WinratePosition(object):
    NEAR_ICON = 'near_icon'
    BEFORE_VEHICLE = 'before_vehicle'
    BEFORE_NICKNAME = BEFORE_VEHICLE
    NONE = 'none'


class PanelMetric(object):
    NONE = 'none'
    WINRATE = 'winrate'
    WN8 = 'wn8'


class PanelDisplayMode(object):
    ALWAYS = 'always'
    ALT = 'alt'


class PanelValueFormat(object):
    EXACT = 'exact'
    WHOLE = 'whole'


class PanelTextColorMetric(object):
    WN8 = 'wn8'
    WINRATE = 'winrate'


class RatingMode(object):
    OVERALL_WN8 = 'overall_wn8'
    RECENT_WN8 = 'recent_wn8'
    RECENT_WNX = 'recent_wnx'
    OVERALL_WNX = 'overall_wnx'


class ApiRegion(object):
    EU = 'eu'
    NA = 'na'
    ASIA = 'asia'


class ConfigParams(object):
    def __init__(self):
        self.enabled = CheckboxParameter(['enabled'], defaultValue=True)
        self.showWn8 = CheckboxParameter(['show-wn8'], defaultValue=True)
        self.showWinrate = CheckboxParameter(['show-winrate'], defaultValue=True)
        self.showBattles = CheckboxParameter(['show-battles'], defaultValue=True)
        self.battleResultsDeanonimize = CheckboxParameter(['battle-results-deanonimize'], defaultValue=True)
        self.panelDisplayMode = DropdownParameter(['panel-display-mode'], [
            OptionItem(PanelDisplayMode.ALWAYS, 0, Translator.PANEL_DISPLAY_MODE_ALWAYS),
            OptionItem(PanelDisplayMode.ALT, 1, Translator.PANEL_DISPLAY_MODE_ALT)], PanelDisplayMode.ALWAYS)
        self.panelWinratePosition = DropdownParameter(['panel-winrate-position'], [
            OptionItem(WinratePosition.NEAR_ICON, 0, Translator.WINRATE_NEAR_ICON),
            OptionItem(WinratePosition.BEFORE_NICKNAME, 1, Translator.WINRATE_BEFORE_NICKNAME)], WinratePosition.NEAR_ICON)
        self.panelMetric = DropdownParameter(['panel-metric'], [
            OptionItem(PanelMetric.WINRATE, 0, Translator.PANEL_METRIC_WINRATE),
            OptionItem(PanelMetric.WN8, 1, Translator.PANEL_METRIC_WN8),
            OptionItem(PanelMetric.NONE, 2, Translator.WINRATE_NONE)], PanelMetric.WN8)
        self.panelWinrateFontSize = SliderParameter(['panel-winrate-font-size'], 12, 8, 24, 1)
        self.panelHorizontalOffset = SliderParameter(['panel-horizontal-offset'], 0, 0, 250, 1)
        self.panelValueFormat = DropdownParameter(['panel-value-format'], [
            OptionItem(PanelValueFormat.EXACT, 0, Translator.PANEL_VALUE_FORMAT_EXACT),
            OptionItem(PanelValueFormat.WHOLE, 1, Translator.PANEL_VALUE_FORMAT_WHOLE)], PanelValueFormat.WHOLE)
        self.ratingMode = DropdownParameter(['rating-mode'], [
            OptionItem(RatingMode.OVERALL_WN8, 0, Translator.RATING_OVERALL_WN8),
            OptionItem(RatingMode.RECENT_WN8, 1, Translator.RATING_RECENT_WN8)], RatingMode.OVERALL_WN8)
        self.wgApiRegion = DropdownParameter(['wg-api-region'], [
            OptionItem(ApiRegion.EU, 0, Translator.REGION_EU),
            OptionItem(ApiRegion.NA, 1, Translator.REGION_NA),
            OptionItem(ApiRegion.ASIA, 2, Translator.REGION_ASIA)], ApiRegion.EU)
        self.colorizePanelText = CheckboxParameter(['colorize-panel-text'], defaultValue=True)
        self.panelTextColorMetric = DropdownParameter(['panel-text-color-metric'], [
            OptionItem(PanelTextColorMetric.WN8, 0, Translator.PANEL_TEXT_COLOR_WN8),
            OptionItem(PanelTextColorMetric.WINRATE, 1, Translator.PANEL_TEXT_COLOR_WINRATE)], PanelTextColorMetric.WN8)
        self.showAnonymizerIcon = CheckboxParameter(['show-anonymizer-icon'], defaultValue=True)

    def items(self):
        return {
            'enabled': self.enabled, 'showWn8': self.showWn8, 'showWinrate': self.showWinrate,
            'showBattles': self.showBattles, 'battleResultsDeanonimize': self.battleResultsDeanonimize,
            'panelDisplayMode': self.panelDisplayMode, 'panelWinratePosition': self.panelWinratePosition,
            'panelMetric': self.panelMetric, 'panelWinrateFontSize': self.panelWinrateFontSize,
            'panelHorizontalOffset': self.panelHorizontalOffset, 'panelValueFormat': self.panelValueFormat,
            'ratingMode': self.ratingMode, 'wgApiRegion': self.wgApiRegion,
            'colorizePanelText': self.colorizePanelText, 'panelTextColorMetric': self.panelTextColorMetric,
        }


g_configParams = ConfigParams()


class ConfigFile(object):
    def __init__(self, configParams):
        self.configPath = os.path.join('mods', 'configs', 'under_pressure', 'wn8withoutxvm.json')
        self.configParams = configParams
        self._loadedConfigData = None

    def _ensureConfigExists(self):
        try:
            configDir = os.path.dirname(self.configPath)
            if not os.path.exists(configDir):
                os.makedirs(configDir)
            if not os.path.exists(self.configPath):
                return self._createDefaultConfig()
            return True
        except Exception as e:
            logger.error('[ConfigFile] Error ensuring config exists: %s', str(e))
            return False

    def _createDefaultConfig(self):
        try:
            configData = {tokenName: param.defaultValue for tokenName, param in self.configParams.items().items()}
            with open(self.configPath, 'w') as f:
                json.dump(configData, f, indent=4, ensure_ascii=False)
            return os.path.exists(self.configPath)
        except Exception as e:
            logger.error('[ConfigFile] Error creating default config: %s', str(e))
            return False

    def load_config(self):
        try:
            if not self._ensureConfigExists():
                for param in self.configParams.items().values():
                    param.value = param.defaultValue
                return False
            with open(self.configPath, 'r') as f:
                content = f.read().strip()
            if not content:
                if not self._createDefaultConfig():
                    return False
                with open(self.configPath, 'r') as f:
                    content = f.read().strip()
            configData = json.loads(content)
            self._loadedConfigData = configData
            for tokenName, param in self.configParams.items().items():
                if tokenName in configData:
                    try:
                        param.value = configData[tokenName]
                    except Exception as e:
                        logger.error('[ConfigFile] Error loading parameter %s: %s', tokenName, str(e))
                        param.value = param.defaultValue
                else:
                    param.value = param.defaultValue
            return True
        except ValueError as e:
            logger.error('[ConfigFile] Invalid JSON in config file: %s', str(e))
        except Exception as e:
            logger.error('[ConfigFile] Error loading config: %s', str(e))
        self._loadedConfigData = None
        for param in self.configParams.items().values():
            param.value = param.defaultValue
        return False

    def save_config(self):
        try:
            configDir = os.path.dirname(self.configPath)
            if not os.path.exists(configDir):
                os.makedirs(configDir)
            configData = {tokenName: param.value for tokenName, param in self.configParams.items().items()}
            with open(self.configPath, 'w') as f:
                json.dump(configData, f, indent=4, ensure_ascii=False)
            self._loadedConfigData = configData
            return os.path.exists(self.configPath)
        except Exception as e:
            logger.error('[ConfigFile] Error saving config: %s', str(e))
            return False

    def exists(self): return os.path.exists(self.configPath)
    def getConfigPath(self): return self.configPath


class Template(object):
    def __init__(self, configParams):
        self.configParams = configParams
        self.modDisplayName = None
        self.column1Items = []
        self.column2Items = []

    def _defaultEnabled(self):
        enabledParam = getattr(self.configParams, 'enabled', None)
        return enabledParam.defaultValue if enabledParam else True

    def setModDisplayName(self, name):
        self.modDisplayName = unicode(name) if hasattr(__builtins__, 'unicode') else str(name)
        return self

    def addToColumn1(self, item):
        if isinstance(item, dict): self.column1Items.append(item)
        return self

    def addToColumn2(self, item):
        if isinstance(item, dict): self.column2Items.append(item)
        return self

    def addParameterToColumn1(self, paramName, header=None, body=None, note=None, attention=None):
        param = getattr(self.configParams, paramName, None)
        if param and hasattr(param, 'renderParam'):
            self.addToColumn1(param.renderParam(header=header or paramName.title(), body=body, note=note, attention=attention))
        return self

    def addParameterToColumn2(self, paramName, header=None, body=None, note=None, attention=None):
        param = getattr(self.configParams, paramName, None)
        if param and hasattr(param, 'renderParam'):
            self.addToColumn2(param.renderParam(header=header or paramName.title(), body=body, note=note, attention=attention))
        return self

    def clearColumns(self):
        self.column1Items = []
        self.column2Items = []
        return self

    def generateTemplate(self):
        return {'modDisplayName': self.modDisplayName, 'enabled': self._defaultEnabled(), 'column1': list(self.column1Items), 'column2': list(self.column2Items)}


_GAMEFACE_I18N_KEYS = (
    'modname', 'menu.subtitle', 'menu.close', 'section.tab', 'section.playerPanel',
    'section.battleResults', 'section.playerPanelSettings', 'section.ratingApi', 'help.showExample',
    'showWn8.header', 'showWinrate.header', 'showBattles.header', 'battleResultsDeanonimize.header',
    'colorizePanelText.header', 'showAnonymizerIcon.header', 'panelTextColorMetric.header',
    'panelDisplayMode.header', 'panelWinratePosition.header', 'panelMetric.header',
    'panelWinrateFontSize.header', 'panelHorizontalOffset.header', 'panelHorizontalOffset.body',
    'panelValueFormat.header', 'ratingMode.header', 'wgApiRegion.header')

try:
    string_types = (basestring,)
except NameError:
    string_types = (str,)
try:
    text_type = unicode
except NameError:
    text_type = str


class Config(object):
    def __init__(self):
        self.configParams = g_configParams
        self.configFile = ConfigFile(self.configParams)
        self._loadedSuccessfully = False
        self._loadConfigFileToParams()

    def _normalizeRatingMode(self):
        try:
            current = getattr(self.configParams.ratingMode, 'value', RatingMode.OVERALL_WN8)
            if current not in (RatingMode.OVERALL_WN8, RatingMode.RECENT_WN8):
                self.configParams.ratingMode.value = RatingMode.OVERALL_WN8
                logger.info('[Config] Legacy rating mode reset to Overall WN8: %s', current)
                return True
        except Exception as e:
            logger.error('[Config] Error normalizing rating mode: %s', str(e))
        return False

    def _loadConfigFileToParams(self):
        self._loadedSuccessfully = False
        try:
            success = self.configFile.load_config()
            if success:
                self._loadedSuccessfully = True
            changed = self._normalizeRatingMode()
            if changed or not self.configFile.exists():
                self.configFile.save_config()
        except Exception as e:
            logger.error('[Config] Failed to load config: %s', str(e))
            for param in self.configParams.items().values():
                param.value = param.defaultValue

    def _normalizeIncoming(self, param, value):
        try:
            class_name = param.__class__.__name__
            if class_name == 'CheckboxParameter':
                if isinstance(value, string_types):
                    return value.lower() in ('1', 'true', 'yes', 'on')
                return bool(value)
            if class_name == 'SliderParameter':
                return param.fromMsaValue(value)
            if class_name == 'DropdownParameter':
                for option in getattr(param, 'options', ()):
                    if text_type(option.value) == text_type(value):
                        return option.value
                return param.defaultValue
        except Exception:
            pass
        return value

    def _snapshotPanelSettings(self):
        p = self.configParams
        return {
            'enabled': bool(p.enabled.value), 'showWn8': bool(p.showWn8.value),
            'showWinrate': bool(p.showWinrate.value), 'showBattles': bool(p.showBattles.value),
            'panelWinrateFontSize': int(p.panelWinrateFontSize.value),
            'panelHorizontalOffset': int(p.panelHorizontalOffset.value),
            'panelDisplayMode': p.panelDisplayMode.value, 'panelWinratePosition': p.panelWinratePosition.value,
            'panelMetric': p.panelMetric.value, 'panelValueFormat': p.panelValueFormat.value,
            'colorizePanelText': bool(p.colorizePanelText.value),
            'panelTextColorMetric': p.panelTextColorMetric.value,
            'showAnonymizerIcon': bool(p.showAnonymizerIcon.value)}

    def _refreshRuntime(self, old):
        p = self.configParams
        try:
            enabled_changed = old['enabled'] != bool(p.enabled.value)
            show_wn8_changed = old['showWn8'] != bool(p.showWn8.value)
            show_winrate_changed = old['showWinrate'] != bool(p.showWinrate.value)
            show_battles_changed = old['showBattles'] != bool(p.showBattles.value)
            font_changed = old['panelWinrateFontSize'] != int(p.panelWinrateFontSize.value)
            offset_changed = old['panelHorizontalOffset'] != int(p.panelHorizontalOffset.value)
            display_changed = old['panelDisplayMode'] != p.panelDisplayMode.value
            position_changed = old['panelWinratePosition'] != p.panelWinratePosition.value
            metric_changed = old['panelMetric'] != p.panelMetric.value
            format_changed = old['panelValueFormat'] != p.panelValueFormat.value
            color_changed = old['colorizePanelText'] != bool(p.colorizePanelText.value)
            color_metric_changed = old['panelTextColorMetric'] != p.panelTextColorMetric.value
            anonymizer_changed = old['showAnonymizerIcon'] != bool(p.showAnonymizerIcon.value)
            if not any((enabled_changed, show_wn8_changed, show_winrate_changed, show_battles_changed,
                        font_changed, offset_changed, display_changed, position_changed, metric_changed,
                        format_changed, color_changed, color_metric_changed, anonymizer_changed)):
                return
            import BigWorld
            from . import g_panel_view
            if g_panel_view is None:
                return
            if position_changed or offset_changed:
                callback = g_panel_view.refreshStatContainer
            elif (enabled_changed or show_wn8_changed or show_winrate_changed or show_battles_changed or
                  display_changed or metric_changed or anonymizer_changed):
                callback = g_panel_view.updateAllPlayers
            else:
                callback = g_panel_view._scheduleReapplyAllColors
            BigWorld.callback(0.0, callback)
        except Exception:
            logger.exception('[Config] Failed to refresh player-panel statistic')

    def applyGamefaceSetting(self, key, value):
        if not self._loadedSuccessfully:
            self._loadConfigFileToParams()
            if not self._loadedSuccessfully:
                return False
        param = self.configParams.items().get(key)
        if param is None:
            logger.warning('[Config] Unknown Gameface setting ignored: %s', key)
            return False
        old = self._snapshotPanelSettings()
        try:
            param.value = self._normalizeIncoming(param, value)
            self._normalizeRatingMode()
            self.configFile.save_config()
            self._refreshRuntime(old)
            return True
        except Exception:
            logger.exception('[Config] Failed to apply Gameface setting %s', key)
            return False

    def _optionsFor(self, param):
        return [{'value': option.value, 'label': option.displayName} for option in getattr(param, 'options', ())]

    def getGamefacePayload(self):
        p = self.configParams
        settings, options, meta = {}, {}, {}
        for key, param in p.items().items():
            settings[key] = param.value
            option_items = self._optionsFor(param)
            if option_items:
                options[key] = option_items
            if hasattr(param, 'minimum'):
                meta[key] = {'minimum': int(param.minimum), 'maximum': int(param.maximum), 'step': int(param.step)}
        meta['showPanelHorizontalOffset'] = (p.panelWinratePosition.value == WinratePosition.NEAR_ICON)
        i18n = {key: getTranslation(key) for key in _GAMEFACE_I18N_KEYS}
        return {'settings': settings, 'options': options, 'meta': meta, 'i18n': i18n}


g_config = Config()

__all__ = [
    'g_config', 'g_configParams', 'Config', 'ConfigFile', 'ConfigParams',
    'RatingMode', 'WinratePosition', 'PanelMetric', 'PanelDisplayMode',
    'PanelValueFormat', 'PanelTextColorMetric', 'ApiRegion', 'Translator',
    'getTranslation', 'Template'
]
