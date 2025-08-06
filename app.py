# -*- coding: utf-8 -*-
"""
Pääsovellusluokka EclipseHelperApp, joka sisältää käyttöliittymän
rakentamisen ja sovelluksen päätoiminnallisuuden.
"""
import sys
import os
import datetime
from functools import partial

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QListWidget, QMessageBox,
    QCheckBox, QSpacerItem, QSizePolicy, QScrollArea, QFrame, QTabWidget,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QCompleter, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QSize, QStringListModel, QUrl # QUrl lisätty
from PyQt5.QtGui import QFont, QPixmap, QTextCursor

from config import (
    APP_VERSION, EMOJI_SEARCH, COLOR_DEFAULT_BG, COMMON_OARS, EMOJI_INFO
)
from calculations import calculate_ptv_crop, format_dose
from text_utils import bold
from gui_widgets import StepWidget, OarPtvOverlapDialog
from guide_logic import generate_guide_steps
from optimization_criteria import generate_optimization_criteria_html


class EclipseHelperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.ptv_doses_list = []
        self.oars_data = []
        self.step_widgets = [] # Lista StepWidget-instansseista
        self.total_steps = 0
        self.completed_steps = 0
        self.crop_summary_data = {}
        self.current_search_index = -1
        self.last_search_term = ""
        self.highlighted_widget = None
        self.initUI()
        self._apply_global_styles()

    def _apply_global_styles(self):
        self.setStyleSheet(f"""
            QWidget {{ font-family: 'Segoe UI', sans-serif; font-size: 10pt; }}
            QFrame#InputGroup, QFrame#OptionsGroup, QFrame#OARGroup {{ border: 1px solid #e0e0e0; border-radius: 4px; margin: 0px; padding: 1px; }}
            QPushButton {{ padding: 5px 10px; border-radius: 3px; border: 1px solid #b0b0b0; background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f3f3f3, stop:1 #e2e2e2); }}
            QPushButton:hover {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f0f0f0); border: 1px solid #909090; }}
            QPushButton:pressed {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e2e2e2, stop:1 #f3f3f3); }}
            QPushButton#GenerateButton {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66bb6a, stop:1 #43a047); color: white; padding: 8px 15px; font-size: 11pt; font-weight: bold; border: 1px solid #388E3C; }}
            QPushButton#GenerateButton:hover {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #81c784, stop:1 #66bb6a); border: 1px solid #4caf50; }}
            QPushButton#GenerateButton:pressed {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #43a047, stop:1 #66bb6a); }}
            QPushButton#GenerateButton:disabled {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e0e0e0, stop:1 #d0d0d0); color: #888888; border: 1px solid #b0b0b0; }}
            QPushButton#DeleteDoseButton, QPushButton.DeleteOARButton, QPushButton.ConfigureOARButton,
            QPushButton#FindNextButton, QPushButton#FindPrevButton, QPushButton#ClearSearchButton {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f0f0, stop:1 #e0e0e0); border: 1px solid #c0c0c0; padding: 3px 6px; font-size: 9pt; }}
            QPushButton#DeleteDoseButton:hover, QPushButton.DeleteOARButton:hover, QPushButton.ConfigureOARButton:hover,
            QPushButton#FindNextButton:hover, QPushButton#FindPrevButton:hover, QPushButton#ClearSearchButton:hover {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f5f5f5); border: 1px solid #909090; }}
            QPushButton.DeleteOARButton {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #fddede, stop:1 #fcc2c2); border: 1px solid #fca4a4; }}
            QPushButton.DeleteOARButton:hover {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffecec, stop:1 #fddede); border: 1px solid #f88787; }}
            QPushButton#DeleteDoseButton:disabled {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e0e0e0, stop:1 #d0d0d0); color: #888888; border: 1px solid #b0b0b0; }}
            QPushButton#FindNextButton:disabled, QPushButton#FindPrevButton:disabled {{ background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e0e0e0, stop:1 #d0d0d0); color: #aaaaaa; border: 1px solid #c0c0c0; }}
            QTabWidget::pane {{ border: 1px solid #d0d0d0; border-top: none; margin-top: -1px; background-color: white; }}
            QTabBar::tab {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f0f0f0, stop:1 #e0e0e0); border: 1px solid #c0c0c0; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px; min-width: 100px; padding: 7px 12px; margin-right: 1px; color: #333; }}
            QTabBar::tab:selected, QTabBar::tab:hover {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #f5f5f5); }}
            QTabBar::tab:selected {{ border-color: #d0d0d0; margin-bottom: 0px; color: black; font-weight: bold; }}
            QTabBar::tab:!selected {{ margin-top: 2px; }}
            QScrollArea {{ border: none; }} #ScrollWidget {{ background-color: {COLOR_DEFAULT_BG}; }}
            QListWidget, QTableWidget {{ border: 1px solid #d0d0d0; }}
            QLineEdit {{ border: 1px solid #d0d0d0; padding: 3px; border-radius: 2px; }}
            QRadioButton {{ margin-top: 2px; margin-bottom: 2px; }}
            #SearchLineEdit {{ padding: 4px; }}
        """)

    def initUI(self):
        self.setWindowTitle(f'Eclipse Contouring Helper {APP_VERSION} ({datetime.date.today().strftime("%Y-%m-%d")})')
        self.setGeometry(30, 30, 1300, 900)
        main_layout = QVBoxLayout(self); main_layout.setContentsMargins(10,10,10,10); main_layout.setSpacing(10)
        top_grid = QGridLayout(); top_grid.setSpacing(10)

        # Dose Input
        dose_gb = QFrame(); dose_gb.setObjectName("InputGroup"); dose_gb.setFrameShape(QFrame.StyledPanel)
        dose_lo = QVBoxLayout(dose_gb); dose_lo.setContentsMargins(10,8,10,8); dose_lo.setSpacing(6)
        dose_lo.addWidget(QLabel(bold("1. Syötä PTV-annokset (Gy):")))
        dose_entry_lo = QHBoxLayout()
        self.dose_input = QLineEdit(); self.dose_input.setPlaceholderText("Esim. 66 tai 50,4")
        self.add_dose_btn = QPushButton("Lisää"); self.add_dose_btn.clicked.connect(self.add_dose)
        dose_entry_lo.addWidget(self.dose_input, 1); dose_entry_lo.addWidget(self.add_dose_btn)
        dose_lo.addLayout(dose_entry_lo)
        self.dose_list_w = QListWidget(); self.dose_list_w.setFixedHeight(100)
        self.dose_list_w.itemSelectionChanged.connect(self.update_delete_button_state)
        dose_lo.addWidget(self.dose_list_w)
        self.del_dose_btn = QPushButton("Poista valittu"); self.del_dose_btn.setObjectName("DeleteDoseButton")
        self.del_dose_btn.setToolTip("Poistaa valitun annoksen listasta"); self.del_dose_btn.setEnabled(False)
        self.del_dose_btn.clicked.connect(self.remove_selected_dose_button_clicked)
        dose_lo.addWidget(self.del_dose_btn)
        top_grid.addWidget(dose_gb, 0, 0)

        # OAR Input
        oar_gb = QFrame(); oar_gb.setObjectName("OARGroup"); oar_gb.setFrameShape(QFrame.StyledPanel)
        oar_lo = QVBoxLayout(oar_gb); oar_lo.setContentsMargins(10,8,10,8); oar_lo.setSpacing(6)
        oar_lo.addWidget(QLabel(bold("2. Syötä tervekudokset (OAR):")))
        oar_entry_lo = QHBoxLayout()
        self.oar_input = QLineEdit(); self.oar_input.setPlaceholderText("Esim. Rectum, Heart...")
        self.add_oar_btn = QPushButton("Lisää OAR"); self.add_oar_btn.clicked.connect(self.add_oar)
        oar_entry_lo.addWidget(self.oar_input, 1); oar_entry_lo.addWidget(self.add_oar_btn)
        oar_lo.addLayout(oar_entry_lo)
        self.oar_table_w = QTableWidget(); self.oar_table_w.setColumnCount(3)
        self.oar_table_w.setHorizontalHeaderLabels(["OAR Nimi", "dPTV+OAR Overlapit", "Toiminto"])
        self.oar_table_w.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.oar_table_w.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.oar_table_w.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.oar_table_w.setMinimumHeight(130); oar_lo.addWidget(self.oar_table_w)
        top_grid.addWidget(oar_gb, 0, 1)

        # Options
        opt_gb = QFrame(); opt_gb.setObjectName("OptionsGroup"); opt_gb.setFrameShape(QFrame.StyledPanel)
        opt_lo = QVBoxLayout(opt_gb); opt_lo.setContentsMargins(10,8,10,8); opt_lo.setSpacing(8)
        opt_lo.addWidget(QLabel(bold("3. Muut valinnat:")))
        self.niska_cb = QCheckBox("Luo vNiska?"); self.niska_cb.setToolTip("Luo vNiska-rakenteen (vaatii SpinalCord).")
        opt_lo.addWidget(self.niska_cb)
        opt_lo.addStretch(1) # Add stretch to push the checkbox to the top
        top_grid.addWidget(opt_gb, 1, 0)


        # Generate Button
        gen_cont = QWidget()
        gen_lo = QVBoxLayout(gen_cont); gen_lo.setContentsMargins(0,0,0,0)
        self.gen_btn = QPushButton("Generoi Ohjeet"); self.gen_btn.setObjectName("GenerateButton")
        self.gen_btn.setIconSize(QSize(18,18)); self.gen_btn.clicked.connect(self.generate_output)
        gen_lo.addSpacerItem(QSpacerItem(20,10,QSizePolicy.Minimum, QSizePolicy.Expanding))
        gen_lo.addWidget(self.gen_btn)
        gen_lo.addSpacerItem(QSpacerItem(20,10,QSizePolicy.Minimum, QSizePolicy.Expanding))
        top_grid.addWidget(gen_cont, 1, 1, Qt.AlignVCenter | Qt.AlignHCenter)

        top_grid.setColumnStretch(0,1); top_grid.setColumnStretch(1,1)
        top_grid.setRowMinimumHeight(0,200); top_grid.setRowMinimumHeight(1,150)
        main_layout.addLayout(top_grid)


        # Tabs
        self.tabs = QTabWidget()
        # Guide Tab
        self.guide_tab_w = QWidget()
        guide_lo = QVBoxLayout(self.guide_tab_w); guide_lo.setContentsMargins(0,5,0,0); guide_lo.setSpacing(5)
        search_lo = QHBoxLayout(); search_lo.setContentsMargins(5,0,5,0)
        search_icon = QLabel(EMOJI_SEARCH); search_icon.setStyleSheet("font-size: 12pt;")
        self.search_in = QLineEdit(); self.search_in.setObjectName("SearchLineEdit"); self.search_in.setPlaceholderText("Etsi ohjeista...")
        self.search_in.textChanged.connect(self._on_search_text_changed); self.search_in.returnPressed.connect(self._find_next)
        self.find_next_btn = QPushButton("Seuraava"); self.find_next_btn.setObjectName("FindNextButton")
        self.find_prev_btn = QPushButton("Edellinen"); self.find_prev_btn.setObjectName("FindPrevButton")
        self.clear_search_btn = QPushButton("Tyhjennä"); self.clear_search_btn.setObjectName("ClearSearchButton")
        self.find_next_btn.clicked.connect(self._find_next); self.find_prev_btn.clicked.connect(self._find_previous); self.clear_search_btn.clicked.connect(self._clear_search)
        self.find_next_btn.setEnabled(False); self.find_prev_btn.setEnabled(False)
        search_lo.addWidget(search_icon); search_lo.addWidget(self.search_in,1); search_lo.addWidget(self.find_prev_btn); search_lo.addWidget(self.find_next_btn); search_lo.addWidget(self.clear_search_btn)
        guide_lo.addLayout(search_lo)

        prog_area_lo = QHBoxLayout(); prog_area_lo.setContentsMargins(5,0,5,0); prog_area_lo.addStretch(1)
        self.prog_lbl = QLabel("Vaiheet: 0 / 0"); self.prog_lbl.setFont(QFont("Segoe UI",9)); self.prog_lbl.setStyleSheet("QLabel{margin-right:5px; color:#555;}")
        prog_area_lo.addWidget(self.prog_lbl); guide_lo.addLayout(prog_area_lo)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_w = QWidget(); self.scroll_w.setObjectName("ScrollWidget")
        self.steps_lo = QVBoxLayout(self.scroll_w); self.steps_lo.setContentsMargins(5,5,10,5); self.steps_lo.setSpacing(0); self.steps_lo.addStretch(1)
        self.scroll.setWidget(self.scroll_w); guide_lo.addWidget(self.scroll,1)

        # Criteria Tab
        self.crit_tab_w = QWidget(); crit_lo = QVBoxLayout(self.crit_tab_w); crit_lo.setContentsMargins(5,5,5,5)
        self.crit_text = QTextEdit(); self.crit_text.setReadOnly(True); self.crit_text.setFont(QFont("Segoe UI",10))
        crit_lo.addWidget(self.crit_text)


        # Crop Summary Tab
        self.crop_sum_tab_w = QWidget(); crop_sum_lo = QVBoxLayout(self.crop_sum_tab_w); crop_sum_lo.setContentsMargins(5,5,5,5)
        self.crop_sum_text = QTextEdit(); self.crop_sum_text.setReadOnly(True); self.crop_sum_text.setFont(QFont("Segoe UI",9))
        crop_sum_lo.addWidget(self.crop_sum_text)

        self.tabs.addTab(self.guide_tab_w, "Vaiheittainen ohje"); self.tabs.addTab(self.crit_tab_w, "Optimointikriteerit"); self.tabs.addTab(self.crop_sum_tab_w, "Crop Yhteenveto")
        main_layout.addWidget(self.tabs,1)

        self._setup_oar_completer()
        self.update_generate_button_state(); self.update_delete_button_state(); self._update_oar_table_widget()

    def _setup_oar_completer(self):
        self.oar_compl_model = QStringListModel(COMMON_OARS, self)
        self.oar_compl = QCompleter(self.oar_compl_model, self)
        self.oar_compl.setCaseSensitivity(Qt.CaseInsensitive); self.oar_compl.setCompletionMode(QCompleter.PopupCompletion)
        self.oar_input.setCompleter(self.oar_compl); self.oar_compl.activated.connect(self._add_oar_from_completer)

    def _add_oar_from_completer(self, text):
        self.oar_input.setText(text)
        self.add_oar()

    def add_dose(self):
        txt = self.dose_input.text().strip().replace(',','.')
        if not txt: return
        try:
            d = float(txt)
            if d <= 0: QMessageBox.warning(self, "Virheellinen annos", "Annostason on oltava positiivinen."); return
            if d in self.ptv_doses_list: QMessageBox.warning(self, "Annos jo lisätty", f"Annos {format_dose(d)} Gy on jo listalla."); return
            self.ptv_doses_list.append(d); self.ptv_doses_list.sort(reverse=True)
            self.update_dose_list_widget(); self.dose_input.clear(); self._update_oar_table_widget()
        except ValueError: QMessageBox.warning(self, "Virheellinen syöte", f"'{txt}' ei ole numero.")
        self.update_generate_button_state(); self.clear_output()

    def remove_selected_dose_button_clicked(self):
        items = self.dose_list_w.selectedItems()
        if not items: return
        removed = False
        for item in items:
            try:
                d_rem_str = item.text().replace(" Gy","").replace(",",".")
                d_rem = float(d_rem_str)
                if d_rem in self.ptv_doses_list:
                    self.ptv_doses_list.remove(d_rem)
                    for o_data in self.oars_data:
                        if d_rem in o_data.get('overlap_with_ptv_doses',[]):
                            o_data['overlap_with_ptv_doses'].remove(d_rem)
                    removed = True
            except ValueError:
                QMessageBox.critical(self, "Virhe", f"Annosta '{item.text()}' poistaessa muunnasvirhe.")
            except Exception as e:
                QMessageBox.critical(self, "Virhe", f"Annosta poistaessa virhe: {e}")

        if removed:
            self.update_dose_list_widget()
            self.update_generate_button_state()
            self._update_oar_table_widget()
            self.clear_output()
            self.update_delete_button_state()

    def update_dose_list_widget(self):
        self.dose_list_w.clear()
        for d in sorted(self.ptv_doses_list, reverse=True):
            self.dose_list_w.addItem(f"{format_dose(d)} Gy")

    def update_generate_button_state(self):
        if hasattr(self,'gen_btn'): self.gen_btn.setEnabled(len(self.ptv_doses_list) > 0)

    def update_delete_button_state(self):
        if hasattr(self,'del_dose_btn'): self.del_dose_btn.setEnabled(len(self.dose_list_w.selectedItems()) > 0)

    def add_oar(self):
        name = self.oar_input.text().strip()
        if not name: return
        if any(o['name'] == name for o in self.oars_data):
            QMessageBox.warning(self,"OAR jo lisätty", f"OAR '{name}' on jo listalla."); self.oar_input.clear(); return
        self.oars_data.append({'name':name, 'overlap_with_ptv_doses':[]})
        self.oars_data.sort(key=lambda item: item['name'])
        self._update_oar_table_widget(); self.oar_input.clear(); self.clear_output()

    def _remove_oar_at_row(self, row):
        if 0 <= row < len(self.oars_data):
            del self.oars_data[row]
            self._update_oar_table_widget()
            self.clear_output()

    def _configure_oar_ptv_overlaps(self, oar_row_idx):
        if not (0 <= oar_row_idx < len(self.oars_data)): return

        o_item = self.oars_data[oar_row_idx]
        o_name = o_item['name']
        initially_selected_doses = o_item.get('overlap_with_ptv_doses', [])

        if not self.ptv_doses_list:
            QMessageBox.information(self,"Ei PTV-annoksia","Syötä PTV-annoksia ensin, jotta voit määrittää päällekkäisyyksiä."); return

        dlg = OarPtvOverlapDialog(o_name, self.ptv_doses_list, initially_selected_doses, self)
        if dlg.exec_() == OarPtvOverlapDialog.Accepted:
            self.oars_data[oar_row_idx]['overlap_with_ptv_doses'] = dlg.get_selected_ptv_doses()
            self._update_oar_table_widget()
            self.clear_output()

    def _update_oar_table_widget(self):
        self.oar_table_w.setSortingEnabled(False)
        self.oar_table_w.setRowCount(0)
        self.oar_table_w.setRowCount(len(self.oars_data))

        for i, oar_item in enumerate(self.oars_data):
            name_item = QTableWidgetItem(oar_item['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
            self.oar_table_w.setItem(i, 0, name_item)

            overlap_cell_widget = QWidget()
            overlap_layout = QHBoxLayout(overlap_cell_widget)
            overlap_layout.setContentsMargins(2,0,2,0); overlap_layout.setSpacing(4)

            btn_configure = QPushButton("Määritä...")
            btn_configure.setObjectName("ConfigureOARButton")
            btn_configure.setToolTip(f"Määritä PTV-päällekkäisyydet OAR:lle {oar_item['name']}")
            btn_configure.clicked.connect(partial(self._configure_oar_ptv_overlaps, oar_row_idx=i))
            overlap_layout.addWidget(btn_configure)

            selected_doses = oar_item.get('overlap_with_ptv_doses', [])
            selected_doses_str = ", ".join([format_dose(d) for d in sorted(selected_doses, reverse=True)]) if selected_doses else "Ei valittu"
            if len(selected_doses_str) > 25:
                 selected_doses_str = f"{len(selected_doses)} PTV:tä valittu"
            label_selected_doses = QLabel(selected_doses_str)
            label_selected_doses.setStyleSheet("font-size:8pt; color:#555; margin-left:3px;")
            overlap_layout.addWidget(label_selected_doses)
            overlap_layout.addStretch()
            self.oar_table_w.setCellWidget(i, 1, overlap_cell_widget)

            btn_delete_oar = QPushButton("Poista")
            btn_delete_oar.setObjectName("DeleteOARButton")
            btn_delete_oar.clicked.connect(partial(self._remove_oar_at_row, row=i))

            delete_button_widget = QWidget()
            delete_button_layout = QHBoxLayout(delete_button_widget)
            delete_button_layout.addWidget(btn_delete_oar)
            delete_button_layout.setAlignment(Qt.AlignCenter)
            delete_button_layout.setContentsMargins(0,0,0,0)
            self.oar_table_w.setCellWidget(i, 2, delete_button_widget)

        self.oar_table_w.resizeRowsToContents()
        self.oar_table_w.resizeColumnsToContents()
        self.oar_table_w.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.oar_table_w.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.oar_table_w.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.oar_table_w.setSortingEnabled(True)

    def clear_output(self):
        if hasattr(self,'steps_lo'):
            if self.highlighted_widget:
                self.highlighted_widget.set_highlighted(False)
                self.highlighted_widget=None
            self.current_search_index = -1

            for widget in self.step_widgets:
                if widget:
                    widget.deleteLater()
            self.step_widgets.clear()

            while self.steps_lo.count():
                 child = self.steps_lo.takeAt(0)
                 if child.widget():
                     child.widget().deleteLater()
                 elif child.layout(): # Poista myös alilayoutit, jos niitä olisi
                     while child.layout().count():
                         sub_child = child.layout().takeAt(0)
                         if sub_child.widget():
                             sub_child.widget().deleteLater()
                     child.layout().deleteLater()
                 elif child.spacerItem():
                     self.steps_lo.removeItem(child) # SpacerItemeille riittää removeItem

            self.steps_lo.addStretch(1) # Lisää stretch takaisin

        self.total_steps=0
        self.completed_steps=0
        self.update_progress_label()
        if hasattr(self,'crit_text'): self.crit_text.clear()
        if hasattr(self,'crop_sum_text'): self.crop_sum_text.clear()
        self.crop_summary_data = {}
        if hasattr(self,'search_in') and self.search_in: self.search_in.clear()
        if hasattr(self,'find_next_btn'): self.find_next_btn.setEnabled(False)
        if hasattr(self,'find_prev_btn'): self.find_prev_btn.setEnabled(False)

    def generate_output(self):
        if not self.ptv_doses_list:
            QMessageBox.warning(self,"Ei annoksia","Syötä vähintään yksi PTV-annos."); return

        required_attributes = ['niska_cb','steps_lo','crit_text','crop_sum_text','tabs']
        for attr in required_attributes:
            if not hasattr(self,attr):
                QMessageBox.critical(self,"Käyttöliittymävirhe",f"Elementti '{attr}' puuttuu sovelluksen alustuksesta."); return

        self.clear_output()

        sorted_doses = sorted(self.ptv_doses_list, reverse=True)
        create_niska = self.niska_cb.isChecked()
        current_oars_data = list(self.oars_data)

        # MUUTOKSET TÄSSÄ: Arvot kovakoodattu
        selected_ring_prefix = "NT"
        selected_dptv_oar_crop_cm = 0.1

        calculated_crops = {}
        final_names_for_criteria = {}
        v_prefix = "v"; ptv_base_name = f"{v_prefix}PTV"; ctv_base_name = f"{v_prefix}CTV"; crop_suffix_raw = "crop"

        try:
            if sorted_doses:
                hd = sorted_doses[0]
                final_names_for_criteria[hd] = (f"{ptv_base_name}{format_dose(hd)}", f"{ctv_base_name}{format_dose(hd)}")

            if len(sorted_doses) >= 2:
                for j_idx in range(1, len(sorted_doses)):
                    lower_d = sorted_doses[j_idx]
                    lower_d_str_fmt = format_dose(lower_d)
                    final_ptv_n = f"{ptv_base_name}{lower_d_str_fmt}{crop_suffix_raw}"
                    final_ctv_n = f"{ctv_base_name}{lower_d_str_fmt}{crop_suffix_raw}"
                    final_names_for_criteria[lower_d] = (final_ptv_n, final_ctv_n)

                    for i_idx in range(j_idx):
                        higher_d_i = sorted_doses[i_idx]
                        crop_key = (higher_d_i, lower_d)
                        if crop_key not in calculated_crops: calculated_crops[crop_key] = {}
                        calculated_crops[crop_key]['PTV'] = calculate_ptv_crop(higher_d_i, lower_d)

            QApplication.setOverrideCursor(Qt.WaitCursor)
            guide_data, self.crop_summary_data = generate_guide_steps(
                sorted_doses, calculated_crops, create_niska,
                current_oars_data, selected_ring_prefix, selected_dptv_oar_crop_cm
            )

            temp_total_steps = 0

            for i, step_data in enumerate(guide_data):
                step_widget = StepWidget(
                    step_data.get("id"),
                    step_data.get("title","Nimetön vaihe"),
                    step_data.get("details_html","<p>Ei tarkempia ohjeita.</p>"),
                    step_data.get("emoji", EMOJI_INFO),
                    is_alt_row=(i%2==1)
                )

                if "toc_anchor_target_id" in step_data:
                    step_widget.toc_anchor_target_id = step_data["toc_anchor_target_id"]

                if step_data.get("id") == 0:
                    step_widget.checkbox.setVisible(False)
                    step_widget.details_label.setOpenExternalLinks(False)
                    step_widget.details_label.linkActivated.connect(self.handle_toc_link_activated) # KORJATTU TÄHÄN
                else:
                    step_widget.completionChanged.connect(self.update_progress)
                    temp_total_steps += 1

                if self.steps_lo.count() > 0 and self.steps_lo.itemAt(self.steps_lo.count()-1).spacerItem():
                    self.steps_lo.insertWidget(self.steps_lo.count()-1, step_widget)
                else:
                     self.steps_lo.addWidget(step_widget)

                self.step_widgets.append(step_widget)

            self.total_steps = temp_total_steps
            self.completed_steps = 0

            criteria_html = generate_optimization_criteria_html(
                sorted_doses, final_names_for_criteria, create_niska,
                current_oars_data, selected_ring_prefix
            )
            self.crit_text.setHtml(criteria_html)

            self._generate_and_display_crop_summary()

            self.tabs.setCurrentIndex(0)
            self.update_progress_label()

        except Exception as e:
            QMessageBox.critical(self,"Generointivirhe",f"Ohjeiden generoinnissa tapahtui virhe: {e}\nTarkista syötteet ja yritä uudelleen.");
            import traceback
            traceback.print_exc(file=sys.stderr)
            self.clear_output()
        finally:
            QApplication.restoreOverrideCursor()

    def handle_toc_link_activated(self, link_str: str): # KORJATTU METODIN NIMI JA SIGNAATUURI
        """Käsittelee sisällysluettelon linkkien klikkaukset (QLabel.linkActivated)."""
        url = QUrl(link_str) # Muunna merkkijono QUrl-olioksi
        target_fragment = url.fragment()

        if not target_fragment:
            return

        for widget in self.step_widgets:
            if hasattr(widget, 'toc_anchor_target_id') and widget.toc_anchor_target_id == target_fragment:
                self.scroll.ensureWidgetVisible(widget, yMargin=20)
                break

    def _generate_and_display_crop_summary(self):
        if not self.crop_summary_data:
            self.crop_sum_text.setHtml("<p><i>Ei crop-dataa saatavilla.</i></p>")
            return

        try:
            from config import COLOR_TITLE, COLOR_VALUE
        except ImportError:
            COLOR_TITLE = "#003366"
            COLOR_VALUE = "#005000"

        summary_html = [f"""
        <style>
            body{{font-family:'Segoe UI';font-size:9pt;}}
            h3{{color:{COLOR_TITLE};}}
            table{{width:100%;border-collapse:collapse;margin-top:5px;}}
            th{{background-color:#f0f0f0;border:1px solid #d0d0d0;padding:5px;text-align:left;font-weight:bold;}}
            td{{border:1px solid #e0e0e0;padding:4px 5px;vertical-align:top;}}
            td.step{{font-weight:bold;text-align:right;width:5%;}}
            td.margin{{font-weight:bold;color:{COLOR_VALUE};text-align:right;width:15%;}}
            td.desc{{width:80%;}}
        </style>"""]
        summary_html.append("<h3>Generoidut Crop-marginaalit</h3><table><tr><th>Vaihe</th><th>Kuvaus</th><th>Marginaali (cm)</th></tr>")

        has_content = False
        for step_id in sorted(self.crop_summary_data.keys()):
            data = self.crop_summary_data[step_id]
            description = data.get("text","N/A")
            margin_cm = data.get("margin_cm","N/A")

            if isinstance(margin_cm, (int, float)) and abs(margin_cm) < 0.001:
                continue
            has_content = True

            margin_str = f"{margin_cm:.2f}" if isinstance(margin_cm,(int,float)) else str(margin_cm)
            summary_html.append(f"<tr><td class='step'>{step_id}</td><td class='desc'>{description}</td><td class='margin'>{margin_str}</td></tr>")

        summary_html.append("</table>")

        if not has_content:
            self.crop_sum_text.setHtml("<p><i>Ei crop-marginaaleja näytettäväksi (kaikki olivat 0 cm tai dataa ei ollut).</i></p>")
        else:
            self.crop_sum_text.setHtml("\n".join(summary_html))

    def update_progress(self, is_complete):
        self.completed_steps = sum(1 for widget in self.step_widgets if widget.is_complete and widget.checkbox.isVisible() and widget.step_id != 0)
        self.update_progress_label()

    def update_progress_label(self):
        if hasattr(self,'prog_lbl'): self.prog_lbl.setText(f"Vaiheet: {self.completed_steps} / {self.total_steps}")

    def _on_search_text_changed(self,text):
        term = text.strip()
        has_term = bool(term)
        if hasattr(self,'find_next_btn'): self.find_next_btn.setEnabled(has_term and len(self.step_widgets)>0)
        if hasattr(self,'find_prev_btn'): self.find_prev_btn.setEnabled(has_term and len(self.step_widgets)>0)

        if not has_term and self.highlighted_widget:
            self.highlighted_widget.set_highlighted(False)
            self.highlighted_widget=None

        if term != self.last_search_term:
            self.current_search_index = -1
            if self.highlighted_widget:
                self.highlighted_widget.set_highlighted(False)
                self.highlighted_widget=None
        self.last_search_term = term

    def _clear_search(self):
        if hasattr(self,'search_in') and self.search_in:
            self.search_in.clear()

    def _find_next(self): self._find_search_term(1)
    def _find_previous(self): self._find_search_term(-1)

    def _find_search_term(self,direction):
        if not hasattr(self,'search_in') or not self.search_in: return
        term = self.search_in.text().strip().lower()
        if not term or not self.step_widgets: return

        searchable_widgets = [sw for sw in self.step_widgets if sw.step_id != 0]
        if not searchable_widgets: return
        num_searchable_widgets = len(searchable_widgets)

        start_idx = -1
        if self.highlighted_widget and self.highlighted_widget in searchable_widgets:
            try:
                start_idx = searchable_widgets.index(self.highlighted_widget)
            except ValueError:
                start_idx = -1

        if self.highlighted_widget:
            self.highlighted_widget.set_highlighted(False)
            self.highlighted_widget=None

        found_this_time = False
        for i in range(num_searchable_widgets):
            check_idx = (start_idx + (i * direction) + direction) % num_searchable_widgets
            widget_to_check = searchable_widgets[check_idx]

            if widget_to_check.contains_text(term):
                if hasattr(self,'scroll') and self.scroll:
                    self.scroll.ensureWidgetVisible(widget_to_check, yMargin=50)
                widget_to_check.set_highlighted(True)
                self.highlighted_widget=widget_to_check
                self.current_search_index = check_idx
                found_this_time = True
                break

        if not found_this_time:
            self.current_search_index = -1
            if start_idx == -1:
                 QMessageBox.information(self,"Etsi",f"Tekstiä '{self.search_in.text().strip()}' ei löytynyt ohjeista.");
