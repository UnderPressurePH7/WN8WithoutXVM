import time

import BigWorld
from wg_async import wg_async, AsyncReturn

from ..utils import logger, fetch_data_with_retry
from ..settings.config_param import g_configParams
from .wn8_calc import calc_overall_wn8_from_per_tank
from .wn8_expected import g_wn8_expected
from .disk_cache import DiskCache


REGION_HOSTS = {
    'eu': 'https://api.worldoftanks.eu',
    'na': 'https://api.worldoftanks.com',
    'asia': 'https://api.worldoftanks.asia',
}

DEFAULT_APP_ID = 'bce57ac20af6b67b08be09fd66847ed9'

TANKS_FIELDS = ','.join((
    'tank_id',
    'all.battles',
    'all.wins',
    'all.damage_dealt',
    'all.frags',
    'all.spotted',
    'all.dropped_capture_points',
    'all.survived_battles',
))

_CACHE_LIFETIME = 3 * 24 * 60 * 60
_CACHE_VERSION = 1
_API_MIN_REQ_INTERVAL = 5


class StatsAPI(object):

    def __init__(self):
        self._mem_cache = {}
        self._pending = set()
        self._last_req_time = {}
        self._disk_cache = DiskCache('player_stats.dat',
                                     version=_CACHE_VERSION,
                                     lifetime=_CACHE_LIFETIME)
        self._disk_cache.load()
        g_wn8_expected.load()

    def _resolve_host(self):
        return REGION_HOSTS.get(self._get_region(), REGION_HOSTS['eu'])

    def _get_region(self):
        try:
            value = getattr(g_configParams, 'wgApiRegion', None)
            if value is not None:
                return value.value
        except Exception:
            pass
        return 'eu'

    def _get_app_id(self):
        try:
            value = getattr(g_configParams, 'wgApiKey', None)
            if value is not None and value.value:
                return str(value.value).strip() or DEFAULT_APP_ID
        except Exception:
            pass
        return DEFAULT_APP_ID

    def _build_url(self, path, params):
        host = self._resolve_host()
        params = dict(params)
        params['application_id'] = self._get_app_id()
        query = '&'.join('{}={}'.format(k, v) for k, v in params.items())
        return '{}{}?{}'.format(host, path, query)

    @wg_async
    def _fetch_per_tank_stats(self, accountId):
        url = self._build_url('/wot/tanks/stats/', {
            'account_id': accountId,
            'fields': TANKS_FIELDS,
        })
        try:
            data = yield fetch_data_with_retry(url, retries=2, delay=3, timeout=20.0)
        except Exception:
            logger.exception('[StatsAPI] Per-tank fetch failed for %s', accountId)
            raise AsyncReturn(None)

        if not data or data.get('status') != 'ok':
            logger.debug('[StatsAPI] WG API non-ok for %s: %s', accountId, data)
            raise AsyncReturn(None)

        tanks_block = (data.get('data') or {}).get(str(accountId)) or []
        if not tanks_block:
            raise AsyncReturn(None)

        flat = []
        for tank in tanks_block:
            stats_all = tank.get('all') or {}
            flat.append({
                'tank_id': tank.get('tank_id'),
                'battles': stats_all.get('battles') or 0,
                'wins': stats_all.get('wins') or 0,
                'damage_dealt': stats_all.get('damage_dealt') or 0,
                'frags': stats_all.get('frags') or 0,
                'spotted': stats_all.get('spotted') or 0,
                'dropped_capture_points': stats_all.get('dropped_capture_points') or 0,
                'survived_battles': stats_all.get('survived_battles') or 0,
            })
        raise AsyncReturn(flat)

    @wg_async
    def _compute_stats(self, accountId):
        try:
            tank_stats = yield self._fetch_per_tank_stats(accountId)
            if not tank_stats:
                raise AsyncReturn(None)

            if not g_wn8_expected.is_loaded:
                g_wn8_expected.load()

            wn8, total_battles, total_wins, total_damage = (
                calc_overall_wn8_from_per_tank(tank_stats, g_wn8_expected._table)
            )

            survived = sum(int(t.get('survived_battles') or 0) for t in tank_stats)

            winrate = (float(total_wins) / total_battles * 100.0) if total_battles > 0 else 0.0
            dpg = (float(total_damage) / total_battles) if total_battles > 0 else 0.0
            survival = (float(survived) / total_battles * 100.0) if total_battles > 0 else 0.0

            stats = {
                'wn8': wn8,
                'winrate': winrate,
                'battles': total_battles,
                'avg_damage': dpg,
                'dpg': dpg,
                'survival': survival,
                'dmg_ratio': 0.0,
            }
            logger.debug('[StatsAPI] Computed stats for %s: %s', accountId, stats)
            raise AsyncReturn(stats)

        except AsyncReturn:
            raise
        except Exception:
            logger.exception('[StatsAPI] Error computing stats for %s', accountId)
            raise AsyncReturn(None)

    def get_player_stats(self, accountId, callback):
        cacheKey = str(accountId)

        if cacheKey in self._mem_cache:
            cached = self._mem_cache[cacheKey]
            logger.debug('[StatsAPI] mem-cache hit for %s', accountId)
            BigWorld.callback(0.0, lambda: callback(accountId, cached))
            return

        on_disk = self._disk_cache.get(cacheKey)
        if on_disk is not None:
            logger.debug('[StatsAPI] disk-cache hit for %s', accountId)
            self._mem_cache[cacheKey] = on_disk
            BigWorld.callback(0.0, lambda: callback(accountId, on_disk))
            return

        if cacheKey in self._pending:
            logger.debug('[StatsAPI] dedup pending for %s', accountId)
            self._wait_pending(cacheKey, accountId, callback)
            return

        now = time.time()
        last = self._last_req_time.get(cacheKey, 0)
        if last and (now - last) < _API_MIN_REQ_INTERVAL:
            logger.debug('[StatsAPI] throttled for %s (%.1fs since last)',
                         accountId, now - last)
            BigWorld.callback(0.0, lambda: callback(accountId, None))
            return

        self._pending.add(cacheKey)
        self._last_req_time[cacheKey] = now

        @wg_async
        def worker():
            try:
                stats = yield self._compute_stats(accountId)
                if stats:
                    self._mem_cache[cacheKey] = stats
                    self._disk_cache.set(cacheKey, stats)
                BigWorld.callback(0.0, lambda: callback(accountId, stats))
            except Exception:
                logger.exception('[StatsAPI] worker failed for %s', accountId)
                BigWorld.callback(0.1, lambda: callback(accountId, None))
            finally:
                self._pending.discard(cacheKey)

        worker()

    def _wait_pending(self, cacheKey, accountId, callback):
        attempts = {'n': 0}

        def _poll():
            attempts['n'] += 1
            if cacheKey not in self._pending:
                stats = self._mem_cache.get(cacheKey) or self._disk_cache.get(cacheKey)
                callback(accountId, stats)
                return
            if attempts['n'] > 60:
                callback(accountId, None)
                return
            BigWorld.callback(0.5, _poll)

        BigWorld.callback(0.5, _poll)

    def clear_cache(self):
        self._mem_cache.clear()
        self._pending.clear()
        self._last_req_time.clear()
        logger.debug('[StatsAPI] in-memory cache cleared')

    def fini(self):
        self.clear_cache()
        try:
            self._disk_cache.flush()
        finally:
            self._disk_cache.fini()
        logger.debug('[StatsAPI] Finalized')
