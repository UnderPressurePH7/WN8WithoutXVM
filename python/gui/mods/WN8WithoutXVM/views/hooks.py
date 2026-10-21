# -*- coding: utf-8 -*-

import weakref
import BigWorld
from functools import wraps

from helpers import dependency
from PlayerEvents import g_playerEvents
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from skeletons.gui.battle_session import IBattleSessionProvider

from ..utils import (
    logger,
    get_wn8_color,
    get_winrate_color,
    get_battles_color,
    get_format_battles,
    ANON_RATING_TOKEN,
)
from ..settings.config_param import g_configParams


SEP = u'\t'


class PatchBattlePlayer(object):
    """Attach WN8 data to the stock Gameface battle TabView."""

    def __init__(self, stats_manager):
        self._stats_manager = stats_manager
        self._patches_applied = False
        self._active_players = {}
        self._last_payloads = {}
        self._original_fill_player_model = None
        self._original_invalidate_vehicles_info = None
        self._original_on_vehicle_added = None
        self._original_update_vehicles_stats = None
        self._death_refresh_scheduled = False
        stats_manager.add_update_callback(self._on_stats_updated)

    @staticmethod
    def _strip_payload(value):
        try:
            value = value or u''
            return value.split(SEP, 1)[0] if SEP in value else value
        except Exception:
            return value or u''

    @staticmethod
    def _vehicle_id(player):
        try:
            return player.getVehicleId() if player is not None else None
        except Exception:
            return None

    def _register_player(self, tab_view, player, vehicle_info):
        vehicle_id = self._vehicle_id(player)
        if not vehicle_id or not vehicle_info:
            return
        try:
            vehicle_name = self._strip_payload(player.getVehicleName())
        except Exception:
            vehicle_name = u''
        # Gameface can rebuild a dead vehicle's row with incomplete player
        # metadata. Keep the last known account ID for this vehicle in the
        # same TabView; otherwise a valid rating becomes the anonymous token.
        previous = self._active_players.get(vehicle_id)
        if previous is not None and previous[2]() is tab_view:
            old_info, old_name, _ = previous
            old_account_id = old_info.get('accountDBID') if old_info else None
            new_account_id = vehicle_info.get('accountDBID')
            if not new_account_id and old_account_id:
                vehicle_info = dict(vehicle_info)
                vehicle_info['accountDBID'] = old_account_id
            if not vehicle_name:
                vehicle_name = old_name
        self._active_players[vehicle_id] = (vehicle_info, vehicle_name, weakref.ref(tab_view))
        self._last_payloads.pop(vehicle_id, None)

    def _anonymous_payload(self, original_vehicle_name, account_id=None, mark_anonymous=False):
        return SEP.join((
            original_vehicle_name or u'', ANON_RATING_TOKEN,
            u'', u'', u'', u'', u'', u'', u'',
        ))

    def _build_payload(self, player, vehicle_info, original_vehicle_name):
        account_id = vehicle_info.get('accountDBID') if vehicle_info else None
        if not account_id:
            return self._anonymous_payload(original_vehicle_name)
        stats = self._stats_manager.get_cached_stats(account_id)
        if not stats:
            return self._anonymous_payload(original_vehicle_name)
        wn8 = int(stats.get('wn8', 0) or 0)
        rating = int(stats.get('selected_rating') or wn8 or 0)
        winrate = float(stats.get('winrate', 0) or 0)
        battles = int(stats.get('battles', 0) or 0)
        if not rating and not winrate and not battles:
            return self._anonymous_payload(original_vehicle_name)
        wn8_text = str(rating) if g_configParams.showWn8.value and rating else u''
        winrate_text = ('%.1f%%' % winrate) if g_configParams.showWinrate.value and winrate else u''
        battles_text = get_format_battles(battles) if g_configParams.showBattles.value and battles else u''
        wn8_color = stats.get('selected_rating_color') or (
            get_wn8_color(rating) if rating else '#FFFFFF'
        )
        wr_color = stats.get('winrate_color') or (
            get_winrate_color(winrate) if winrate else '#FFFFFF'
        )
        battles_color = stats.get('battles_color') or (
            get_battles_color(battles) if battles else '#FFFFFF'
        )
        return SEP.join((
            original_vehicle_name or u'', wn8_text, wn8_color,
            winrate_text, wr_color, battles_text, battles_color, u'', u'',
        ))

    def _set_values(self, player, payload):
        try:
            if player is None or not hasattr(player, 'setVehicleName'):
                return False
            try:
                if player.getVehicleName() == payload:
                    return True
            except Exception:
                pass
            player.setVehicleName(payload)
            return True
        except Exception as e:
            logger.debug('[PatchBattlePlayer] set values failed: %s', e)
            return False

    def _refresh_vehicle(self, tab_view, vehicle_id):
        active = self._active_players.get(vehicle_id)
        if tab_view is None or active is None:
            return False
        vehicle_info, original_vehicle_name, tv_ref = active
        try:
            if tv_ref() is not tab_view:
                return False
            payload = self._build_payload(None, vehicle_info, original_vehicle_name)
            # The stock TabView can overwrite vehicleName during a vehicle
            # status refresh (including destruction). Compare against the
            # actual Gameface model, not only our last sent payload.
            with tab_view.modifyBattlePlayer(vehicle_id) as current_player:
                if current_player is None:
                    return False
                if not self._set_values(current_player, payload):
                    return False
                self._last_payloads[vehicle_id] = payload
                return True
        except Exception as e:
            logger.debug('[PatchBattlePlayer] refresh failed vehicle=%s: %s', vehicle_id, e)
            return False

    def _refresh_view(self, tab_view):
        refreshed = 0
        for vehicle_id, active in list(self._active_players.items()):
            try:
                if active[2]() is tab_view and self._refresh_vehicle(tab_view, vehicle_id):
                    refreshed += 1
            except Exception:
                pass
        return refreshed

    def _on_stats_updated(self, account_id):
        for vehicle_id, active in list(self._active_players.items()):
            vehicle_info, _, tv_ref = active
            if vehicle_info.get('accountDBID') != account_id:
                continue
            try:
                tab_view = tv_ref()
            except Exception:
                tab_view = None
            if tab_view is not None:
                self._last_payloads.pop(vehicle_id, None)
                self._refresh_vehicle(tab_view, vehicle_id)

    def _schedule_battle_stats_refresh(self):
        # BattleStatisticsDataController receives destruction/status updates,
        # while TabView._invalidateVehiclesInfo may not run for those updates.
        if self._death_refresh_scheduled or not self._active_players:
            return
        self._death_refresh_scheduled = True
        def _refresh():
            self._death_refresh_scheduled = False
            views = {}
            for vehicle_id, active in list(self._active_players.items()):
                view = active[2]()
                if view is not None:
                    views[id(view)] = view
            for view in views.values():
                self._refresh_view(view)
        BigWorld.callback(0.1, _refresh)

    def _monkey_patch_tab_view(self):
        try:
            from gui.impl.battle.battle_page.tab_view import TabView
        except Exception as e:
            logger.error('[PatchBattlePlayer] TabView import failed: %s', e)
            return False
        try:
            self._original_fill_player_model = TabView._fillPlayerModel
            self._original_invalidate_vehicles_info = TabView._invalidateVehiclesInfo
            self._original_on_vehicle_added = TabView._onVehicleAdded
            from gui.Scaleform.daapi.view.battle.shared.stats_exchange.stats_ctrl import BattleStatisticsDataController
            self._original_update_vehicles_stats = BattleStatisticsDataController.updateVehiclesStats

            @wraps(self._original_fill_player_model)
            def patched_fill_player_model(tab_view, vehicle_id, vehicle_info):
                player = self._original_fill_player_model(tab_view, vehicle_id, vehicle_info)
                if player is not None and vehicle_info:
                    self._register_player(tab_view, player, vehicle_info)
                    current_vehicle_id = self._vehicle_id(player)
                    active = self._active_players.get(current_vehicle_id)
                    if active is not None:
                        # Use the resolved player info rather than the possibly
                        # incomplete update delivered by Gameface.
                        payload = self._build_payload(player, active[0], active[1])
                        if self._set_values(player, payload):
                            self._last_payloads[current_vehicle_id] = payload
                return player

            @wraps(self._original_invalidate_vehicles_info)
            def patched_invalidate_vehicles_info(tab_view, *args, **kwargs):
                result = self._original_invalidate_vehicles_info(tab_view, *args, **kwargs)
                self._refresh_view(tab_view)
                return result

            @wraps(self._original_on_vehicle_added)
            def patched_on_vehicle_added(tab_view, vehicle_id, *args, **kwargs):
                result = self._original_on_vehicle_added(tab_view, vehicle_id, *args, **kwargs)
                self._last_payloads.pop(vehicle_id, None)
                self._refresh_vehicle(tab_view, vehicle_id)
                return result

            @wraps(self._original_update_vehicles_stats)
            def patched_update_vehicles_stats(ctrl, updated, arena_dp):
                result = self._original_update_vehicles_stats(ctrl, updated, arena_dp)
                self._schedule_battle_stats_refresh()
                return result

            BattleStatisticsDataController.updateVehiclesStats = patched_update_vehicles_stats
            TabView._fillPlayerModel = patched_fill_player_model
            TabView._invalidateVehiclesInfo = patched_invalidate_vehicles_info
            TabView._onVehicleAdded = patched_on_vehicle_added
            logger.info('[PatchBattlePlayer] stock Gameface TabView and vehicle stats hooks installed')
            return True
        except Exception:
            logger.exception('[PatchBattlePlayer] TabView patch failed')
            return False

    def apply_patches(self):
        if self._patches_applied:
            return True
        self._patches_applied = self._monkey_patch_tab_view()
        return self._patches_applied

    def remove_patches(self):
        try:
            if self._stats_manager is not None:
                try:
                    self._stats_manager.remove_update_callback(self._on_stats_updated)
                except Exception:
                    pass
            if self._patches_applied:
                from gui.impl.battle.battle_page.tab_view import TabView
                from gui.Scaleform.daapi.view.battle.shared.stats_exchange.stats_ctrl import BattleStatisticsDataController
                if self._original_update_vehicles_stats is not None:
                    BattleStatisticsDataController.updateVehiclesStats = self._original_update_vehicles_stats
                if self._original_fill_player_model is not None:
                    TabView._fillPlayerModel = self._original_fill_player_model
                if self._original_invalidate_vehicles_info is not None:
                    TabView._invalidateVehiclesInfo = self._original_invalidate_vehicles_info
                if self._original_on_vehicle_added is not None:
                    TabView._onVehicleAdded = self._original_on_vehicle_added
            self._active_players.clear()
            self._last_payloads.clear()
            self._patches_applied = False
            return True
        except Exception as e:
            logger.debug('[PatchBattlePlayer] remove failed: %s', e)
            return False

    def is_patched(self):
        return self._patches_applied


class _WN8PrefetchController(IArenaVehiclesController):
    __slots__ = ('_stats_manager', '_fetched')

    def __init__(self, stats_manager):
        super(_WN8PrefetchController, self).__init__()
        self._stats_manager = stats_manager
        self._fetched = set()

    def getControllerID(self):
        return 0

    def startControl(self, battleCtx, arenaVisitor):
        self._fetched.clear()

    def stopControl(self):
        self._fetched.clear()

    def invalidateArenaInfo(self):
        pass

    def invalidateVehiclesInfo(self, arenaDP):
        try:
            for vo in arenaDP.getVehiclesInfoIterator():
                self._request(vo)
        except Exception:
            logger.exception('[WN8Prefetch] invalidateVehiclesInfo failed')

    def addVehicleInfo(self, vo, arenaDP):
        self._request(vo)

    def updateVehiclesInfo(self, updated, arenaDP):
        try:
            for _flags, vo in updated:
                self._request(vo)
        except Exception:
            logger.exception('[WN8Prefetch] updateVehiclesInfo failed')

    def _request(self, vo):
        try:
            account_id = getattr(getattr(vo, 'player', None), 'accountDBID', 0) or 0
            if not account_id or account_id in self._fetched:
                return
            self._fetched.add(account_id)
            logger.debug('[WN8Prefetch] prefetch stats for %s', account_id)
            self._stats_manager.get_player_stats(account_id)
        except Exception:
            logger.exception('[WN8Prefetch] request failed')


class PatchBattleLoading(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, stats_manager):
        self._stats_manager = stats_manager
        self._controller = _WN8PrefetchController(stats_manager)
        self._subscribed = False
        self._registered = False

    def apply_patches(self):
        if self._subscribed:
            return True
        g_playerEvents.onAvatarReady += self._register
        g_playerEvents.onAvatarBecomeNonPlayer += self._unregister
        self._subscribed = True
        logger.debug('[PatchBattleLoading] Subscribed to PlayerEvents')
        return True

    def remove_patches(self):
        self._unregister()
        if self._subscribed:
            try:
                g_playerEvents.onAvatarReady -= self._register
                g_playerEvents.onAvatarBecomeNonPlayer -= self._unregister
            except Exception:
                logger.exception('[PatchBattleLoading] unsubscribe failed')
            self._subscribed = False
        return True

    def _register(self):
        if self._registered:
            return
        try:
            if self.sessionProvider is None:
                logger.debug('[PatchBattleLoading] No sessionProvider yet')
                return
            if self.sessionProvider.addArenaCtrl(self._controller):
                self._registered = True
                logger.debug('[PatchBattleLoading] Prefetch controller registered')
            else:
                logger.debug('[PatchBattleLoading] addArenaCtrl returned False')
        except Exception:
            logger.exception('[PatchBattleLoading] register failed')

    def _unregister(self):
        if not self._registered:
            return
        try:
            if self.sessionProvider is not None:
                self.sessionProvider.removeArenaCtrl(self._controller)
                logger.debug('[PatchBattleLoading] Prefetch controller removed')
        except Exception:
            logger.exception('[PatchBattleLoading] unregister failed')
        finally:
            self._registered = False


class ModePanelAdapters(object):
    """Install redraw hooks only for non-classic player-panel variants."""

    _INVALIDATE_METHODS = (
        'invalidateVehicleStatus', 'invalidateVehicleInfo', '_invalidateVehicle',
        'as_invalidateVehicleStatusS', 'updateVehiclesData',
    )
    _MODE_METHODS = (
        'setInitialMode', 'setLargeMode', '_handleNextMode',
        'as_setPanelModeS', 'tryToSetPanelModeByMouse',
    )

    def __init__(self, events):
        self._events = events
        self._patched = []
        self._applied = False

    def apply_patches(self):
        if self._applied:
            return
        panel_classes = []
        self._append_optional(panel_classes, 'comp7_core.gui.Scaleform.daapi.view.battle.players_panel', 'PlayersPanel', 'Comp7 Core/Light')
        self._append_optional(panel_classes, 'gui.Scaleform.daapi.view.battle.comp7.players_panel', 'PlayersPanel', 'Comp7 legacy')
        self._append_optional(panel_classes, 'gui.Scaleform.daapi.view.battle.epic_random.players_panel', 'EpicRandomPlayersPanel', 'Epic Random')
        self._append_optional(panel_classes, 'gui.Scaleform.daapi.view.battle.epic_random.players_panel', 'PlayersPanel', 'Epic Random legacy')
        seen = set()
        for panel_class, label in panel_classes:
            if panel_class in seen:
                continue
            seen.add(panel_class)
            self._patch_panel_class(panel_class, label)
        self._applied = True
        logger.debug('[ModePanelAdapters] Applied %d hooks', len(self._patched))

    def remove_patches(self):
        while self._patched:
            cls, method_name, original = self._patched.pop()
            try:
                setattr(cls, method_name, original)
            except Exception:
                logger.exception('[ModePanelAdapters] Failed restoring %s.%s', getattr(cls, '__name__', cls), method_name)
        self._applied = False

    def _append_optional(self, target, module_name, class_name, label):
        try:
            module = __import__(module_name, fromlist=[class_name])
            panel_class = getattr(module, class_name, None)
            if panel_class is not None:
                target.append((panel_class, label))
        except Exception as error:
            logger.debug('[ModePanelAdapters] %s unavailable (%s.%s): %s', label, module_name, class_name, error)

    def _patch_panel_class(self, panel_class, label):
        patched_names = set()
        for method_name in self._INVALIDATE_METHODS + self._MODE_METHODS:
            if method_name in patched_names or not hasattr(panel_class, method_name):
                continue
            original = getattr(panel_class, method_name)
            if not callable(original):
                continue
            setattr(panel_class, method_name, self._make_wrapper(original, method_name))
            self._patched.append((panel_class, method_name, original))
            patched_names.add(method_name)
            logger.debug('[ModePanelAdapters] Patched %s.%s', label, method_name)

    def _make_wrapper(self, original, method_name):
        events = self._events

        def wrapped(panel_self, *args, **kwargs):
            result = original(panel_self, *args, **kwargs)
            try:
                events._onPanelModeChanged(panel_self)
            except Exception:
                logger.exception('[ModePanelAdapters] Refresh failed after %s', method_name)
            return result

        wrapped.__name__ = getattr(original, '__name__', method_name)
        wrapped.__doc__ = getattr(original, '__doc__', None)
        return wrapped
