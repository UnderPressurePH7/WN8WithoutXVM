from .config_param_types import (
    CheckboxParameter,
    DropdownParameter,
    OptionItem,
    TextInputParameter
)
from .translations import Translator


class WinratePosition(object):
    NEAR_ICON = 'near_icon'
    BEFORE_VEHICLE = 'before_vehicle'
    NONE = 'none'


class PanelMetric(object):
    WINRATE = 'winrate'
    WN8 = 'wn8'



class RatingMode(object):
    RECENT_WNX = 'recent_wnx'
    RECENT_WN8 = 'recent_wn8'
    OVERALL_WN8 = 'overall_wn8'
    OVERALL_WNX = 'overall_wnx'


class ApiRegion(object):
    EU = 'eu'
    NA = 'na'
    ASIA = 'asia'


class ConfigParams(object):

    def __init__(self):
        self.enabled = CheckboxParameter(
            ['enabled'],
            defaultValue=True
        )

        self.showWn8 = CheckboxParameter(
            ['show-wn8'],
            defaultValue=True
        )

        self.showWinrate = CheckboxParameter(
            ['show-winrate'],
            defaultValue=True
        )

        self.showBattles = CheckboxParameter(
            ['show-battles'],
            defaultValue=True
        )

        self.panelWinratePosition = DropdownParameter(
            ['panel-winrate-position'],
            [
                OptionItem(WinratePosition.NEAR_ICON, 0, Translator.WINRATE_NEAR_ICON),
                OptionItem(WinratePosition.BEFORE_VEHICLE, 1, Translator.WINRATE_BEFORE_VEHICLE),
                OptionItem(WinratePosition.NONE, 2, Translator.WINRATE_NONE),
            ],
            defaultValue=WinratePosition.NEAR_ICON
        )

        self.panelMetric = DropdownParameter(
            ['panel-metric'],
            [
                OptionItem(PanelMetric.WINRATE, 0, Translator.PANEL_METRIC_WINRATE),
                OptionItem(PanelMetric.WN8, 1, Translator.PANEL_METRIC_WN8),
            ],
            defaultValue=PanelMetric.WINRATE
        )

        self.ratingMode = DropdownParameter(
            ['rating-mode'],
            [
                OptionItem(RatingMode.RECENT_WNX, 0, Translator.RATING_RECENT_WNX),
                OptionItem(RatingMode.RECENT_WN8, 1, Translator.RATING_RECENT_WN8),
                OptionItem(RatingMode.OVERALL_WN8, 2, Translator.RATING_OVERALL_WN8),
                OptionItem(RatingMode.OVERALL_WNX, 3, Translator.RATING_OVERALL_WNX),
            ],
            defaultValue=RatingMode.OVERALL_WN8
        )

        self.wgApiRegion = DropdownParameter(
            ['wg-api-region'],
            [
                OptionItem(ApiRegion.EU, 0, Translator.REGION_EU),
                OptionItem(ApiRegion.NA, 1, Translator.REGION_NA),
                OptionItem(ApiRegion.ASIA, 2, Translator.REGION_ASIA),
            ],
            defaultValue=ApiRegion.EU
        )

        self.tomatoApiKey = TextInputParameter(
            ['tomato-api-key'],
            defaultValue=''
        )

        self.colorizeVehicleIcon = CheckboxParameter(
            ['colorize-vehicle-icon'],
            defaultValue=True
        )

    def items(self):
        result = {}
        for attrName in dir(self):
            if not attrName.startswith('_') and attrName != 'items':
                try:
                    attr = getattr(self, attrName)
                    if hasattr(attr, 'tokenName') and hasattr(attr, 'defaultValue'):
                        result[attr.tokenName] = attr
                except Exception:
                    continue
        return result


g_configParams = ConfigParams()
