from .utils import logger
from .stats import initialize_stats, finalize_stats
from .views import PatchBattlePlayer, PanelView, PatchBattleLoading

__all__ = [
    'initialize',
    'finalize'
]

g_patch_battle_player = None
g_patch_battle_loading = None
g_panel_view = None
g_battle_provider = None
g_mode_panel_adapters = None


def _configure_gameface_tab_patch():
    """
    Keep the stock BattlePlayer model layout intact.

    The previous implementation appended six custom string properties to every
    BattlePlayer. Classic TabView tolerated the extended model, but Comp7 and
    Comp7 Light failed to convert playerList.allies/enemies to Gameface objects.
    TabView.js already supports the safe fallback transport packed into
    vehicleName with TAB separators, so custom WULF properties are unnecessary.
    """
    try:
        def _stock_model_is_enough(patch_self):
            patch_self._original_battle_player_constructor = None
            patch_self._original_battle_player_initialize = None
            logger.debug('[WN8WithoutXVM] Using stock BattlePlayer schema for Gameface TAB')
            return True

        def _refresh_tab_player(patch_self, tv_ref, player):
            try:
                tab_view = tv_ref() if tv_ref else None
                if tab_view is None or player is None:
                    return False

                vehicle_id = player.getVehicleId() if hasattr(player, 'getVehicleId') else None
                if not vehicle_id:
                    return False

                active = patch_self._active_players.get(vehicle_id)
                if not active:
                    return False

                _, vehicle_info, original_vehicle_name, _ = active
                # modifyBattlePlayer is a context manager and expects vehicleId,
                # not a BattlePlayer object. Updating the yielded model makes the
                # WULF array invalidate correctly in Random and Comp7.
                with tab_view.modifyBattlePlayer(vehicle_id) as current_player:
                    if current_player is None:
                        return False
                    patch_self._set_values(current_player, vehicle_info, original_vehicle_name)
                return True
            except Exception as e:
                logger.debug('[WN8WithoutXVM] Gameface TAB refresh failed: %s', e)
                return False

        PatchBattlePlayer._monkey_patch_battle_player = _stock_model_is_enough
        PatchBattlePlayer._refresh_tab_player = _refresh_tab_player
    except Exception:
        logger.exception('[WN8WithoutXVM] Failed to configure Gameface TAB compatibility')


def initialize():
    global g_patch_battle_player, g_patch_battle_loading
    global g_panel_view, g_battle_provider, g_mode_panel_adapters
    try:
        initialize_stats()

        from .stats import g_stats_manager

        if g_patch_battle_player is None:
            _configure_gameface_tab_patch()
            g_patch_battle_player = PatchBattlePlayer(g_stats_manager)
            g_patch_battle_player.apply_patches()
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
            from .views.mode_panel_adapters import ModePanelAdapters
            if g_events is not None:
                g_mode_panel_adapters = ModePanelAdapters(g_events)
                g_mode_panel_adapters.apply_patches()
                logger.debug('[WN8WithoutXVM] Mode panel adapters initialized')

        if g_battle_provider is None:
            from .battle_provider import BattleProvider
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
