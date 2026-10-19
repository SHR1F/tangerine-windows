"""Native file-action behavior and non-destructive file management."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QFileDialog

from tangerine import file_actions
from tangerine.main import Controller
from tangerine.icons import has_icon


def test_actions_mode_offers_native_tools_without_conversions(qapp, tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    fake = SimpleNamespace(_labels={})
    items = Controller._items_for(fake, [str(folder)], "actions")
    assert [item.key for item in items] == [key for key, _ in file_actions.FILE_ACTIONS]
    assert all(item.kind == "tool" for item in items)
    assert all(has_icon(item.key) for item in items)


def test_copy_path_and_file_urls(qapp, tmp_path):
    first = tmp_path / "hello world.txt"
    first.write_text("test", encoding="utf-8")
    file_actions.copy_paths([first, first])
    assert QGuiApplication.clipboard().text() == str(first.absolute())

    file_actions.copy_files([first])
    data = QGuiApplication.clipboard().mimeData()
    assert data.hasUrls()
    assert [u.toLocalFile() for u in data.urls()] == [str(first.absolute())]


def test_move_never_overwrites_existing_destination(qapp, tmp_path, monkeypatch):
    source_dir = tmp_path / "source"
    target = tmp_path / "target"
    source_dir.mkdir()
    target.mkdir()
    src = source_dir / "photo.jpg"
    src.write_bytes(b"new")
    (target / "photo.jpg").write_bytes(b"existing")
    monkeypatch.setattr(
        QFileDialog, "getExistingDirectory", lambda *args, **kwargs: str(target)
    )
    moved = file_actions.move_files([src])
    assert len(moved) == 1
    assert moved[0].name == "photo (2).jpg"
    assert moved[0].read_bytes() == b"new"
    assert (target / "photo.jpg").read_bytes() == b"existing"
    assert not src.exists()


def test_folder_cannot_be_moved_into_its_child(tmp_path):
    folder = tmp_path / "folder"
    child = folder / "child"
    child.mkdir(parents=True)
    with pytest.raises(ValueError, match="inside itself"):
        file_actions._safe_destination(folder, child)


def test_float_shelf_exposes_real_file_urls(qapp, tmp_path):
    photo = tmp_path / "photo.jpg"
    photo.write_bytes(b"test")
    shelf = file_actions.FloatingShelf([photo, photo])
    try:
        assert shelf.files.count() == 1
        mime = shelf.files.mimeData([shelf.files.item(0)])
        assert mime.hasUrls()
        assert mime.urls()[0].toLocalFile() == str(photo.absolute())
    finally:
        shelf.close()
        shelf.deleteLater()
