from ..utils import (
    logger,
    get_wn8_color,
    get_winrate_color,
    get_battles_color,
    get_survival_color,
    get_dmg_ratio_color
)


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

    def _format_stats(self, raw_stats):
        wn8 = int(raw_stats.get('wn8', 0))
        winrate = round(float(raw_stats.get('winrate', 0)), 2)
        battles = int(raw_stats.get('battles', 0))
        avg_damage = int(raw_stats.get('avg_damage', 0))
        dpg = int(raw_stats.get('dpg', 0))
        survival = round(float(raw_stats.get('survival', 0)), 2)
        dmg_ratio = round(float(raw_stats.get('dmg_ratio', 0)), 2)

        return {
            'wn8': wn8,
            'wn8_color': get_wn8_color(wn8),
            'winrate': winrate,
            'winrate_color': get_winrate_color(winrate),
            'battles': battles,
            'battles_color': get_battles_color(battles),
            'avg_damage': avg_damage,
            'avg_damage_color': get_wn8_color(avg_damage / 10) if avg_damage > 0 else '#FFFFFF',
            'dpg': dpg,
            'dpg_color': get_wn8_color(dpg / 10) if dpg > 0 else '#FFFFFF',
            'survival': survival,
            'survival_color': get_survival_color(survival),
            'dmg_ratio': dmg_ratio,
            'dmg_ratio_color': get_dmg_ratio_color(dmg_ratio)
        }

    def clear_cache(self):
        self._stats_cache.clear()
        logger.debug('[StatsManager] Cache cleared')
