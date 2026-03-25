"""StepWidget – a collapsible, checkable step card for the guide tab."""

from __future__ import annotations

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from croppilaskuri.config.constants import (
    COLOR_ALT_BG,
    COLOR_BORDER,
    COLOR_COMPLETED_BG,
    COLOR_COMPLETED_FG,
    COLOR_DEFAULT_BG,
    COLOR_SEARCH_HIGHLIGHT_BG,
    COLOR_SEARCH_HIGHLIGHT_BORDER,
)


class StepWidget(QFrame):
    """A single step in the guide, shown as a collapsible card.

    Signals:
        completionChanged: Emitted when the user checks/unchecks the step.
    """

    completionChanged = pyqtSignal(bool)

    def __init__(
        self,
        step_id: int | None,
        title: str,
        details_html: str,
        emoji: str = "",
        *,
        is_alt_row: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.step_id = step_id
        self.is_complete = False
        self.toc_anchor_target_id: str | None = None
        self._is_alt_row = is_alt_row
        self._base_bg = COLOR_ALT_BG if is_alt_row else COLOR_DEFAULT_BG

        self.setFrameShape(QFrame.StyledPanel)
        self._apply_normal_style()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Header row: checkbox + emoji + title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        self.checkbox = QCheckBox()
        self.checkbox.stateChanged.connect(self._on_check_changed)
        header_layout.addWidget(self.checkbox)

        if emoji:
            emoji_label = QLabel(emoji)
            emoji_label.setStyleSheet("font-size: 14pt;")
            header_layout.addWidget(emoji_label)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_label.setWordWrap(True)
        header_layout.addWidget(self.title_label, 1)

        layout.addLayout(header_layout)

        # Details area
        self.details_label = QLabel(details_html)
        self.details_label.setWordWrap(True)
        self.details_label.setTextFormat(Qt.RichText)
        self.details_label.setOpenExternalLinks(True)
        self.details_label.setFont(QFont("Segoe UI", 9))
        self.details_label.setContentsMargins(28, 0, 0, 0)
        layout.addWidget(self.details_label)

    # ── Public API ──────────────────────────────────────────────────

    def contains_text(self, search_term: str) -> bool:
        """Return ``True`` if *search_term* appears in title or details."""
        term = search_term.lower()
        return term in self.title_label.text().lower() or term in self.details_label.text().lower()

    def set_highlighted(self, on: bool) -> None:
        """Toggle visual search-highlight on this step."""
        if on:
            self.setStyleSheet(
                f"QFrame {{ background-color: {COLOR_SEARCH_HIGHLIGHT_BG}; "
                f"border: 2px solid {COLOR_SEARCH_HIGHLIGHT_BORDER}; "
                f"border-radius: 4px; }}"
            )
        else:
            self._apply_normal_style()

    # ── Internals ───────────────────────────────────────────────────

    def _on_check_changed(self, state: int) -> None:
        self.is_complete = state == Qt.Checked
        if self.is_complete:
            self.details_label.setVisible(False)
            self.setStyleSheet(
                f"QFrame {{ background-color: {COLOR_COMPLETED_BG}; "
                f"border: 1px solid {COLOR_BORDER}; border-radius: 4px; }}"
            )
            self.title_label.setStyleSheet(f"color: {COLOR_COMPLETED_FG};")
        else:
            self.details_label.setVisible(True)
            self._apply_normal_style()
            self.title_label.setStyleSheet("")
        self.completionChanged.emit(self.is_complete)

    def _apply_normal_style(self) -> None:
        self.setStyleSheet(
            f"QFrame {{ background-color: {self._base_bg}; "
            f"border: 1px solid {COLOR_BORDER}; border-radius: 4px; }}"
        )
