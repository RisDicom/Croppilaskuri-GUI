"""Panel for entering and managing OAR (organ at risk) structures."""

from __future__ import annotations

from functools import partial
from typing import Any

from PyQt5.QtCore import QStringListModel, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCompleter,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from croppilaskuri.config.oar_data import COMMON_OARS
from croppilaskuri.core.calculations import format_dose
from croppilaskuri.ui.widgets.oar_dialog import OarPtvOverlapDialog
from croppilaskuri.utils.text import bold

OarEntry = dict[str, Any]


class OarInputPanel(QFrame):
    """Input panel for OAR structures with autocomplete and overlap config.

    Signals:
        oarsChanged: Emitted whenever the OAR list or configuration changes.
    """

    oarsChanged = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("OARGroup")
        self.setFrameShape(QFrame.StyledPanel)

        self._oars: list[OarEntry] = []
        self._available_doses: list[float] = []
        self._overlaps_enabled: bool = True

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        layout.addWidget(QLabel(bold("2. Syötä tervekudokset (OAR):")))

        entry_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("Esim. Rectum, Heart...")

        add_btn = QPushButton("Lisää OAR")
        add_btn.clicked.connect(self.add_oar)

        entry_row.addWidget(self._input, 1)
        entry_row.addWidget(add_btn)
        layout.addLayout(entry_row)

        # Overlap disabled banner (hidden by default)
        self._overlap_banner = QLabel(
            "<i style='color:#888;'>OAR-päällekkäisyydet eivät ole "
            "käytössä palliatiivisessa suunnitelmassa.</i>"
        )
        self._overlap_banner.setWordWrap(True)
        self._overlap_banner.setVisible(False)
        layout.addWidget(self._overlap_banner)

        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(["OAR Nimi", "dPTV+OAR Overlapit", "Toiminto"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.setMinimumHeight(130)
        layout.addWidget(self._table)

        self._setup_completer()

    # ── Public API ──────────────────────────────────────────────────

    @property
    def oars_data(self) -> list[OarEntry]:
        """Return a copy of the current OAR data list."""
        import copy

        return copy.deepcopy(self._oars)

    def remove_dose_from_overlaps(self, dose: float) -> None:
        """Remove a dose from every OAR's overlap list (after dose deletion)."""
        for entry in self._oars:
            overlaps: list[float] = entry.get("overlap_with_ptv_doses", [])
            if dose in overlaps:
                overlaps.remove(dose)
        self._refresh_table()

    def refresh_table(self) -> None:
        """Public trigger to re-render the table (e.g. after dose changes)."""
        self._refresh_table()

    def set_available_doses(self, doses: list[float]) -> None:
        """Store the current dose list for use in the overlap dialog."""
        self._available_doses = sorted(doses, reverse=True)

    def set_overlaps_enabled(self, enabled: bool) -> None:
        """Enable or disable overlap configuration (e.g. for palliative plans).

        When disabled, the "Määritä..." buttons are grayed out and a banner
        explains why.  The OAR list itself remains editable.
        """
        self._overlaps_enabled = enabled
        self._overlap_banner.setVisible(not enabled)
        self._refresh_table()

    # ── Slots ───────────────────────────────────────────────────────

    def add_oar(self) -> None:
        """Add an OAR from the input field."""
        name = self._input.text().strip()
        if not name:
            return
        if any(o["name"] == name for o in self._oars):
            QMessageBox.warning(self, "OAR jo lisätty", f"OAR '{name}' on jo listalla.")
            self._input.clear()
            return

        self._oars.append({"name": name, "overlap_with_ptv_doses": []})
        self._oars.sort(key=lambda o: o["name"])
        self._refresh_table()
        self._input.clear()
        self.oarsChanged.emit()

    # ── Internals ───────────────────────────────────────────────────

    def _setup_completer(self) -> None:
        model = QStringListModel(COMMON_OARS, self)
        completer = QCompleter(model, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        self._input.setCompleter(completer)
        completer.activated.connect(self._on_completer_activated)

    def _on_completer_activated(self, text: str) -> None:
        self._input.setText(text)
        self.add_oar()

    def _remove_oar(self, row: int) -> None:
        if 0 <= row < len(self._oars):
            del self._oars[row]
            self._refresh_table()
            self.oarsChanged.emit()

    def _configure_overlaps(self, row: int) -> None:
        if not (0 <= row < len(self._oars)):
            return
        entry = self._oars[row]
        doses = self._available_doses
        if not doses:
            QMessageBox.information(
                self,
                "Ei PTV-annoksia",
                "Syötä PTV-annoksia ensin, jotta voit määrittää päällekkäisyyksiä.",
            )
            return

        dialog = OarPtvOverlapDialog(
            entry["name"],
            doses,
            entry.get("overlap_with_ptv_doses", []),
            self,
        )
        if dialog.exec_() == OarPtvOverlapDialog.Accepted:
            entry["overlap_with_ptv_doses"] = dialog.get_selected_ptv_doses()
            self._refresh_table()
            self.oarsChanged.emit()

    def _refresh_table(self) -> None:
        self._table.setSortingEnabled(False)
        self._table.setRowCount(0)
        self._table.setRowCount(len(self._oars))

        for i, entry in enumerate(self._oars):
            # Name column
            name_item = QTableWidgetItem(entry["name"])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self._table.setItem(i, 0, name_item)

            # Overlap column
            overlap_widget = QWidget()
            overlap_layout = QHBoxLayout(overlap_widget)
            overlap_layout.setContentsMargins(2, 0, 2, 0)
            overlap_layout.setSpacing(4)

            btn_cfg = QPushButton("Määritä...")
            btn_cfg.setObjectName("ConfigureOARButton")
            btn_cfg.setToolTip(f"Määritä PTV-päällekkäisyydet OAR:lle {entry['name']}")
            btn_cfg.clicked.connect(partial(self._configure_overlaps, row=i))

            # Disable overlap button when overlaps are disabled (palliative)
            btn_cfg.setEnabled(self._overlaps_enabled)
            overlap_layout.addWidget(btn_cfg)

            selected: list[float] = entry.get("overlap_with_ptv_doses", [])
            if not self._overlaps_enabled:
                doses_text = "Ei käytössä"
                label_color = "#aaa"
            elif selected:
                doses_text = ", ".join(format_dose(d) for d in sorted(selected, reverse=True))
                if len(doses_text) > 25:
                    doses_text = f"{len(selected)} PTV:tä valittu"
                label_color = "#555"
            else:
                doses_text = "Ei valittu"
                label_color = "#555"

            lbl = QLabel(doses_text)
            lbl.setStyleSheet(f"font-size:8pt; color:{label_color}; margin-left:3px;")
            overlap_layout.addWidget(lbl)
            overlap_layout.addStretch()
            self._table.setCellWidget(i, 1, overlap_widget)

            # Delete column
            btn_del = QPushButton("Poista")
            btn_del.setObjectName("DeleteOARButton")
            btn_del.clicked.connect(partial(self._remove_oar, row=i))

            del_widget = QWidget()
            del_layout = QHBoxLayout(del_widget)
            del_layout.addWidget(btn_del)
            del_layout.setAlignment(Qt.AlignCenter)
            del_layout.setContentsMargins(0, 0, 0, 0)
            self._table.setCellWidget(i, 2, del_widget)

        self._table.resizeRowsToContents()
        self._table.resizeColumnsToContents()
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.setSortingEnabled(True)
