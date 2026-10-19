"""The modifier selects a radial wheel; releasing it must not cancel a drag.

Tangerine for Mac keeps its wheel visible until a file is dropped, while the
user moves between format/tool/action choices by pressing other modifiers.
"""

import pytest
from PySide6.QtCore import QPoint

from tangerine import monitor as monitor_module
from tangerine.monitor import BUTTON_RELEASE_SAMPLES, DragMonitor


@pytest.fixture
def drag(qapp, monkeypatch):
    state = {"left": True, "pos": QPoint(100, 100), "mode": "conversion"}
    monkeypatch.setattr(
        monitor_module, "_is_down",
        lambda vk: state["left"] if vk == monitor_module.VK_LBUTTON else False,
    )
    monkeypatch.setattr(monitor_module.context, "wheel_allowed", lambda: True)
    monkeypatch.setattr(
        DragMonitor, "_mode_for_current_modifiers",
        lambda self: state["mode"],
    )
    monkeypatch.setattr(DragMonitor, "_drag_files", lambda self: None)
    monkeypatch.setattr(DragMonitor, "_cursor", lambda self: QPoint(state["pos"]))
    monitor = DragMonitor()
    monitor.stop()
    events = []
    monitor.wheelShown.connect(lambda pos, files, mode: events.append(("shown", mode)))
    monitor.wheelMoved.connect(lambda pos: events.append(("moved",)))
    monitor.wheelHidden.connect(lambda: events.append(("hidden",)))
    monitor.wheelRefreshed.connect(lambda mode: events.append(("refreshed", mode)))
    try:
        yield monitor, state, events
    finally:
        monitor.stop()
        monitor.deleteLater()


def _start(drag):
    monitor, state, events = drag
    monitor._tick()
    state["pos"] = QPoint(100, 180)
    monitor._tick()
    assert ("shown", "conversion") in events
    assert monitor._visible is True


def test_release_modifier_during_drag_keeps_wheel_visible(drag):
    monitor, state, events = drag
    _start(drag)
    state["mode"] = None
    state["pos"] = QPoint(100, 195)
    monitor._tick()

    assert monitor._visible is True
    assert monitor._mode == "conversion"
    assert ("hidden",) not in events

    state["left"] = False
    for _ in range(BUTTON_RELEASE_SAMPLES):
        monitor._tick()
    assert monitor._visible is False
    assert events.count(("hidden",)) == 1


def test_switch_to_tools_then_release_modifier_keeps_new_mode(drag):
    monitor, state, events = drag
    _start(drag)
    state["mode"] = "tools"
    monitor._tick()
    assert ("refreshed", "tools") in events

    state["mode"] = None
    monitor._tick()
    assert monitor._visible is True
    assert monitor._mode == "tools"
    assert ("hidden",) not in events

    state["mode"] = "actions"
    monitor._tick()
    assert ("refreshed", "actions") in events
