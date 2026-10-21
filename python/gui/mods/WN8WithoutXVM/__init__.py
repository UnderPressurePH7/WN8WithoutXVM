# -*- coding: utf-8 -*-

import sys

from .utils import logger
from . import settings as _settings

# Preserve legacy settings import paths used by existing modules.
_settings.__path__ = []
for _legacy_name in ('config', 'config_file', 'config_param', 'config_param_types', 'config_template', 'translations'):
    sys.modules[__name__ + '.settings.' + _legacy_name] = _settings

# Preserve old consolidated module name for compatibility.
sys.modules[__name__ + '.settings_core'] = _settings

from .stats import initialize_stats, finalize_stats
from .views import PatchBattlePlayer, PanelView, PatchBattleLoading, ModePanelAdapters
from .settings_window import initialize_settings_window, finalize_settings_window
from .battle import (
    BattleProvider,
    initialize_post_battle_deanon,
    finalize_post_battle_deanon,
)

# stats.py is already loaded above; alias the old name without importing it again.
_stats = sys.modules.get(__name__ + '.stats')
if _stats is not None:
    sys.modules[__name__ + '.stats_core'] = _stats

__all__ = [
    'initialize',
    'finalize'
]

g_patch_battle_player = None
g_patch_battle_loading = None
g_panel_view = None
g_battle_provider = None
g_mode_panel_adapters = None


def initialize():
    global g_patch_battle_player, g_patch_battle_loading
    global g_panel_view, g_battle_provider, g_mode_panel_adapters
    try:
        initialize_stats()
        initialize_settings_window()
        initialize_post_battle_deanon()

        from .stats import g_stats_manager

        if g_patch_battle_player is None:
            g_patch_battle_player = PatchBattlePlayer(g_stats_manager)
            if not g_patch_battle_player.apply_patches():
                logger.error('[WN8WithoutXVM] PatchBattlePlayer failed to apply')
            else:
                logger.debug('[WN8WithoutXVM] PatchBattlePlayer created and applied')

        if g_patch_battle_loading is None:
            g_patch_battle_loading = PatchBattleLoading(g_stats_manager)
            g_patch_battle_loading.apply_patches()
            logger.debug('[WN8WithoutXVM] PatchBattleLoading created and applied')

        if g_panel_view is None:
            g_panel_view = PanelView(g_stats_manager)
            logger.debug('[WN8WithoutXVM] PanelView created')

        if g_mode_panel_adapters is None:
            from .views.player_panel import g_events
            if g_events is not None:
                g_mode_panel_adapters = ModePanelAdapters(g_events)
                g_mode_panel_adapters.apply_patches()
                logger.debug('[WN8WithoutXVM] Mode panel adapters initialized')

        if g_battle_provider is None:
            g_battle_provider = BattleProvider(g_stats_manager, g_panel_view)
            logger.debug('[WN8WithoutXVM] BattleProvider initialized')

        logger.debug('[WN8WithoutXVM] All components initialized successfully')

    except Exception:
        logger.exception('[WN8WithoutXVM] Initialization failed')
        finalize()


def finalize():
    global g_patch_battle_player, g_patch_battle_loading
    global g_panel_view, g_battle_provider, g_mode_panel_adapters
    try:
        finalize_settings_window()
        finalize_post_battle_deanon()

        if g_battle_provider:
            g_battle_provider.fini()
            g_battle_provider = None
            logger.debug('[WN8WithoutXVM] BattleProvider finalized')

        if g_mode_panel_adapters:
            g_mode_panel_adapters.remove_patches()
            g_mode_panel_adapters = None
            logger.debug('[WN8WithoutXVM] Mode panel adapters finalized')

        if g_panel_view:
            g_panel_view.destroy()
            g_panel_view = None
            logger.debug('[WN8WithoutXVM] PanelView finalized')

        if g_patch_battle_loading:
            g_patch_battle_loading.remove_patches()
            g_patch_battle_loading = None
            logger.debug('[WN8WithoutXVM] PatchBattleLoading finalized')

        if g_patch_battle_player:
            g_patch_battle_player.remove_patches()
            g_patch_battle_player = None
            logger.debug('[WN8WithoutXVM] PatchBattlePlayer finalized')

        finalize_stats()
        logger.debug('[WN8WithoutXVM] All components finalized successfully')

    except Exception:
        logger.exception('[WN8WithoutXVM] Finalization failed')
