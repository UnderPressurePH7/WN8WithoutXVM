from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

from ..utils import logger, get_wn8_color, get_winrate_color, get_battles_color
from ..settings.config_param import g_configParams


def _format_battles(b):
    if not b:
        return ''
    if b >= 1000000:
        return '%.1fM' % (b / 1000000.0)
    if b >= 1000:
        return '%.1fk' % (b / 1000.0)
    return str(b)


def _build_suffix(stats):
    parts = []
    wn8 = int(stats.get('wn8', 0) or 0)
    winrate = float(stats.get('winrate', 0) or 0)
    battles = int(stats.get('battles', 0) or 0)

    if g_configParams.showWn8.value and wn8 > 0:
        parts.append("<font color='{}'>{}</font>".format(get_wn8_color(wn8), wn8))
    if g_configParams.showWinrate.value and winrate > 0:
        parts.append("<font color='{}'>{:.1f}%</font>".format(get_winrate_color(winrate), winrate))
    if g_configParams.showBattles.value and battles > 0:
        parts.append("<font color='{}'>{}</font>".format(get_battles_color(battles), _format_battles(battles)))

    if not parts:
        return ''
    return ' ' + ' '.join(parts)


class PatchStatsExchange(object):

    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    _PLAYER_NAME_FIELDS = ('playerName', 'playerFullName')
    _MARKER = u'\u200b'

    def __init__(self, stats_manager):
        self._stats_manager = stats_manager
        self._applied = False
        self._original_add = None
        self._vehicle_component_cls = None
        self._known_accounts = set()
        stats_manager.add_update_callback(self._on_stats_ready)

    def apply_patches(self):
        if self._applied:
            return True

        try:
            from gui.Scaleform.daapi.view.battle.shared.stats_exchange.vehicle import VehicleInfoComponent
        except Exception:
            logger.exception('[PatchStatsExchange] VehicleInfoComponent import failed')
            return False

        try:
            self._vehicle_component_cls = VehicleInfoComponent
            self._original_add = VehicleInfoComponent.addVehicleInfo

            original = self._original_add
            mod_self = self

            def patched_addVehicleInfo(component_self, vInfoVO, overrides):
                original(component_self, vInfoVO, overrides)
                mod_self._inject_stats(component_self, vInfoVO)

            VehicleInfoComponent.addVehicleInfo = patched_addVehicleInfo
            self._applied = True
            logger.debug('[PatchStatsExchange] VehicleInfoComponent patched')
            return True
        except Exception:
            logger.exception('[PatchStatsExchange] apply failed')
            return False

    def remove_patches(self):
        if not self._applied:
            return True
        try:
            if self._vehicle_component_cls is not None and self._original_add is not None:
                self._vehicle_component_cls.addVehicleInfo = self._original_add
                logger.debug('[PatchStatsExchange] VehicleInfoComponent restored')
        except Exception:
            logger.exception('[PatchStatsExchange] remove failed')
        self._vehicle_component_cls = None
        self._original_add = None
        self._applied = False
        self._known_accounts.clear()
        return True

    def _inject_stats(self, component, vInfoVO):
        try:
            account_id = getattr(getattr(vInfoVO, 'player', None), 'accountDBID', 0) or 0
            if not account_id:
                return

            data = getattr(component, '_data', None)
            if not isinstance(data, dict):
                return

            stats = self._stats_manager.get_cached_stats(account_id)
            if stats is None:
                if account_id not in self._known_accounts:
                    self._known_accounts.add(account_id)
                    self._stats_manager.get_player_stats(account_id)
                return

            suffix = _build_suffix(stats)
            if not suffix:
                return

            tagged_suffix = self._MARKER + suffix
            for field in self._PLAYER_NAME_FIELDS:
                value = data.get(field)
                if not value or not isinstance(value, basestring):
                    continue
                if self._MARKER in value:
                    idx = value.find(self._MARKER)
                    value = value[:idx]
                data[field] = value + tagged_suffix
        except Exception:
            logger.exception('[PatchStatsExchange] inject failed')

    def _on_stats_ready(self, account_id):
        if not self._applied:
            return
        try:
            sp = self.sessionProvider
            if sp is None:
                return
            arenaDP = sp.getArenaDP()
            if arenaDP is None:
                return

            found = False
            for vInfoVO in arenaDP.getVehiclesInfoIterator():
                if getattr(getattr(vInfoVO, 'player', None), 'accountDBID', 0) == account_id:
                    found = True
                    break
            if not found:
                return

            listeners = getattr(sp, '_BattleSessionProvider__arenaListeners', None)
            if listeners is None:
                return
            vehicles_listener = getattr(listeners, '_ListenersCollection__vehicles', None)
            if vehicles_listener is None:
                return
            vehicles_listener._invokeListenersMethod('invalidateVehiclesInfo', arenaDP)
        except Exception:
            logger.exception('[PatchStatsExchange] stats-ready refresh failed')
