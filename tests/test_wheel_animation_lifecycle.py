"""Regression checks for short-lived wheel animations.

Hover targets change very quickly when a pointer moves over neighboring petals.
Only the newest animation may update the wheel, or hover/capsule effects
jitter and accumulate QObjects over a long tray session.
"""

from PySide6.QtCore import QAbstractAnimation

from tangerine.wheel import FanItem, TangerineWheel


def _wheel():
    wheel = TangerineWheel()
    wheel.set_items([FanItem("png", "PNG"), FanItem("webp", "WEBP")])
    return wheel


def test_hover_replaces_active_animations(qapp):
    wheel = _wheel()
    try:
        wheel._set_hover_index(0)
        old_hover = wheel._hover_anim
        old_capsule = wheel._capsule_anim
        assert old_hover.state() == QAbstractAnimation.State.Running
        assert old_capsule.state() == QAbstractAnimation.State.Running

        wheel._set_hover_index(1)
        assert old_hover.state() == QAbstractAnimation.State.Stopped
        assert old_capsule.state() == QAbstractAnimation.State.Stopped
        assert wheel._hover_anim is not old_hover
        assert wheel._capsule_anim is not old_capsule
        assert wheel._hover == 1

        wheel._stop_animations()
        assert wheel._hover_anim is None
        assert wheel._capsule_anim is None
    finally:
        wheel.reset()
        wheel.close()
        wheel.deleteLater()


def test_depart_replacement_does_not_invoke_stale_callback(qapp):
    wheel = _wheel()
    try:
        callbacks = []
        wheel._animate_depart(lambda: callbacks.append("stale"))
        first = wheel._depart_anim
        wheel._animate_depart(lambda: callbacks.append("current"))
        assert first.state() == QAbstractAnimation.State.Stopped
        assert wheel._depart_anim is not first
        assert callbacks == []

        wheel._stop_animations()
        assert wheel._depart_anim is None
        assert callbacks == []
    finally:
        wheel.reset()
        wheel.close()
        wheel.deleteLater()
