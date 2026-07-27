from ..utils import logger


class ModePanelAdapters(object):
    """Install redraw hooks for non-classic supported battle UIs.

    Classic/Stronghold already use the hooks installed by player_panel.Events.
    This adapter extends the same refresh contract to Comp7 and Epic Random.
    Imports are optional because WG can omit seasonal packages from a client.
    """

    _INVALIDATE_METHODS = (
        'invalidateVehicleStatus',
        'invalidateVehicleInfo',
        '_invalidateVehicle',
        'as_invalidateVehicleStatusS',
        'updateVehiclesData',
    )

    _MODE_METHODS = (
        'setInitialMode',
        'setLargeMode',
        '_handleNextMode',
        'as_setPanelModeS',
        'tryToSetPanelModeByMouse',
        'setOverrideExInfo',
        '_PlayersPanel__handleShowExtendedInfo',
    )

    def __init__(self, events):
        self._events = events
        self._patched = []
        self._applied = False

    def apply_patches(self):
        if self._applied:
            return

        panel_classes = []

        # WoT 2.3.x moved Comp7 and Comp7 Light to the shared comp7_core
        # extension package. Keep the older path as a compatibility fallback.
        self._append_optional(
            panel_classes,
            'comp7_core.gui.Scaleform.daapi.view.battle.players_panel',
            'PlayersPanel',
            'Comp7 Core/Light',
        )
        self._append_optional(
            panel_classes,
            'gui.Scaleform.daapi.view.battle.comp7.players_panel',
            'PlayersPanel',
            'Comp7 legacy',
        )

        self._append_optional(
            panel_classes,
            'gui.Scaleform.daapi.view.battle.epic_random.players_panel',
            'EpicRandomPlayersPanel',
            'Epic Random',
        )
        self._append_optional(
            panel_classes,
            'gui.Scaleform.daapi.view.battle.epic_random.players_panel',
            'PlayersPanel',
            'Epic Random legacy',
        )

        seen = set()
        for panel_class, label in panel_classes:
            if panel_class in seen:
                continue
            seen.add(panel_class)
            self._patch_panel_class(panel_class, label)

        self._applied = True
        logger.debug('[ModePanelAdapters] Applied %d hooks', len(self._patched))

    def remove_patches(self):
        while self._patched:
            cls, method_name, original = self._patched.pop()
            try:
                setattr(cls, method_name, original)
            except Exception:
                logger.exception(
                    '[ModePanelAdapters] Failed restoring %s.%s',
                    getattr(cls, '__name__', cls), method_name,
                )
        self._applied = False

    def _append_optional(self, target, module_name, class_name, label):
        try:
            module = __import__(module_name, fromlist=[class_name])
            panel_class = getattr(module, class_name, None)
            if panel_class is not None:
                target.append((panel_class, label))
        except Exception as error:
            logger.debug(
                '[ModePanelAdapters] %s unavailable (%s.%s): %s',
                label, module_name, class_name, error,
            )

    def _patch_panel_class(self, panel_class, label):
        patched_names = set()
        for method_name in self._INVALIDATE_METHODS + self._MODE_METHODS:
            if method_name in patched_names or not hasattr(panel_class, method_name):
                continue
            original = getattr(panel_class, method_name)
            if not callable(original):
                continue
            setattr(panel_class, method_name, self._make_wrapper(original, method_name))
            self._patched.append((panel_class, method_name, original))
            patched_names.add(method_name)
            logger.debug('[ModePanelAdapters] Patched %s.%s', label, method_name)

    def _make_wrapper(self, original, method_name):
        events = self._events

        def wrapped(panel_self, *args, **kwargs):
            result = original(panel_self, *args, **kwargs)
            try:
                events._onPanelModeChanged(panel_self)
                events._scheduleUpdateModeBurst()
            except Exception:
                logger.exception(
                    '[ModePanelAdapters] Refresh failed after %s', method_name,
                )
            return result

        wrapped.__name__ = getattr(original, '__name__', method_name)
        wrapped.__doc__ = getattr(original, '__doc__', None)
        return wrapped
