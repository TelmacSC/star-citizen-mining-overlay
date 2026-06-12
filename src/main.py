import sys

from PySide6.QtCore import QObject, QThread, Signal, Qt
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from pynput import keyboard

from minerals import MINERALS
from overlay import OverlayWindow
from preferences import load_preferences, save_preferences


def format_mineral_line(name: str, values: list[int], name_width: int) -> str:
    return f"{name:<{name_width}} " + " | ".join(str(value) for value in values)


class HotkeyWorker(QObject):
    toggled = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._listener: keyboard.Listener | None = None

    def run(self) -> None:
        def on_press(key) -> None:
            if key == keyboard.Key.f10:
                self.toggled.emit()

        self._listener = keyboard.Listener(on_press=on_press)
        self._listener.start()
        self._listener.join()

    def stop(self) -> None:
        if self._listener:
            self._listener.stop()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Star Citizen - Minage")
        self.resize(520, 680)

        self.overlay = OverlayWindow()
        self.checkboxes: dict[str, QCheckBox] = {}
        self.preferences = load_preferences(default_minerals=["Gold", "Bexalite", "Laranite"])

        self._build_ui()
        self._apply_preferences()
        self._connect_hotkey()
        self._sync_overlay()

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setSpacing(12)

        title = QLabel("Minerais a afficher")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        root_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        list_container = QWidget()
        grid = QGridLayout(list_container)
        grid.setVerticalSpacing(6)
        grid.setHorizontalSpacing(20)

        for index, mineral_name in enumerate(MINERALS):
            checkbox = QCheckBox(mineral_name)
            checkbox.stateChanged.connect(self._on_selection_changed)
            self.checkboxes[mineral_name] = checkbox
            grid.addWidget(checkbox, index // 2, index % 2)

        scroll.setWidget(list_container)
        root_layout.addWidget(scroll, stretch=1)

        overlay_group = QGroupBox("Overlay")
        overlay_layout = QVBoxLayout(overlay_group)

        self.click_through_checkbox = QCheckBox("Clic traversant")
        self.click_through_checkbox.stateChanged.connect(self._on_click_through_changed)
        overlay_layout.addWidget(self.click_through_checkbox)

        hint = QLabel("F10 affiche ou masque l'overlay.")
        hint.setStyleSheet("color: #555;")
        overlay_layout.addWidget(hint)
        root_layout.addWidget(overlay_group)

        actions = QHBoxLayout()
        self.show_button = QPushButton("Afficher l'overlay")
        self.hide_button = QPushButton("Masquer l'overlay")
        self.show_button.clicked.connect(self.show_overlay)
        self.hide_button.clicked.connect(self.hide_overlay)
        actions.addWidget(self.show_button)
        actions.addWidget(self.hide_button)
        root_layout.addLayout(actions)

        self.setCentralWidget(root)

    def _apply_preferences(self) -> None:
        selected = set(self.preferences["selected_minerals"])
        for mineral_name, checkbox in self.checkboxes.items():
            checkbox.setChecked(mineral_name in selected)

        self.click_through_checkbox.setChecked(self.preferences["click_through"])
        self.overlay.set_click_through(self.preferences["click_through"])

        position = self.preferences["overlay_position"]
        if isinstance(position, list) and len(position) == 2:
            self.overlay.move(int(position[0]), int(position[1]))
        else:
            self.overlay.move(80, 80)

        self.overlay.moved.connect(lambda position: self._save_preferences())

        if self.preferences["overlay_visible"]:
            self.show_overlay()

    def _connect_hotkey(self) -> None:
        self.hotkey_thread = QThread(self)
        self.hotkey_worker = HotkeyWorker()
        self.hotkey_worker.moveToThread(self.hotkey_thread)
        self.hotkey_thread.started.connect(self.hotkey_worker.run)
        self.hotkey_worker.toggled.connect(self.toggle_overlay)
        self.hotkey_thread.start()

    def selected_minerals(self) -> list[str]:
        return [
            mineral_name
            for mineral_name, checkbox in self.checkboxes.items()
            if checkbox.isChecked()
        ]

    def overlay_lines(self) -> list[str]:
        selected = self.selected_minerals()
        if not selected:
            return []

        name_width = max(len(name) for name in selected)
        return [
            format_mineral_line(name, MINERALS[name], name_width)
            for name in selected
        ]

    def _sync_overlay(self) -> None:
        self.overlay.set_lines(self.overlay_lines())
        self._save_preferences()

    def _save_preferences(self) -> None:
        save_preferences(
            selected_minerals=self.selected_minerals(),
            overlay_visible=self.overlay.isVisible(),
            click_through=self.click_through_checkbox.isChecked(),
            overlay_position=(self.overlay.x(), self.overlay.y()),
        )

    def _on_selection_changed(self) -> None:
        self._sync_overlay()

    def _on_click_through_changed(self) -> None:
        self.overlay.set_click_through(self.click_through_checkbox.isChecked())
        self._save_preferences()

    def show_overlay(self) -> None:
        self._sync_overlay()
        self.overlay.show()
        self.overlay.raise_()
        self._save_preferences()

    def hide_overlay(self) -> None:
        self.overlay.hide()
        self._save_preferences()

    def toggle_overlay(self) -> None:
        if self.overlay.isVisible():
            self.hide_overlay()
        else:
            self.show_overlay()

    def closeEvent(self, event: QCloseEvent) -> None:
        self._save_preferences()
        self.hotkey_worker.stop()
        self.hotkey_thread.quit()
        self.hotkey_thread.wait(1500)
        self.overlay.close()
        event.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("StarCitizenMiningOverlay")
    app.setOrganizationName("StarCitizenMiningOverlay")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
