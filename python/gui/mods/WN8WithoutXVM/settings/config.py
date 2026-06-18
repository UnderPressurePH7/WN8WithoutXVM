from .config_file import ConfigFile
from .config_param import ConfigParams, g_configParams, RatingMode
from .config_template import Template
from .translations import Translator
from ..utils import logger

try:
    from gui.modsSettingsApi import g_modsSettingsApi
except ImportError:
    logger.error("[Config] Failed to import g_modsSettingsApi")
    g_modsSettingsApi = None

MOD_LINKAGE = 'me.under-pressure.wn8withoutxvm'


class Config(object):

    def __init__(self):
        self.configParams = g_configParams
        self.configTemplate = Template(self.configParams)
        self.configFile = ConfigFile(self.configParams)
        self._loadedSuccessfully = False

        self._loadConfigFileToParams()

        if g_modsSettingsApi:
            self._registerMod()

    def _registerMod(self):
        if not g_modsSettingsApi:
            return

        try:
            self.configTemplate.setModDisplayName(Translator.MOD_NAME)

            self.configTemplate.addParameterToColumn1(
                "showWn8",
                header=Translator.SHOW_WN8_HEADER,
                body=Translator.SHOW_WN8_BODY
            )

            self.configTemplate.addParameterToColumn1(
                "showWinrate",
                header=Translator.SHOW_WINRATE_HEADER,
                body=Translator.SHOW_WINRATE_BODY
            )

            self.configTemplate.addParameterToColumn1(
                "showBattles",
                header=Translator.SHOW_BATTLES_HEADER,
                body=Translator.SHOW_BATTLES_BODY
            )

            self.configTemplate.addParameterToColumn2(
                "panelWinratePosition",
                header=Translator.PANEL_WINRATE_POSITION_HEADER,
                body=Translator.PANEL_WINRATE_POSITION_BODY
            )

            self.configTemplate.addParameterToColumn2(
                "panelMetric",
                header=Translator.PANEL_METRIC_HEADER,
                body=Translator.PANEL_METRIC_BODY
            )

            self.configTemplate.addParameterToColumn2(
                "ratingMode",
                header=Translator.RATING_MODE_HEADER,
                body=Translator.RATING_MODE_BODY
            )

            self.configTemplate.addParameterToColumn2(
                "wgApiRegion",
                header=Translator.WG_API_REGION_HEADER,
                body=Translator.WG_API_REGION_BODY
            )

            self.configTemplate.addParameterToColumn2(
                "tomatoApiKey",
                header=Translator.TOMATO_API_KEY_HEADER,
                body=Translator.TOMATO_API_KEY_BODY,
                note=Translator.TOMATO_API_KEY_NOTE,
                attention=Translator.TOMATO_API_KEY_ATTENTION
            )

            from .translations import getTranslation
            self.configTemplate.addParameterToColumn2(
                "colorizeVehicleIcon",
                header=getTranslation("colorizeVehicleIcon.header"),
                body=getTranslation("colorizeVehicleIcon.body")
            )

            template = self.configTemplate.generateTemplate()

            settings = g_modsSettingsApi.setModTemplate(
                MOD_LINKAGE,
                template,
                self._onSettingsChanged
            )

            if settings:
                self._applySettingsFromMsa(settings)

        except Exception as e:
            import traceback
            logger.error("[Config] Error registering mod template: %s", str(e))
            logger.error("[Config] Traceback: %s", traceback.format_exc())

    def _hasTomatoApiKey(self):
        try:
            key = getattr(self.configParams.tomatoApiKey, 'value', '')
            return bool(str(key).strip())
        except Exception:
            return False

    def _isTomatoRatingMode(self, mode):
        return mode in (
            RatingMode.RECENT_WNX,
            RatingMode.RECENT_WN8,
            RatingMode.OVERALL_WNX
        )

    def _enforceTomatoKeyRules(self):
        # Do not allow Tomato-only rating modes without a Tomato API key.
        try:
            currentMode = getattr(self.configParams.ratingMode, 'value', RatingMode.OVERALL_WN8)
            if self._isTomatoRatingMode(currentMode) and not self._hasTomatoApiKey():
                self.configParams.ratingMode.value = RatingMode.OVERALL_WN8
                logger.info("[Config] Tomato API key is empty. Rating mode was reset to Overall WN8.")
                return True
        except Exception as e:
            logger.error("[Config] Error enforcing Tomato API key rules: %s", str(e))
        return False

    def _applySettingsFromMsa(self, settings):
        try:
            configItems = self.configParams.items()
            for paramName, value in settings.items():
                if paramName in configItems:
                    param = configItems[paramName]
                    try:
                        param.msaValue = value
                    except Exception as e:
                        logger.error("[Config] Error applying MSA setting %s = %s: %s",
                            paramName, value, str(e))

            changed = self._enforceTomatoKeyRules()
            self.configFile.save_config()
            if changed:
                self.syncWithMsa()

        except Exception as e:
            logger.error("[Config] Error applying MSA settings: %s", str(e))

    def _onSettingsChanged(self, linkage, newSettings):
        if linkage != MOD_LINKAGE:
            return

        if not self._loadedSuccessfully:
            self._loadConfigFileToParams()
            if not self._loadedSuccessfully:
                return

        try:
            configItems = self.configParams.items()
            for tokenName, value in newSettings.items():
                if tokenName in configItems:
                    param = configItems[tokenName]
                    try:
                        param.msaValue = value
                    except Exception as e:
                        logger.error("[Config] Error setting parameter %s to %s: %s",
                            tokenName, value, str(e))

            changed = self._enforceTomatoKeyRules()
            self.configFile.save_config()
            if changed:
                self.syncWithMsa()

        except Exception as e:
            logger.error("[Config] Error updating settings from MSA: %s", str(e))

    def _loadConfigFileToParams(self):
        self._loadedSuccessfully = False

        try:
            success = self.configFile.load_config()
            if success:
                self._loadedSuccessfully = True

            changed = self._enforceTomatoKeyRules()

            if changed or not self.configFile.exists():
                self.configFile.save_config()

        except Exception as e:
            logger.error("[Config] Failed to load config: %s", str(e))
            configItems = self.configParams.items()
            for tokenName, param in configItems.items():
                param.value = param.defaultValue

    def syncWithMsa(self):
        try:
            if g_modsSettingsApi:
                currentSettings = {}
                configItems = self.configParams.items()
                for paramName, param in configItems.items():
                    currentSettings[paramName] = param.msaValue

                g_modsSettingsApi.updateModSettings(MOD_LINKAGE, currentSettings)
        except Exception as e:
            logger.error("[Config] Error in MSA sync: %s", str(e))
