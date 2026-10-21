# -*- coding: utf-8 -*-

import copy
import sys
import weakref

import BigWorld
from PlayerEvents import g_playerEvents
from constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE

from .settings.config_param import g_configParams
from .utils import logger, override, restore_overrides


# -----------------------------------------------------------------------------
# Supported battle modes
# -----------------------------------------------------------------------------

def _enum_values(enum_cls, names):
    """Return existing enum values without dropping a legitimate numeric zero."""
    values = []
    for name in names:
        value = getattr(enum_cls, name, None)
        if value is not None:
            values.append(value)
    return frozenset(values)


ALLOWED_GUI_TYPES = _enum_values(ARENA_GUI_TYPE, (
    'RANDOM',
    'STRONGHOLD_BATTLES',
    'SORTIE',
    'FORT_BATTLE',
    'EPIC_BATTLE',
))

ALLOWED_BONUS_TYPES = _enum_values(ARENA_BONUS_TYPE, (
    'REGULAR',
    'RANDOM_NP2',
    'SORTIE_2',
    'FORT_BATTLE_2',
    'COMP7',
    'TOURNAMENT_COMP7',
    'TRAINING_COMP7',
    'COMP7_LIGHT',
    'EPIC_RANDOM',
    'EPIC_RANDOM_2',
))


def is_supported(arena):
    if arena is None:
        return False
    gui_type = getattr(arena, 'guiType', None)
    bonus_type = getattr(arena, 'bonusType', None)
    if gui_type is not None and gui_type in ALLOWED_GUI_TYPES:
        return True
    if bonus_type is not None and bonus_type in ALLOWED_BONUS_TYPES:
        return True
    return False


# -----------------------------------------------------------------------------
# Battle provider
# -----------------------------------------------------------------------------

class BattleProvider(object):
    MAX_RETRIES = 10
    _instance = None
    _hooked = False

    def __init__(self, statsManager, panelView):
        logger.debug('[BattleProvider] Initializing...')
        self._arena = None
        self._playerTeam = None
        self._statsManager = statsManager
        self._panelView = panelView
        self._battleSessionId = 0
        self._retryCount = 0
        self._isBattleActive = False
        self._loadedAccounts = set()
        self._fallbackSubscribed = False
        BattleProvider._instance = self
        self._installOverrides()
        logger.debug('[BattleProvider] Initialized')

    def _installOverrides(self):
        if BattleProvider._hooked:
            return
        try:
            from Avatar import PlayerAvatar

            @override(PlayerAvatar, 'onBecomePlayer')
            def hooked_onBecomePlayer(base, avatar, *args, **kwargs):
                base(avatar, *args, **kwargs)
                inst = BattleProvider._instance
                if inst is not None:
                    inst._onAvatarReady()

            @override(PlayerAvatar, 'onBecomeNonPlayer')
            def hooked_onBecomeNonPlayer(base, avatar, *args, **kwargs):
                inst = BattleProvider._instance
                if inst is not None:
                    inst._onAvatarBecomeNonPlayer()
                base(avatar, *args, **kwargs)

            BattleProvider._hooked = True
            logger.debug('[BattleProvider] Hooked PlayerAvatar lifecycle')
        except Exception:
            logger.exception('[BattleProvider] Avatar hook failed, falling back to g_playerEvents')
            g_playerEvents.onAvatarReady += self._onAvatarReady
            g_playerEvents.onAvatarBecomeNonPlayer += self._onAvatarBecomeNonPlayer
            self._fallbackSubscribed = True

    def fini(self):
        logger.debug('[BattleProvider] Finalizing...')
        self._battleSessionId += 1
        self._isBattleActive = False
        self._arena = None
        self._playerTeam = None
        self._loadedAccounts.clear()
        BattleProvider._instance = None
        if self._fallbackSubscribed:
            try:
                g_playerEvents.onAvatarReady -= self._onAvatarReady
                g_playerEvents.onAvatarBecomeNonPlayer -= self._onAvatarBecomeNonPlayer
            except Exception:
                logger.exception('[BattleProvider] Error unsubscribing g_playerEvents')
            self._fallbackSubscribed = False
        restore_overrides()
        BattleProvider._hooked = False

    def getArena(self):
        return self._arena

    def _onAvatarReady(self):
        logger.debug('[BattleProvider] Avatar ready')
        try:
            if not g_configParams.enabled.value:
                logger.debug('[BattleProvider] Mod disabled - skipping')
                return
        except Exception:
            logger.exception('[BattleProvider] Failed to check config')
            return
        self._battleSessionId += 1
        self._retryCount = 0
        self._loadedAccounts.clear()
        self._tryInitializeBattle(self._battleSessionId)

    def _tryInitializeBattle(self, sessionId):
        if sessionId != self._battleSessionId:
            return
        try:
            player = BigWorld.player()
            if player is None:
                self._scheduleRetry(sessionId, 'player is None')
                return
            arena = getattr(player, 'arena', None)
            if arena is None:
                self._scheduleRetry(sessionId, 'arena is None')
                return
            if not hasattr(player, 'team') or not hasattr(player, 'playerVehicleID'):
                self._scheduleRetry(sessionId, 'player attrs not ready')
                return
            self._onBattleReady(player, arena)
        except Exception:
            logger.exception('[BattleProvider] Error in _tryInitializeBattle')

    def _scheduleRetry(self, sessionId, reason):
        if self._retryCount >= self.MAX_RETRIES:
            logger.error('[BattleProvider] Giving up after %s retries (%s)', self.MAX_RETRIES, reason)
            return
        self._retryCount += 1
        logger.debug('[BattleProvider] Retry %s/%s: %s', self._retryCount, self.MAX_RETRIES, reason)
        ref = weakref.ref(self)

        def _retry():
            inst = ref()
            if inst is None or inst._battleSessionId != sessionId:
                return
            inst._tryInitializeBattle(sessionId)

        BigWorld.callback(0.5, _retry)

    def _onBattleReady(self, player, arena):
        if not is_supported(arena):
            logger.debug('[BattleProvider] Battle mode not supported (guiType=%s bonusType=%s) - skipping',
                         getattr(arena, 'guiType', None), getattr(arena, 'bonusType', None))
            return
        self._arena = arena
        self._playerTeam = player.team
        self._isBattleActive = True
        logger.debug('[BattleProvider] Player team: %s', self._playerTeam)
        logger.debug('[BattleProvider] Arena acquired: %s vehicles', len(arena.vehicles) if arena.vehicles else 0)
        if self._panelView is not None:
            self._panelView.setArena(arena)
            self._panelView.initialize()
        sessionId = self._battleSessionId
        ref = weakref.ref(self)

        def _startLoading():
            inst = ref()
            if inst is None or inst._battleSessionId != sessionId:
                return
            inst._loadAllPlayersStats()

        BigWorld.callback(0.5, _startLoading)

    def _loadAllPlayersStats(self):
        if not self._isBattleActive:
            return
        if not self._arena or not self._arena.vehicles:
            logger.debug('[BattleProvider] No arena or vehicles')
            return
        accountIds = []
        for vehicleData in self._arena.vehicles.values():
            accountId = vehicleData.get('accountDBID')
            if not accountId:
                continue
            try:
                self._statsManager.set_player_nickname(accountId, vehicleData.get('name'))
            except Exception:
                logger.exception('[BattleProvider] Failed to pass nickname for %s', accountId)
            if accountId not in self._loadedAccounts:
                accountIds.append(accountId)
        logger.debug('[BattleProvider] Loading stats for %s players', len(accountIds))
        for accountId in accountIds:
            self._loadedAccounts.add(accountId)
            self._statsManager.get_player_stats(accountId, self._onPlayerStatsLoaded)

    def _onPlayerStatsLoaded(self, accountId, stats):
        if not self._isBattleActive:
            return
        logger.debug('[BattleProvider] Stats loaded for account %s: %s', accountId, stats)
        try:
            if self._panelView is not None and stats:
                self._panelView._updatePlayerDisplay(accountId, stats)
        except Exception:
            logger.exception('[BattleProvider] Error updating for account %s', accountId)

    def _onAvatarBecomeNonPlayer(self):
        logger.debug('[BattleProvider] Avatar become non-player')
        self._battleSessionId += 1
        self._isBattleActive = False
        self._arena = None
        self._playerTeam = None
        self._loadedAccounts.clear()
        try:
            if self._panelView is not None:
                self._panelView.setArena(None)
                self._panelView.finalize()
            if self._statsManager is not None:
                self._statsManager.clear_cache()
        except Exception:
            logger.exception('[BattleProvider] Failed to stop battle session')
        finally:
            self._arena = None
            self._playerTeam = None
            self._retryCount = 0
            self._loadedAccounts.clear()

    def getPlayerStats(self, accountId):
        if self._statsManager is not None:
            return self._statsManager.get_cached_stats(accountId)
        return None

    def isStatsLoaded(self, accountId):
        if self._statsManager is not None:
            return self._statsManager.is_stats_loaded(accountId)
        return False


# -----------------------------------------------------------------------------
# Battle Results de-anonymization
# -----------------------------------------------------------------------------

_PATCHES = []


def _is_enabled():
    try:
        return bool(g_configParams.battleResultsDeanonimize.value)
    except Exception:
        return True


def _format_full_name(user_name, clan_abbrev):
    if clan_abbrev:
        return u'%s [%s]' % (user_name, clan_abbrev)
    return user_name


def _iter_values(value):
    if isinstance(value, dict):
        try:
            return value.itervalues()
        except AttributeError:
            return value.values()
    if isinstance(value, (list, tuple)):
        return value
    return ()


def _restore_item(item):
    if not isinstance(item, dict):
        return False
    real_name = item.get('realName')
    if not real_name:
        return False
    changed = False
    for key in ('name', 'fakeName', 'userName', 'displayName'):
        if key in item and item.get(key) != real_name:
            item[key] = real_name
            changed = True
    if 'fullName' in item:
        clan = item.get('clanAbbrev', item.get('clanTag', '')) or ''
        full_name = _format_full_name(real_name, clan)
        if item.get('fullName') != full_name:
            item['fullName'] = full_name
            changed = True
    return changed


def _restore_tree(value):
    changed = 0
    if isinstance(value, dict):
        if _restore_item(value):
            changed += 1
        try:
            values = value.itervalues()
        except AttributeError:
            values = value.values()
        for child in values:
            changed += _restore_tree(child)
    elif isinstance(value, (list, tuple)):
        for child in value:
            changed += _restore_tree(child)
    return changed


def _deanonimize_results_dict(results):
    if not isinstance(results, dict):
        return results, 0
    data = copy.deepcopy(results)
    changed = 0
    players = data.get('players')
    for player in _iter_values(players):
        if not isinstance(player, dict):
            continue
        real_name = player.get('realName')
        if not real_name:
            continue
        if player.get('name') != real_name:
            player['name'] = real_name
            changed += 1
        if 'fakeName' in player and player.get('fakeName') != real_name:
            player['fakeName'] = real_name
    return data, changed


def _deanonimize_battle_results_vo(data):
    if not isinstance(data, dict):
        return data, 0
    result = copy.deepcopy(data)
    changed = 0
    for key in ('team1', 'team2'):
        if key in result:
            changed += _restore_tree(result.get(key))
    personal = result.get('personal')
    if isinstance(personal, dict):
        details = personal.get('details')
        if details is not None:
            changed += _restore_tree(details)
        changed += _restore_item(personal)
    common = result.get('common')
    if common is not None:
        changed += _restore_tree(common)
    if 'players' in result:
        changed += _restore_tree(result.get('players'))
    return result, changed


def _patch_method(cls, method_name, wrapper_factory):
    try:
        marker = '_wn8DeanonOriginal_%s' % method_name
        if hasattr(cls, marker):
            return False
        original = getattr(cls, method_name, None)
        if original is None or not callable(original):
            return False
        setattr(cls, marker, original)
        setattr(cls, method_name, wrapper_factory(original))
        _PATCHES.append((cls, method_name, marker))
        logger.info('[BattleResultsDeanon] patched %s.%s', cls.__name__, method_name)
        return True
    except Exception:
        logger.exception('[BattleResultsDeanon] failed to patch %s.%s', getattr(cls, '__name__', '?'), method_name)
        return False


def _make_pack_battle_results_wrapper(original):
    def _wrapped(self, battle_results, *args, **kwargs):
        if _is_enabled():
            try:
                results = getattr(battle_results, 'results', None)
                if isinstance(results, dict):
                    new_results, changed = _deanonimize_results_dict(results)
                    if changed:
                        from gui.battle_results import reusable
                        from gui.battle_results.stats_ctrl import BattleResults
                        reusable_info = reusable.createReusableInfo(new_results)
                        if reusable_info is not None:
                            battle_results = BattleResults(new_results, reusable_info)
                            logger.debug('[BattleResultsDeanon] rebuilt BattleResults with %d restored players', changed)
            except Exception:
                logger.exception('[BattleResultsDeanon] packBattleResults transform failed')
        return original(self, battle_results, *args, **kwargs)
    return _wrapped


def _make_post_result_wrapper(original):
    def _wrapped(self, result, *args, **kwargs):
        if _is_enabled() and isinstance(result, dict):
            try:
                result, changed = _deanonimize_results_dict(result)
                if changed:
                    logger.debug('[BattleResultsDeanon] postResult restored %d players before reusable info', changed)
            except Exception:
                logger.exception('[BattleResultsDeanon] postResult transform failed')
        return original(self, result, *args, **kwargs)
    return _wrapped


def _make_set_battle_results_data_wrapper(original):
    def _wrapped(self, data, *args, **kwargs):
        if _is_enabled() and isinstance(data, dict):
            try:
                data, changed = _deanonimize_battle_results_vo(data)
                if changed:
                    logger.debug('[BattleResultsDeanon] setBattleResultsData restored %d VO entries', changed)
            except Exception:
                logger.exception('[BattleResultsDeanon] Battle Results VO transform failed')
        return original(self, data, *args, **kwargs)
    return _wrapped


def initialize_post_battle_deanon():
    patched = False
    try:
        from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
        patched |= _patch_method(BattleResultsSubPresenter, 'packBattleResults', _make_pack_battle_results_wrapper)
    except Exception:
        logger.exception('[BattleResultsDeanon] BattleResultsSubPresenter unavailable')
    try:
        from gui.battle_results.service import BattleResultsService
        patched |= _patch_method(BattleResultsService, 'postResult', _make_post_result_wrapper)
        if hasattr(BattleResultsService, 'setBattleResultsData'):
            patched |= _patch_method(BattleResultsService, 'setBattleResultsData', _make_set_battle_results_data_wrapper)
    except Exception:
        logger.exception('[BattleResultsDeanon] BattleResultsService unavailable')
    if patched:
        logger.info('[BattleResultsDeanon] Tomato-style raw Battle Results deanon enabled')
    else:
        logger.warning('[BattleResultsDeanon] no compatible Battle Results hooks found')


def finalize_post_battle_deanon():
    while _PATCHES:
        cls, method_name, marker = _PATCHES.pop()
        try:
            original = getattr(cls, marker, None)
            if original is not None:
                setattr(cls, method_name, original)
            if hasattr(cls, marker):
                delattr(cls, marker)
        except Exception:
            logger.exception('[BattleResultsDeanon] failed to restore %s.%s', getattr(cls, '__name__', '?'), method_name)


# Preserve old imports after the original files are removed.
_this = sys.modules[__name__]
for _legacy_name in ('battle_modes', 'battle_provider', 'post_battle_deanon'):
    sys.modules[__package__ + '.' + _legacy_name] = _this

del _legacy_name
