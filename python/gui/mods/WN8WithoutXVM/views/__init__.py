from .hooks import PatchBattlePlayer, PatchBattleLoading, ModePanelAdapters
from .panel_view import PanelView
from ..settings.config_param import g_configParams, PanelDisplayMode


def _is_panel_display_visible(self):
    try:
        if g_configParams.panelDisplayMode.value != PanelDisplayMode.ALT:
            return True
        from .player_panel import g_events
        return bool(g_events and g_events.isExtendedInfoVisible())
    except Exception:
        return True


PanelView._isPanelDisplayVisible = _is_panel_display_visible


__all__ = [
    'PatchBattlePlayer',
    'PanelView',
    'PatchBattleLoading',
    'ModePanelAdapters',
]
