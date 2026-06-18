import json
import threading
from ..utils import logger

import ResMgr
from helpers import getClientLanguage


class TranslationManager(object):

    def __init__(self):
        self._defaultTranslationsMap = {}
        self._translationsMap = {}
        self._currentLanguage = None
        self._translationCache = {}
        self._cacheLock = threading.Lock()
        self._translationsLoaded = False
        self.fallbackLanguage = "en"
        self.translationPathTemplate = "mods/under_pressure.wn8withoutxvm/{}.json"

    def _safeJsonLoad(self, content, language):
        try:
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return json.loads(content)
        except (ValueError, TypeError, UnicodeDecodeError) as e:
            logger.error("[TranslationManager] Failed to parse JSON for language %s: %s", language, e)
            return None

    def _loadLanguageFile(self, language):
        try:
            translationPath = self.translationPathTemplate.format(language)
            translationsRes = ResMgr.openSection(translationPath)

            if translationsRes is None:
                logger.debug("[TranslationManager] Translation file not found for language: %s", language)
                return None

            content = translationsRes.asBinary
            if not content:
                logger.debug("[TranslationManager] Empty translation file for language: %s", language)
                return None

            return self._safeJsonLoad(content, language)

        except Exception as e:
            logger.error("[TranslationManager] Error loading translation file for %s: %s", language, e)
            return None

    def _validateTranslations(self, translations, language):
        if not isinstance(translations, dict):
            logger.error("[TranslationManager] Invalid translation format for %s: expected dict", language)
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
            logger.error("[TranslationManager] Critical error during translation loading: %s", e)
            self._defaultTranslationsMap = self._getHardcodedDefaults()
            self._translationsMap = self._defaultTranslationsMap.copy()
            self._translationsLoaded = True
            return True

    def _getHardcodedDefaults(self):
        return {
            "modname": "WN8 Without XVM",
            "checked": "enabled",
            "unchecked": "disabled",
            "defaultValue": "default",
            "showWn8.header": "Show WN8",
            "showWn8.body": "Display WN8 rating in battle",
            "showWinrate.header": "Show Winrate",
            "showWinrate.body": "Display winrate percentage in battle",
            "showBattles.header": "Show Battles",
            "showBattles.body": "Display number of battles",
            "panelWinratePosition.header": "Позиція показника у вухах",
            "panelWinratePosition.body": "Де показувати вибраний показник у бокових панелях гравців",
            "panelMetric.header": "Що показувати у вухах",
            "panelMetric.body": "Вибери, що показувати у бокових панелях: відсоток перемог або рейтинг WN8/WNX",
            "panelMetric.winrate": "Відсоток перемог",
            "panelMetric.wn8": "WN8 / WNX рейтинг",
            "ratingMode.header": "Режим рейтингу",
            "ratingMode.body": "Стандартний режим без ключа — Загальний WN8. Для WN8/WNX за 1000 боїв і для WNX потрібен Tomato.gg API key.",
            "ratingMode.recentWnx": "WNX за 1000 боїв (потрібен Tomato key)",
            "ratingMode.recentWn8": "WN8 за 1000 боїв (потрібен Tomato key)",
            "ratingMode.overallWn8": "Загальний WN8 (без ключа)",
            "ratingMode.overallWnx": "Загальний WNX (потрібен Tomato key)",
            "tomatoApiKey.header": "Tomato.gg API key",
            "tomatoApiKey.body": "Щоб увімкнути статистику за 1000 боїв: встав Tomato.gg API key і вибери режим WNX за 1000 боїв або WN8 за 1000 боїв.",
            "tomatoApiKey.note": "Без ключа стандартно працює тільки Загальний WN8. Режими з позначкою Tomato key без ключа будуть скидатися на Загальний WN8.",
            "tomatoApiKey.attention": "Не показуй і не передавай свій Tomato API key іншим.",
            "winratePosition.nearIcon": "Near vehicle icon",
            "winratePosition.beforeVehicle": "Before vehicle name",
            "winratePosition.none": "Don't show",
            "wgApiRegion.header": "WG API Region",
            "wgApiRegion.body": "Server region used for WG Public API requests",
            "region.eu": "Europe",
            "region.na": "North America",
            "region.asia": "Asia",
            "colorizeVehicleIcon.header": "Colorize Vehicle Icon",
            "colorizeVehicleIcon.body": "Tint tank icons with WN8 color in the player panel and Tab screen"
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
            logger.error("[TranslationManager] Critical error initializing translations: %s", e)


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

        translation = None
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
    MOD_NAME = TranslationElement("modname")
    CHECKED = TranslationElement("checked")
    UNCHECKED = TranslationElement("unchecked")
    DEFAULT_VALUE = TranslationElement("defaultValue")

    SHOW_WN8_HEADER = TranslationElement("showWn8.header")
    SHOW_WN8_BODY = TranslationElement("showWn8.body")
    SHOW_WINRATE_HEADER = TranslationElement("showWinrate.header")
    SHOW_WINRATE_BODY = TranslationElement("showWinrate.body")
    SHOW_BATTLES_HEADER = TranslationElement("showBattles.header")
    SHOW_BATTLES_BODY = TranslationElement("showBattles.body")

    PANEL_WINRATE_POSITION_HEADER = TranslationElement("panelWinratePosition.header")
    PANEL_WINRATE_POSITION_BODY = TranslationElement("panelWinratePosition.body")
    PANEL_METRIC_HEADER = TranslationElement("panelMetric.header")
    PANEL_METRIC_BODY = TranslationElement("panelMetric.body")
    PANEL_METRIC_WINRATE = TranslationElement("panelMetric.winrate")
    PANEL_METRIC_WN8 = TranslationElement("panelMetric.wn8")

    RATING_MODE_HEADER = TranslationElement("ratingMode.header")
    RATING_MODE_BODY = TranslationElement("ratingMode.body")
    RATING_RECENT_WNX = TranslationElement("ratingMode.recentWnx")
    RATING_RECENT_WN8 = TranslationElement("ratingMode.recentWn8")
    RATING_OVERALL_WN8 = TranslationElement("ratingMode.overallWn8")
    RATING_OVERALL_WNX = TranslationElement("ratingMode.overallWnx")

    TOMATO_API_KEY_HEADER = TranslationElement("tomatoApiKey.header")
    TOMATO_API_KEY_BODY = TranslationElement("tomatoApiKey.body")
    TOMATO_API_KEY_NOTE = TranslationElement("tomatoApiKey.note")
    TOMATO_API_KEY_ATTENTION = TranslationElement("tomatoApiKey.attention")

    WINRATE_NEAR_ICON = TranslationElement("winratePosition.nearIcon")
    WINRATE_BEFORE_VEHICLE = TranslationElement("winratePosition.beforeVehicle")
    WINRATE_NONE = TranslationElement("winratePosition.none")

    WG_API_REGION_HEADER = TranslationElement("wgApiRegion.header")
    WG_API_REGION_BODY = TranslationElement("wgApiRegion.body")

    REGION_EU = TranslationElement("region.eu")
    REGION_NA = TranslationElement("region.na")
    REGION_ASIA = TranslationElement("region.asia")

    COLORIZE_VEHICLE_ICON_HEADER = TranslationElement("colorizeVehicleIcon.header")
    COLORIZE_VEHICLE_ICON_BODY = TranslationElement("colorizeVehicleIcon.body")


def getTranslation(key):
    if not g_translationManager._translationsLoaded:
        g_translationManager.loadTranslations()

    if key in g_translationManager._translationsMap:
        return g_translationManager._translationsMap[key]
    elif key in g_translationManager._defaultTranslationsMap:
        return g_translationManager._defaultTranslationsMap[key]
    else:
        return key.replace('.', ' ').replace('_', ' ').title()
