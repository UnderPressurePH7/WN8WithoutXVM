# -*- coding: utf-8 -*-

import cPickle
import functools
import json
import os
import re
import time
import zlib
from collections import deque

import BigWorld
from wg_async import wg_async, AsyncReturn, await_callback

from .utils import (
    logger,
    cancelCallbackSafe,
    fetch_data_with_retry,
    get_wn8_color,
    get_winrate_color,
    get_battles_color,
    ANON_RATING_TOKEN,
)
from .settings.config_param import g_configParams, RatingMode


# =============================================================================
# Disk cache
# =============================================================================

def _resolve_cache_dir():
    try:
        prefs_path = BigWorld.wg_getPreferencesFilePath()
    except AttributeError:
        try:
            prefs_path = BigWorld.getPreferencesFilePath()
        except Exception:
            prefs_path = ''
    base = os.path.dirname(prefs_path) if prefs_path else ''
    return os.path.normpath(os.path.join(base, 'mods', 'wn8withoutxvm'))


CACHE_DIR = _resolve_cache_dir()


class DiskCache(object):
    SAVE_DELAY = 1.0

    def __init__(self, filename, version=1, lifetime=3600):
        self._path = os.path.join(CACHE_DIR, filename)
        self._version = int(version)
        self._lifetime = int(lifetime)
        self._data = {}
        self._save_rev = 0
        self._save_cb = None
        self._loaded = False

    def load(self):
        if self._loaded:
            return True
        self._loaded = True
        if not os.path.isdir(CACHE_DIR):
            try:
                os.makedirs(CACHE_DIR)
            except OSError as e:
                logger.error('[DiskCache:%s] mkdir failed: %s', self._path, e)
                return False
        if not os.path.isfile(self._path):
            return False
        try:
            with open(self._path, 'rb') as fh:
                payload, version = cPickle.loads(zlib.decompress(fh.read()))
            if version != self._version:
                logger.debug('[DiskCache:%s] version mismatch (%s != %s) - dropping',
                             self._path, version, self._version)
                self._data = {}
                return False
            self._data = payload.get('data', {}) if isinstance(payload, dict) else {}
            logger.debug('[DiskCache:%s] loaded %d entries', self._path, len(self._data))
            return True
        except Exception:
            logger.exception('[DiskCache:%s] load failed', self._path)
            self._data = {}
            return False

    def save(self):
        self._save_rev += 1
        rev = self._save_rev
        cancelCallbackSafe(self._save_cb)
        self._save_cb = BigWorld.callback(self.SAVE_DELAY, functools.partial(self._do_save, rev))

    def _do_save(self, rev):
        self._save_cb = None
        if rev != self._save_rev:
            return
        try:
            if not os.path.isdir(CACHE_DIR):
                os.makedirs(CACHE_DIR)
            payload = {'data': self._data}
            blob = zlib.compress(
                cPickle.dumps((payload, self._version), cPickle.HIGHEST_PROTOCOL),
                1
            )
            with open(self._path, 'wb') as fh:
                fh.write(blob)
            logger.debug('[DiskCache:%s] saved %d entries', self._path, len(self._data))
        except Exception:
            logger.exception('[DiskCache:%s] save failed', self._path)

    def flush(self):
        if self._save_cb is None:
            return
        cancelCallbackSafe(self._save_cb)
        self._save_cb = None
        self._do_save(self._save_rev)

    def fini(self):
        cancelCallbackSafe(self._save_cb)
        self._save_cb = None

    def get(self, key):
        entry = self._data.get(key)
        if entry is None:
            return None
        if self._lifetime > 0 and (time.time() - entry.get('ts', 0)) > self._lifetime:
            return None
        return entry.get('payload')

    def set(self, key, payload):
        self._data[key] = {'payload': payload, 'ts': time.time()}
        self.save()

    def has(self, key):
        return self.get(key) is not None

    def discard(self, key):
        if key in self._data:
            del self._data[key]
            self.save()

    def clear(self):
        if not self._data:
            return
        self._data = {}
        self.save()

    def __len__(self):
        return len(self._data)


# =============================================================================
# WN8 expected values
# =============================================================================

WN8_EXP_URLS = (
    'https://static.modxvm.com/wn8-data-exp/json/wg/wn8exp.json',
    'https://static.modxvm.com/wn8-data-exp/json/wn8exp.json',
    'https://wotnumbers.com/wn8/wn8.json',
)

_EXPECTED_CACHE_LIFETIME = 7 * 24 * 3600
_EXPECTED_CACHE_VERSION = 1
_EXPECTED_CACHE_KEY = 'table'


class WN8ExpectedValues(object):
    def __init__(self):
        self._table = {}
        self._is_loaded = False
        self._is_loading = False
        self._waiters = []
        self._cache = DiskCache(
            'wn8_expected.dat',
            version=_EXPECTED_CACHE_VERSION,
            lifetime=_EXPECTED_CACHE_LIFETIME,
        )
        self._cache.load()

    @property
    def is_loaded(self):
        return self._is_loaded

    def get(self, tank_id):
        return self._table.get(int(tank_id))

    def load(self, callback=None):
        if self._is_loaded:
            if callback:
                BigWorld.callback(0.0, lambda: callback(True))
            return
        if callback:
            self._waiters.append(callback)
        if self._is_loading:
            return
        self._is_loading = True
        try:
            if self._load_from_cache():
                self._notify(True)
                self.refresh()
                return
        except Exception:
            logger.exception('[WN8Expected] cache load failed')
        self._fetch_from_network()

    def refresh(self):
        if self._is_loading:
            return
        self._is_loading = True
        self._fetch_from_network()

    def _load_from_cache(self):
        cached = self._cache.get(_EXPECTED_CACHE_KEY)
        if not cached or not isinstance(cached, dict):
            return False
        self._table = cached
        self._is_loaded = True
        logger.debug('[WN8Expected] loaded %d tanks from disk cache', len(self._table))
        return True

    @wg_async
    def _fetch_from_network(self):
        for url in WN8_EXP_URLS:
            try:
                logger.debug('[WN8Expected] fetching %s', url)
                data = yield fetch_data_with_retry(url, retries=2, delay=3, timeout=20.0)
                if not data:
                    continue
                table = self._build_table(data)
                if not table:
                    logger.error('[WN8Expected] empty/invalid table from %s', url)
                    continue
                self._table = table
                self._is_loaded = True
                self._cache.set(_EXPECTED_CACHE_KEY, table)
                logger.debug('[WN8Expected] loaded %d tanks from network', len(self._table))
                self._notify(True)
                raise AsyncReturn(None)
            except AsyncReturn:
                raise
            except Exception:
                logger.exception('[WN8Expected] fetch failed for %s', url)
        if self._is_loaded:
            logger.warning('[WN8Expected] refresh failed; keeping %d cached tanks', len(self._table))
            self._notify(True)
        else:
            logger.error('[WN8Expected] all sources failed; WN8 will report 0')
            self._notify(False)
        raise AsyncReturn(None)

    def _build_table(self, raw):
        if not raw:
            return {}
        items = raw.get('data') if isinstance(raw, dict) else raw
        if not items:
            return {}
        table = {}
        for item in items:
            try:
                tid = int(item.get('IDNum'))
            except (TypeError, ValueError):
                continue
            table[tid] = {
                'expDamage': float(item.get('expDamage', 0) or 0),
                'expFrag': float(item.get('expFrag', 0) or 0),
                'expSpot': float(item.get('expSpot', 0) or 0),
                'expDef': float(item.get('expDef', 0) or 0),
                'expWinRate': float(item.get('expWinRate', 0) or 0),
            }
        return table

    def _notify(self, ok):
        self._is_loading = False
        waiters = self._waiters
        self._waiters = []
        for cb in waiters:
            try:
                BigWorld.callback(0.0, lambda c=cb, value=ok: c(value))
            except Exception:
                logger.exception('[WN8Expected] notify error')

    def fini(self):
        try:
            self._cache.flush()
        finally:
            self._cache.fini()


g_wn8_expected = WN8ExpectedValues()


# =============================================================================
# WN8 calculation
# =============================================================================

def calc_wn8(avg_damage, avg_spot, avg_frag, avg_def, avg_win_pct,
             exp_damage, exp_spot, exp_frag, exp_def, exp_win_pct):
    if exp_damage <= 0 or exp_win_pct <= 0:
        return 0
    rDAMAGE = float(avg_damage) / exp_damage
    rSPOT = (float(avg_spot) / exp_spot) if exp_spot > 0 else 0.0
    rFRAG = (float(avg_frag) / exp_frag) if exp_frag > 0 else 0.0
    rDEF = (float(avg_def) / exp_def) if exp_def > 0 else 0.0
    rWIN = float(avg_win_pct) / exp_win_pct
    rDAMAGEc = max(0.0, (rDAMAGE - 0.22) / (1 - 0.22))
    rWINc = max(0.0, (rWIN - 0.71) / (1 - 0.71))
    rFRAGc = max(0.0, min(rDAMAGEc + 0.2, (rFRAG - 0.12) / (1 - 0.12)))
    rSPOTc = max(0.0, min(rDAMAGEc + 0.1, (rSPOT - 0.38) / (1 - 0.38)))
    rDEFc = max(0.0, min(rDAMAGEc + 0.1, (rDEF - 0.10) / (1 - 0.10)))
    wn8 = (
        980.0 * rDAMAGEc
        + 210.0 * rDAMAGEc * rFRAGc
        + 155.0 * rFRAGc * rSPOTc
        + 75.0 * rDEFc * rFRAGc
        + 145.0 * min(1.8, rWINc)
    )
    return wn8


def calc_overall_wn8_from_per_tank(tank_stats, exp_table):
    total_battles = 0
    total_wins = 0
    total_damage = 0
    counted_battles = 0
    counted_wins = 0
    counted_damage = 0
    counted_frags = 0
    counted_spot = 0
    counted_def = 0
    expDamage_sum = 0.0
    expSpot_sum = 0.0
    expFrag_sum = 0.0
    expDef_sum = 0.0
    expWin_sum = 0.0
    for tank in tank_stats:
        battles = int(tank.get('battles') or 0)
        if battles <= 0:
            continue
        damage = int(tank.get('damage_dealt') or 0)
        wins = int(tank.get('wins') or 0)
        total_battles += battles
        total_wins += wins
        total_damage += damage
        tid = tank.get('tank_id')
        exp = exp_table.get(int(tid)) if tid is not None else None
        if not exp:
            continue
        frags = int(tank.get('frags') or 0)
        spotted = int(tank.get('spotted') or 0)
        dropped = int(tank.get('dropped_capture_points') or 0)
        counted_battles += battles
        counted_wins += wins
        counted_damage += damage
        counted_frags += frags
        counted_spot += spotted
        counted_def += dropped
        expDamage_sum += float(exp.get('expDamage', 0)) * battles
        expSpot_sum += float(exp.get('expSpot', 0)) * battles
        expFrag_sum += float(exp.get('expFrag', 0)) * battles
        expDef_sum += float(exp.get('expDef', 0)) * battles
        expWin_sum += float(exp.get('expWinRate', 0)) * battles
    if counted_battles == 0:
        return 0, total_battles, total_wins, total_damage
    avg_damage = float(counted_damage) / counted_battles
    avg_spot = float(counted_spot) / counted_battles
    avg_frag = float(counted_frags) / counted_battles
    avg_def = float(counted_def) / counted_battles
    avg_win_pct = float(counted_wins) / counted_battles * 100.0
    exp_damage = expDamage_sum / counted_battles
    exp_spot = expSpot_sum / counted_battles
    exp_frag = expFrag_sum / counted_battles
    exp_def = expDef_sum / counted_battles
    exp_win = expWin_sum / counted_battles
    wn8 = calc_wn8(avg_damage, avg_spot, avg_frag, avg_def, avg_win_pct,
                   exp_damage, exp_spot, exp_frag, exp_def, exp_win)
    return int(round(wn8)), total_battles, total_wins, total_damage


# =============================================================================
# Base statistics API
# =============================================================================

REGION_HOSTS = {
    'eu': 'https://api.worldoftanks.eu',
    'na': 'https://api.worldoftanks.com',
    'asia': 'https://api.worldoftanks.asia',
}
TOMATO_SERVER_BY_REGION = {'eu': 'eu', 'na': 'com', 'asia': 'asia'}
TOMATO_API_HOST = 'https://api.tomato.gg'
DEFAULT_APP_ID = 'bce57ac20af6b67b08be09fd66847ed9'
TANKS_FIELDS = ','.join((
    'tank_id', 'all.battles', 'all.wins', 'all.damage_dealt', 'all.frags',
    'all.spotted', 'all.dropped_capture_points', 'all.survived_battles',
))
_PLAYER_CACHE_LIFETIME = 3 * 24 * 60 * 60
_PLAYER_CACHE_VERSION = 4
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
        self._generation = 0
        self._last_req_time = {}
        self._disk_cache = DiskCache('player_stats_v4.dat',
                                     version=_PLAYER_CACHE_VERSION,
                                     lifetime=_PLAYER_CACHE_LIFETIME)
        self._cleanup_old_cache(('player_stats.dat', 'player_stats_v3.dat'))
        self._disk_cache.load()
        g_wn8_expected.load()

    def _cleanup_old_cache(self, filenames):
        try:
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
        return bool(self._get_tomato_key())

    def _get_rating_mode(self):
        try:
            return getattr(g_configParams.ratingMode, 'value', RatingMode.OVERALL_WN8)
        except Exception:
            return RatingMode.OVERALL_WN8

    def _requires_tomato(self):
        return self._get_rating_mode() == RatingMode.OVERALL_WNX

    def _requires_recent_scrape(self):
        return self._get_rating_mode() in (RatingMode.RECENT_WNX, RatingMode.RECENT_WN8)

    def _has_tomato_for_mode(self, stats):
        if not isinstance(stats, dict):
            return not (self._requires_tomato() or self._requires_recent_scrape())
        mode = self._get_rating_mode()
        if mode == RatingMode.RECENT_WN8:
            return _as_int(stats.get('recent_wn8')) > 0
        if mode == RatingMode.RECENT_WNX:
            return _as_int(stats.get('recent_wnx')) > 0
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
        return '{}{}?{}'.format(TOMATO_API_HOST, path, query) if query else '{}{}'.format(TOMATO_API_HOST, path)

    def _tomato_headers(self):
        return [
            ('Content-Type', 'application/json'),
            ('User-Agent', 'WN8WithoutXVM/0.0.2'),
            ('x-api-key', self._get_tomato_key()),
        ]

    @wg_async
    def _fetch_per_tank_stats(self, accountId):
        url = self._build_url('/wot/tanks/stats/', {'account_id': accountId, 'fields': TANKS_FIELDS})
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
        if not html:
            return None
        try:
            m = re.search(r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>', html, re.S)
            return json.loads(m.group(1)) if m else None
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
        page = next_data.get('pageProps')
        return page if isinstance(page, dict) else None

    def _select_recent_1000_overall(self, recent_data):
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
        return bucket if _first_number(bucket, ('overallWN8', 'wn8', 'wnx', 'overallWNX')) is not None else None

    def _parse_tomato_recent_nextdata(self, response):
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
        overall = self._select_recent_1000_overall(recent_stats.get('data'))
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
        return {'eu': 'EU', 'na': 'NA', 'asia': 'ASIA'}.get(self._get_region(), 'EU')

    @wg_async
    def _resolve_nickname(self, accountId):
        url = self._build_url('/wot/account/info/', {'account_id': accountId, 'fields': 'nickname'})
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
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language', 'en-US,en;q=0.9'),
        ]

    def _parse_tomato_meta(self, html):
        result = {}
        if not html:
            return result
        try:
            m = re.search(r'player-stats\?([^"\'\s<>]+)', html)
            if not m:
                return result
            query = m.group(1).replace('&amp;', '&')
            params = {}
            for pair in query.split('&'):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    params[k.lower()] = v
            if params.get('recentwn8') is not None:
                result['recent_wn8'] = _as_int(params.get('recentwn8'))
            if params.get('recentwinrate') is not None:
                result['recent_winrate'] = _as_float(params.get('recentwinrate'))
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
        slug = '{}-{}'.format(quote(str(nickname)), accountId)
        url = 'https://tomato.gg/stats/{}/{}'.format(slug, region)
        try:
            html = yield fetch_data_with_retry(url, retries=1, delay=1,
                                               headers=self._browser_headers(),
                                               timeout=10.0, as_json=False)
            parsed = self._parse_tomato_meta(html)
            if _as_int(parsed.get('recent_wn8')) > 0:
                raise AsyncReturn(parsed)
            next_data = self._extract_next_data(html)
            if next_data is not None:
                nd_parsed = self._parse_tomato_recent_nextdata(next_data)
                if nd_parsed:
                    parsed.update(nd_parsed)
            if parsed:
                raise AsyncReturn(parsed)
            logger.debug('[StatsAPI] Tomato recent page contained no usable recent WN8 for %s', accountId)
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
            data = yield fetch_data_with_retry(url, retries=1, delay=1,
                                               headers=self._tomato_headers(), timeout=8.0)
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
                try:
                    yield await_callback(g_wn8_expected.load, timeout=35.0)()
                except Exception:
                    logger.exception('[StatsAPI] waiting for WN8 expected values failed')
            if not g_wn8_expected.is_loaded:
                logger.warning('[StatsAPI] WN8 expected values unavailable for %s', accountId)
                raise AsyncReturn(None)
            wn8, total_battles, total_wins, total_damage = calc_overall_wn8_from_per_tank(
                tank_stats, g_wn8_expected._table)
            survived = sum(int(t.get('survived_battles') or 0) for t in tank_stats)
            winrate = (float(total_wins) / total_battles * 100.0) if total_battles > 0 else 0.0
            dpg = (float(total_damage) / total_battles) if total_battles > 0 else 0.0
            survival = (float(survived) / total_battles * 100.0) if total_battles > 0 else 0.0
            stats = {
                'wn8': wn8, 'overall_wn8': wn8, 'recent_wn8': 0,
                'wnx': 0, 'overall_wnx': 0, 'recent_wnx': 0,
                'winrate': winrate, 'battles': total_battles,
                'avg_damage': dpg, 'dpg': dpg, 'survival': survival,
                'dmg_ratio': 0.0,
            }
            mode = self._get_rating_mode()
            if mode in (RatingMode.RECENT_WNX, RatingMode.RECENT_WN8):
                recent_stats = yield self._fetch_tomato_recent(accountId)
                if recent_stats:
                    stats.update(recent_stats)
                stats['tomato_fetched'] = _as_int(stats.get('recent_wn8')) > 0
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
        if self._worker_active or not self._queue:
            return
        accountId = self._queue.popleft()
        cacheKey = str(accountId)
        self._worker_active = True
        generation = self._generation
        self._last_req_time[cacheKey] = time.time()
        logger.debug('[StatsAPI] dequeued %s (remaining=%d)', accountId, len(self._queue))

        @wg_async
        def worker():
            stats = None
            try:
                stats = yield self._compute_stats(accountId)
                if stats and generation == self._generation:
                    self._mem_cache[cacheKey] = stats
                    self._disk_cache.set(cacheKey, stats)
            except Exception:
                logger.exception('[StatsAPI] worker failed for %s', accountId)
            finally:
                if generation == self._generation:
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
        self._generation += 1
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


# =============================================================================
# Tomato parser
# =============================================================================

class TomatoStatsAPI(StatsAPI):
    @staticmethod
    def _decode_next_f_payload(html):
        if not html:
            return ''
        chunks = []
        try:
            pattern = re.compile(
                r'self\.__next_f\.push\(\[\s*\d+\s*,\s*("(?:\\.|[^"\\])*")\s*\]\)',
                re.S,
            )
            for match in pattern.finditer(html):
                try:
                    chunks.append(json.loads(match.group(1)))
                except Exception:
                    continue
        except Exception:
            logger.exception('[StatsAPI] Tomato Next.js payload decode failed')
        return ''.join(chunks)

    @staticmethod
    def _plain_text(value):
        if not value:
            return ''
        value = re.sub(r'<script\b[^>]*>.*?</script>', ' ', value, flags=re.I | re.S)
        value = re.sub(r'<style\b[^>]*>.*?</style>', ' ', value, flags=re.I | re.S)
        value = re.sub(r'<[^>]+>', ' ', value)
        value = value.replace('&nbsp;', ' ').replace('&amp;', '&')
        return re.sub(r'\s+', ' ', value).strip()

    def _parse_recent_labels(self, text):
        result = {}
        if not text:
            return result
        for source in (text, self._plain_text(text)):
            if not source:
                continue
            match = re.search(r'Recent\s*WN8.{0,300}?([0-9][0-9,]{2,7})', source, re.I | re.S)
            if match:
                wn8 = _as_int(match.group(1).replace(',', ''))
                if wn8 > 0:
                    result['recent_wn8'] = wn8
            match = re.search(r'Recent\s*Winrate.{0,200}?([0-9]+(?:\.[0-9]+)?)\s*%', source, re.I | re.S)
            if match:
                result['recent_winrate'] = _as_float(match.group(1))
            if _as_int(result.get('recent_wn8')) > 0:
                logger.debug('[StatsAPI] Tomato recent parsed from summary labels: %s', result)
                return result
        return result

    @staticmethod
    def _extract_balanced_object(text, open_pos):
        if not text or open_pos < 0 or open_pos >= len(text) or text[open_pos] != '{':
            return None
        depth = 0
        in_string = False
        escaped = False
        quote = ''
        for pos in range(open_pos, len(text)):
            ch = text[pos]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == quote:
                    in_string = False
                continue
            if ch in ('"', "'"):
                in_string = True
                quote = ch
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[open_pos:pos + 1]
        return None

    @staticmethod
    def _find_rating_block(node):
        if not isinstance(node, dict):
            return None
        overall = node.get('overall')
        if isinstance(overall, dict) and _first_number(overall, ('overallWN8', 'wn8', 'WN8')) is not None:
            return overall
        if _first_number(node, ('overallWN8', 'wn8', 'WN8')) is not None:
            return node
        for value in node.values():
            if isinstance(value, dict):
                found = TomatoStatsAPI._find_rating_block(value)
                if found is not None:
                    return found
        return None

    def _parse_1000_bucket_from_text(self, text):
        result = {}
        if not text:
            return result
        patterns = (
            re.compile(r'["\']1000["\']\s*:\s*\{'),
            re.compile(r'["\']1000 Battles["\']\s*:\s*\{', re.I),
        )
        for pattern in patterns:
            for match in pattern.finditer(text):
                open_pos = text.find('{', match.start())
                raw_obj = self._extract_balanced_object(text, open_pos)
                if not raw_obj:
                    continue
                try:
                    bucket = json.loads(raw_obj)
                except Exception:
                    continue
                block = self._find_rating_block(bucket)
                if not isinstance(block, dict):
                    continue
                wn8 = _as_int(_first_number(block, ('overallWN8', 'wn8', 'WN8')))
                if wn8 <= 0:
                    continue
                result['recent_wn8'] = wn8
                wnx = _as_int(_first_number(block, ('overallWNX', 'wnx', 'wnX', 'WNX')))
                if wnx > 0:
                    result['recent_wnx'] = wnx
                wr = _first_number(block, ('overallWinrate', 'winrate', 'winRate', 'wr'))
                if wr is not None:
                    result['recent_winrate'] = _as_float(wr)
                battles = _first_number(block, ('overallBattles', 'battles', 'battleCount'))
                if battles is None:
                    battles = _first_number(bucket, ('overallBattles', 'battles', 'battleCount'))
                if battles is not None and not isinstance(battles, dict):
                    result['recent_battles'] = _as_int(battles)
                logger.debug('[StatsAPI] Tomato recent 1000 parsed from JSON payload: %s', result)
                return result
        return result

    def _parse_recent_table_html(self, html):
        result = {}
        if not html:
            return result
        try:
            rows = re.findall(r'<tr\b[^>]*>(.*?)</tr>', html, re.I | re.S)
            for row in rows:
                cells = re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>', row, re.I | re.S)
                if len(cells) < 2:
                    continue
                values = [self._plain_text(cell) for cell in cells]
                label = values[0].strip().upper()
                last = values[-1].strip()
                if label == 'WN8':
                    m = re.search(r'\b(\d{2,5})\b', last.replace(',', ''))
                    if m:
                        result['recent_wn8'] = _as_int(m.group(1))
                elif label == 'BATTLES':
                    m = re.search(r'\b([\d,]+)\b', last)
                    if m:
                        result['recent_battles'] = _as_int(m.group(1).replace(',', ''))
                elif label in ('WINS', 'WINRATE'):
                    m = re.search(r'(\d+(?:\.\d+)?)\s*%', last)
                    if m:
                        result['recent_winrate'] = _as_float(m.group(1))
            if _as_int(result.get('recent_wn8')) > 0:
                logger.debug('[StatsAPI] Tomato recent 1000 parsed from HTML table: %s', result)
                return result
        except Exception:
            logger.exception('[StatsAPI] Tomato recent HTML table parse failed')
        return {}

    def _parse_tomato_recent_current(self, html):
        if not html:
            return {}
        parsed = self._parse_recent_labels(html)
        if _as_int(parsed.get('recent_wn8')) > 0:
            return parsed
        payload = self._decode_next_f_payload(html)
        parsed = self._parse_recent_labels(payload)
        if _as_int(parsed.get('recent_wn8')) > 0:
            return parsed
        parsed = self._parse_1000_bucket_from_text(payload)
        if _as_int(parsed.get('recent_wn8')) > 0:
            return parsed
        parsed = self._parse_1000_bucket_from_text(html)
        if _as_int(parsed.get('recent_wn8')) > 0:
            return parsed
        return self._parse_recent_table_html(html)

    @wg_async
    def _fetch_tomato_recent(self, accountId):
        nickname = yield self._resolve_nickname(accountId)
        if not nickname:
            logger.debug('[StatsAPI] Tomato recent: nickname unavailable for %s', accountId)
            raise AsyncReturn({})
        region = self._get_region_code()
        try:
            from urllib.parse import quote
        except ImportError:
            from urllib import quote
        slug = '{}-{}'.format(quote(str(nickname)), accountId)
        urls = (
            'https://cf.tomato.gg/stats/{}/{}'.format(region, slug),
            'https://tomato.gg/stats/{}/{}'.format(slug, region),
        )
        for url in urls:
            try:
                logger.debug('[StatsAPI] Tomato recent request: %s', url)
                html = yield fetch_data_with_retry(
                    url, retries=1, delay=1, headers=self._browser_headers(),
                    timeout=12.0, as_json=False,
                )
                if not html:
                    logger.debug('[StatsAPI] Tomato recent empty response for %s', accountId)
                    continue
                logger.debug('[StatsAPI] Tomato recent response length for %s: %d', accountId, len(html))
                parsed = self._parse_tomato_meta(html)
                if _as_int(parsed.get('recent_wn8')) > 0:
                    raise AsyncReturn(parsed)
                next_data = self._extract_next_data(html)
                if next_data is not None:
                    old_parsed = self._parse_tomato_recent_nextdata(next_data)
                    if old_parsed:
                        parsed.update(old_parsed)
                if _as_int(parsed.get('recent_wn8')) > 0:
                    raise AsyncReturn(parsed)
                current = self._parse_tomato_recent_current(html)
                if current:
                    parsed.update(current)
                if _as_int(parsed.get('recent_wn8')) > 0:
                    logger.debug('[StatsAPI] Tomato recent parsed for %s: %s', accountId, parsed)
                    raise AsyncReturn(parsed)
                logger.debug('[StatsAPI] Tomato page had no usable recent WN8 for %s (%s)', accountId, url)
            except AsyncReturn:
                raise
            except Exception:
                logger.exception('[StatsAPI] Tomato recent fetch failed for %s via %s', accountId, url)
        raise AsyncReturn({})


# =============================================================================
# Fast Tomato retry API
# =============================================================================

class TomatoRetryStatsAPI(TomatoStatsAPI):
    def __init__(self):
        TomatoStatsAPI.__init__(self)
        self._nickname_hints = {}

    def set_player_nickname(self, accountId, nickname):
        if not accountId or not nickname:
            return
        try:
            value = unicode(nickname) if 'unicode' in globals() else str(nickname)
        except Exception:
            try:
                value = str(nickname)
            except Exception:
                return
        value = value.strip()
        if value:
            self._nickname_hints[str(accountId)] = value

    @wg_async
    def _resolve_nickname(self, accountId):
        hint = self._nickname_hints.get(str(accountId))
        if hint:
            raise AsyncReturn(hint)
        try:
            nickname = yield TomatoStatsAPI._resolve_nickname(self, accountId)
            raise AsyncReturn(nickname)
        except AsyncReturn:
            raise
        except Exception:
            logger.exception('[StatsAPI] fallback nickname resolve failed for %s', accountId)
            raise AsyncReturn(None)

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
        slug = '{}-{}'.format(quote(str(nickname)), accountId)
        url = 'https://tomato.gg/stats/{}/{}'.format(slug, region)
        try:
            html = yield fetch_data_with_retry(
                url, retries=1, delay=0, headers=self._browser_headers(),
                timeout=7.0, as_json=False,
            )
            if not html:
                raise AsyncReturn({})
            parsed = self._parse_tomato_meta(html)
            if _as_int(parsed.get('recent_wn8')) > 0:
                raise AsyncReturn(parsed)
            next_data = self._extract_next_data(html)
            if next_data is not None:
                old_parsed = self._parse_tomato_recent_nextdata(next_data)
                if old_parsed:
                    parsed.update(old_parsed)
            if _as_int(parsed.get('recent_wn8')) > 0:
                raise AsyncReturn(parsed)
            current = self._parse_tomato_recent_current(html)
            if current:
                parsed.update(current)
            if _as_int(parsed.get('recent_wn8')) > 0:
                raise AsyncReturn(parsed)
            logger.error('[StatsAPI] Tomato returned HTTP 200 but no recent WN8 for %s (body=%s bytes)',
                         accountId, len(html))
            raise AsyncReturn({})
        except AsyncReturn:
            raise
        except Exception:
            logger.exception('[StatsAPI] Tomato recent fetch failed for %s via %s', accountId, url)
            raise AsyncReturn({})


# =============================================================================
# Stats manager
# =============================================================================

class StatsManager(object):
    def __init__(self, stats_api):
        self._stats_api = stats_api
        self._stats_cache = {}
        self._update_callbacks = []
        logger.debug('[StatsManager] Initialized')

    def add_update_callback(self, callback):
        if callback not in self._update_callbacks:
            self._update_callbacks.append(callback)

    def remove_update_callback(self, callback):
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)

    def _notify_update(self, account_id):
        for callback in self._update_callbacks:
            try:
                callback(account_id)
            except Exception:
                logger.exception('[StatsManager] Error in update callback')

    def set_player_nickname(self, account_id, nickname):
        try:
            setter = getattr(self._stats_api, 'set_player_nickname', None)
            if setter is not None:
                setter(account_id, nickname)
        except Exception:
            logger.exception('[StatsManager] Failed to store nickname for %s', account_id)

    def get_player_stats(self, account_id, callback=None):
        cache_key = str(account_id)
        if cache_key in self._stats_cache:
            stats = self._stats_cache[cache_key]
            if callback:
                callback(account_id, stats)
            return stats

        def on_stats_received(acc_id, raw_stats):
            if raw_stats:
                formatted_stats = self._format_stats(raw_stats)
                self._stats_cache[str(acc_id)] = formatted_stats
                self._notify_update(acc_id)
                if callback:
                    callback(acc_id, formatted_stats)
            elif callback:
                callback(acc_id, None)

        self._stats_api.get_player_stats(account_id, on_stats_received)
        return None

    def get_cached_stats(self, account_id):
        return self._stats_cache.get(str(account_id))

    def is_stats_loaded(self, account_id):
        return str(account_id) in self._stats_cache

    def _select_rating(self, raw_stats):
        try:
            mode = getattr(g_configParams.ratingMode, 'value', RatingMode.OVERALL_WN8)
        except Exception:
            mode = RatingMode.OVERALL_WN8
        if mode == RatingMode.RECENT_WNX:
            value = int(raw_stats.get('recent_wnx') or 0)
            if value <= 0:
                fallback = int(raw_stats.get('overall_wnx') or raw_stats.get('wnx') or 0)
                return fallback, get_wn8_color(fallback), 'WNX', 'overall_wnx'
            return value, get_wn8_color(value), 'WNX', 'recent_wnx'
        if mode == RatingMode.RECENT_WN8:
            value = int(raw_stats.get('recent_wn8') or 0)
            if value <= 0:
                fallback = int(raw_stats.get('overall_wn8') or raw_stats.get('wn8') or 0)
                return fallback, get_wn8_color(fallback), 'WN8', 'overall_wn8'
            return value, get_wn8_color(value), 'WN8', 'recent_wn8'
        if mode == RatingMode.OVERALL_WNX:
            value = int(raw_stats.get('overall_wnx') or raw_stats.get('wnx') or 0)
            return value, get_wn8_color(value), 'WNX', 'overall_wnx'
        value = int(raw_stats.get('overall_wn8') or raw_stats.get('wn8') or 0)
        return value, get_wn8_color(value), 'WN8', 'overall_wn8'

    def _format_stats(self, raw_stats):
        wn8 = int(raw_stats.get('wn8', 0))
        winrate = round(float(raw_stats.get('winrate', 0)), 2)
        battles = int(raw_stats.get('battles', 0))
        selected_rating, selected_rating_color, selected_rating_name, selected_rating_key = self._select_rating(raw_stats)
        try:
            mode = getattr(g_configParams.ratingMode, 'value', RatingMode.OVERALL_WN8)
        except Exception:
            mode = RatingMode.OVERALL_WN8
        if mode in (RatingMode.RECENT_WN8, RatingMode.RECENT_WNX):
            recent_wr = raw_stats.get('recent_winrate')
            if recent_wr is not None and float(recent_wr) > 0:
                winrate = round(float(recent_wr), 2)
        return {
            'wn8': wn8,
            'overall_wn8': int(raw_stats.get('overall_wn8') or wn8),
            'recent_wn8': int(raw_stats.get('recent_wn8') or 0),
            'wnx': int(raw_stats.get('wnx') or 0),
            'overall_wnx': int(raw_stats.get('overall_wnx') or raw_stats.get('wnx') or 0),
            'recent_wnx': int(raw_stats.get('recent_wnx') or 0),
            'selected_rating': selected_rating,
            'selected_rating_color': selected_rating_color,
            'selected_rating_name': selected_rating_name,
            'selected_rating_key': selected_rating_key,
            'wn8_color': get_wn8_color(wn8),
            'winrate': winrate,
            'winrate_color': get_winrate_color(winrate),
            'battles': battles,
            'battles_color': get_battles_color(battles),
        }

    def set_anonymous_player(self, account_id):
        if not account_id:
            return
        self._stats_cache[str(account_id)] = {
            'anonymous': True,
            'wn8': 0,
            'wn8_text': ANON_RATING_TOKEN,
            'selected_rating': 0,
            'selected_rating_color': '',
            'selected_rating_name': '',
            'selected_rating_key': '',
            'wn8_color': '',
            'winrate': 0,
            'winrate_color': '',
            'battles': 0,
            'battles_color': '',
        }
        self._notify_update(account_id)

    def clear_cache(self):
        self._stats_cache.clear()
        logger.debug('[StatsManager] Cache cleared')

    def clear_update_callbacks(self):
        self._update_callbacks[:] = []
        logger.debug('[StatsManager] Update callbacks cleared')


# =============================================================================
# Lifecycle
# =============================================================================

__all__ = ['initialize_stats', 'finalize_stats', 'g_stats_manager', 'g_stats_api']

g_stats_api = None
g_stats_manager = None


def initialize_stats():
    global g_stats_api, g_stats_manager
    try:
        if g_stats_api is None:
            g_stats_api = TomatoRetryStatsAPI()
            logger.debug('[StatsAPI] Initialized')
        if g_stats_manager is None:
            g_stats_manager = StatsManager(g_stats_api)
            logger.debug('[StatsManager] Initialized')
        logger.debug('[WN8WithoutXVM] Stats components initialized successfully')
    except Exception:
        logger.exception('[WN8WithoutXVM] Stats initialization failed')


def finalize_stats():
    global g_stats_api, g_stats_manager
    try:
        if g_stats_manager:
            g_stats_manager.clear_update_callbacks()
            g_stats_manager.clear_cache()
            g_stats_manager = None
            logger.debug('[StatsManager] Finalized')
        if g_stats_api:
            g_stats_api.fini()
            g_stats_api = None
            logger.debug('[StatsAPI] Finalized')
        try:
            g_wn8_expected.fini()
        except Exception:
            logger.exception('[WN8Expected] fini failed')
        logger.debug('[WN8WithoutXVM] Stats components finalized successfully')
    except Exception:
        logger.exception('[WN8WithoutXVM] Stats finalization failed')
