"""Native Windows file actions for the third radial wheel.

No conversion is performed: the user explicitly chooses how to handle selected
files and folders. Clipboard actions never mutate sources; Move requests a
destination before changing anything. Sharing/AirDrop is not emulated here:
Windows does not expose macOS AirDrop.
"""

from __future__ import annotations

import base64
import logging
import shutil
import subprocess
from pathlib import Path

from PySide6.QtCore import QMimeData, Qt, QUrl
from PySide6.QtGui import QDrag, QGuiApplication
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from . import theme

log = logging.getLogger("tangerine")

FILE_ACTIONS = (
    ("file.copy", "Copy"),
    ("file.move", "Move"),
    ("file.path", "Copy Path"),
    ("file.terminal", "Terminal"),
    ("file.float", "Float"),
)

_SHELVES: set[QWidget] = set()


def _existing(paths) -> list[Path]:
    """Remove duplicates, nonexistent paths and empty strings safely."""
    result: list[Path] = []
    seen: set[str] = set()
    for item in paths:
        if not str(item):
            continue
        path = Path(item)
        key = str(path.absolute()).casefold()
        if key not in seen and path.exists():
            seen.add(key)
            result.append(path)
    return result


def _mime(paths: list[Path]) -> QMimeData:
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(path.absolute())) for path in paths])
    return mime


def copy_files(paths) -> None:
    """Place real file URLs on the Windows clipboard for Explorer paste."""
    chosen = _existing(paths)
    if chosen:
        QGuiApplication.clipboard().setMimeData(_mime(chosen))


def copy_paths(paths) -> None:
    chosen = _existing(paths)
    if chosen:
        QGuiApplication.clipboard().setText(
            "\r\n".join(str(path.absolute()) for path in chosen)
        )


def _safe_destination(source: Path, folder: Path) -> Path:
    """Choose a non-colliding destination; never replace or nest folders."""
    src = source.resolve()
    target_dir = folder.resolve()
    if source.is_dir() and target_dir.is_relative_to(src):
        raise ValueError("Cannot move a folder inside itself.")
    candidate = target_dir / source.name
    if candidate.resolve() == src:
        raise ValueError("Source and destination are the same.")
    if not candidate.exists():
        return candidate
    index = 2
    while True:
        alternative = target_dir / f"{source.stem} ({index}){source.suffix}"
        if not alternative.exists():
            return alternative
        index += 1


def move_files(paths, parent=None) -> list[Path]:
    chosen = _existing(paths)
    if not chosen:
        return []
    dest = QFileDialog.getExistingDirectory(
        parent, "Move files to folder", str(Path.home()),
        QFileDialog.Option.ShowDirsOnly,
    )
    if not dest:
        return []
    folder = Path(dest)
    results = []
    errors = []
    for source in chosen:
        try:
            target = _safe_destination(source, folder)
            shutil.move(str(source), str(target))
            results.append(target)
        except (OSError, ValueError) as exc:
            errors.append(f"{source.name}: {exc}")
    if errors:
        QMessageBox.warning(
            parent, "Some files could not be moved", "\n".join(errors[:12])
        )
    return results


def open_terminal(paths) -> None:
    chosen = _existing(paths)
    if not chosen:
        return
    first = chosen[0]
    directory = first if first.is_dir() else first.parent
    # EncodedCommand preserves Unicode, apostrophes and shell metacharacters.
    quoted = str(directory.resolve()).replace("'", "''")
    script = f"Set-Location -LiteralPath '{quoted}'"
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    subprocess.Popen(
        ["powershell.exe", "-NoExit", "-EncodedCommand", encoded],
        close_fds=True,
    )


class _FilesList(QListWidget):
    """Expose file URL MIME data when dragging from the floating shelf."""

    def mimeData(self, items) -> QMimeData:
        paths = [Path(item.data(Qt.ItemDataRole.UserRole)) for item in items]
        return _mime(paths)


class FloatingShelf(QWidget):
    """Compact, always-on-top source shelf for dragging files into other apps."""

    def __init__(self, paths, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.setWindowTitle("Tangerine — Floating files")
        self.setMinimumSize(280, 170)
        self.resize(335, 270)
        self.setAcceptDrops(True)

        dark = theme.is_dark()
        palette = theme.palette(dark)
        self.setStyleSheet(
            "QWidget { background: " + palette["window"] + "; color: "
            + palette["text"] + "; } "
            "QListWidget { background: " + palette["card"] + "; "
            "border: 1px solid " + palette["border"] + "; border-radius: 10px; }"
        )
        layout = QVBoxLayout(self)
        top = QHBoxLayout()
        self.summary = QLabel()
        top.addWidget(self.summary, 1)
        close = QPushButton("×")
        close.setToolTip("Close shelf")
        close.setFixedSize(32, 30)
        close.clicked.connect(self.close)
        top.addWidget(close)
        layout.addLayout(top)

        self.files = _FilesList()
        self.files.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.files.setDragEnabled(True)
        self.files.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.files.setDefaultDropAction(Qt.DropAction.CopyAction)
        layout.addWidget(self.files)
        self._add(paths)

    def _add(self, paths) -> None:
        existing = {
            str(self.files.item(i).data(Qt.ItemDataRole.UserRole)).casefold()
            for i in range(self.files.count())
        }
        for path in _existing(paths):
            absolute = str(path.absolute())
            if absolute.casefold() in existing:
                continue
            existing.add(absolute.casefold())
            item = QListWidgetItem(path.name)
            item.setToolTip(absolute)
            item.setData(Qt.ItemDataRole.UserRole, absolute)
            self.files.addItem(item)
        self.summary.setText(f"Floating files · {self.files.count()}")

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            self._add(
                [url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()]
            )
            event.acceptProposedAction()


def float_files(paths) -> FloatingShelf | None:
    if not _existing(paths):
        return None
    shelf = FloatingShelf(paths)
    _SHELVES.add(shelf)
    shelf.destroyed.connect(lambda *_args, w=shelf: _SHELVES.discard(w))
    shelf.show()
    return shelf


def run_file_action(paths, key: str, parent=None):
    """Dispatch an explicitly selected action, including folders."""
    chosen = _existing(paths)
    if not chosen:
        return None
    try:
        if key == "file.copy":
            return copy_files(chosen)
        if key == "file.move":
            return move_files(chosen, parent)
        if key == "file.path":
            return copy_paths(chosen)
        if key == "file.terminal":
            return open_terminal(chosen)
        if key == "file.float":
            return float_files(chosen)
        raise ValueError(f"Unknown file action: {key}")
    except (OSError, ValueError) as exc:
        log.exception("File action failed")
        QMessageBox.warning(parent, "File action failed", str(exc))
        return None
