"""Panel for entering and managing PTV dose levels."""

from __future__ import annotations

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from croppilaskuri.core.calculations import format_dose
from croppilaskuri.utils.text import bold


class DoseInputPanel(QFrame):
    """Input panel for PTV dose levels.

    Signals:
        dosesChanged: Emitted whenever the dose list changes.
    """

    dosesChanged = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("InputGroup")
        self.setFrameShape(QFrame.StyledPanel)

        self._doses: list[float] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        layout.addWidget(QLabel(bold("1. Syötä PTV-annokset (Gy):")))

        entry_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Esim. 66 tai 50,4")
        self._input.returnPressed.connect(self.add_dose)

        self._add_btn = QPushButton("Lisää")
        self._add_btn.clicked.connect(self.add_dose)

        entry_row.addWidget(self._input, 1)
        entry_row.addWidget(self._add_btn)
        layout.addLayout(entry_row)

        self._list_widget = QListWidget()
        self._list_widget.setFixedHeight(100)
        self._list_widget.itemSelectionChanged.connect(self._update_delete_btn)
        layout.addWidget(self._list_widget)

        self._del_btn = QPushButton("Poista valittu")
        self._del_btn.setObjectName("DeleteDoseButton")
        self._del_btn.setToolTip("Poistaa valitun annoksen listasta")
        self._del_btn.setEnabled(False)
        self._del_btn.clicked.connect(self.remove_selected)
        layout.addWidget(self._del_btn)

    # ── Public API ──────────────────────────────────────────────────

    @property
    def doses(self) -> list[float]:
        """Return the current dose list (sorted descending)."""
        return list(self._doses)

    def remove_dose(self, dose: float) -> None:
        """Remove a specific dose from the list."""
        if dose in self._doses:
            self._doses.remove(dose)
            self._refresh_list()
            self.dosesChanged.emit()

    # ── Slots ───────────────────────────────────────────────────────

    def add_dose(self) -> None:
        """Parse and add a dose from the input field."""
        text = self._input.text().strip().replace(",", ".")
        if not text:
            return
        try:
            dose = float(text)
        except ValueError:
            QMessageBox.warning(self, "Virheellinen syöte", f"'{text}' ei ole numero.")
            return

        if dose <= 0:
            QMessageBox.warning(self, "Virheellinen annos", "Annostason on oltava positiivinen.")
            return
        if dose in self._doses:
            QMessageBox.warning(
                self, "Annos jo lisätty", f"Annos {format_dose(dose)} Gy on jo listalla."
            )
            return

        self._doses.append(dose)
        self._doses.sort(reverse=True)
        self._refresh_list()
        self._input.clear()
        self.dosesChanged.emit()

    def remove_selected(self) -> None:
        """Remove the dose(s) currently selected in the list widget."""
        items = self._list_widget.selectedItems()
        if not items:
            return
        for item in items:
            try:
                value = float(item.text().replace(" Gy", "").replace(",", "."))
                if value in self._doses:
                    self._doses.remove(value)
            except ValueError:
                pass
        self._refresh_list()
        self._update_delete_btn()
        self.dosesChanged.emit()

    # ── Internals ───────────────────────────────────────────────────

    def _refresh_list(self) -> None:
        self._list_widget.clear()
        for d in sorted(self._doses, reverse=True):
            self._list_widget.addItem(f"{format_dose(d)} Gy")

    def _update_delete_btn(self) -> None:
        self._del_btn.setEnabled(len(self._list_widget.selectedItems()) > 0)
