"""Precision-scroll regression tests for the radial picker."""

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QWheelEvent

from tangerine.wheel import FanItem, TangerineWheel


def _scroll(*, angle=0, pixel=0):
    return QWheelEvent(
        QPointF(0.0, 0.0),
        QPointF(0.0, 0.0),
        QPoint(0, pixel),
        QPoint(0, angle),
        Qt.MouseButton.NoButton,
        Qt.KeyboardModifier.NoModifier,
        Qt.ScrollPhase.ScrollUpdate,
        False,
    )


def test_fractional_angle_deltas_count_as_one_notch(qapp):
    wheel = TangerineWheel()
    wheel.set_items([FanItem("png", "PNG"), FanItem("jpg", "JPG")])
    try:
        for _ in range(11):
            event = _scroll(angle=-10)
            wheel.wheelEvent(event)
            assert event.isAccepted()
            assert wheel._hover == -1
        wheel.wheelEvent(_scroll(angle=-10))
        assert wheel._hover == 0

        wheel.wheelEvent(_scroll(angle=-120))
        assert wheel._hover == 1
    finally:
        wheel.reset()
        wheel.close()
        wheel.deleteLater()


def test_pixel_only_trackpad_scroll_and_reset(qapp):
    wheel = TangerineWheel()
    wheel.set_items([FanItem("png", "PNG"), FanItem("jpg", "JPG")])
    try:
        wheel.wheelEvent(_scroll(pixel=-15))
        wheel.wheelEvent(_scroll(pixel=-15))
        assert wheel._hover == -1
        wheel.wheelEvent(_scroll(pixel=-10))
        assert wheel._hover == 0

        wheel.reset()
        assert wheel._scroll_pixel == 0
        assert wheel._scroll_angle == 0
    finally:
        wheel.reset()
        wheel.close()
        wheel.deleteLater()
