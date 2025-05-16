# -*- coding: utf-8 -*-
"""
Määrittelee kustomoidut PyQt5-widgetit, kuten StepWidget ja OarPtvOverlapDialog,
joita käytetään Eclipse Contouring Helper -sovelluksen käyttöliittymässä.
"""
from PyQt5.QtWidgets import (
    QFrame, QHBoxLayout, QCheckBox, QVBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# Paikalliset importit (oletetaan, että tiedostot ovat samassa hakemistossa)
from config import (
    COLOR_COMPLETED_BG, COLOR_COMPLETED_FG, COLOR_DEFAULT_BG, COLOR_ALT_BG,
    COLOR_BORDER, COLOR_TITLE, COLOR_INSTRUCTION, COLOR_SEARCH_HIGHLIGHT_BG,
    COLOR_SEARCH_HIGHLIGHT_BORDER
)
from text_utils import bold, code
from calculations import format_dose

class StepWidget(QFrame):
    completionChanged = pyqtSignal(bool)

    def __init__(self, step_id, title, details_html, emoji="•", is_alt_row=False, parent=None):
        super().__init__(parent)
        self.step_id = step_id
        self.original_title = title
        self.is_complete = False
        self.details_html = details_html
        self.is_alt_row = is_alt_row
        self.emoji = emoji
        self._is_highlighted = False # For search

        self.setObjectName("StepWidgetFrame")
        self.setFrameShape(QFrame.StyledPanel)

        main_layout = QHBoxLayout(self); main_layout.setContentsMargins(8, 6, 10, 6); main_layout.setSpacing(8)

        self.checkbox = QCheckBox(); self.checkbox.setToolTip("Merkitse vaihe tehdyksi")
        self.checkbox.setStyleSheet("QCheckBox { margin-top: 3px; }")
        self.checkbox.stateChanged.connect(self._on_checkbox_changed)
        main_layout.addWidget(self.checkbox, 0, Qt.AlignTop)

        content_layout = QVBoxLayout(); content_layout.setContentsMargins(0, 0, 0, 0); content_layout.setSpacing(3)

        self.title_label = QLabel()
        title_font = QFont("Segoe UI", 11, QFont.Bold); self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        content_layout.addWidget(self.title_label)

        self.details_label = QLabel(details_html)
        self.details_label.setFont(QFont("Segoe UI", 9)); self.details_label.setWordWrap(True)
        self.details_label.setTextFormat(Qt.RichText); self.details_label.setOpenExternalLinks(True)
        self.details_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse) # Allow text selection
        content_layout.addWidget(self.details_label)

        main_layout.addLayout(content_layout, 1)
        self._update_style() # Initial style set

    def _on_checkbox_changed(self, state):
        self.is_complete = (state == Qt.Checked)
        self._update_style() # Update style based on completion
        self.details_label.setVisible(not self.is_complete)
        self.completionChanged.emit(self.is_complete)
        if self.parentWidget() and self.parentWidget().layout():
             self.parentWidget().layout().activate()

    def _update_style(self):
        base_frame_style_list = ["border: 1px solid", "border-radius: 3px", "margin-bottom: 4px", "padding: 0px"]
        base_label_style = "background-color: transparent;"

        if self.is_complete:
            bg_color = COLOR_COMPLETED_BG; title_color = COLOR_COMPLETED_FG; instruction_color = COLOR_COMPLETED_FG
            instruction_style = f"color: {instruction_color}; text-decoration: line-through; padding-left: 2px; line-height: 130%;"
            title_style = f"color: {title_color}; text-decoration: line-through;"
            border_color = COLOR_BORDER
        else:
            bg_color = COLOR_ALT_BG if self.is_alt_row else COLOR_DEFAULT_BG
            title_color = COLOR_TITLE; instruction_color = COLOR_INSTRUCTION
            instruction_style = f"color: {instruction_color}; text-decoration: none; padding-left: 2px; line-height: 130%;"
            title_style = f"color: {title_color};"
            border_color = COLOR_BORDER

        if self._is_highlighted:
            bg_color = COLOR_SEARCH_HIGHLIGHT_BG
            border_color = COLOR_SEARCH_HIGHLIGHT_BORDER
            base_frame_style_list[0] = f"border: 2px solid"

        base_frame_style_list.append(f"background-color: {bg_color}")
        base_frame_style_list[0] += f" {border_color}"

        self.setStyleSheet(f"QFrame#StepWidgetFrame {{ {'; '.join(base_frame_style_list)}; }}")
        self.title_label.setText(f"{self.emoji} {bold(str(self.step_id) + '.')} {bold(self.original_title)}")
        self.title_label.setStyleSheet(base_label_style + title_style)
        self.details_label.setStyleSheet(base_label_style + instruction_style)

    def set_highlighted(self, highlighted):
        if self._is_highlighted != highlighted:
            self._is_highlighted = highlighted
            self._update_style()

    def contains_text(self, text):
        if not text: return False
        search_text = text.lower()
        return search_text in self.original_title.lower() or \
               search_text in self.details_label.text().lower()


class OarPtvOverlapDialog(QDialog):
    def __init__(self, oar_name, all_ptv_doses, initially_selected_doses, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"PTV Overlapit: {oar_name}")
        self.setMinimumWidth(300)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Valitse PTV-annostasot, joihin {code(oar_name)}<br>muodostaa {code(f'dPTV+{oar_name}')}-rakenteen:"))
        self.ptv_list_widget = QListWidget()
        for dose_val in sorted(list(all_ptv_doses), reverse=True):
            item = QListWidgetItem(f"{format_dose(dose_val)} Gy PTV")
            item.setData(Qt.UserRole, dose_val)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if dose_val in initially_selected_doses else Qt.Unchecked)
            self.ptv_list_widget.addItem(item)
        layout.addWidget(self.ptv_list_widget)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept); button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_ptv_doses(self):
        return [self.ptv_list_widget.item(i).data(Qt.UserRole) for i in range(self.ptv_list_widget.count()) if self.ptv_list_widget.item(i).checkState() == Qt.Checked]