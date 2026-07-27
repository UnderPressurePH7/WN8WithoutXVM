import BigWorld
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent

from gui.battle_control.arena_info import vos_collections

from ..utils import logger, get_anonymize_icon_html, ANON_ICON_PANEL_SIZE
from ..settings.config_param import g_configParams, WinratePosition, PanelMetric

try:
    from .player_panel import g_events, TYPE_PP
    HAS_PANEL_CORE_UI = g_events is not None
except Exception as e:
    logger.error('[PanelView] playerPanel import failed: %s', e)
    HAS_PANEL_CORE_UI = False
    g_events = None
    TYPE_PP = 'pp'


class PanelView(CallbackDelayer):

    CONTAINER_PP_WINRATE = 'wn8withoutxvm_pp_winrate'
    CONTAINER_PP_ANON = 'wn8withoutxvm_pp_anon'
    CONTAINER_VEHICLE_NAME = 'wn8withoutxvm_vehicle_name'

    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, statsManager):
        CallbackDelayer.__init__(self)
        self._statsManager = statsManager
        self._isInitialized = False
        self._hasPanelCoreUI = HAS_PANEL_CORE_UI
        self._containersCreated = False
        self._arena = None
        self._updatedVehicles = set()
        self._vehicleAccountMap = {}
        self._accountVehicleMap = {}
        self._createdContainers = []
        self._pendingStats = {}
        self._lastUpdateTime = 0
        self._playerTeam = None
        logger.debug('[PanelView] Initialized (hasPanelCoreUI: %s)', self._hasPanelCoreUI)

    def setArena(self, arena):
        self._arena = arena
        self._updatedVehicles.clear()
        self._vehicleAccountMap.clear()
        self._accountVehicleMap.clear()
        self._pendingStats.clear()
        if arena:
            self._buildVehicleMaps()
        logger.debug('[PanelView] Arena set: %s', arena is not None)

    def _buildVehicleMaps(self):
        if not self._arena or not self._arena.vehicles:
            return
        for vehicleID, vehicleData in self._arena.vehicles.items():
            accountDBID = vehicleData.get('accountDBID')
            if accountDBID:
                self._vehicleAccountMap[vehicleID] = accountDBID
                self._accountVehicleMap[accountDBID] = vehicleID

    def initialize(self):
        if not self._hasPanelCoreUI or self._isInitialized:
            return self._isInitialized
        try:
            if g_events:
                g_events.updateMode += self._onUpdateMode
                g_events.onUIReady += self._onUIReady
            g_eventBus.addListener(GameEvent.FULL_STATS, self._onFullStats, EVENT_BUS_SCOPE.BATTLE)
            self._isInitialized = True
            if g_events and g_events.viewLoad:
                self.delayCallback(0.3, self._initializeContainers)
            logger.debug('[PanelView] Initialized')
            return True
        except Exception as e:
            logger.error('[PanelView] initialize error: %s', e)
            return False

    def _onUIReady(self, *args):
        logger.debug('[PanelView] UI Ready')
        self.delayCallback(0.2, self._initializeContainers)

    def _initializeContainers(self):
        if not self._containersCreated:
            self._createContainers()
        self._processAllPlayers()

    def _onUpdateMode(self):
        currentTime = BigWorld.time()
        if currentTime - self._lastUpdateTime < 0.05:
            return
        self._lastUpdateTime = currentTime
        self._scheduleReapplyAllColors()

    def _onFullStats(self, event):
        self._scheduleReapplyAllColors()

    def _scheduleReapplyAllColors(self):
        self._reapplyAllColors()
        for delay in (0.05, 0.15, 0.30, 0.60, 1.00, 1.50, 2.00, 3.00):
            BigWorld.callback(delay, self._reapplyAllColors)

    def _reapplyAllColors(self):
        if not self._hasPanelCoreUI or not g_events or not g_events.viewLoad:
            return
        try:
            arena = self._getArena()
            if not arena or not arena.vehicles:
                return
            arenaDP = self._getArenaDP()
            if not arenaDP:
                return
            for vehicleID, vehicleData in arena.vehicles.items():
                accountDBID = vehicleData.get('accountDBID')
                if not accountDBID:
                    continue
                stats = self._statsManager.get_cached_stats(accountDBID)
                if stats:
                    self._reapplyVehicleColors(vehicleID, vehicleData, stats, arenaDP)
            # Scaleform Full Stats (Comp7 and legacy modes) is created only
            # after TAB is pressed. Re-send the rows on every FULL_STATS burst.
            self._pushTabOverlays(arenaDP)
        except Exception as e:
            logger.error('[PanelView] _reapplyAllColors error: %s', e)

    def _createContainers(self):
        if self._containersCreated:
            return
        if not self._hasPanelCoreUI or not g_events or not g_events.viewLoad:
            logger.debug('[PanelView] Cannot create containers - not ready')
            return
        if not g_events.componentUI:
            logger.debug('[PanelView] Cannot create containers - no componentUI')
            return

        try:
            self._createdContainers = []
            g_events.createPP(self.CONTAINER_PP_ANON, self._buildPpAnonConfig())
            self._createdContainers.append(self.CONTAINER_PP_ANON)
            logger.debug('[PanelView] PP anonymous icon container created')

            if g_configParams.panelWinratePosition.value == WinratePosition.NEAR_ICON:
                g_events.createPP(self.CONTAINER_PP_WINRATE, self._buildPpWinrateConfig())
                self._createdContainers.append(self.CONTAINER_PP_WINRATE)
                logger.debug('[PanelView] PP Winrate container created')

            self._containersCreated = True
            logger.debug('[PanelView] Containers created: %s', self._createdContainers)

            if self._pendingStats:
                logger.debug('[PanelView] Processing %s pending stats', len(self._pendingStats))
                for accountDBID, stats in self._pendingStats.items():
                    self._updatePlayerDisplay(accountDBID, stats)
                self._pendingStats.clear()
        except Exception as e:
            logger.error('[PanelView] _createContainers error: %s', e)


    def _buildPpAnonConfig(self):
        state_offsets_left = {'state%d' % s: {'x': 10, 'y': 3} for s in range(8)}
        state_offsets_right = {'state%d' % s: {'x': -24, 'y': 3} for s in range(8)}
        return {
            'textKey': 'pp_anon',
            'holder': 'vehicleIcon',
            'child': 'vehicleTF',
            'left': {
                'x': 10, 'y': 3, 'width': 20, 'height': 20, 'align': 'left',
                'hideInStates': [8], 'stateOffsets': state_offsets_left,
            },
            'right': {
                'x': -24, 'y': 3, 'width': 20, 'height': 20, 'align': 'right',
                'hideInStates': [8], 'stateOffsets': state_offsets_right,
            },
            'shadow': {
                'distance': 0, 'angle': 90, 'color': '#000000',
                'alpha': 100, 'size': 2, 'strength': 200,
            },
        }

    def _buildPpWinrateConfig(self):
        # Трохи ближче до танка/іконки, як у режимі з ніками.
        state_offsets_left = {'state%d' % s: {'x': 20, 'y': 4} for s in range(8)}
        state_offsets_right = {'state%d' % s: {'x': -70, 'y': 4} for s in range(8)}
        return {
            'textKey': 'pp_winrate',
            'holder': 'vehicleIcon',
            'child': 'vehicleTF',
            'left': {
                'x': 28, 'y': 4, 'width': 50, 'height': 20, 'align': 'left',
                'hideInStates': [8], 'stateOffsets': state_offsets_left,
            },
            'right': {
                'x': -78, 'y': 4, 'width': 50, 'height': 20, 'align': 'right',
                'hideInStates': [8], 'stateOffsets': state_offsets_right,
            },
            'shadow': {
                'distance': 0, 'angle': 90, 'color': '#000000',
                'alpha': 100, 'size': 2, 'strength': 200,
            },
        }

    def _buildVehicleNameConfig(self):
        state_offsets = {'state%d' % s: {'x': 0, 'y': 0} for s in range(8)}
        return {
            'textKey': 'vehicle_name',
            'holder': 'vehicleTF',
            'child': 'vehicleTF',
            'left': {
                'x': 0, 'y': 0, 'width': 105, 'height': 20, 'align': 'right',
                'hideInStates': [8], 'stateOffsets': state_offsets,
            },
            'right': {
                'x': 0, 'y': 0, 'width': 105, 'height': 20, 'align': 'right',
                'hideInStates': [8], 'stateOffsets': state_offsets,
            },
            'shadow': {
                'distance': 0, 'angle': 90, 'color': '#000000',
                'alpha': 100, 'size': 2, 'strength': 200,
            },
        }

    def _applyOverlayName(self, vehicleID, playerInfo, team):
        return

    def _getArena(self):
        if self._arena is not None:
            return self._arena
        try:
            player = BigWorld.player()
            if player and hasattr(player, 'arena'):
                return player.arena
        except Exception as e:
            logger.debug('[PanelView] _getArena error: %s', e)
        return None

    def _getArenaDP(self):
        try:
            sp = self.sessionProvider
            if sp is not None:
                return sp.getArenaDP()
        except Exception as e:
            logger.debug('[PanelView] _getArenaDP error: %s', e)
        return None

    def _processAllPlayers(self):
        if not self._hasPanelCoreUI or not g_events or not g_events.viewLoad:
            return
        try:
            if not self._containersCreated:
                self._createContainers()
                if not self._containersCreated:
                    logger.debug('[PanelView] Containers not ready, retrying...')
                    self.delayCallback(0.5, self._processAllPlayers)
                    return

            arena = self._getArena()
            if not arena or not arena.vehicles:
                return
            arenaDP = self._getArenaDP()
            if not arenaDP:
                return

            self._buildVehicleMaps()
            for vehicleID, vehicleData in arena.vehicles.items():
                accountDBID = vehicleData.get('accountDBID')
                stats = self._statsManager.get_cached_stats(accountDBID) if accountDBID else None

                # Простий режим: якщо для рядка немає стати і в оригіналі там були прочерки,
                # показуємо біля нього іконку анонімайзера.
                if not stats:
                    self._applyNoStatsAnonymousIcon(vehicleID, True)
                    continue

                self._applyStatsToVehicle(vehicleID, vehicleData, stats, arenaDP)
                self._updatedVehicles.add(vehicleID)

            self._pushTabOverlays(arenaDP)
        except Exception as e:
            logger.error('[PanelView] _processAllPlayers error: %s', e)

    def _applyStatsToVehicle(self, vehicleID, vehicleData, stats, arenaDP):
        if not g_events or not g_events.componentUI:
            return
        try:
            listItem = g_events.getPPListItem(vehicleID)
            if not listItem:
                return

            accountDBID = vehicleData.get('accountDBID')
            isAlly = arenaDP.isAllyTeam(vehicleData['team'])
            team = 'left' if isAlly else 'right'

            if stats and stats.get('anonymous'):
                self._applyAnonymousPlayer(listItem, vehicleID, team)
                return
            if not accountDBID:
                self._applyNoStatsAnonymousIcon(vehicleID, True)
                return

            self._applyNoStatsAnonymousIcon(vehicleID, False)

            playerInfo = {
                'wn8': stats.get('wn8', 0),
                'wn8_color': stats.get('wn8_color', '#FFFFFF'),
                'selected_rating': stats.get('selected_rating', stats.get('wn8', 0)),
                'selected_rating_color': stats.get('selected_rating_color', stats.get('wn8_color', '#FFFFFF')),
                'selected_rating_name': stats.get('selected_rating_name', 'WN8'),
                'winrate': stats.get('winrate', 0),
                'winrate_color': stats.get('winrate_color', '#FFFFFF'),
                'nick': vehicleData.get('name', ''),
                'vehicle': self._getVehicleName(vehicleData),
            }

            self._applyPlayerNameWithWN8(listItem, playerInfo, team)
            self._applyWinrateDisplay(vehicleID, listItem, playerInfo, team)
            self._applyVehicleNameColor(vehicleID, listItem, playerInfo)
            self._applyOverlayName(vehicleID, playerInfo, team)
        except Exception as e:
            logger.error('[PanelView] _applyStatsToVehicle error for %s: %s', vehicleID, e)

    def _applyVehicleNameColor(self, vehicleID, listItem, playerInfo):
        try:
            vehicleColor = playerInfo.get('selected_rating_color') or playerInfo.get('wn8_color') or '#FFFFFF'
            g_events.setPanelTextColor(vehicleID, vehicleColor)
        except Exception as e:
            logger.error('[PanelView] _applyVehicleNameColor error for %s: %s', vehicleID, e)

    def _isVehicleNameVisible(self, listItem):
        try:
            if not listItem or (hasattr(listItem, 'visible') and not listItem.visible):
                return False
            if not hasattr(listItem, 'vehicleTF') or not listItem.vehicleTF:
                return False
            tf = listItem.vehicleTF
            if hasattr(tf, 'visible') and not tf.visible:
                return False
            if hasattr(tf, 'width') and tf.width <= 1:
                return False
            if hasattr(tf, 'height') and tf.height <= 1:
                return False
            return True
        except Exception:
            return True

    def _setVehicleNameOverlay(self, vehicleID, text):
        g_events.update(self.CONTAINER_VEHICLE_NAME, {
            'vehicleID': vehicleID,
            'text': text,
        })
        g_events.updatePosition(self.CONTAINER_VEHICLE_NAME, vehicleID)

    def _clearOriginalVehicleName(self, listItem):
        try:
            if hasattr(listItem, 'vehicleTF') and listItem.vehicleTF:
                listItem.vehicleTF.htmlText = ''
                listItem.vehicleTF.text = ''
                listItem.vehicleTF.alpha = 0
        except Exception:
            pass

    def _applyPlayerNameWithWN8(self, listItem, playerInfo, team):
        return

    def _getPanelMetricText(self, playerInfo):
        try:
            metric = g_configParams.panelMetric.value
        except Exception:
            metric = PanelMetric.WINRATE

        if metric == PanelMetric.WN8:
            value = int(playerInfo.get('selected_rating') or playerInfo.get('wn8') or 0)
            if not value:
                return '', '#FFFFFF'
            return str(value), playerInfo.get('selected_rating_color') or playerInfo.get('wn8_color') or '#FFFFFF'

        try:
            value = float(playerInfo.get('winrate') or 0)
        except Exception:
            value = 0
        if not value:
            return '', '#FFFFFF'
        valueText = ('%.2f' % value).rstrip('0').rstrip('.') + '%'
        return valueText, playerInfo.get('winrate_color') or '#FFFFFF'

    def _applyWinrateDisplay(self, vehicleID, listItem, playerInfo, team):
        winratePosition = g_configParams.panelWinratePosition.value
        statText, statColor = self._getPanelMetricText(playerInfo)
        if winratePosition == WinratePosition.NEAR_ICON:
            if self.CONTAINER_PP_WINRATE in self._createdContainers:
                displayText = "<font color='{}' size='10'><b>{}</b></font>".format(
                    statColor, statText) if statText else ''
                g_events.update(self.CONTAINER_PP_WINRATE, {
                    'vehicleID': vehicleID,
                    'text': displayText,
                })
                g_events.updatePosition(self.CONTAINER_PP_WINRATE, vehicleID)
        elif winratePosition == WinratePosition.BEFORE_VEHICLE:
            # The stock vehicle field is colored in AS3. Adding text before it
            # would require an overlay again and reintroduce mode-switch jumps.
            pass

    def _applyAnonymousIcon(self, vehicleID, visible):
        try:
            if self.CONTAINER_PP_ANON in self._createdContainers:
                g_events.update(self.CONTAINER_PP_ANON, {
                    'vehicleID': vehicleID,
                    'text': get_anonymize_icon_html(ANON_ICON_PANEL_SIZE) if visible else '',
                })
                g_events.updatePosition(self.CONTAINER_PP_ANON, vehicleID)
        except Exception as e:
            logger.error('[PanelView] update anonymous panel icon failed for %s: %s', vehicleID, e)

    def _applyNoStatsAnonymousIcon(self, vehicleID, visible=True):
        # Для цього моду немає 100% надійного прапорця аноніма в panel data.
        # Тому використовуємо просту логіку: немає стати / були прочерки => ставимо іконку.
        self._applyAnonymousIcon(vehicleID, visible)
        if visible and self.CONTAINER_PP_WINRATE in self._createdContainers:
            try:
                g_events.update(self.CONTAINER_PP_WINRATE, {
                    'vehicleID': vehicleID,
                    'text': '',
                })
                g_events.updatePosition(self.CONTAINER_PP_WINRATE, vehicleID)
            except Exception:
                pass

    def _applyAnonymousPlayer(self, listItem, vehicleID, team):
        try:
            self._applyAnonymousIcon(vehicleID, True)
            if g_configParams.panelWinratePosition.value == WinratePosition.NEAR_ICON:
                if self.CONTAINER_PP_WINRATE in self._createdContainers:
                    g_events.update(self.CONTAINER_PP_WINRATE, {
                        'vehicleID': vehicleID,
                        'text': '',
                    })
                    g_events.updatePosition(self.CONTAINER_PP_WINRATE, vehicleID)
        except Exception as e:
            logger.error('[PanelView] _applyAnonymousPlayer error: %s', e)

    def _reapplyVehicleColors(self, vehicleID, vehicleData, stats, arenaDP):
        if not g_events or not g_events.componentUI:
            return
        try:
            listItem = g_events.getPPListItem(vehicleID)
            if not listItem:
                return
            accountDBID = vehicleData.get('accountDBID')
            if stats and stats.get('anonymous'):
                self._applyAnonymousPlayer(listItem, vehicleID, 'left' if arenaDP.isAllyTeam(vehicleData['team']) else 'right')
                return
            if not accountDBID:
                self._applyNoStatsAnonymousIcon(vehicleID, True)
                return

            self._applyNoStatsAnonymousIcon(vehicleID, False)

            playerInfo = {
                'wn8': stats.get('wn8', 0),
                'wn8_color': stats.get('wn8_color', '#FFFFFF'),
                'selected_rating': stats.get('selected_rating', stats.get('wn8', 0)),
                'selected_rating_color': stats.get('selected_rating_color', stats.get('wn8_color', '#FFFFFF')),
                'selected_rating_name': stats.get('selected_rating_name', 'WN8'),
                'winrate': stats.get('winrate', 0),
                'winrate_color': stats.get('winrate_color', '#FFFFFF'),
                'nick': vehicleData.get('name', ''),
                'vehicle': self._getVehicleName(vehicleData),
            }
            self._applyVehicleNameColor(vehicleID, listItem, playerInfo)
        except Exception as e:
            logger.error('[PanelView] _reapplyVehicleColors error for %s: %s', vehicleID, e)

    def _getVehicleName(self, vehicleData):
        try:
            vehicleType = vehicleData.get('vehicleType')
            if vehicleType and hasattr(vehicleType, 'type') and hasattr(vehicleType.type, 'shortUserString'):
                return vehicleType.type.shortUserString
        except Exception:
            pass
        return ''

    def _pushTabOverlays(self, arenaDP):
        """
        Push rows to fixed-row Scaleform Full Stats (Comp7 and Stronghold).
        Frontline is deliberately excluded: FrontlineFullStatsTable uses
        recycled scrolling renderers and needs a dedicated adapter.
        """
        if not arenaDP or not g_events or not g_events.componentUI:
            return
        if self._isFrontlineBattle():
            return
        try:
            allies = [
                self._buildTabRow(vehicleID)
                for vehicleID in self._getTabVehicleIDs(arenaDP, True)
            ]
            enemies = [
                self._buildTabRow(vehicleID, True)
                for vehicleID in self._getTabVehicleIDs(arenaDP, False)
            ]
            g_events.setTabOverlay(allies, enemies)
            logger.debug(
                '[PanelView] TAB overlays pushed: allies=%d enemies=%d',
                len(allies), len(enemies),
            )
        except Exception as e:
            logger.error('[PanelView] _pushTabOverlays error: %s', e)

    def _isFrontlineBattle(self):
        arena = self._getArena()
        bonus_type = getattr(arena, 'bonusType', None) if arena else None
        try:
            from constants import ARENA_BONUS_TYPE
            return bonus_type in tuple(
                value for value in (
                    getattr(ARENA_BONUS_TYPE, 'EPIC_RANDOM', None),
                    getattr(ARENA_BONUS_TYPE, 'EPIC_RANDOM_2', None),
                ) if value is not None
            )
        except Exception:
            return False

    def _getTabVehicleIDs(self, arenaDP, allies):
        """Return vehicle IDs in the same order as the stock Full Stats table."""
        collection_class = (
            vos_collections.AllyItemsCollection
            if allies else vos_collections.EnemyItemsCollection
        )
        sort_key = self._getTabSortKey()
        try:
            # WoT 2.x API: collection receives a key *class*, while arenaDP is
            # passed to ids()/iterator(). Passing arenaDP to the constructor
            # silently installs it as the sort key and breaks every Flash TAB.
            collection = collection_class(sortKey=sort_key)
            return list(collection.ids(arenaDP))
        except Exception as e:
            logger.debug('[PanelView] stock TAB collection failed: %s', e)
            return self._getFallbackTabVehicleIDs(arenaDP, allies, sort_key)

    def _getTabSortKey(self):
        """Use the same sorting policy as each mode's statistics controller."""
        arena = self._getArena()
        bonus_type = getattr(arena, 'bonusType', None) if arena else None

        try:
            from constants import ARENA_BONUS_TYPE
            comp7_types = tuple(
                value for value in (
                    getattr(ARENA_BONUS_TYPE, 'COMP7', None),
                    getattr(ARENA_BONUS_TYPE, 'TOURNAMENT_COMP7', None),
                    getattr(ARENA_BONUS_TYPE, 'TRAINING_COMP7', None),
                    getattr(ARENA_BONUS_TYPE, 'COMP7_LIGHT', None),
                ) if value is not None
            )
            if bonus_type in comp7_types:
                from comp7.gui.battle_control.arena_info import vos_collections as comp7_collections
                return comp7_collections.Comp7SortKey
        except Exception as e:
            logger.debug('[PanelView] Comp7 sort key unavailable: %s', e)

        try:
            from constants import ARENA_BONUS_TYPE
            epic_types = tuple(
                value for value in (
                    getattr(ARENA_BONUS_TYPE, 'EPIC_RANDOM', None),
                    getattr(ARENA_BONUS_TYPE, 'EPIC_RANDOM_2', None),
                ) if value is not None
            )
            if bonus_type in epic_types:
                return vos_collections.EpicRankSortKey
        except Exception as e:
            logger.debug('[PanelView] Frontline sort key unavailable: %s', e)

        return vos_collections.VehicleInfoSortKey

    def _getFallbackTabVehicleIDs(self, arenaDP, allies, sort_key):
        """Compatibility fallback when WG changes collection construction."""
        vehicles = []
        for vehicle in arenaDP.getVehiclesInfoIterator():
            try:
                is_ally = arenaDP.isAllyTeam(vehicle.team)
            except Exception:
                arena = self._getArena()
                data = arena.vehicles.get(vehicle.vehicleID, {}) if arena else {}
                is_ally = arenaDP.isAllyTeam(data.get('team'))
            if is_ally == allies:
                vehicles.append(vehicle)

        try:
            vehicles.sort(key=sort_key)
        except Exception:
            vehicles.sort(key=lambda vehicle: getattr(vehicle, 'vehicleID', 0))
        return [vehicle.vehicleID for vehicle in vehicles if vehicle.vehicleID]

    def _buildTabRow(self, vehicleID, mirrored=False):
        if not vehicleID:
            return {'vehicleID': 0, 'text': ''}
        arena = self._getArena()
        if not arena or not arena.vehicles:
            return {'vehicleID': vehicleID, 'text': ''}
        vehicleData = arena.vehicles.get(vehicleID) or {}
        accountDBID = vehicleData.get('accountDBID')
        if not accountDBID:
            return {'vehicleID': vehicleID, 'text': ''}
        stats = self._statsManager.get_cached_stats(accountDBID)
        if not stats:
            return {'vehicleID': vehicleID, 'text': ''}

        def tab_cell(value, color, bold=False):
            value = str(value)
            if bold:
                value = '<b>{}</b>'.format(value)
            return "<font color='{}'>{}</font>".format(color, value)

        def compact_battles(value):
            value = int(value or 0)
            if value >= 1000000:
                return '{:.1f}m'.format(value / 1000000.0)
            if value >= 1000:
                return '{:.1f}k'.format(value / 1000.0)
            return str(value)

        parts = []
        if g_configParams.showWn8.value:
            rating = int(stats.get('selected_rating') or stats.get('wn8', 0) or 0)
            if rating:
                parts.append(tab_cell(
                    rating,
                    stats.get('selected_rating_color') or stats.get('wn8_color', '#FFFFFF'),
                    bold=True))
        if g_configParams.showWinrate.value:
            winrate = float(stats.get('winrate', 0) or 0)
            if winrate > 0:
                parts.append(tab_cell(
                    '{:.1f}%'.format(winrate),
                    stats.get('winrate_color', '#FFFFFF')))
        if g_configParams.showBattles.value:
            battles = int(stats.get('battles', 0) or 0)
            if battles:
                parts.append(tab_cell(
                    compact_battles(battles),
                    stats.get('battles_color', '#FFFFFF')))

        # Read from the tank towards the outer edge:
        # allies  (visual left -> right): battles, winrate, WN8
        # enemies (visual left -> right): WN8, winrate, battles
        if not mirrored:
            parts.reverse()
        return {'vehicleID': vehicleID, 'text': '\t'.join(parts)}

    def _updatePlayerDisplay(self, accountDBID, stats=None):
        if not stats:
            return
        if not self._containersCreated:
            self._pendingStats[accountDBID] = stats
            return
        vehicleID = self._accountVehicleMap.get(accountDBID)
        if vehicleID is None:
            arena = self._getArena()
            if arena and arena.vehicles:
                for vID, vData in arena.vehicles.items():
                    if vData.get('accountDBID') == accountDBID:
                        vehicleID = vID
                        self._vehicleAccountMap[vID] = accountDBID
                        self._accountVehicleMap[accountDBID] = vID
                        break
        if vehicleID is not None:
            self._updatedVehicles.add(vehicleID)
            self.delayCallback(0.1, self._processAllPlayers)

    def updateAllPlayers(self):
        self.delayCallback(0, self._processAllPlayers)

    def finalize(self):
        if not self._isInitialized:
            return
        try:
            if self._hasPanelCoreUI and g_events:
                try:
                    g_events.updateMode -= self._onUpdateMode
                    g_eventBus.removeListener(GameEvent.FULL_STATS, self._onFullStats, EVENT_BUS_SCOPE.BATTLE)
                except Exception:
                    pass
                try:
                    g_events.onUIReady -= self._onUIReady
                except Exception:
                    pass
                g_events.clearTabOverlay()
                g_events.clearCache()
                for container in self._createdContainers:
                    try:
                        g_events.delete(container)
                    except Exception as e:
                        logger.debug('[PanelView] Error deleting %s: %s', container, e)

            self._createdContainers = []
            self._updatedVehicles.clear()
            self._vehicleAccountMap.clear()
            self._accountVehicleMap.clear()
            self._pendingStats.clear()
            self._isInitialized = False
            self._containersCreated = False
            self._arena = None
            self._playerTeam = None
            self.clearCallbacks()
            logger.debug('[PanelView] Finalized')
        except Exception as e:
            logger.error('[PanelView] finalize error: %s', e)

    def destroy(self):
        self.finalize()
        self._statsManager = None
        self._updatedVehicles.clear()
        self._vehicleAccountMap.clear()
        self._accountVehicleMap.clear()
        self._createdContainers = []
        self._pendingStats.clear()
        self._arena = None
        logger.debug('[PanelView] Destroyed')
