from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class OverlayWindow(QWidget):
    moved = Signal(tuple)

    def __init__(self) -> None:
        super().__init__()
        self._drag_offset: QPoint | None = None
        self._click_through = False

        self.setWindowTitle("Star Citizen Mining Overlay")
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.WindowDoesNotAcceptFocus
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.label = QLabel("Aucun minerai selectionne")
        self.label.setFont(QFont("Consolas", 11))
        self.label.setStyleSheet("color: white;")
        self.label.setTextInteractionFlags(Qt.NoTextInteraction)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(self.label)

        self.setStyleSheet(
            """
            QWidget {
                background-color: rgba(0, 0, 0, 170);
                border: 1px solid rgba(255, 255, 255, 70);
            }
            QLabel {
                background: transparent;
                border: none;
            }
            """
        )

    def set_lines(self, lines: list[str]) -> None:
        self.label.setText("\n".join(lines) if lines else "Aucun minerai selectionne")
        self.adjustSize()

    def set_click_through(self, enabled: bool) -> None:
        self._click_through = enabled
        self.setAttribute(Qt.WA_TransparentForMouseEvents, enabled)

        flags = self.windowFlags()
        if enabled:
            flags |= Qt.WindowTransparentForInput
        else:
            flags &= ~Qt.WindowTransparentForInput
        self.setWindowFlags(flags)
        if self.isVisible():
            self.show()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and not self._click_through:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is not None and not self._click_through:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._drag_offset is not None:
            self._drag_offset = None
            self.moved.emit((self.x(), self.y()))
            event.accept()
