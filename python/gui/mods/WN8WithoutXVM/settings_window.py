# -*- coding: utf-8 -*-

"""Standalone WN8 Without XVM settings entry and Gameface window."""

import json

from PlayerEvents import g_playerEvents
from .utils import logger

__all__ = ('initialize_settings_window', 'finalize_settings_window', 'open_settings_window')

_AVAILABLE = False
_IMPORT_ERROR = None
try:
    from frameworks.wulf import ViewModel, ViewSettings, ViewFlags, WindowFlags, WindowLayer, PositionAnchor
    from gui.impl.pub import ViewImpl, WindowImpl
    from gui.impl.gen import R
    _AVAILABLE = True
except Exception as exc:
    _IMPORT_ERROR = repr(exc)

RES_ID = 'WN8SettingsView'
VIEW_WIDTH = 980
VIEW_HEIGHT = 640
_MOD_ID = 'wn8_settings'

_active = None
_registered = False
_retry_cb = None
_battle_close_subscribed = False


def _config():
    from .settings import g_config
    return g_config


def _payload():
    try:
        return json.dumps(
            _config().getGamefacePayload(),
            ensure_ascii=False,
            separators=(',', ':'),
        )
    except Exception:
        logger.exception('[WN8WithoutXVM] Failed to build settings payload')
        return '{"settings":{},"options":{},"meta":{},"i18n":{}}'


def _surface_size():
    try:
        import GUI
        width, height = GUI.screenResolution()
        return max(VIEW_WIDTH, int(width)), max(VIEW_HEIGHT, int(height))
    except Exception:
        return VIEW_WIDTH, VIEW_HEIGHT


def _drop_active(view=None):
    global _active
    if _active is not None and (view is None or _active[1] is view):
        _active = None


if _AVAILABLE:
    class SettingsVM(ViewModel):
        __slots__ = ('onClose', 'onSet')

        def __init__(self):
            super(SettingsVM, self).__init__(properties=3, commands=2)

        def _initialize(self):
            super(SettingsVM, self)._initialize()
            self._addStringProperty('payload', '{}')
            self._addNumberProperty('surfaceWidth', VIEW_WIDTH)
            self._addNumberProperty('surfaceHeight', VIEW_HEIGHT)
            self.onClose = self._addCommand('onClose')
            self.onSet = self._addCommand('onSet')

        def setPayload(self, value):
            self._setString(0, value)

        def setSurfaceSize(self, width, height):
            self._setNumber(1, int(width))
            self._setNumber(2, int(height))


    class SettingsView(ViewImpl):
        _layoutID = R.mods.dictor.wn8.WN8SettingsView

        def __init__(self):
            settings = ViewSettings(
                layoutID=self._layoutID(),
                flags=ViewFlags.VIEW,
                model=SettingsVM(),
            )
            super(SettingsView, self).__init__(settings)

        @property
        def viewModel(self):
            return super(SettingsView, self).getViewModel()

        def _getEvents(self):
            return (
                (self.viewModel.onClose, self._onClose),
                (self.viewModel.onSet, self._onSet),
            )

        def _onLoading(self, *args, **kwargs):
            super(SettingsView, self)._onLoading(*args, **kwargs)
            refresh()

        def _onClose(self, *args, **kwargs):
            close()

        def _onSet(self, args=None, *unused, **kwargs):
            if not isinstance(args, dict):
                return
            key = args.get('key')
            if not key:
                return
            try:
                _config().applyGamefaceSetting(key, args.get('value'))
                refresh()
            except Exception:
                logger.exception('[WN8WithoutXVM] Gameface setting update failed: %s', key)

        def _finalize(self):
            _drop_active(self)
            super(SettingsView, self)._finalize()


    class SettingsWindow(WindowImpl):
        def __init__(self, content):
            super(SettingsWindow, self).__init__(
                WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN,
                content=content,
                layer=WindowLayer.WINDOW,
            )

        def _onReady(self):
            try:
                self.show(focus=True)
            except Exception:
                logger.exception('[WN8WithoutXVM] Settings window show failed')
                close()
                return

            try:
                self.move(
                    0,
                    0,
                    xAnchor=PositionAnchor.LEFT,
                    yAnchor=PositionAnchor.TOP,
                )
            except Exception:
                logger.exception('[WN8WithoutXVM] Settings window placement failed')

            refresh()


def available():
    if not _AVAILABLE:
        logger.error('[WN8WithoutXVM] Gameface settings unavailable: %s', _IMPORT_ERROR)
    return bool(_AVAILABLE)


def _live_model():
    if _active is None:
        return None
    try:
        return _active[1].viewModel
    except Exception:
        _drop_active()
        return None


def _open_fresh():
    global _active

    stage = 'resolve layout'
    try:
        layout = SettingsView._layoutID()
        if layout is None or layout < 0:
            logger.error('[WN8WithoutXVM] Gameface resource %s was not registered', RES_ID)
            return False

        stage = 'create view model/view'
        view = SettingsView()

        stage = 'create window'
        window = SettingsWindow(view)
        _active = (window, view)

        stage = 'load window'
        window.load()
        return True
    except Exception:
        _drop_active()
        logger.exception('[WN8WithoutXVM] Settings window failed at stage: %s', stage)
        return False


def is_open():
    return _live_model() is not None


def show():
    if not available():
        return False
    if is_open():
        return refresh()
    return _open_fresh()


def refresh():
    model = _live_model()
    if model is None:
        return False

    try:
        width, height = _surface_size()
        with model.transaction() as vm:
            vm.setPayload(_payload())
            vm.setSurfaceSize(width, height)
        return True
    except Exception:
        logger.exception('[WN8WithoutXVM] Settings window model refresh failed')
        return False


def close(destroy=True):
    global _active
    if _active is None:
        return

    window = _active[0]
    _active = None
    try:
        window.destroy()
    except Exception:
        logger.exception('[WN8WithoutXVM] Settings window destroy failed')


def open_settings_window(*args, **kwargs):
    try:
        return show()
    except Exception:
        logger.exception('[WN8WithoutXVM] Failed to open Gameface settings window')
        return False


def _get_lobby_app():
    try:
        from helpers import dependency
        from skeletons.gui.app_loader import IAppLoader
        return dependency.instance(IAppLoader).getDefLobbyApp()
    except Exception:
        try:
            from gui.app_loader import g_appLoader
            return g_appLoader.getDefLobbyApp()
        except Exception:
            return None


def _is_login_space():
    try:
        import BigWorld
        player = BigWorld.player()
        return player is not None and 'login' in player.__class__.__name__.lower()
    except Exception:
        return False


def _is_hangar_state_active():
    try:
        from gui.lobby_state_machine import g_stateMachine
        state = g_stateMachine.getCurrentState()
        if state is not None:
            name = type(state).__name__.lower()
            if 'hangar' in name or 'defaultlobby' in name:
                return True
    except Exception:
        pass

    try:
        import BigWorld
        from Account import PlayerAccount
        return isinstance(BigWorld.player(), PlayerAccount)
    except Exception:
        return False


def _lobby_ready():
    return not _is_login_space() and _is_hangar_state_active() and _get_lobby_app() is not None


def _find_mods_list_api():
    for module_name in ('gui.mods.modsListApi', 'modsListApi', 'gui.modsListApi'):
        try:
            module = __import__(module_name, fromlist=['g_modsListApi'])
            api = getattr(module, 'g_modsListApi', None)
            if api is not None:
                return api
        except Exception:
            pass
    return None


def _register_now():
    global _registered
    if _registered:
        return True
    if not _lobby_ready():
        return False

    api = _find_mods_list_api()
    if api is None:
        return False

    entry = {
        'id': _MOD_ID,
        'name': u'WN8 Without XVM',
        'description': u'WN8 Without XVM',
        'icon': 'gui/maps/icons/wn8withoutxvm/inq_wn8.png',
        'enabled': True,
        'login': False,
        'lobby': True,
        'callback': open_settings_window,
    }

    method = getattr(api, 'addModification', None)
    if method is not None:
        try:
            method(**entry)
            _registered = True
            return True
        except TypeError:
            try:
                method(
                    entry['id'], entry['name'], entry['description'], entry['icon'],
                    entry['enabled'], entry['login'], entry['lobby'], entry['callback']
                )
                _registered = True
                return True
            except Exception:
                pass
        except Exception:
            logger.exception('[WN8WithoutXVM] modsListApi.addModification failed')
            return False

    legacy = getattr(api, 'addMod', None)
    if legacy is not None:
        try:
            legacy(
                entry['id'], entry['name'], entry['icon'],
                entry['enabled'], entry['login'], entry['lobby'], entry['callback']
            )
            _registered = True
            return True
        except Exception:
            logger.exception('[WN8WithoutXVM] modsListApi.addMod failed')
    return False


def _retry_register(attempt=0):
    global _retry_cb
    _retry_cb = None
    if _register_now() or attempt >= 60:
        return
    try:
        import BigWorld
        _retry_cb = BigWorld.callback(1.0, lambda: _retry_register(attempt + 1))
    except Exception:
        _retry_cb = None


def _close_for_battle(*args, **kwargs):
    try:
        close(destroy=True)
    except Exception:
        pass


def _subscribe_lifecycle():
    global _battle_close_subscribed
    if _battle_close_subscribed:
        return
    try:
        g_playerEvents.onAvatarReady += _close_for_battle
        _battle_close_subscribed = True
    except Exception:
        logger.exception('[WN8WithoutXVM] Failed to subscribe settings lifecycle')


def _unsubscribe_lifecycle():
    global _battle_close_subscribed
    if not _battle_close_subscribed:
        return
    try:
        g_playerEvents.onAvatarReady -= _close_for_battle
    except Exception:
        pass
    _battle_close_subscribed = False


def initialize_settings_window():
    try:
        _subscribe_lifecycle()
        _retry_register(0)
    except Exception:
        logger.exception('[WN8WithoutXVM] Settings window registration failed')


def finalize_settings_window():
    global _retry_cb, _registered
    try:
        close(destroy=True)
    except Exception:
        pass

    _unsubscribe_lifecycle()

    if _retry_cb is not None:
        try:
            import BigWorld
            BigWorld.cancelCallback(_retry_cb)
        except Exception:
            pass
    _retry_cb = None
    _registered = False
