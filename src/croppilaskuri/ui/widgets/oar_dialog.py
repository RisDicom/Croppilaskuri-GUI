"""Dialog for configuring which PTV dose levels overlap with an OAR."""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from croppilaskuri.core.calculations import format_dose


class OarPtvOverlapDialog(QDialog):
    """Let the user tick which PTV dose levels create dPTV+OAR structures.

    Args:
        oar_name: Display name of the OAR.
        available_ptv_doses: All currently entered PTV dose levels.
        initially_selected: Dose levels already selected for this OAR.
        parent: Parent widget.
    """

    def __init__(
        self,
        oar_name: str,
        available_ptv_doses: list[float],
        initially_selected: list[float],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"dPTV+OAR asetukset: {oar_name}")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)
        layout.addWidget(
            QLabel(
                f"Valitse PTV-annostasot joille luodaan\n"
                f"<b>dPTV+{oar_name}</b> -päällekkäisyysrakenne:"
            )
        )

        self._checkboxes: list[tuple[float, QCheckBox]] = []
        for dose in sorted(available_ptv_doses, reverse=True):
            cb = QCheckBox(f"PTV {format_dose(dose)} Gy")
            cb.setChecked(dose in initially_selected)
            layout.addWidget(cb)
            self._checkboxes.append((dose, cb))

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_ptv_doses(self) -> list[float]:
        """Return the list of dose values the user has checked."""
        return [dose for dose, cb in self._checkboxes if cb.isChecked()]
