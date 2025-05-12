# -*- coding: utf-8 -*-
import math
import sys
import os
import datetime
# Lisätty functools-importti NameErrorin korjaamiseksi
from functools import partial
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QListWidget, QListWidgetItem, QMessageBox,
    QCheckBox, QSpacerItem, QSizePolicy, QScrollArea, QFrame, QTabWidget,
    QStyle, qApp, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QCompleter, QDialog, QDialogButtonBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QSize, QStringListModel
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QTextCursor

APP_VERSION = "v0.2.2-alpha" # <--- SOVELLUKSEN VERSIO PÄIVITETTY (functools fix)

# --- Emojit ja Värit ---
EMOJI_COPY = "📋"; EMOJI_CROP_IN = "✂️"; EMOJI_CROP_OUT = "✂️"
EMOJI_UNION = "➕"; EMOJI_RING = "💍"; EMOJI_MARGIN = "↔️"
EMOJI_BOOLEAN = "🧩"; EMOJI_CHECK = "👀"; EMOJI_WARNING = "⚠️"
EMOJI_MANUAL = "✍️"; EMOJI_INFO = "ℹ️"; EMOJI_DONE = "✅"
EMOJI_SEARCH = "🔍"

COLOR_COMPLETED_BG = "#e8f5e9"; COLOR_COMPLETED_FG = "#555555"
COLOR_DEFAULT_BG = "white"; COLOR_ALT_BG = "#f8f8f8"; COLOR_BORDER = "#d0d0d0"
COLOR_TITLE = "#003366"; COLOR_INSTRUCTION = "#333333"; COLOR_CODE = "#000080"
COLOR_VALUE = "#005000"; COLOR_PLACEHOLDER = "#444444"; COLOR_TOOL = "#005000"
COLOR_ACTION = "#c00000"; COLOR_NOTE = "#555555"
COLOR_SEARCH_HIGHLIGHT_BG = "#fff3cd" # Background for search highlight (temporary)
COLOR_SEARCH_HIGHLIGHT_BORDER = "#ffc107" # Border for search highlight (temporary)

# Updated list including common OARs and those extracted from the provided text
COMMON_OARS = sorted(list(set([
    "A_Aorta", "A_Carotid_L", "A_Carotid_R", "A_LAD", "A_Pulm",
    "Arytenoid_L", "Arytenoid_R", "Atrium_L", "Atrium_R",
    "Bag_Bowel", "Bladder", "Bone_Mandible", "Bone_Pelvic", "BowelBag", "BowelLarge", "BowelSmall",
    "BrachialPlex_L", "BrachialPlex_R", "BrachialPlexus_L", "BrachialPlexus_R",
    "Brain", "Brainstem", "Breast_L", "Breast_R", "Breast_RTOG_L", "Breast_RTOG_R",
    "Bronchus_Prox", "BrTW_RTOG_L", "BrTW_RTOG_R", "Buccal_Mucosa_L", "Buccal_Mucosa_R",
    "CaudaEquina", "Cavity_Oral", "Chestwall_L", "Chestwall_R", "Cochlea_L", "Cochlea_R",
    "Cricophar_inlet", "Duodenum", "Esophagus", "Esophagus_S",
    "Eye_Ant_L", "Eye_Ant_R", "Eye_L", "Eye_R", "Eye_Post_L", "Eye_Post_R",
    "FemoralHead_L", "FemoralHead_R", "Femur_Head_L", "Femur_Head_R", "Femur_Implant_L", "Femur_Implant_R", "Femur_L", "Femur_R",
    "Fossa_Pituitary", "Glnd_Lacrimal_L", "Glnd_Lacrimal_R", "Glnd_Submand_L", "Glnd_Submand_R", "Glnd_Thyroid",
    "Glottis", "Heart", "Heart+A_Pulm", "Humerus_Head_L", "Humerus_Head_R", "Humerus_L", "Humerus_R",
    "Hippocampus_L", "Hippocampus_R",
    "Kidney_L", "Kidney_R", "Kidneys_Total",
    "L4_VB", "L5_VB", "Larynx", "Larynx_SG", "Lens_L", "Lens_R", "Lips", "Liver",
    "LN_Axilla_RTOG_L", "LN_Axilla_RTOG_R", "LN_Axillary_L", "LN_Axillary_R", # Broad regions
    "LN_Inguinal_L", "LN_Inguinal_R", "LN_NRG", "LN_Pivotal", "LN_RTOG", # General node volumes
    "Lung_L", "Lung_R", "Lungs_Total",
    "Mandible", "Markers", "Musc_Coccygeus_L", "Musc_Coccygeus_R", "Musc_Constrict",
    "Musc_Iliacus_L", "Musc_Iliacus_R", "Musc_Obt_Int_L", "Musc_Obt_Int_R",
    "Musc_Pirifor_L", "Musc_Pirifor_R", "Musc_Psoas_Maj_L", "Musc_Psoas_Maj_R",
    "OpticChiasm", "OpticChiasm_cnv", "OpticNerve_L", "OpticNerve_R", "OpticNrv_L", "OpticNrv_R", "OpticNrv_cnv_L", "OpticNrv_cnv_R",
    "OralCavity", "Pancreas", "Parotid_L", "Parotid_R", "PenileBulb", "PharynxConstrictors",
    "Pituitary", "Prostate", "RectoSigmoid", "Rectum", "Sacrum", "SeminalVes",
    "SpinalCanal", "SpinalCord", "Spleen", "Stomach",
    "Thyroid", "Trachea", "Trachea_Prox",
    "V_Venacava_I", "V_Venacava_S", "Ventricle_L", "Ventricle_R",
    "Vessels_L", "Vessels_Long_L", "Vessels_Long_R", "Vessels_R"
    # Note: Specific LN levels (e.g., LN_Neck_II_L) were excluded as they are often targets or specific levels rather than general OARs.
    # Jaw structures (LJ_Front_L/R etc.) were also excluded as they seem part of a separate 'Jaw Model'.
])))


# --- Laskentafunktiot ---
def calculate_ptv_crop(higher_dose, lower_dose):
    """Calculates PTV crop margin in cm."""
    if higher_dose <= 0: return 0.0
    if lower_dose >= higher_dose: return 0.0
    ratio = lower_dose / higher_dose; percentage = ratio * 100
    rounded_percentage_down = math.floor(percentage / 5) * 5
    steps = 0 if rounded_percentage_down >= 95 else (95 - rounded_percentage_down) / 5
    return int(steps) / 10.0

def calculate_ring_crop(ring_ptv_dose, target_ptv_dose):
    """Calculates Ring crop margin in cm."""
    if ring_ptv_dose == target_ptv_dose: return 0.1
    if target_ptv_dose <= 0: return 0.0
    ring_effective_dose = ring_ptv_dose * 0.8
    if ring_effective_dose >= target_ptv_dose: return 0.1
    ratio = ring_effective_dose / target_ptv_dose; percentage = ratio * 100
    rounded_percentage_down = math.floor(percentage / 5) * 5
    steps = 0 if rounded_percentage_down >= 95 else (95 - rounded_percentage_down) / 5
    final_crop_mm = max(1.0, float(int(steps)))
    return final_crop_mm / 10.0

def format_dose(dose):
    """Formats dose value for display (int or float with comma)."""
    if dose == int(dose): return str(int(dose))
    else: return str(dose).replace('.', ',')

# --- Helpers for Rich Text Formatting ---
def bold(text): return f'<b>{text}</b>'
def code(text): return f'<span style="font-weight:bold; color:{COLOR_CODE};">{text}</span>'
def value(text): return f'<span style="font-weight:bold; color:{COLOR_VALUE};">{str(text)}</span>'
def placeholder(text): return f'<i style="color:{COLOR_PLACEHOLDER};">{text}</i>'
def tool(text): return f'<i style="color:{COLOR_TOOL};">{text}</i>'
def action(text): return f'<b style="color:{COLOR_ACTION};">{text}</b>'
def note(text): return f'<i style="color:{COLOR_NOTE};">{text}</i>'


# --- Custom Step Widget ---
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
        # Force layout update if needed (usually automatic)
        if self.parentWidget() and self.parentWidget().layout():
             self.parentWidget().layout().activate()

    def _update_style(self):
        """Updates the visual style based on completion and highlight state."""
        base_frame_style_list = ["border: 1px solid", "border-radius: 3px", "margin-bottom: 4px", "padding: 0px"]
        base_label_style = "background-color: transparent;"

        if self.is_complete:
            bg_color = COLOR_COMPLETED_BG
            title_color = COLOR_COMPLETED_FG
            instruction_color = COLOR_COMPLETED_FG
            instruction_style = f"color: {instruction_color}; text-decoration: line-through; padding-left: 2px; line-height: 130%;"
            title_style = f"color: {title_color}; text-decoration: line-through;"
            border_color = COLOR_BORDER # Use default border even when complete
        else:
            bg_color = COLOR_ALT_BG if self.is_alt_row else COLOR_DEFAULT_BG
            title_color = COLOR_TITLE
            instruction_color = COLOR_INSTRUCTION
            instruction_style = f"color: {instruction_color}; text-decoration: none; padding-left: 2px; line-height: 130%;"
            title_style = f"color: {title_color};"
            border_color = COLOR_BORDER # Default border

        # Apply search highlight style if active
        if self._is_highlighted:
            bg_color = COLOR_SEARCH_HIGHLIGHT_BG
            border_color = COLOR_SEARCH_HIGHLIGHT_BORDER
            base_frame_style_list[0] = f"border: 2px solid" # Make border thicker for highlight

        base_frame_style_list.append(f"background-color: {bg_color}")
        base_frame_style_list[0] += f" {border_color}" # Add color to border style

        self.setStyleSheet(f"QFrame#StepWidgetFrame {{ {'; '.join(base_frame_style_list)}; }}")
        self.title_label.setText(f"{self.emoji} {bold(str(self.step_id) + '.')} {bold(self.original_title)}")
        self.title_label.setStyleSheet(base_label_style + title_style)
        self.details_label.setStyleSheet(base_label_style + instruction_style)

    def set_highlighted(self, highlighted):
        """Sets or removes the search highlight style."""
        if self._is_highlighted != highlighted:
            self._is_highlighted = highlighted
            self._update_style() # Re-apply styles with new highlight state

    def contains_text(self, text):
        """Checks if the title or details contain the given text (case-insensitive)."""
        if not text:
            return False
        search_text = text.lower()
        # Check title (plain text) and details (might contain HTML, check plain text version)
        return search_text in self.original_title.lower() or \
               search_text in self.details_label.text().lower()


# --- OAR PTV Overlap Configuration Dialog ---
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
            if dose_val in initially_selected_doses:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.ptv_list_widget.addItem(item)
        layout.addWidget(self.ptv_list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_selected_ptv_doses(self):
        selected_doses = []
        for i in range(self.ptv_list_widget.count()):
            item = self.ptv_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_doses.append(item.data(Qt.UserRole))
        return selected_doses

# --- Guide Step Generation ---
def generate_guide_steps(ptv_doses, calculated_crops_dict, create_vniska, oars_data_list, ring_prefix, dptv_oar_crop_margin_cm):
    """Generates step-by-step instructions and collects crop data."""
    steps = []
    crop_summary_data = {} # Dictionary to store {step_id: {"text": "Description", "margin_cm": value}}
    if not ptv_doses: return steps, crop_summary_data
    step_num = 0
    v = "v"; ptv_prefix = f"{v}PTV"; ctv_prefix = f"{v}CTV"; # ring_prefix passed as argument
    dptv_base_prefix = "dPTV"; crop_suffix = "crop"
    body_name_raw = "Body"; spinal_cord_raw = "SpinalCord"
    vptv_kaikki_raw = f"{v}PTVkaikki"; vctv_kaikki_raw = f"{v}CTVkaikki"

    all_original_ptv_raw = {d: f"PTV{format_dose(d)}" for d in ptv_doses}; all_original_ctv_raw = {d: f"CTV{format_dose(d)}" for d in ptv_doses}
    all_vptv_raw = {d: f"{v}PTV{format_dose(d)}" for d in ptv_doses}; all_vctv_raw = {d: f"{v}CTV{format_dose(d)}" for d in ptv_doses}
    highest_dose = ptv_doses[0]; is_multi_dose = len(ptv_doses) > 1
    final_volume_raw_names = {}; all_ring_raw_names = {}

    step_num += 1
    step1_details = f"""<ul><li>{action('Kopioi')} PTV:t: {', '.join([code(n) for n in all_original_ptv_raw.values()])} &rarr; {', '.join([code(n) for n in all_vptv_raw.values()])}</li>
                         <li>{action('Kopioi')} CTV:t: {', '.join([code(n) for n in all_original_ctv_raw.values()])} &rarr; {', '.join([code(n) for n in all_vctv_raw.values()])}</li>
                         <li>{note('Alkuperäisiä OAR:ja ja Bodya käytetään suoraan työkaluina, ellei alla toisin mainita.')}</li></ul>"""
    steps.append({"id": step_num, "title": "Kopioi alkuperäiset PTV/CTV rakenteet", "details_html": step1_details, "emoji": EMOJI_COPY})

    final_volume_raw_names[highest_dose] = (all_vptv_raw[highest_dose], all_vctv_raw[highest_dose])
    step_num += 1
    step2_high_details = f"<p>Korkeimman annostason ({value(highest_dose)} Gy) rakenteita {code(all_vptv_raw[highest_dose])} ja {code(all_vctv_raw[highest_dose])} käytetään sellaisenaan.</p>{note('Ei croppeja.')}"
    steps.append({"id": step_num, "title": f"Tarkista korkein annostaso ({value(highest_dose)} Gy)", "details_html": step2_high_details, "emoji": EMOJI_INFO})

    if is_multi_dose:
        for j in range(1, len(ptv_doses)):
            lower_dose = ptv_doses[j]; lower_dose_str_fmt = format_dose(lower_dose)
            vptv_crop_raw_name = f"{ptv_prefix}{lower_dose_str_fmt}{crop_suffix}"; vctv_crop_raw_name = f"{ctv_prefix}{lower_dose_str_fmt}{crop_suffix}"
            final_volume_raw_names[lower_dose] = (vptv_crop_raw_name, vctv_crop_raw_name)
            step_num += 1; steps.append({"id": step_num, "title": f"Luo {code(vptv_crop_raw_name)} kopioimalla", "details_html": f"<p>{action('Kopioi')} {code(all_vptv_raw[lower_dose])} &rarr; {code(vptv_crop_raw_name)}.</p>{note('Tätä muokataan.')}", "emoji": EMOJI_COPY})
            step_num += 1; steps.append({"id": step_num, "title": f"Luo {code(vctv_crop_raw_name)} kopioimalla", "details_html": f"<p>{action('Kopioi')} {code(all_vctv_raw[lower_dose])} &rarr; {code(vctv_crop_raw_name)}.</p>{note('Tätä muokataan.')}", "emoji": EMOJI_COPY})
            for i in range(j):
                higher_dose_i = ptv_doses[i]; vptv_high_tool_raw_name = all_vptv_raw[higher_dose_i]
                crop_key = (higher_dose_i, lower_dose); ptv_crop_cm = calculated_crops_dict.get(crop_key, {}).get('PTV', 0.0)
                step_num += 1
                # Lyhennetty ohjeteksti (esimerkki)
                crop_ptv_details = f"<p>{action('Crop (inside)')} {code(vptv_crop_raw_name)} työkalulla {code(vptv_high_tool_raw_name)} ({value(f'{ptv_crop_cm:.1f} cm')}).</p>"
                # Alkuperäinen pidempi ohje kommentoituna:
                # crop_ptv_details = f"<p>{action('Croppaa')} {code(vptv_crop_raw_name)} työkalulla {code(vptv_high_tool_raw_name)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{ptv_crop_cm:.1f} cm')}</li><li>Kohde: {code(vptv_crop_raw_name)} {note('(korvaa)')}</li></ul>"
                steps.append({"id": step_num, "title": f"Crop {code(vptv_crop_raw_name)} vs {code(vptv_high_tool_raw_name)}", "details_html": crop_ptv_details, "emoji": EMOJI_CROP_IN})
                crop_summary_data[step_num] = {"text": f"Crop {vptv_crop_raw_name} vs {vptv_high_tool_raw_name} (inside)", "margin_cm": ptv_crop_cm}

                step_num += 1
                # Lyhennetty ohjeteksti (esimerkki)
                crop_ctv_details = f"<p>{action('Crop (inside)')} {code(vctv_crop_raw_name)} työkalulla {code(vptv_high_tool_raw_name)} ({value(f'{ptv_crop_cm:.1f} cm')}).</p>"
                # Alkuperäinen pidempi ohje kommentoituna:
                # crop_ctv_details = f"<p>{action('Croppaa')} {code(vctv_crop_raw_name)} työkalulla {code(vptv_high_tool_raw_name)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{ptv_crop_cm:.1f} cm')}</li><li>Kohde: {code(vctv_crop_raw_name)} {note('(korvaa)')}</li></ul>"
                steps.append({"id": step_num, "title": f"Crop {code(vctv_crop_raw_name)} vs {code(vptv_high_tool_raw_name)}", "details_html": crop_ctv_details, "emoji": EMOJI_CROP_IN})
                crop_summary_data[step_num] = {"text": f"Crop {vctv_crop_raw_name} vs {vptv_high_tool_raw_name} (inside)", "margin_cm": ptv_crop_cm}


    step_num += 1
    # Lyhennetty ohjeteksti (esimerkki)
    step3_details = f"<p>{action('Union')} {bold('alkuperäiset')} vPTV:t &rarr; {code(vptv_kaikki_raw)}.</p>"
    # Alkuperäinen pidempi ohje kommentoituna:
    # step3_details = f"<p>{action('Yhdistä')} {bold('alkuperäiset')} vPTV:t: {', '.join([code(n) for n in all_vptv_raw.values()])}</p><ul><li>Työkalu: {tool('Boolean Operators')}</li><li>Operaatio: Union {note('( | )')}</li><li>Kohde: {code(vptv_kaikki_raw)} {note('(Luo uusi)')}</li></ul>"
    steps.append({"id": step_num, "title": f"Luo {code(vptv_kaikki_raw)}", "details_html": step3_details, "emoji": EMOJI_UNION})

    step_num += 1
    final_vctv_names_to_union = [code(final_volume_raw_names[dose][1]) for dose in ptv_doses]
    # Lyhennetty ohjeteksti (esimerkki)
    step4_details = f"<p>{action('Union')} {bold('lopulliset')} vCTV:t ({', '.join(final_vctv_names_to_union)}) &rarr; {code(vctv_kaikki_raw)}.</p>"
    # Alkuperäinen pidempi ohje kommentoituna:
    # step4_details = f"<p>{action('Yhdistä')} {bold('lopulliset')} vCTV:t: {', '.join(final_vctv_names_to_union)}</p><ul><li>Työkalu: {tool('Boolean Operators')}</li><li>Operaatio: Union {note('( | )')}</li><li>Kohde: {code(vctv_kaikki_raw)} {note('(Luo uusi)')}</li></ul>"
    steps.append({"id": step_num, "title": f"Luo {code(vctv_kaikki_raw)}", "details_html": step4_details, "emoji": EMOJI_UNION})

    for dose_r in ptv_doses:
        dose_str_fmt = format_dose(dose_r); vptv_original_raw_name = all_vptv_raw[dose_r]
        ring_raw_name = f"{ring_prefix}{dose_str_fmt}"; all_ring_raw_names[dose_r] = ring_raw_name
        step_num += 1
        # Lyhennetty ohjeteksti (esimerkki)
        create_ring_details = f"<p>{action('Luo Ring/NT')} {code(ring_raw_name)} pohjasta {code(vptv_original_raw_name)} ({value('-0.5 cm')} / {value('2.5-3.0 cm')}).</p>"
        # Alkuperäinen pidempi ohje kommentoituna:
        # create_ring_details = f"<p>{action('Luo')} {code(ring_raw_name)} pohjana {code(vptv_original_raw_name)}.</p><ul><li>Työkalu: {tool('Create Ring Structure')}</li><li>Sisäraja: {value('-0.5 cm')}</li><li>Ulkoraja: {value('2.5 - 3.0 cm')} {note('(Säädä tarv.)')}</li><li>Kohde: {code(ring_raw_name)} {note('(Luo uusi)')}</li></ul>"
        steps.append({"id": step_num, "title": f"Luo {code(ring_raw_name)}", "details_html": create_ring_details, "emoji": EMOJI_RING})

        step_num += 1
        crop_ring_body_margin_cm = 0.0
        # Lyhennetty ohjeteksti (esimerkki)
        crop_ring_body_details = f"<p>{action('Crop (outside)')} {code(ring_raw_name)} vs {code(body_name_raw)} ({value(f'{crop_ring_body_margin_cm:.1f} cm')}).</p>"
        # Alkuperäinen pidempi ohje kommentoituna:
        # crop_ring_body_details = f"<p>{action('Croppaa')} {code(ring_raw_name)} vs {code(body_name_raw)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part outside:')}</li><li>Työkalurakenne: {code(body_name_raw)}</li><li>Marginaali: {value(f'{crop_ring_body_margin_cm:.1f} cm')}</li><li>Kohde: {code(ring_raw_name)} {note('(korvaa)')}</li></ul>"
        steps.append({"id": step_num, "title": f"Crop {code(ring_raw_name)} vs {code(body_name_raw)}", "details_html": crop_ring_body_details, "emoji": EMOJI_CROP_OUT})
        crop_summary_data[step_num] = {"text": f"Crop {ring_raw_name} vs {body_name_raw} (outside)", "margin_cm": crop_ring_body_margin_cm}


    for dose_xx in ptv_doses:
        dose_str_fmt = format_dose(dose_xx)
        final_ptv_raw_name = final_volume_raw_names[dose_xx][0]; final_ctv_raw_name = final_volume_raw_names[dose_xx][1]
        dptv_for_ctv_crop_raw_name = f"{dptv_base_prefix}{dose_str_fmt}"
        step_num += 1; steps.append({"id": step_num, "title": f"Luo {code(dptv_for_ctv_crop_raw_name)} kopioimalla", "details_html": f"<p>{action('Kopioi')} {code(final_ptv_raw_name)} &rarr; {code(dptv_for_ctv_crop_raw_name)}.</p>", "emoji": EMOJI_COPY})

        step_num += 1
        dptv_vs_ctv_crop_cm = 0.1 # Standard 1mm crop
        # Lyhennetty ohjeteksti (esimerkki)
        crop_dptv_details = f"<p>{action('Crop (inside)')} {code(dptv_for_ctv_crop_raw_name)} vs {code(final_ctv_raw_name)} ({value(f'{dptv_vs_ctv_crop_cm:.1f} cm')}).</p>"
        # Alkuperäinen pidempi ohje kommentoituna:
        # crop_dptv_details = f"<p>{action('Croppaa')} {code(dptv_for_ctv_crop_raw_name)} vs {code(final_ctv_raw_name)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{dptv_vs_ctv_crop_cm:.1f} cm')} {note('(1 mm)')}</li><li>Kohde: {code(dptv_for_ctv_crop_raw_name)} {note('(korvaa)')}</li></ul>"
        steps.append({"id": step_num, "title": f"Crop {code(dptv_for_ctv_crop_raw_name)} vs {code(final_ctv_raw_name)}", "details_html": crop_dptv_details, "emoji": EMOJI_CROP_IN})
        crop_summary_data[step_num] = {"text": f"Crop {dptv_for_ctv_crop_raw_name} vs {final_ctv_raw_name} (inside)", "margin_cm": dptv_vs_ctv_crop_cm}


    if oars_data_list:
        step_num += 1
        oar_titles = ", ".join([code(o['name']) for o in oars_data_list])
        oar_processing_intro_details = f"<p>{bold(f'Käsittele OAR:t:')} {oar_titles}</p>" # Lyhennetty
        steps.append({"id": step_num, "title": "Riskielinten (OAR) käsittely", "details_html": oar_processing_intro_details, "emoji": EMOJI_INFO})

        for oar_item in oars_data_list:
            oar_name = oar_item['name']
            oar_name_code_fmt = code(oar_name)
            voar_crop_name_raw = f"v{oar_name}Crop"
            voar_crop_name_code_fmt = code(voar_crop_name_raw)
            step_num += 1
            copy_oar_details = f"<p>{action('Kopioi')} {oar_name_code_fmt} &rarr; {voar_crop_name_code_fmt}.</p>"
            steps.append({"id": step_num, "title": f"Kopioi {oar_name_code_fmt} &rarr; {voar_crop_name_code_fmt}", "details_html": copy_oar_details, "emoji": EMOJI_COPY})

            step_num += 1
            voar_vs_vptvall_crop_cm = 0.1 # Standard 1mm crop
            # Lyhennetty ohjeteksti (esimerkki)
            crop_oar_details = f"<p>{action('Crop (inside)')} {voar_crop_name_code_fmt} vs {code(vptv_kaikki_raw)} ({value(f'{voar_vs_vptvall_crop_cm:.1f} cm')}).</p>"
            # Alkuperäinen pidempi ohje kommentoituna:
            # crop_oar_details = f"<p>{action('Croppaa')} {voar_crop_name_code_fmt} vs {code(vptv_kaikki_raw)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{voar_vs_vptvall_crop_cm:.1f} cm')} {note('(1 mm)')}</li><li>Kohde: {voar_crop_name_code_fmt} {note('(korvaa)')}</li></ul>"
            steps.append({"id": step_num, "title": f"Crop {voar_crop_name_code_fmt} vs {code(vptv_kaikki_raw)}", "details_html": crop_oar_details, "emoji": EMOJI_CROP_IN})
            crop_summary_data[step_num] = {"text": f"Crop {voar_crop_name_raw} vs {vptv_kaikki_raw} (inside)", "margin_cm": voar_vs_vptvall_crop_cm}

    else:
        step_num += 1
        no_oar_details = f"<p>Ei määriteltyjä OAReja erilliseen käsittelyyn.</p>"
        steps.append({"id": step_num, "title": f"Ei OAR Crop -rakenteita", "details_html": no_oar_details, "emoji": EMOJI_INFO})

    any_oar_has_ptv_overlap_config = any(oar_item.get('overlap_with_ptv_doses') for oar_item in oars_data_list)
    if any_oar_has_ptv_overlap_config:
        oars_involved_in_any_overlap = []
        for oar_item in oars_data_list:
            if oar_item.get('overlap_with_ptv_doses'):
                oars_involved_in_any_overlap.append(oar_item['name'])

        if oars_involved_in_any_overlap:
            step_num += 1
            overlap_intro_list_str = "<ul>"
            for o_name in oars_involved_in_any_overlap:
                current_oar_item = next((o for o in oars_data_list if o['name'] == o_name), None)
                if current_oar_item and current_oar_item.get('overlap_with_ptv_doses'):
                    sorted_overlap_doses = sorted(current_oar_item['overlap_with_ptv_doses'], reverse=True)
                    ptv_levels_str = ', '.join([format_dose(d) + ' Gy' for d in sorted_overlap_doses])
                    overlap_intro_list_str += f"<li>{code(o_name)} (PTV-tasot: {ptv_levels_str})</li>"
            overlap_intro_list_str += "</ul>"
            overlap_info_details = f"<p>{bold('Luo dPTV+OAR Overlapit:')}</p>{overlap_intro_list_str}" # Lyhennetty
            steps.append({"id": step_num, "title": "Luo dPTV+OAR Overlapit (OAR & PTV-kohtainen)", "details_html": overlap_info_details, "emoji": EMOJI_INFO})

            for oar_item in oars_data_list:
                oar_name = oar_item['name']
                oar_name_code_fmt = code(oar_name)
                ptv_doses_for_this_oar_overlap = oar_item.get('overlap_with_ptv_doses', [])
                if not ptv_doses_for_this_oar_overlap:
                    continue

                sorted_ptv_doses_for_overlap = sorted(ptv_doses_for_this_oar_overlap, reverse=True)

                for ptv_dose_value in sorted_ptv_doses_for_overlap:
                    if ptv_dose_value not in ptv_doses: continue

                    ptv_dose_str_fmt = format_dose(ptv_dose_value)
                    source_ptv_for_boolean_raw_name = final_volume_raw_names.get(ptv_dose_value, ("", ""))[0]
                    if not source_ptv_for_boolean_raw_name: continue
                    target_dptv_to_crop_raw_name = f"{dptv_base_prefix}{ptv_dose_str_fmt}"

                    overlap_tool_raw_name = f"{dptv_base_prefix}{ptv_dose_str_fmt}+{oar_name}"
                    overlap_tool_code_fmt = code(overlap_tool_raw_name)

                    step_num += 1
                    # Lyhennetty ohjeteksti (esimerkki)
                    create_overlap_details = f"<p>{action('Boolean AND')} {code(source_ptv_for_boolean_raw_name)} & {oar_name_code_fmt} &rarr; {overlap_tool_code_fmt}.</p>"
                    # Alkuperäinen pidempi ohje kommentoituna:
                    # create_overlap_details = f"<p>{action('Luo leikkaus')} ({tool('Boolean Op: AND')}) {code(source_ptv_for_boolean_raw_name)} & {oar_name_code_fmt}.</p><ul><li>Kohde: {overlap_tool_code_fmt} {note('(Luo uusi työkalu)')}</li></ul>"
                    steps.append({"id": step_num, "title": f"Luo {overlap_tool_code_fmt}", "details_html": create_overlap_details, "emoji": EMOJI_BOOLEAN})

                    step_num += 1
                    dptv_vs_overlap_crop_cm = dptv_oar_crop_margin_cm
                    dptv_vs_overlap_crop_mm_str = f"{dptv_vs_overlap_crop_cm * 10:.1f}".replace('.0', '') + " mm"
                    # Lyhennetty ohjeteksti (esimerkki)
                    crop_dptv_overlap_details = f"<p>{action('Crop (inside)')} {code(target_dptv_to_crop_raw_name)} vs {overlap_tool_code_fmt} ({value(f'{dptv_vs_overlap_crop_cm:.2f} cm')} / {dptv_vs_overlap_crop_mm_str}).</p>"
                    # Alkuperäinen pidempi ohje kommentoituna:
                    # crop_dptv_overlap_details = f"<p>{action('Croppaa')} {code(target_dptv_to_crop_raw_name)} vs {overlap_tool_code_fmt}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{dptv_vs_overlap_crop_cm:.2f} cm')} {note(f'({dptv_vs_overlap_crop_mm_str})')}</li><li>Kohde: {code(target_dptv_to_crop_raw_name)} {note('(korvaa)')}</li></ul>"
                    steps.append({"id": step_num, "title": f"Crop {code(target_dptv_to_crop_raw_name)} vs {overlap_tool_code_fmt}", "details_html": crop_dptv_overlap_details, "emoji": EMOJI_CROP_IN})
                    crop_summary_data[step_num] = {"text": f"Crop {target_dptv_to_crop_raw_name} vs {overlap_tool_raw_name} (inside)", "margin_cm": dptv_vs_overlap_crop_cm}


    if is_multi_dose:
        step_num += 1
        ring_crop_info_details = f"<p>Seuraavaksi {action('cropataan')} {ring_prefix}-rakenteita muista vPTV:istä.</p>" # Lyhennetty
        steps.append({"id": step_num, "title": f"Muokkaa {ring_prefix}-rakenteita (Yleisohje)", "details_html": ring_crop_info_details, "emoji": EMOJI_INFO})
        for dose_r in ptv_doses:
            ring_to_crop_raw_name = all_ring_raw_names[dose_r]
            for i, dose_p in enumerate(ptv_doses):
                if dose_r == dose_p: continue
                ptv_tool_raw_name = all_vptv_raw[dose_p]; ring_crop_cm = calculate_ring_crop(dose_r, dose_p)
                step_num += 1
                # Lyhennetty ohjeteksti (esimerkki)
                crop_ring_details = f"<p>{action('Crop (inside)')} {code(ring_to_crop_raw_name)} vs {code(ptv_tool_raw_name)} ({value(f'{ring_crop_cm:.1f} cm')}).</p>"
                # Alkuperäinen pidempi ohje kommentoituna:
                # crop_ring_details = f"<p>{action('Croppaa')} {code(ring_to_crop_raw_name)} vs {code(ptv_tool_raw_name)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{ring_crop_cm:.1f} cm')}</li><li>Kohde: {code(ring_to_crop_raw_name)} {note('(korvaa)')}</li></ul>"
                steps.append({"id": step_num, "title": f"Crop {code(ring_to_crop_raw_name)} vs {code(ptv_tool_raw_name)}", "details_html": crop_ring_details, "emoji": EMOJI_CROP_IN})
                crop_summary_data[step_num] = {"text": f"Crop {ring_to_crop_raw_name} vs {ptv_tool_raw_name} (inside)", "margin_cm": ring_crop_cm}


    if create_vniska:
        v_niska_raw_name = "vNiska"
        step_num += 1; steps.append({"id": step_num, "title": f"Tarkista {code(spinal_cord_raw)}", "details_html": f"<p>{action('Tarkista')} {code(spinal_cord_raw)} piirto.</p>", "emoji": EMOJI_CHECK})
        step_num += 1
        # Lyhennetty ohjeteksti (esimerkki)
        create_niska_details = f"<p>{action('Luo Margin')} {code(v_niska_raw_name)} laajentamalla {code(spinal_cord_raw)} (Ant/Post/LR: {value('1.0')}/{value('5.0')}/{value('3.0 cm')}). {note('Tarkista manuaalisesti.')}</p>"
        # Alkuperäinen pidempi ohje kommentoituna:
        # create_niska_details = f"<p>{action('Luo')} {code(v_niska_raw_name)} laajentamalla {code(spinal_cord_raw)}.</p><ul><li>Työkalu: {tool('Margin Geometry')}</li><li>Marginaalit: Ant {value('1.0')}, Post {value('5.0')}, L/R {value('3.0 cm')}</li><li>Kohde: {code(v_niska_raw_name)} {note('(Luo uusi)')}</li></ul> {note('Tarkista ja muokkaa rajat manuaalisesti.')}"
        steps.append({"id": step_num, "title": f"Luo {code(v_niska_raw_name)}", "details_html": create_niska_details, "emoji": EMOJI_MARGIN})

        step_num += 1
        niska_vs_ptvall_crop_cm = 1.0
        # Lyhennetty ohjeteksti (esimerkki)
        crop_niska_ptv_details = f"<p>{action('Crop (inside)')} {code(v_niska_raw_name)} vs {code(vptv_kaikki_raw)} ({value(f'{niska_vs_ptvall_crop_cm:.1f} cm')}).</p>"
        # Alkuperäinen pidempi ohje kommentoituna:
        # crop_niska_ptv_details = f"<p>{action('Croppaa')} {code(v_niska_raw_name)} vs {code(vptv_kaikki_raw)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value('1.0 cm')}</li><li>Kohde: {code(v_niska_raw_name)} {note('(korvaa)')}</li></ul>"
        steps.append({"id": step_num, "title": f"Crop {code(v_niska_raw_name)} vs {code(vptv_kaikki_raw)}", "details_html": crop_niska_ptv_details, "emoji": EMOJI_CROP_IN})
        crop_summary_data[step_num] = {"text": f"Crop {v_niska_raw_name} vs {vptv_kaikki_raw} (inside)", "margin_cm": niska_vs_ptvall_crop_cm}

        step_num += 1
        niska_vs_body_crop_cm = 0.0
        # Lyhennetty ohjeteksti (esimerkki)
        crop_niska_body_details = f"<p>{action('Crop (outside)')} {code(v_niska_raw_name)} vs {code(body_name_raw)} ({value(f'{niska_vs_body_crop_cm:.1f} cm')}).</p>"
        # Alkuperäinen pidempi ohje kommentoituna:
        # crop_niska_body_details = f"<p>{action('Croppaa')} {code(v_niska_raw_name)} vs {code(body_name_raw)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part outside:')}</li><li>Marginaali: {value('0.0 cm')}</li><li>Kohde: {code(v_niska_raw_name)} {note('(korvaa)')}</li></ul>"
        steps.append({"id": step_num, "title": f"Crop {code(v_niska_raw_name)} vs {code(body_name_raw)}", "details_html": crop_niska_body_details, "emoji": EMOJI_CROP_OUT})
        crop_summary_data[step_num] = {"text": f"Crop {v_niska_raw_name} vs {body_name_raw} (outside)", "margin_cm": niska_vs_body_crop_cm}

    step_num += 1
    final_check_details = f"<p>{action('Tarkista')} kaikki luodut rakenteet huolellisesti.</p>"
    steps.append({"id": step_num, "title": "Lopullinen tarkistus", "details_html": final_check_details, "emoji": EMOJI_DONE})

    return steps, crop_summary_data

# --- Optimization Criteria Generation ---
def generate_optimization_criteria_html(ptv_doses, final_volume_names_main, create_vniska, oars_data_list, ring_prefix):
    """Generates HTML for optimization criteria based on inputs."""
    if not ptv_doses: return "<p><b>Ei PTV-annoksia syötetty kriteerien luontiin.</b></p>"

    criteria_html = []
    all_generated_ptv_lower_gy = []
    all_generated_ptv_upper_gy = []
    all_generated_ctv_lower_gy = []
    all_generated_ctv_upper_gy = []

    # Style definitions (same as before)
    criteria_html.append(f"""
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; font-size: 9.5pt; }}
        h2 {{ color: {COLOR_TITLE}; margin-bottom: 15px; font-size: 14pt;}}
        h4 {{ color: {COLOR_TITLE}; margin-top: 15px; margin-bottom: 8px; border-bottom: 1px solid #e0e0e0; padding-bottom: 3px; font-size: 11pt;}}
        h5 {{ color: {COLOR_INSTRUCTION}; margin-top:10px; margin-bottom:3px; font-size: 10pt; font-weight:bold;}}
        p.crit_item {{ margin: 1px 0px 8px 15px; line-height: 1.35; }}
        span.label {{ font-weight: bold; color: {COLOR_CODE}; }}
        span.value {{ font-weight: bold; color: {COLOR_VALUE}; }}
        span.unit {{ color: {COLOR_NOTE}; font-size: 9pt; }}
        span.note {{ font-style: italic; color: {COLOR_NOTE}; font-size: 9pt; }}
        p.warning {{ color: {COLOR_ACTION}; font-weight: bold; margin-top: 10px; border: 1px solid {COLOR_ACTION}; padding: 5px; border-radius: 3px; background-color:#fff0f0;}}
        ul.nto {{ margin-left: 15px; list-style-type: disc; }}
        li.nto {{ margin-bottom: 4px; }}
    </style>""")
    criteria_html.append("<h2>Optimointikriteerit (Esimerkkiarvot)</h2>")

    criteria_html.append(f"<p class='warning'>HUOM: Optimointikertoimet PTV-rakenteille voivat vaihdella annostasoittain riippuen siitä, onko kyseiselle PTV-annostasolle määritelty {code('dPTV+OAR')} -leikkauksia. {bold('TARKISTA AINA PROTOKOLLA!')}</p>")

    niska_name_html = f"<span class='label'>vNiska</span>";
    vptv_kaikki_name_html = f"<span class='label'>vPTVkaikki</span>";
    vctv_kaikki_name_html = f"<span class='label'>vCTVkaikki</span>";
    max_ptv_dose_val = ptv_doses[0]

    # Factors (same as before)
    dptv_lower_factor, dptv_upper_factor = 0.985, 1.015
    ctv_final_lower_factor, ctv_final_upper_factor = 1.00, 1.02
    dptv_oar_overlap_lower_factor, dptv_oar_overlap_upper_factor = 0.96, 0.99
    ring_upper_factor = 0.80 # Factor for Ring/NT upper limit

    any_ptv_oar_overlap_defined = any(oar.get('overlap_with_ptv_doses') for oar in oars_data_list)
    oar_crop_upper_factor = 0.85 if any_ptv_oar_overlap_defined else 0.90

    def format_criteria_html(label_html, lower_val=None, upper_val=None, note_text=None):
        line = f"<p class='crit_item'>{label_html}:"; indent = "&nbsp;&nbsp;&nbsp;"; details = []
        if upper_val is not None: details.append(f"{indent}Upper = <span class='value'>{upper_val:.2f}</span> <span class='unit'>Gy</span>")
        if lower_val is not None: details.append(f"{indent}Lower = <span class='value'>{lower_val:.2f}</span> <span class='unit'>Gy</span>")
        if details: line += "<br>" + "<br>".join(details)
        if note_text: line += f"<br>{indent}<span class='note'>{note_text}</span>"
        line += "</p>"; return line

    for dose_xx in ptv_doses:
        dose_str_fmt = format_dose(dose_xx)
        final_ptv_raw, final_ctv_raw = final_volume_names_main.get(dose_xx, (f"???PTV{dose_str_fmt}", f"???CTV{dose_str_fmt}"))

        is_this_ptv_dose_involved_in_overlap = any(dose_xx in oar.get('overlap_with_ptv_doses', []) for oar in oars_data_list)

        # Determine factors based on overlap involvement (same logic)
        if is_this_ptv_dose_involved_in_overlap:
            current_ptv_final_lower_factor, current_ptv_final_upper_factor = 0.96, 1.02
            current_ptv_orig_lower_factor = 0.96
            ptv_note = f"({note('Sis. dPTV+OAR')})"
        else:
            current_ptv_final_lower_factor, current_ptv_final_upper_factor = 0.985, 1.02
            current_ptv_orig_lower_factor = 0.985
            ptv_note = f"({note('Ei dPTV+OAR')})"

        # Generate HTML labels
        dptv_label_html = f"<span class='label'>dPTV{dose_str_fmt}</span>";
        final_ptv_label_html = f"<span class='label'>{final_ptv_raw}</span> {ptv_note}"
        final_ctv_label_html = f"<span class='label'>{final_ctv_raw}</span>";
        original_vptv_name = f"vPTV{dose_str_fmt}"
        orig_vptv_label_html = f"<span class='label'>{original_vptv_name}</span> <span class='note'>(orig)</span> {ptv_note}"
        # Use the selected ring_prefix here!
        ring_label_html = f"<span class='label'>{ring_prefix}{dose_str_fmt}</span> <span class='note'>(NT)</span>"

        criteria_html.append(f"<h4>Annostaso {dose_xx} Gy</h4>")

        # Calculate and add criteria lines (same calculations, just using generated labels)
        lower_gy_dptv = dptv_lower_factor * dose_xx
        upper_gy_dptv = dptv_upper_factor * dose_xx
        all_generated_ptv_lower_gy.append(lower_gy_dptv)
        all_generated_ptv_upper_gy.append(upper_gy_dptv)
        criteria_html.append(format_criteria_html(dptv_label_html, lower_gy_dptv, upper_gy_dptv))

        lower_gy_final_ptv = current_ptv_final_lower_factor * dose_xx
        upper_gy_final_ptv = current_ptv_final_upper_factor * dose_xx
        all_generated_ptv_lower_gy.append(lower_gy_final_ptv)
        all_generated_ptv_upper_gy.append(upper_gy_final_ptv)
        criteria_html.append(format_criteria_html(final_ptv_label_html, lower_gy_final_ptv, upper_gy_final_ptv))

        if final_ptv_raw != original_vptv_name:
            lower_gy_orig_ptv = current_ptv_orig_lower_factor * dose_xx
            upper_gy_orig_ptv = max(upper_gy_final_ptv, current_ptv_final_upper_factor * max_ptv_dose_val)
            all_generated_ptv_lower_gy.append(lower_gy_orig_ptv)
            all_generated_ptv_upper_gy.append(upper_gy_orig_ptv)
            criteria_html.append(format_criteria_html(orig_vptv_label_html, lower_gy_orig_ptv, upper_gy_orig_ptv))

        lower_gy_final_ctv = ctv_final_lower_factor * dose_xx
        upper_gy_final_ctv = ctv_final_upper_factor * dose_xx
        all_generated_ctv_lower_gy.append(lower_gy_final_ctv)
        all_generated_ctv_upper_gy.append(upper_gy_final_ctv)
        criteria_html.append(format_criteria_html(final_ctv_label_html, lower_gy_final_ctv, upper_gy_final_ctv))

        oars_overlapping_this_ptv_dose = [oar['name'] for oar in oars_data_list if dose_xx in oar.get('overlap_with_ptv_doses', [])]
        if oars_overlapping_this_ptv_dose:
            criteria_html.append(f"<h5>&nbsp;&nbsp;&nbsp;↳ {code(f'dPTV{dose_str_fmt}+OAR')} Leikkaukset</h5>")
            for oar_name_for_overlap in oars_overlapping_this_ptv_dose:
                overlap_struct_name = f"dPTV{dose_str_fmt}+{oar_name_for_overlap}"
                overlap_label_html = f"<span class='label'>{overlap_struct_name}</span>"
                lower_gy_dptv_oar = dptv_oar_overlap_lower_factor * dose_xx
                upper_gy_dptv_oar = dptv_oar_overlap_upper_factor * dose_xx
                all_generated_ptv_lower_gy.append(lower_gy_dptv_oar)
                all_generated_ptv_upper_gy.append(upper_gy_dptv_oar)
                criteria_html.append(format_criteria_html(overlap_label_html, lower_gy_dptv_oar, upper_gy_dptv_oar))

        # Use the correct ring label here
        criteria_html.append(format_criteria_html(ring_label_html, upper_val=ring_upper_factor * dose_xx))

    # General structures (same logic)
    criteria_html.append("<h4>Yleiset rakenteet</h4>")
    min_overall_ptv_lower_gy = min(all_generated_ptv_lower_gy) if all_generated_ptv_lower_gy else 0.0
    max_overall_ptv_upper_gy = max(all_generated_ptv_upper_gy) if all_generated_ptv_upper_gy else 0.0
    min_overall_ctv_lower_gy = min(all_generated_ctv_lower_gy) if all_generated_ctv_lower_gy else 0.0
    max_overall_ctv_upper_gy = max(all_generated_ctv_upper_gy) if all_generated_ctv_upper_gy else 0.0
    criteria_html.append(format_criteria_html(vptv_kaikki_name_html, min_overall_ptv_lower_gy, max_overall_ptv_upper_gy))
    criteria_html.append(format_criteria_html(vctv_kaikki_name_html, min_overall_ctv_lower_gy, max_overall_ctv_upper_gy))

    # OAR Crops (same logic)
    if oars_data_list:
        criteria_html.append(f"<h4>Riskielin Cropit ({code('v<OAR>Crop')})</h4>")
        for oar_item in oars_data_list:
            oar_name = oar_item['name']
            oar_crop_label_html = f"<span class='label'>v{oar_name}Crop</span>"
            criteria_html.append(format_criteria_html(oar_crop_label_html, upper_val=oar_crop_upper_factor * max_ptv_dose_val))

    # vNiska (same logic)
    if create_vniska:
        niska_crit = format_criteria_html(niska_name_html, upper_val=None)
        niska_crit = niska_crit.replace("</p>", f"<br>&nbsp;&nbsp;&nbsp;Upper = <span class='value'>???</span> <span class='unit'>Gy</span> <span class='note'>(TÄYTÄ MANUAALISESTI PROTOKOLLAN MUKAAN!)</span></p>")
        criteria_html.append(niska_crit)

    # NTO Reminder (same logic)
    criteria_html.append("<h4>Normal Tissue Objective (NTO) Muistutus</h4>")
    criteria_html.append("<p><b>HUOM:</b> Aseta NTO-parametrit manuaalisesti Eclipseen protokollan mukaisesti.</p>")
    criteria_html.append("<p>Yleiset esimerkkiarvot (<span style='color:red; font-weight:bold;'>TARKISTA AINA PAIKALLINEN PROTOKOLLA!</span>):</p>")
    criteria_html.append("<ul class='nto'>")
    criteria_html.append(f"<li class='nto'>Priority: <span class='value'>~100</span></li>")
    criteria_html.append(f"<li class='nto'>Distance from Target Border: <span class='value'>0.1 - 0.2</span> <span class='unit'>cm</span></li>")
    start_dose_example_lower = 0.9 * max_ptv_dose_val if max_ptv_dose_val > 0 else 0
    start_dose_example_upper = 0.95 * max_ptv_dose_val if max_ptv_dose_val > 0 else 0
    end_dose_example = 0.5 * max_ptv_dose_val if max_ptv_dose_val > 0 else 0
    criteria_html.append(f"<li class='nto'>Start Dose [%]: <span class='value'>90 - 95%</span> <span class='note'>(Esim. {start_dose_example_lower:.1f} - {start_dose_example_upper:.1f} Gy)</span></li>")
    criteria_html.append(f"<li class='nto'>End Dose [%]: <span class='value'>~50%</span> <span class='note'>(Esim. {end_dose_example:.1f} Gy)</span></li>")
    criteria_html.append(f"<li class='nto'>Fall-off: <span class='value'>0.15 - 0.25</span></li>")
    criteria_html.append("</ul>")

    # TÄMÄ FUNKTIO ON VALMIS, ÄLÄ MUOKKAA TÄTÄ ENÄÄ TEKOÄLYLLÄ!
    return "\n".join(criteria_html)


# --- PyQt5 GUI Class ---
class EclipseHelperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.ptv_doses_list = []
        self.oars_data = []
        self.step_widgets = []
        self.total_steps = 0
        self.completed_steps = 0
        self.crop_summary_data = {} # To store crop data for summary tab
        self.current_search_index = -1 # For tracking search position
        self.last_search_term = "" # Store last search term
        self.highlighted_widget = None # Keep track of the currently highlighted widget

        self.initUI()
        self._apply_global_styles()

    def _apply_global_styles(self):
        # Added styles for search buttons and potentially radio buttons if needed
        self.setStyleSheet(f"""
            QWidget {{ font-family: 'Segoe UI', sans-serif; font-size: 10pt; }}
            QFrame#InputGroup, QFrame#OptionsGroup, QFrame#OARGroup {{
                border: 1px solid #e0e0e0; border-radius: 4px; margin: 0px; padding: 1px;
            }}
            QPushButton {{
                padding: 5px 10px; border-radius: 3px;
                border: 1px solid #b0b0b0;
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f3f3f3, stop: 1 #e2e2e2);
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffffff, stop: 1 #f0f0f0);
                border: 1px solid #909090;
            }}
            QPushButton:pressed {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e2e2e2, stop: 1 #f3f3f3);
            }}
            QPushButton#GenerateButton {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #66bb6a, stop: 1 #43a047);
                color: white; padding: 8px 15px; font-size: 11pt; font-weight: bold; border: 1px solid #388E3C;
            }}
            QPushButton#GenerateButton:hover {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #81c784, stop: 1 #66bb6a);
                border: 1px solid #4caf50;
            }}
            QPushButton#GenerateButton:pressed {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #43a047, stop: 1 #66bb6a);
            }}
            QPushButton#GenerateButton:disabled {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e0e0e0, stop: 1 #d0d0d0);
                color: #888888; border: 1px solid #b0b0b0;
            }}
            QPushButton#DeleteDoseButton, QPushButton.DeleteOARButton, QPushButton.ConfigureOARButton,
            QPushButton#FindNextButton, QPushButton#FindPrevButton, QPushButton#ClearSearchButton {{ /* Added search buttons */
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f0f0f0, stop: 1 #e0e0e0);
                border: 1px solid #c0c0c0; padding: 3px 6px; font-size: 9pt;
            }}
            QPushButton#DeleteDoseButton:hover, QPushButton.DeleteOARButton:hover, QPushButton.ConfigureOARButton:hover,
            QPushButton#FindNextButton:hover, QPushButton#FindPrevButton:hover, QPushButton#ClearSearchButton:hover {{ /* Added search buttons */
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffffff, stop: 1 #f5f5f5);
                border: 1px solid #909090;
            }}
            QPushButton.DeleteOARButton {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #fddede, stop: 1 #fcc2c2);
                border: 1px solid #fca4a4;
            }}
            QPushButton.DeleteOARButton:hover {{
                background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffecec, stop: 1 #fddede);
                border: 1px solid #f88787;
            }}
             QPushButton#DeleteDoseButton:disabled {{
                 background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e0e0e0, stop: 1 #d0d0d0);
                 color: #888888; border: 1px solid #b0b0b0;
             }}
             QPushButton#FindNextButton:disabled, QPushButton#FindPrevButton:disabled {{ /* Disabled search style */
                 background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e0e0e0, stop: 1 #d0d0d0);
                 color: #aaaaaa; border: 1px solid #c0c0c0;
             }}
            QTabWidget::pane {{ border: 1px solid #d0d0d0; border-top: none; margin-top: -1px; background-color: white; }}
            QTabBar::tab {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #f0f0f0, stop: 1 #e0e0e0);
                border: 1px solid #c0c0c0; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;
                min-width: 100px; /* Adjusted min-width for more tabs */
                padding: 7px 12px; margin-right: 1px; color: #333;
            }}
            QTabBar::tab:selected, QTabBar::tab:hover {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffffff, stop: 1 #f5f5f5);
            }}
            QTabBar::tab:selected {{ border-color: #d0d0d0; margin-bottom: 0px; color: black; font-weight: bold; }}
            QTabBar::tab:!selected {{ margin-top: 2px; }}
            QScrollArea {{ border: none; }}
            #ScrollWidget {{ background-color: {COLOR_DEFAULT_BG}; }}
            QListWidget, QTableWidget {{ border: 1px solid #d0d0d0; }}
            QLineEdit {{ border: 1px solid #d0d0d0; padding: 3px; border-radius: 2px; }}
            QRadioButton {{ margin-top: 2px; margin-bottom: 2px; }}
            #SearchLineEdit {{ padding: 4px; }} /* Specific style for search input */
        """)

    def initUI(self):
        self.setWindowTitle(f'Eclipse Contouring Helper {APP_VERSION} ({datetime.date.today().strftime("%Y-%m-%d")})')
        self.setGeometry(30, 30, 1300, 900) # Slightly wider for options

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10); main_layout.setSpacing(10)

        top_grid_layout = QGridLayout(); top_grid_layout.setSpacing(10)

        # --- Dose Input Group (Column 0, Row 0) ---
        dose_input_groupbox = QFrame(); dose_input_groupbox.setObjectName("InputGroup"); dose_input_groupbox.setFrameShape(QFrame.StyledPanel)
        dose_input_layout = QVBoxLayout(dose_input_groupbox); dose_input_layout.setContentsMargins(10, 8, 10, 8); dose_input_layout.setSpacing(6)
        dose_input_layout.addWidget(QLabel(bold("1. Syötä PTV-annokset (Gy):")))
        dose_entry_layout = QHBoxLayout()
        self.dose_input = QLineEdit(); self.dose_input.setPlaceholderText("Esim. 66 tai 50,4")
        self.add_dose_button = QPushButton("Lisää"); self.add_dose_button.clicked.connect(self.add_dose)
        dose_entry_layout.addWidget(self.dose_input, 1); dose_entry_layout.addWidget(self.add_dose_button)
        dose_input_layout.addLayout(dose_entry_layout)
        self.dose_list_widget = QListWidget(); self.dose_list_widget.setFixedHeight(100)
        self.dose_list_widget.itemSelectionChanged.connect(self.update_delete_button_state)
        dose_input_layout.addWidget(self.dose_list_widget)
        self.delete_dose_button = QPushButton("Poista valittu"); self.delete_dose_button.setObjectName("DeleteDoseButton")
        self.delete_dose_button.setToolTip("Poistaa valitun annoksen listasta"); self.delete_dose_button.setEnabled(False)
        self.delete_dose_button.clicked.connect(self.remove_selected_dose_button_clicked)
        dose_input_layout.addWidget(self.delete_dose_button)
        top_grid_layout.addWidget(dose_input_groupbox, 0, 0)

        # --- OAR Management Group (Column 1, Row 0) ---
        oar_groupbox = QFrame(); oar_groupbox.setObjectName("OARGroup"); oar_groupbox.setFrameShape(QFrame.StyledPanel)
        oar_layout = QVBoxLayout(oar_groupbox); oar_layout.setContentsMargins(10, 8, 10, 8); oar_layout.setSpacing(6)
        oar_layout.addWidget(QLabel(bold("2. Syötä terveyskudokset (OAR):")))
        oar_entry_layout = QHBoxLayout()
        self.oar_input = QLineEdit(); self.oar_input.setPlaceholderText("Esim. Rectum, Heart...")
        self.add_oar_button = QPushButton("Lisää OAR"); self.add_oar_button.clicked.connect(self.add_oar)
        oar_entry_layout.addWidget(self.oar_input, 1); oar_entry_layout.addWidget(self.add_oar_button)
        oar_layout.addLayout(oar_entry_layout)
        self.oar_table_widget = QTableWidget(); self.oar_table_widget.setColumnCount(3)
        self.oar_table_widget.setHorizontalHeaderLabels(["OAR Nimi", "dPTV+OAR Overlapit", "Toiminto"])
        self.oar_table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.oar_table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.oar_table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.oar_table_widget.setMinimumHeight(130)
        oar_layout.addWidget(self.oar_table_widget)
        top_grid_layout.addWidget(oar_groupbox, 0, 1)

        # --- Options Group (Column 0, Row 1) ---
        options_groupbox = QFrame(); options_groupbox.setObjectName("OptionsGroup"); options_groupbox.setFrameShape(QFrame.StyledPanel)
        options_layout = QVBoxLayout(options_groupbox); options_layout.setContentsMargins(10, 8, 10, 8); options_layout.setSpacing(8)
        options_layout.addWidget(QLabel(bold("3. Muut valinnat:")))

        # vNiska Checkbox
        self.niska_checkbox = QCheckBox("Luo vNiska?"); self.niska_checkbox.setToolTip("Luo vNiska-rakenteen (vaatii SpinalCord-rakenteen).")
        options_layout.addWidget(self.niska_checkbox)

        options_layout.addWidget(QFrame(frameShape=QFrame.HLine, frameShadow=QFrame.Sunken)) # Separator

        # Ring Prefix Radio Buttons
        options_layout.addWidget(QLabel("Ring/NT Nimi:"))
        self.ring_prefix_group = QButtonGroup(self)
        self.ring_radio_ring = QRadioButton("Ring")
        self.ring_radio_nt = QRadioButton("NT")
        self.ring_radio_ring.setChecked(True) # Default
        self.ring_prefix_group.addButton(self.ring_radio_ring)
        self.ring_prefix_group.addButton(self.ring_radio_nt)
        ring_prefix_layout = QHBoxLayout()
        ring_prefix_layout.addWidget(self.ring_radio_ring)
        ring_prefix_layout.addWidget(self.ring_radio_nt)
        ring_prefix_layout.addStretch(1)
        options_layout.addLayout(ring_prefix_layout)

        options_layout.addWidget(QFrame(frameShape=QFrame.HLine, frameShadow=QFrame.Sunken)) # Separator

        # dPTV+OAR Crop Margin Radio Buttons
        options_layout.addWidget(QLabel("dPTV+OAR Crop Marginaali:"))
        self.dptv_oar_crop_group = QButtonGroup(self)
        self.dptv_oar_crop_05mm = QRadioButton("0.5 mm (0.05 cm)")
        self.dptv_oar_crop_10mm = QRadioButton("1.0 mm (0.1 cm)")
        self.dptv_oar_crop_05mm.setChecked(True) # Default
        self.dptv_oar_crop_group.addButton(self.dptv_oar_crop_05mm)
        self.dptv_oar_crop_group.addButton(self.dptv_oar_crop_10mm)
        dptv_crop_layout = QHBoxLayout()
        dptv_crop_layout.addWidget(self.dptv_oar_crop_05mm)
        dptv_crop_layout.addWidget(self.dptv_oar_crop_10mm)
        dptv_crop_layout.addStretch(1)
        options_layout.addLayout(dptv_crop_layout)

        options_layout.addStretch(1) # Push options up
        top_grid_layout.addWidget(options_groupbox, 1, 0)

        # --- Generate Button Group (Column 1, Row 1) ---
        generate_layout_container = QWidget()
        generate_layout = QVBoxLayout(generate_layout_container); generate_layout.setContentsMargins(0,0,0,0);
        self.generate_button = QPushButton("Generoi Ohjeet"); self.generate_button.setObjectName("GenerateButton")
        self.generate_button.setIconSize(QSize(18,18)); self.generate_button.clicked.connect(self.generate_output)
        generate_layout.addSpacerItem(QSpacerItem(20,10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        generate_layout.addWidget(self.generate_button)
        generate_layout.addSpacerItem(QSpacerItem(20,10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        top_grid_layout.addWidget(generate_layout_container, 1, 1, Qt.AlignVCenter | Qt.AlignHCenter) # Center horizontally too

        # Set column stretch factors
        top_grid_layout.setColumnStretch(0, 1)
        top_grid_layout.setColumnStretch(1, 1)
        # Ensure rows have reasonable minimum heights if needed
        top_grid_layout.setRowMinimumHeight(0, 200) # Min height for dose/oar inputs
        top_grid_layout.setRowMinimumHeight(1, 150) # Min height for options/generate button

        main_layout.addLayout(top_grid_layout)

        # --- Tabs ---
        self.tab_widget = QTabWidget()

        # -- Guide Tab --
        self.guide_tab = QWidget()
        guide_layout = QVBoxLayout(self.guide_tab); guide_layout.setContentsMargins(0, 5, 0, 0); guide_layout.setSpacing(5)

        # Search Bar Area
        search_layout = QHBoxLayout(); search_layout.setContentsMargins(5, 0, 5, 0) # Add margins
        search_icon_label = QLabel(EMOJI_SEARCH); search_icon_label.setStyleSheet("font-size: 12pt;")
        self.search_input = QLineEdit(); self.search_input.setObjectName("SearchLineEdit")
        self.search_input.setPlaceholderText("Etsi ohjeista...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        # Connect returnPressed signal to _find_next for Enter key search
        self.search_input.returnPressed.connect(self._find_next)
        self.find_next_button = QPushButton("Seuraava"); self.find_next_button.setObjectName("FindNextButton")
        self.find_prev_button = QPushButton("Edellinen"); self.find_prev_button.setObjectName("FindPrevButton")
        self.clear_search_button = QPushButton("Tyhjennä"); self.clear_search_button.setObjectName("ClearSearchButton")
        self.find_next_button.clicked.connect(self._find_next)
        self.find_prev_button.clicked.connect(self._find_previous)
        self.clear_search_button.clicked.connect(self._clear_search)
        self.find_next_button.setEnabled(False)
        self.find_prev_button.setEnabled(False)
        search_layout.addWidget(search_icon_label)
        search_layout.addWidget(self.search_input, 1) # Make input stretch
        search_layout.addWidget(self.find_prev_button)
        search_layout.addWidget(self.find_next_button)
        search_layout.addWidget(self.clear_search_button)
        guide_layout.addLayout(search_layout)

        # Progress Label Area
        progress_area_layout = QHBoxLayout(); progress_area_layout.setContentsMargins(5, 0, 5, 0)
        progress_area_layout.addStretch(1)
        self.progress_label = QLabel("Vaiheet: 0 / 0"); progress_font = QFont("Segoe UI", 9); self.progress_label.setFont(progress_font)
        self.progress_label.setStyleSheet("QLabel { margin-right: 5px; color: #555; }")
        progress_area_layout.addWidget(self.progress_label); guide_layout.addLayout(progress_area_layout)

        # Scroll Area for Steps
        self.scroll_area = QScrollArea(); self.scroll_area.setWidgetResizable(True); self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_widget = QWidget(); self.scroll_widget.setObjectName("ScrollWidget")
        self.steps_layout = QVBoxLayout(self.scroll_widget); self.steps_layout.setContentsMargins(5, 5, 10, 5); self.steps_layout.setSpacing(0)
        self.steps_layout.addStretch(1) # Add stretch at the end
        self.scroll_area.setWidget(self.scroll_widget); guide_layout.addWidget(self.scroll_area, 1) # Make scroll area stretch

        # -- Criteria Tab --
        self.criteria_tab = QWidget(); criteria_layout = QVBoxLayout(self.criteria_tab); criteria_layout.setContentsMargins(5, 5, 5, 5)
        self.criteria_text = QTextEdit(); self.criteria_text.setReadOnly(True); self.criteria_text.setFont(QFont("Segoe UI", 10))
        criteria_layout.addWidget(self.criteria_text)

        # -- Crop Summary Tab --
        self.crop_summary_tab = QWidget(); crop_summary_layout = QVBoxLayout(self.crop_summary_tab); crop_summary_layout.setContentsMargins(5, 5, 5, 5)
        self.crop_summary_text = QTextEdit(); self.crop_summary_text.setReadOnly(True); self.crop_summary_text.setFont(QFont("Segoe UI", 9))
        crop_summary_layout.addWidget(self.crop_summary_text)

        # Add tabs to widget
        self.tab_widget.addTab(self.guide_tab, "Vaiheittainen ohje");
        self.tab_widget.addTab(self.criteria_tab, "Optimointikriteerit")
        self.tab_widget.addTab(self.crop_summary_tab, "Crop Yhteenveto") # New Tab

        main_layout.addWidget(self.tab_widget, 1) # Make tab widget stretch

        self._setup_oar_completer()
        self.update_generate_button_state(); self.update_delete_button_state()
        self._update_oar_table_widget()

    def _setup_oar_completer(self):
        """Sets up the autocompleter for the OAR input field."""
        self.oar_completer_model = QStringListModel(COMMON_OARS, self)
        self.oar_completer = QCompleter(self.oar_completer_model, self)
        self.oar_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.oar_completer.setCompletionMode(QCompleter.PopupCompletion)
        self.oar_input.setCompleter(self.oar_completer)
        # Connect activated signal to add_oar when an item is selected from completer
        self.oar_completer.activated.connect(self._add_oar_from_completer)


    def _add_oar_from_completer(self, text):
        """Adds the OAR selected from the completer list."""
        self.oar_input.setText(text) # Set the text in the input field
        self.add_oar() # Call the regular add_oar function

    def add_dose(self):
        """Adds a dose value from the input field to the list."""
        dose_text = self.dose_input.text().strip().replace(',', '.')
        if not dose_text: return
        try:
            dose = float(dose_text)
            if dose <= 0: QMessageBox.warning(self, "Virheellinen annos", "Annostason tulee olla positiivinen luku."); return
            if dose in self.ptv_doses_list: QMessageBox.warning(self, "Annos jo lisätty", f"Annos {format_dose(dose)} Gy on jo listalla."); return
            self.ptv_doses_list.append(dose); self.ptv_doses_list.sort(reverse=True)
            self.update_dose_list_widget(); self.dose_input.clear()
            self._update_oar_table_widget() # Update OAR table in case overlap config needs refresh
        except ValueError: QMessageBox.warning(self, "Virheellinen syöte", f"'{dose_text}' ei ole kelvollinen numero.")
        self.update_generate_button_state(); self.clear_output()

    def remove_selected_dose_button_clicked(self):
        """Removes the selected dose from the list and updates related data."""
        selected_items = self.dose_list_widget.selectedItems()
        if not selected_items: return
        removed = False
        for item in selected_items:
            try:
                dose_to_remove_str = item.text().replace(" Gy", "").replace(",", ".")
                dose_to_remove = float(dose_to_remove_str)

                if dose_to_remove in self.ptv_doses_list:
                    self.ptv_doses_list.remove(dose_to_remove)
                    # Also remove this dose from any OAR overlap configurations
                    for oar_data_item in self.oars_data:
                        if dose_to_remove in oar_data_item.get('overlap_with_ptv_doses', []):
                            oar_data_item['overlap_with_ptv_doses'].remove(dose_to_remove)
                    removed = True
            except ValueError:
                QMessageBox.critical(self, "Virhe", f"Annosta '{item.text()}' poistaessa tapahtui muunnasvirhe.")
            except Exception as e:
                QMessageBox.critical(self, "Virhe", f"Annosta poistaessa tapahtui virhe: {e}")
        if removed:
            self.update_dose_list_widget(); self.update_generate_button_state()
            self._update_oar_table_widget() # Update OAR table to reflect removed dose possibility
            self.clear_output(); self.update_delete_button_state()

    def update_dose_list_widget(self):
        """Updates the QListWidget displaying PTV doses."""
        self.dose_list_widget.clear()
        for dose in sorted(self.ptv_doses_list, reverse=True): self.dose_list_widget.addItem(f"{format_dose(dose)} Gy")

    def update_generate_button_state(self):
        """Enables/disables the generate button based on whether doses exist."""
        if hasattr(self, 'generate_button'): # Check if UI element exists
            self.generate_button.setEnabled(len(self.ptv_doses_list) > 0)

    def update_delete_button_state(self):
        """Enables/disables the delete dose button based on selection."""
        if hasattr(self, 'delete_dose_button'): # Check if UI element exists
            self.delete_dose_button.setEnabled(len(self.dose_list_widget.selectedItems()) > 0)

    def add_oar(self):
        """Adds an OAR name from the input field to the list."""
        oar_name = self.oar_input.text().strip()
        if not oar_name:
            # Don't show warning if triggered by completer selection of empty string (unlikely)
            # QMessageBox.warning(self, "Tyhjä OAR", "Anna OAR:lle nimi.")
            return
        if any(o['name'] == oar_name for o in self.oars_data):
            QMessageBox.warning(self, "OAR jo lisätty", f"OAR '{oar_name}' on jo listalla.")
            # Clear input even if duplicate to allow selecting another from completer
            self.oar_input.clear()
            return

        self.oars_data.append({'name': oar_name, 'overlap_with_ptv_doses': []}) # Initialize with empty overlap list
        # Sort OAR data list alphabetically by name for consistent table order
        self.oars_data.sort(key=lambda item: item['name'])
        self._update_oar_table_widget()
        self.oar_input.clear()
        self.clear_output() # Clear generated output as inputs changed

    def _remove_oar_at_row(self, row):
        """Removes the OAR at the specified table row."""
        # Need to map the visible row index back to the actual data index if sorting is applied dynamically
        # For now, assuming self.oars_data is kept sorted and row index corresponds directly
        if 0 <= row < len(self.oars_data):
            del self.oars_data[row]
            # No need to re-sort here as deletion maintains order
            self._update_oar_table_widget()
            self.clear_output() # Clear generated output

    def _configure_oar_ptv_overlaps(self, oar_row_index):
        """Opens a dialog to configure which PTVs overlap with a specific OAR."""
         # Assuming self.oars_data is sorted, oar_row_index directly maps
        if not (0 <= oar_row_index < len(self.oars_data)):
            print(f"Error: Invalid OAR row index {oar_row_index}") # Debug print
            return

        oar_item = self.oars_data[oar_row_index]
        oar_name = oar_item['name']
        initially_selected = oar_item.get('overlap_with_ptv_doses', [])

        if not self.ptv_doses_list:
            QMessageBox.information(self, "Ei PTV-annoksia", "Syötä ensin PTV-annoksia, jotta voit määrittää päällekkäisyydet.")
            return

        dialog = OarPtvOverlapDialog(oar_name, self.ptv_doses_list, initially_selected, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_doses_for_overlap = dialog.get_selected_ptv_doses()
            # Update the specific item in the already sorted list
            self.oars_data[oar_row_index]['overlap_with_ptv_doses'] = selected_doses_for_overlap
            self._update_oar_table_widget() # Update table display
            self.clear_output() # Clear generated output as configuration changed

    def _update_oar_table_widget(self):
        """Updates the QTableWidget displaying OARs and their configurations."""
        self.oar_table_widget.setSortingEnabled(False) # Disable sorting during update
        self.oar_table_widget.setRowCount(0) # Clear existing rows
        self.oar_table_widget.setRowCount(len(self.oars_data))

        # Populate rows based on the sorted self.oars_data
        for i, oar_item in enumerate(self.oars_data):
            # OAR Name Column (Read-only)
            name_item = QTableWidgetItem(oar_item['name'])
            name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable) # Make non-editable
            self.oar_table_widget.setItem(i, 0, name_item)

            # Overlap Configuration Column (Button + Label)
            overlap_cell_widget = QWidget()
            overlap_layout = QHBoxLayout(overlap_cell_widget)
            overlap_layout.setContentsMargins(2,0,2,0); overlap_layout.setSpacing(4)

            btn_configure = QPushButton("Määritä...")
            btn_configure.setObjectName("ConfigureOARButton")
            btn_configure.setToolTip(f"Määritä PTV-päällekkäisyydet OAR:lle {oar_item['name']}")
            # Use partial to pass the current row index 'i' which corresponds to the sorted list
            # TÄMÄ ON KOHTA, JOSSA partial TARVITAAN
            btn_configure.clicked.connect(partial(self._configure_oar_ptv_overlaps, oar_row_index=i))
            overlap_layout.addWidget(btn_configure)

            # Display selected PTV doses concisely
            selected_doses = oar_item.get('overlap_with_ptv_doses', [])
            if not selected_doses:
                selected_doses_str = "Ei valittu"
            else:
                 # Sort doses numerically before formatting
                selected_doses_str = ", ".join([format_dose(d) for d in sorted(selected_doses, reverse=True)])

            # Truncate if too long
            max_len = 25
            if len(selected_doses_str) > max_len:
                 num_selected = len(selected_doses)
                 selected_doses_str = f"{num_selected} PTV:tä valittu"

            lbl_selected_ptvs = QLabel(selected_doses_str)
            lbl_selected_ptvs.setStyleSheet("font-size: 8pt; color: #555; margin-left: 3px;") # Small text, gray color
            overlap_layout.addWidget(lbl_selected_ptvs)
            overlap_layout.addStretch() # Push content left

            self.oar_table_widget.setCellWidget(i, 1, overlap_cell_widget)

            # Delete Button Column
            btn_delete_oar = QPushButton("Poista")
            btn_delete_oar.setObjectName("DeleteOARButton") # For specific styling
            # Use partial to pass the current row index 'i'
            # TÄMÄ ON TOINEN KOHTA, JOSSA partial TARVITAAN
            btn_delete_oar.clicked.connect(partial(self._remove_oar_at_row, row=i))
            # Center the button in the cell
            delete_button_widget = QWidget()
            delete_button_layout = QHBoxLayout(delete_button_widget)
            delete_button_layout.addWidget(btn_delete_oar)
            delete_button_layout.setAlignment(Qt.AlignCenter)
            delete_button_layout.setContentsMargins(0,0,0,0)
            self.oar_table_widget.setCellWidget(i, 2, delete_button_widget)

        self.oar_table_widget.resizeRowsToContents()
        # Adjust column widths after populating
        self.oar_table_widget.resizeColumnsToContents()
        self.oar_table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) # Let name stretch
        self.oar_table_widget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents) # Resize overlap col
        self.oar_table_widget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents) # Resize action col
        # self.oar_table_widget.setSortingEnabled(True) # Re-enable sorting if desired


    def clear_output(self):
        """Clears all generated output (steps, criteria, summary, search)."""
        # Clear step widgets
        if hasattr(self, 'steps_layout'):
             # Remove previous highlight if any
            if self.highlighted_widget:
                self.highlighted_widget.set_highlighted(False)
                self.highlighted_widget = None
            self.current_search_index = -1

            while self.steps_layout.count() > 1: # Keep the stretch item at the end
                item = self.steps_layout.takeAt(0); widget = item.widget()
                if widget: widget.deleteLater() # Delete the widget properly
        self.step_widgets = []; self.total_steps = 0; self.completed_steps = 0
        self.update_progress_label()

        # Clear criteria text
        if hasattr(self, 'criteria_text'):
            self.criteria_text.clear()

        # Clear crop summary text
        if hasattr(self, 'crop_summary_text'):
            self.crop_summary_text.clear()
        self.crop_summary_data = {}

        # Clear search field and disable buttons
        if hasattr(self, 'search_input'):
            # Check if search input exists before clearing
             if self.search_input:
                self.search_input.clear() # This will trigger _on_search_text_changed
        if hasattr(self, 'find_next_button'):
             self.find_next_button.setEnabled(False)
        if hasattr(self, 'find_prev_button'):
             self.find_prev_button.setEnabled(False)


    def generate_output(self):
        """Generates the guide steps, criteria, and summary based on inputs."""
        if not self.ptv_doses_list:
            QMessageBox.warning(self, "Ei annoksia", "Syötä vähintään yksi PTV-annos.")
            return

        # Check essential UI elements exist before proceeding
        required_attrs = ['niska_checkbox', 'steps_layout', 'criteria_text', 'crop_summary_text', 'tab_widget',
                          'ring_radio_ring', 'ring_radio_nt', 'dptv_oar_crop_05mm', 'dptv_oar_crop_10mm']
        for attr in required_attrs:
            if not hasattr(self, attr):
                QMessageBox.critical(self, "UI Virhe", f"Tarvittavaa UI-elementtiä '{attr}' ei ole alustettu.")
                return

        self.clear_output() # Clear previous results first

        # --- Get Inputs ---
        sorted_doses = sorted(self.ptv_doses_list, reverse=True)
        create_niska = self.niska_checkbox.isChecked()
        # Use the already sorted oars_data list
        current_oars_data = list(self.oars_data) # Use a copy

        # Get selected Ring prefix
        selected_ring_prefix = "Ring" # Default
        if self.ring_radio_nt.isChecked():
            selected_ring_prefix = "NT"

        # Get selected dPTV+OAR crop margin
        selected_dptv_oar_crop_margin_cm = 0.05 # Default 0.5 mm
        if self.dptv_oar_crop_10mm.isChecked():
            selected_dptv_oar_crop_margin_cm = 0.1 # 1.0 mm

        # --- Pre-calculate Crops (same logic as before) ---
        calculated_crops = {}; final_names = {}
        v = "v"; ptv_prefix_raw = f"{v}PTV"; ctv_prefix_raw = f"{v}CTV"; crop_suffix_raw = "crop"
        try:
            # Calculate PTV-vs-PTV crops
            final_names[sorted_doses[0]] = (f"{ptv_prefix_raw}{format_dose(sorted_doses[0])}", f"{ctv_prefix_raw}{format_dose(sorted_doses[0])}")
            if len(sorted_doses) >= 2:
                for j in range(1, len(sorted_doses)):
                    lower_dose = sorted_doses[j]; lower_dose_str = format_dose(lower_dose)
                    final_ptv_name_raw = f"{ptv_prefix_raw}{lower_dose_str}{crop_suffix_raw}"; final_ctv_name_raw = f"{ctv_prefix_raw}{lower_dose_str}{crop_suffix_raw}"
                    final_names[lower_dose] = (final_ptv_name_raw, final_ctv_name_raw)
                    for i in range(j):
                        higher_dose_i = sorted_doses[i]; crop_key = (higher_dose_i, lower_dose)
                        if crop_key not in calculated_crops: calculated_crops[crop_key] = {}
                        calculated_crops[crop_key]['PTV'] = calculate_ptv_crop(higher_dose_i, lower_dose)

            # --- Generate Content ---
            QApplication.setOverrideCursor(Qt.WaitCursor)

            # Generate Guide Steps and Crop Summary Data
            # HUOM: generate_guide_steps sisältää nyt esimerkkejä lyhennetyistä ohjeista.
            # Voit poistaa kommentit alkuperäisten pidempien ohjeiden ympäriltä, jos haluat ne takaisin.
            guide_step_data, self.crop_summary_data = generate_guide_steps(
                sorted_doses, calculated_crops, create_niska, current_oars_data,
                selected_ring_prefix, selected_dptv_oar_crop_margin_cm # Pass new options
            )
            self.total_steps = len(guide_step_data)

            # Populate Guide Tab
            for i, step_data in enumerate(guide_step_data):
                step_widget = StepWidget(
                    step_id=step_data.get("id", i+1), title=step_data.get("title", "Nimetön vaihe"),
                    details_html=step_data.get("details_html", "<p>Ei ohjeita.</p>"), emoji=step_data.get("emoji", "•"),
                    is_alt_row=(i % 2 == 1) )

                # Insert before the stretch item
                if self.steps_layout.count() > 0:
                    self.steps_layout.insertWidget(self.steps_layout.count() - 1, step_widget)
                else: # Should not happen if stretch item is always there
                     self.steps_layout.addWidget(step_widget)

                self.step_widgets.append(step_widget)
                step_widget.completionChanged.connect(self.update_progress)

            # Generate Optimization Criteria HTML
            criteria_html_output = generate_optimization_criteria_html(
                sorted_doses, final_names, create_niska, current_oars_data,
                selected_ring_prefix # Pass new option
            )
            self.criteria_text.setHtml(criteria_html_output)

            # Generate and Populate Crop Summary Tab
            self._generate_and_display_crop_summary()

            # --- Final UI Updates ---
            self.tab_widget.setCurrentIndex(0) # Switch to guide tab
            self.update_progress_label()
            QApplication.restoreOverrideCursor()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "Generointivirhe", f"Virhe generoinnissa:\n{e}\n\nTarkista syötteet ja OAR-määritykset.")
            import traceback
            traceback.print_exc(file=sys.stderr)
            self.clear_output() # Clear partial results on error

    def _generate_and_display_crop_summary(self):
        """Formats the collected crop data into HTML and displays it."""
        if not self.crop_summary_data:
            self.crop_summary_text.setHtml("<p><i>Ei croppeja generoitu tai dataa ei löytynyt.</i></p>")
            return

        summary_html = []
        summary_html.append(f"""
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; font-size: 9pt; }}
            h3 {{ color: {COLOR_TITLE}; margin-bottom: 10px; font-size: 12pt;}}
            table {{ width: 100%; border-collapse: collapse; margin-top: 5px; }}
            th {{ background-color: #f0f0f0; border: 1px solid #d0d0d0; padding: 5px; text-align: left; font-weight: bold; }}
            td {{ border: 1px solid #e0e0e0; padding: 4px 5px; vertical-align: top; }}
            td.step {{ font-weight: bold; text-align: right; width: 5%; }}
            td.margin {{ font-weight: bold; color: {COLOR_VALUE}; text-align: right; width: 15%; }}
            td.desc {{ width: 80%; }}
        </style>""")
        summary_html.append("<h3>Generoidut Crop-marginaalit</h3>")
        summary_html.append("<table>")
        summary_html.append("<tr><th>Vaihe</th><th>Kuvaus</th><th>Marginaali (cm)</th></tr>")

        # Sort by step number (which are the keys)
        for step_id in sorted(self.crop_summary_data.keys()):
            data = self.crop_summary_data[step_id]
            description = data.get("text", "N/A")
            margin_cm = data.get("margin_cm", "N/A")
            margin_str = f"{margin_cm:.2f}" if isinstance(margin_cm, (int, float)) else str(margin_cm)

            summary_html.append(f"<tr><td class='step'>{step_id}</td><td class='desc'>{description}</td><td class='margin'>{margin_str}</td></tr>")

        summary_html.append("</table>")
        self.crop_summary_text.setHtml("\n".join(summary_html))


    def update_progress(self, is_complete):
        """Updates the count of completed steps."""
        self.completed_steps = sum(1 for widget in self.step_widgets if widget.is_complete)
        self.update_progress_label()

    def update_progress_label(self):
        """Updates the progress label text."""
        if hasattr(self, 'progress_label'):
            self.progress_label.setText(f"Vaiheet: {self.completed_steps} / {self.total_steps}")

    # --- Search Functionality ---
    def _on_search_text_changed(self, text):
        """Called when text in the search input changes."""
        search_term = text.strip()
        has_term = bool(search_term)

        # Enable/disable buttons only if they exist
        if hasattr(self, 'find_next_button'):
            self.find_next_button.setEnabled(has_term and len(self.step_widgets) > 0)
        if hasattr(self, 'find_prev_button'):
            self.find_prev_button.setEnabled(has_term and len(self.step_widgets) > 0)

        # If search term is cleared, remove highlight
        if not has_term and self.highlighted_widget:
            self.highlighted_widget.set_highlighted(False)
            self.highlighted_widget = None
            self.current_search_index = -1

        # Reset search index if term changes
        if search_term != self.last_search_term:
             self.current_search_index = -1
             if self.highlighted_widget:
                 self.highlighted_widget.set_highlighted(False)
                 self.highlighted_widget = None
        self.last_search_term = search_term


    def _clear_search(self):
        """Clears the search input and removes highlights."""
        if hasattr(self, 'search_input') and self.search_input:
            self.search_input.clear() # This triggers _on_search_text_changed

    def _find_next(self):
        """Finds the next occurrence of the search term."""
        self._find_search_term(direction=1)

    def _find_previous(self):
        """Finds the previous occurrence of the search term."""
        self._find_search_term(direction=-1)

    def _find_search_term(self, direction):
        """Searches for the term in the specified direction."""
        if not hasattr(self, 'search_input') or not self.search_input:
             return # Safety check
        search_term = self.search_input.text().strip()
        if not search_term or not self.step_widgets:
            # Maybe provide feedback if search term is empty but button was clicked?
            # Or just return silently as buttons should be disabled.
            return

        num_widgets = len(self.step_widgets)
        start_index = self.current_search_index

        # Remove highlight from the previous match
        if self.highlighted_widget:
            self.highlighted_widget.set_highlighted(False)
            self.highlighted_widget = None

        found = False
        for i in range(num_widgets):
            # Calculate next index with wrap-around
            check_index = (start_index + (i * direction) + direction) % num_widgets

            widget = self.step_widgets[check_index]
            if widget.contains_text(search_term):
                # Found a match
                self.current_search_index = check_index
                if hasattr(self, 'scroll_area') and self.scroll_area: # Check scroll_area exists
                    self.scroll_area.ensureWidgetVisible(widget, yMargin=50) # Scroll to widget with margin
                widget.set_highlighted(True) # Highlight the found widget
                self.highlighted_widget = widget
                found = True
                break # Stop searching

        # If loop completes without finding a new match (and didn't find one this time)
        if not found:
            QMessageBox.information(self, "Etsi", f"Tekstiä '{search_term}' ei löytynyt enempää.")
            self.current_search_index = -1 # Reset index if no further matches


# --- Pääohjelma ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Force the style to be consistent, e.g., Fusion
    # app.setStyle("Fusion") # Uncomment if needed for cross-platform consistency
    ex = EclipseHelperApp()
    ex.show()
    sys.exit(app.exec_())