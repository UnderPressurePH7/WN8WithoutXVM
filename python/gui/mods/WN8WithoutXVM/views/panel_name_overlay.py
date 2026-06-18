# panel_name_overlay.py  — Python 2.7
# GUI.Text overlay that draws colored vehicle names over the WoT player panel.
# Uses Flash stage coords via as_getVehicleTFPositions.

import GUI
import BigWorld
from gui import g_guiResetters

from ..utils import logger
from ..settings.config_param import g_configParams, WinratePosition


def _hex_to_rgba(hex_color):
    try:
        h = hex_color.lstrip('#')
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    except Exception:
        return (255, 255, 255, 255)


def _stage_to_clip(sx, sy):
    """Convert Flash stage pixels (top-left origin) to GUI clip space."""
    try:
        w, h = GUI.screenResolution()[:2]
        cx = (float(sx) / w) * 2.0 - 1.0
        cy = 1.0 - (float(sy) / h) * 2.0
        return (cx, cy, 1.0)
    except Exception:
        return (0.0, 0.0, 1.0)


class _NameLabel(object):
    def __init__(self):
        self._widget = None

    def create(self):
        try:
            label = GUI.Text(u'')
            label.multiline = False
            label.horizontalAnchor = 'LEFT'
            label.verticalAnchor   = 'TOP'
            label.font = 'default_small.font'
            label.colour = (255, 255, 255, 255)
            label.shadow = True
            label.shadowColour = (0, 0, 0, 200)
            label.visible = False
            GUI.addRoot(label)
            self._widget = label
        except Exception as e:
            logger.error('[NameLabel] create error: %s', e)
        return self

    def show(self, text, color_rgba, clip_pos):
        if not self._widget:
            return
        try:
            self._widget.text = text
            self._widget.colour = color_rgba
            self._widget.position = clip_pos
            self._widget.visible = True
        except Exception as e:
            logger.debug('[NameLabel] show error: %s', e)

    def hide(self):
        if self._widget:
            try:
                self._widget.visible = False
            except Exception:
                pass

    def destroy(self):
        if self._widget:
            try:
                GUI.delRoot(self._widget)
            except Exception:
                pass
            self._widget = None


class PanelNameOverlay(object):
    MAX_LABELS = 30

    def __init__(self):
        self._labels     = []
        self._data       = {}   # vehicleID -> (name, wn8_color)
        self._active     = False
        self._refresh_cb = None

    def init(self):
        self._createLabels()
        g_guiResetters.add(self._onRecreateDevice)
        self._active = True
        self._scheduleRefresh(0.5)
        logger.debug('[PanelNameOverlay] init')

    def fini(self):
        self._active = False
        g_guiResetters.discard(self._onRecreateDevice)
        self._cancelRefresh()
        self._destroyLabels()
        self._data.clear()
        logger.debug('[PanelNameOverlay] fini')

    def setVehicle(self, vehicleID, name, wn8_color):
        if not g_configParams.colorizeVehicleIcon.value:
            return
        if wn8_color and name:
            self._data[vehicleID] = (name, wn8_color)
        else:
            self._data.pop(vehicleID, None)

    def refresh(self):
        if self._active:
            self._doRefresh()

    def _scheduleRefresh(self, delay=0.5):
        if not self._active:
            return
        self._refresh_cb = BigWorld.callback(delay, self._periodicRefresh)

    def _periodicRefresh(self):
        self._refresh_cb = None
        if not self._active:
            return
        self._doRefresh()
        self._scheduleRefresh(0.5)

    def _cancelRefresh(self):
        if self._refresh_cb is not None:
            try:
                BigWorld.cancelCallback(self._refresh_cb)
            except Exception:
                pass
            self._refresh_cb = None

    def _onRecreateDevice(self):
        if self._active:
            BigWorld.callback(0, self._doRefresh)

    def _doRefresh(self):
        if not self._active or not self._data:
            self._hideAll()
            return
        if not g_configParams.colorizeVehicleIcon.value:
            self._hideAll()
            return

        try:
            from .player_panel import g_events
        except Exception:
            self._hideAll()
            return

        if not g_events:
            self._hideAll()
            return

        vehicle_ids = list(self._data.keys())
        positions   = g_events.getVehicleTFPositions(vehicle_ids)

        logger.debug('[PanelNameOverlay] positions for %d vehicles: %s',
                     len(vehicle_ids), positions)

        # Build pos_map
        pos_map = {}
        for p in (positions or []):
            try:
                vid = int(p.get('vehicleID', -1))
                if vid > 0:
                    pos_map[vid] = p
            except Exception:
                pass

        self._hideAll()

        label_idx = 0
        for vehicleID, (name, wn8_color) in self._data.items():
            if label_idx >= len(self._labels):
                break
            pos = pos_map.get(vehicleID)
            if not pos:
                continue
            sx = pos.get('x', 0)
            sy = pos.get('y', 0)
            if not pos.get('visible', True):
                continue
            clip = _stage_to_clip(sx, sy)
            color = _hex_to_rgba(wn8_color)
            self._labels[label_idx].show(name, color, clip)
            label_idx += 1

    def _hideAll(self):
        for lbl in self._labels:
            lbl.hide()

    def _createLabels(self):
        self._destroyLabels()
        for _ in range(self.MAX_LABELS):
            self._labels.append(_NameLabel().create())

    def _destroyLabels(self):
        for lbl in self._labels:
            lbl.destroy()
        self._labels = []


g_overlay = PanelNameOverlay()
