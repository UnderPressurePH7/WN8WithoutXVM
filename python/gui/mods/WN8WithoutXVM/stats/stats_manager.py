from ..utils import (
    logger,
    get_wn8_color,
    get_winrate_color,
    get_battles_color,
    ANON_RATING_TOKEN
)
from ..settings.config_param import g_configParams, RatingMode


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
            else:
                if callback:
                    callback(acc_id, None)

        self._stats_api.get_player_stats(account_id, on_stats_received)
        return None

    def get_cached_stats(self, account_id):
        cache_key = str(account_id)
        return self._stats_cache.get(cache_key)

    def is_stats_loaded(self, account_id):
        cache_key = str(account_id)
        return cache_key in self._stats_cache

    def _select_rating(self, raw_stats):
        try:
            mode = getattr(g_configParams.ratingMode, 'value', RatingMode.OVERALL_WN8)
        except Exception:
            mode = RatingMode.OVERALL_WN8

        if mode == RatingMode.RECENT_WNX:
            value = int(raw_stats.get('recent_wnx') or 0)
            return value, get_wn8_color(value), 'WNX', 'recent_wnx'
        if mode == RatingMode.RECENT_WN8:
            value = int(raw_stats.get('recent_wn8') or 0)
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
            'battles_color': get_battles_color(battles)
        }


    def set_anonymous_player(self, account_id):
        if not account_id:
            return
        cache_key = str(account_id)
        self._stats_cache[cache_key] = {
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
            'battles_color': ''
        }
        self._notify_update(account_id)

    def clear_cache(self):
        self._stats_cache.clear()
        logger.debug('[StatsManager] Cache cleared')

    def clear_update_callbacks(self):
        self._update_callbacks[:] = []
        logger.debug('[StatsManager] Update callbacks cleared')
