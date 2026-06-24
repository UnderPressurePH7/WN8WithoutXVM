import time
from collections import deque

import BigWorld
from wg_async import wg_async, AsyncReturn

from ..utils import logger, fetch_data_with_retry
from ..settings.config_param import g_configParams, RatingMode
from .wn8_calc import calc_overall_wn8_from_per_tank
from .wn8_expected import g_wn8_expected
from .disk_cache import DiskCache


REGION_HOSTS = {
    'eu': 'https://api.worldoftanks.eu',
    'na': 'https://api.worldoftanks.com',
    'asia': 'https://api.worldoftanks.asia',
}

TOMATO_SERVER_BY_REGION = {
    'eu': 'eu',
    'na': 'com',
    'asia': 'asia',
}

TOMATO_API_HOST = 'https://api.tomato.gg'

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
_CACHE_VERSION = 3
_QUEUE_INTERVAL = 0.25
_COOLDOWN_AFTER_FAIL = 30.0


def _as_int(value, default=0):
    try:
        if value is None:
            return default
        return int(round(float(value)))
    except Exception:
        return default


def _as_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def _deep_get(data, path, default=None):
    cur = data
    for key in path:
        if isinstance(cur, dict) and key in cur:
            cur = cur.get(key)
        else:
            return default
    return cur


def _first_number(data, keys):
    if not isinstance(data, dict):
        return None
    for key in keys:
        if key in data and data.get(key) is not None:
            return data.get(key)
    lower_map = {}
    for key, value in data.items():
        try:
            lower_map[str(key).lower()] = value
        except Exception:
            pass
    for key in keys:
        value = lower_map.get(str(key).lower())
        if value is not None:
            return value
    return None


class StatsAPI(object):

    def __init__(self):
        self._mem_cache = {}
        self._waiters = {}
        self._queue = deque()
        self._queued = set()
        self._worker_active = False
        self._last_req_time = {}
        self._disk_cache = DiskCache('player_stats_v3.dat',
                                     version=_CACHE_VERSION,
                                     lifetime=_CACHE_LIFETIME)
        self._cleanup_old_cache(('player_stats.dat',))
        self._disk_cache.load()
        g_wn8_expected.load()

    def _cleanup_old_cache(self, filenames):
        # Silently remove obsolete cache files from previous versions so users
        # don't have to delete anything by hand.
        try:
            import os
            cache_dir = os.path.dirname(self._disk_cache._path)
            for name in filenames:
                old_path = os.path.join(cache_dir, name)
                if os.path.isfile(old_path):
                    os.remove(old_path)
                    logger.debug('[StatsAPI] removed obsolete cache file: %s', name)
        except Exception:
            logger.exception('[StatsAPI] old cache cleanup failed')

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

    def _get_tomato_server(self):
        return TOMATO_SERVER_BY_REGION.get(self._get_region(), 'eu')

    def _get_tomato_key(self):
        try:
            param = getattr(g_configParams, 'tomatoApiKey', None)
            if param is not None:
                key = param.value or ''
                return str(key).strip()
        except Exception:
            pass
        return ''

    def _has_tomato_key(self):
        key = self._get_tomato_key()
        return bool(key)

    def _get_rating_mode(self):
        try:
            return getattr(g_configParams.ratingMode, 'value', RatingMode.OVERALL_WN8)
        except Exception:
            return RatingMode.OVERALL_WN8

    def _requires_tomato(self):
        # OVERALL_WNX still uses the keyed API; recent modes scrape HTML (no key needed).
        mode = self._get_rating_mode()
        return mode == RatingMode.OVERALL_WNX

    def _requires_recent_scrape(self):
        mode = self._get_rating_mode()
        return mode in (RatingMode.RECENT_WNX, RatingMode.RECENT_WN8)

    def _has_tomato_for_mode(self, stats):
        if not isinstance(stats, dict):
            return not (self._requires_tomato() or self._requires_recent_scrape())
        mode = self._get_rating_mode()
        if mode in (RatingMode.RECENT_WNX, RatingMode.RECENT_WN8):
            # already queried tomato (even if this profile has no recent data) -> don't refetch
            if stats.get('tomato_fetched'):
                return True
            if mode == RatingMode.RECENT_WNX:
                return _as_int(stats.get('recent_wnx')) > 0
            return _as_int(stats.get('recent_wn8')) > 0
        if mode == RatingMode.OVERALL_WNX:
            if not self._has_tomato_key():
                return True
            return _as_int(stats.get('overall_wnx') or stats.get('wnx')) > 0
        return True

    def _needs_tomato_refresh(self, stats):
        if self._requires_recent_scrape():
            return not self._has_tomato_for_mode(stats)
        return self._requires_tomato() and self._has_tomato_key() and not self._has_tomato_for_mode(stats)

    def _get_app_id(self):
        return DEFAULT_APP_ID

    def _build_url(self, path, params):
        host = self._resolve_host()
        params = dict(params)
        params['application_id'] = self._get_app_id()
        query = '&'.join('{}={}'.format(k, v) for k, v in params.items())
        return '{}{}?{}'.format(host, path, query)

    def _build_tomato_url(self, path, params=None):
        params = params or {}
        query = '&'.join('{}={}'.format(k, v) for k, v in params.items())
        if query:
            return '{}{}?{}'.format(TOMATO_API_HOST, path, query)
        return '{}{}'.format(TOMATO_API_HOST, path)

    def _tomato_headers(self):
        return [
            ('Content-Type', 'application/json'),
            ('User-Agent', 'WN8WithoutXVM/0.0.2'),
            ('x-api-key', self._get_tomato_key())
        ]

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

    def _extract_next_data(self, html):
        # tomato.gg is a Next.js site; the data lives in a JSON <script id="__NEXT_DATA__">
        if not html:
            return None
        try:
            import re as _re
            m = _re.search(
                r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
                html, _re.S)
            if not m:
                return None
            return json.loads(m.group(1))
        except Exception:
            logger.exception('[StatsAPI] failed to extract __NEXT_DATA__')
            return None

    def _get_page_props(self, next_data):
        if not isinstance(next_data, dict):
            return None
        props = next_data.get('props')
        if isinstance(props, dict):
            page = props.get('pageProps')
            if isinstance(page, dict):
                return page
        # some builds put pageProps at top level
        page = next_data.get('pageProps')
        return page if isinstance(page, dict) else None

    def _select_recent_1000_overall(self, recent_data):
        # recent_data == pageProps['recentStats']['data']
        if not isinstance(recent_data, dict):
            return None
        battles = recent_data.get('battles')
        if not isinstance(battles, dict):
            return None
        bucket = battles.get('1000')
        if bucket is None:
            bucket = battles.get(1000)
        if not isinstance(bucket, dict):
            return None
        overall = bucket.get('overall')
        if isinstance(overall, dict):
            return overall
        # fallback: bucket itself may already hold the rating
        return bucket if _first_number(bucket, ('overallWN8', 'wn8', 'wnx', 'overallWNX')) is not None else None

    def _parse_tomato_recent_nextdata(self, response):
        # `response` may be either the parsed __NEXT_DATA__ JSON (from HTML)
        # or already a pageProps dict. Handle both.
        result = {}
        page_props = self._get_page_props(response)
        if page_props is None and isinstance(response, dict):
            page_props = response if 'recentStats' in response else None
        if not isinstance(page_props, dict):
            logger.debug('[StatsAPI] recent: no pageProps in response')
            return result

        recent_stats = page_props.get('recentStats')
        if not isinstance(recent_stats, dict):
            logger.debug('[StatsAPI] recent: missing recentStats')
            return result

        meta = recent_stats.get('meta') or {}
        if isinstance(meta, dict) and meta.get('status') == 'error':
            logger.debug('[StatsAPI] recent: recentStats error %s', meta.get('message'))
            return result

        recent_data = recent_stats.get('data')
        overall = self._select_recent_1000_overall(recent_data)
        if not isinstance(overall, dict):
            logger.debug('[StatsAPI] recent: no recent 1000 battles bucket')
            return result

        result['recent_wn8'] = _as_int(_first_number(overall, ('overallWN8', 'wn8', 'WN8')))
        result['recent_wnx'] = _as_int(_first_number(overall, ('overallWNX', 'wnx', 'wnX', 'wn_x', 'WNX')))
        recent_wr = _first_number(overall, ('overallWinrate', 'winrate', 'wr', 'winRate'))
        if recent_wr is not None:
            result['recent_winrate'] = _as_float(recent_wr)
        recent_battles = _first_number(overall, ('overallBattles', 'battles', 'battleCount'))
        if recent_battles is not None:
            result['recent_battles'] = _as_int(recent_battles)
        return result

    def _parse_tomato_overall(self, response):
        result = {}
        data = (response or {}).get('data') or {}
        if not isinstance(data, dict):
            return result

        candidates = [data]
        for key in ('overall', 'summary', 'player', 'stats'):
            value = data.get(key)
            if isinstance(value, dict):
                candidates.append(value)

        for block in candidates:
            wnx = _first_number(block, ('wnx', 'WNX'))
            wn8 = _first_number(block, ('wn8', 'WN8'))
            wr = _first_number(block, ('winrate', 'wr', 'winsPercent'))
            battles = _first_number(block, ('battles', 'battleCount'))
            if wnx is not None and not result.get('overall_wnx'):
                result['overall_wnx'] = _as_int(wnx)
                result['wnx'] = result['overall_wnx']
            if wn8 is not None and not result.get('tomato_overall_wn8'):
                result['tomato_overall_wn8'] = _as_int(wn8)
            if wr is not None and not result.get('tomato_winrate'):
                result['tomato_winrate'] = _as_float(wr)
            if battles is not None and not result.get('tomato_battles'):
                result['tomato_battles'] = _as_int(battles)
        return result

    def _get_region_code(self):
        # tomato.gg URLs use upper-case region codes
        return {'eu': 'EU', 'na': 'NA', 'asia': 'ASIA'}.get(self._get_region(), 'EU')

    @wg_async
    def _resolve_nickname(self, accountId):
        # tomato.gg stats URL needs the nickname: /stats/<REGION>/<nick>=<id>
        url = self._build_url('/wot/account/info/', {
            'account_id': accountId,
            'fields': 'nickname',
        })
        try:
            data = yield fetch_data_with_retry(url, retries=1, delay=1, timeout=8.0)
            if data and data.get('status') == 'ok':
                info = (data.get('data') or {}).get(str(accountId)) or {}
                nick = info.get('nickname')
                if nick:
                    raise AsyncReturn(nick)
        except AsyncReturn:
            raise
        except Exception:
            logger.exception('[StatsAPI] nickname resolve failed for %s', accountId)
        raise AsyncReturn(None)

    def _browser_headers(self):
        return [
            ('User-Agent',
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.9'),
        ]

    def _parse_tomato_meta(self, html):
        # Fast/robust path: recent stats are embedded in the og:image meta URL, e.g.
        # .../api/og/player-stats?username=..&wn8=3861&recentWn8=3834&recentWinrate=61.6&..
        result = {}
        if not html:
            return result
        try:
            import re as _re
            # find the og:image (or twitter:image) url that points to player-stats
            m = _re.search(r'player-stats\?([^"\'\s<>]+)', html)
            if not m:
                return result
            query = m.group(1).replace('&amp;', '&')
            params = {}
            for pair in query.split('&'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    params[k.lower()] = v
            recent_wn8 = params.get('recentwn8')
            if recent_wn8 is not None:
                result['recent_wn8'] = _as_int(recent_wn8)
            recent_wr = params.get('recentwinrate')
            if recent_wr is not None:
                result['recent_winrate'] = _as_float(recent_wr)
            # overall fields also available, useful as fallback
            if params.get('wn8') is not None:
                result['tomato_overall_wn8'] = _as_int(params.get('wn8'))
            if params.get('winrate') is not None:
                result['tomato_winrate'] = _as_float(params.get('winrate'))
            if params.get('battles') is not None:
                result['tomato_battles'] = _as_int(params.get('battles'))
        except Exception:
            logger.exception('[StatsAPI] meta parse failed')
        return result

    @wg_async
    def _fetch_tomato_recent(self, accountId):
        nickname = yield self._resolve_nickname(accountId)
        if not nickname:
            raise AsyncReturn({})

        region = self._get_region_code()
        try:
            from urllib.parse import quote
        except ImportError:
            from urllib import quote
        # Current tomato.gg format: /stats/<nick>-<id>/<REGION>
        slug = '{}-{}'.format(quote(str(nickname)), accountId)
        url = 'https://tomato.gg/stats/{}/{}'.format(slug, region)
        try:
            html = yield fetch_data_with_retry(
                url, retries=1, delay=1, headers=self._browser_headers(),
                timeout=10.0, as_json=False)

            # Primary: recent stats embedded in meta og:image url
            parsed = self._parse_tomato_meta(html)
            if _as_int(parsed.get('recent_wn8')) > 0:
                raise AsyncReturn(parsed)

            # Fallback: try __NEXT_DATA__ structure
            next_data = self._extract_next_data(html)
            if next_data is not None:
                nd_parsed = self._parse_tomato_recent_nextdata(next_data)
                if nd_parsed:
                    parsed.update(nd_parsed)
            if parsed:
                raise AsyncReturn(parsed)

            raise AsyncReturn({})
        except AsyncReturn:
            raise
        except Exception:
            logger.exception('[StatsAPI] Tomato recent fetch failed for %s', accountId)
            raise AsyncReturn({})

    @wg_async
    def _fetch_tomato_overall(self, accountId):
        if not self._has_tomato_key():
            raise AsyncReturn({})
        path = '/api/player/overall/{}/{}'.format(self._get_tomato_server(), accountId)
        url = self._build_tomato_url(path, {'cache': 'true'})
        try:
            data = yield fetch_data_with_retry(url, retries=1, delay=1, headers=self._tomato_headers(), timeout=8.0)
            raise AsyncReturn(self._parse_tomato_overall(data))
        except AsyncReturn:
            raise
        except Exception:
            logger.exception('[StatsAPI] Tomato overall fetch failed for %s', accountId)
            raise AsyncReturn({})

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
                'overall_wn8': wn8,
                'recent_wn8': 0,
                'wnx': 0,
                'overall_wnx': 0,
                'recent_wnx': 0,
                'winrate': winrate,
                'battles': total_battles,
                'avg_damage': dpg,
                'dpg': dpg,
                'survival': survival,
                'dmg_ratio': 0.0,
            }

            mode = self._get_rating_mode()
            if mode in (RatingMode.RECENT_WNX, RatingMode.RECENT_WN8):
                recent_stats = yield self._fetch_tomato_recent(accountId)
                # mark that we already queried tomato for this player, so we don't
                # re-fetch endlessly when a profile simply has no recent data
                stats['tomato_fetched'] = True
                if recent_stats:
                    stats.update(recent_stats)
            elif mode == RatingMode.OVERALL_WNX and self._has_tomato_key():
                overall_stats = yield self._fetch_tomato_overall(accountId)
                if overall_stats:
                    stats.update(overall_stats)

            logger.debug('[StatsAPI] Computed stats for %s: %s', accountId, stats)
            raise AsyncReturn(stats)

        except AsyncReturn:
            raise
        except Exception:
            logger.exception('[StatsAPI] Error computing stats for %s', accountId)
            raise AsyncReturn(None)

    def get_player_stats(self, accountId, callback=None):
        cacheKey = str(accountId)

        if cacheKey in self._mem_cache:
            cached = self._mem_cache[cacheKey]
            if not self._needs_tomato_refresh(cached):
                if callback is not None:
                    BigWorld.callback(0.0, lambda: callback(accountId, cached))
                return

        on_disk = self._disk_cache.get(cacheKey)
        if on_disk is not None and not self._needs_tomato_refresh(on_disk):
            self._mem_cache[cacheKey] = on_disk
            if callback is not None:
                BigWorld.callback(0.0, lambda: callback(accountId, on_disk))
            return

        now = time.time()
        last = self._last_req_time.get(cacheKey, 0)
        if last and (now - last) < _COOLDOWN_AFTER_FAIL and cacheKey not in self._queued:
            if callback is not None:
                BigWorld.callback(0.0, lambda: callback(accountId, None))
            return

        if callback is not None:
            self._waiters.setdefault(cacheKey, []).append(callback)

        if cacheKey not in self._queued:
            self._queued.add(cacheKey)
            self._queue.append(accountId)
            logger.debug('[StatsAPI] enqueued %s (queue size=%d)', accountId, len(self._queue))
            self._pump_queue()

    def _pump_queue(self):
        if self._worker_active:
            return
        if not self._queue:
            return

        accountId = self._queue.popleft()
        cacheKey = str(accountId)
        self._worker_active = True
        self._last_req_time[cacheKey] = time.time()
        logger.debug('[StatsAPI] dequeued %s (remaining=%d)', accountId, len(self._queue))

        @wg_async
        def worker():
            stats = None
            try:
                stats = yield self._compute_stats(accountId)
                if stats:
                    self._mem_cache[cacheKey] = stats
                    self._disk_cache.set(cacheKey, stats)
            except Exception:
                logger.exception('[StatsAPI] worker failed for %s', accountId)
            finally:
                self._queued.discard(cacheKey)
                self._dispatch_waiters(cacheKey, accountId, stats)
                self._worker_active = False
                BigWorld.callback(_QUEUE_INTERVAL, self._pump_queue)

        worker()

    def _dispatch_waiters(self, cacheKey, accountId, stats):
        callbacks = self._waiters.pop(cacheKey, [])
        for cb in callbacks:
            try:
                BigWorld.callback(0.0, lambda c=cb, s=stats: c(accountId, s))
            except Exception:
                logger.exception('[StatsAPI] dispatch waiter error')

    def clear_cache(self):
        self._mem_cache.clear()
        self._queued.clear()
        self._queue.clear()
        self._waiters.clear()
        self._last_req_time.clear()
        self._worker_active = False
        logger.debug('[StatsAPI] in-memory cache cleared')

    def fini(self):
        self.clear_cache()
        try:
            self._disk_cache.flush()
        finally:
            self._disk_cache.fini()
        logger.debug('[StatsAPI] Finalized')
