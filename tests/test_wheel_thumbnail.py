"""Cached wheel-hub image preview tests (offscreen Qt)."""

from PySide6.QtGui import QColor, QImage

from tangerine.wheel import FanItem, TangerineWheel


def test_image_preview_is_scaled_and_cleared(qapp, tmp_path):
    photo = tmp_path / "preview.png"
    pixels = QImage(1200, 800, QImage.Format.Format_RGB32)
    pixels.fill(QColor(20, 160, 80))
    assert pixels.save(str(photo))

    wheel = TangerineWheel()
    try:
        wheel.set_items([FanItem("webp", "WEBP")])
        wheel.set_files([str(photo)])
        assert wheel._thumbnail_image is not None
        assert max(wheel._thumbnail_image.width(), wheel._thumbnail_image.height()) <= 192
        cached = wheel._thumbnail_image
        wheel.set_files([str(photo)])
        assert wheel._thumbnail_image is cached
        wheel.set_files([str(tmp_path / "unrelated.pdf")])
        assert wheel._thumbnail_image is None
        wheel.set_files([str(photo)])
        assert wheel._thumbnail_image is not None
        wheel.reset()
        assert wheel._thumbnail_image is None
    finally:
        wheel.close()
        wheel.deleteLater()


def test_unknown_image_does_not_crash_or_decode(qapp, tmp_path):
    photo = tmp_path / "empty.jpg"
    photo.write_bytes(b"not-an-image")
    wheel = TangerineWheel()
    try:
        wheel.set_files([str(photo)])
        assert wheel._thumbnail_image is None
    finally:
        wheel.reset()
        wheel.close()
        wheel.deleteLater()
