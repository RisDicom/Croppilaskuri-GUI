"""Main application window – orchestrates panels, tabs, and generation."""

from __future__ import annotations

import datetime
import sys
import traceback
from typing import Any

from PyQt5.QtCore import QSize, Qt, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from croppilaskuri.config.constants import (
    APP_VERSION,
    COLOR_TITLE,
    COLOR_VALUE,
    CROP_SUFFIX,
    DEFAULT_DPTV_OAR_CROP_CM,
    DEFAULT_RING_PREFIX,
    EMOJI_INFO,
    EMOJI_SEARCH,
    V_PREFIX,
)
from croppilaskuri.core.calculations import calculate_ptv_crop, format_dose
from croppilaskuri.core.guide_logic import generate_guide_steps
from croppilaskuri.core.optimization_criteria import generate_optimization_criteria_html
from croppilaskuri.core.types import OarEntry, PlanType
from croppilaskuri.ui.panels.dose_panel import DoseInputPanel
from croppilaskuri.ui.panels.oar_panel import OarInputPanel
from croppilaskuri.ui.styles import get_global_stylesheet
from croppilaskuri.ui.widgets.step_widget import StepWidget


class MainWindow(QWidget):
    """Top-level window for the Eclipse Contouring Helper application."""

    def __init__(self) -> None:
        super().__init__()
        self._step_widgets: list[StepWidget] = []
        self._total_steps = 0
        self._completed_steps = 0
        self._crop_summary: dict[int, dict[str, Any]] = {}
        self._current_search_idx = -1
        self._last_search_term = ""
        self._highlighted_widget: StepWidget | None = None

        self._init_ui()
        self.setStyleSheet(get_global_stylesheet())

    # ═══════════════════════════════════════════════════════════════
    # Properties
    # ═══════════════════════════════════════════════════════════════

    @property
    def selected_plan_type(self) -> PlanType:
        """Return the currently selected plan type."""
        idx = self._plan_type_combo.currentIndex()
        return list(PlanType)[idx]

    # ═══════════════════════════════════════════════════════════════
    # UI Construction
    # ═══════════════════════════════════════════════════════════════

    def _init_ui(self) -> None:
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.setWindowTitle(f"Eclipse Contouring Helper {APP_VERSION} ({today})")
        self.setGeometry(30, 30, 1300, 900)

        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        # ── Top grid: dose + OAR + options + generate ────────────
        grid = QGridLayout()
        grid.setSpacing(10)

        self._dose_panel = DoseInputPanel()
        self._dose_panel.dosesChanged.connect(self._on_doses_changed)
        grid.addWidget(self._dose_panel, 0, 0)

        self._oar_panel = OarInputPanel()
        self._oar_panel.oarsChanged.connect(self._clear_output)
        grid.addWidget(self._oar_panel, 0, 1)

        # Options
        opt_frame = QFrame()
        opt_frame.setObjectName("OptionsGroup")
        opt_frame.setFrameShape(QFrame.StyledPanel)
        opt_lo = QVBoxLayout(opt_frame)
        opt_lo.setContentsMargins(10, 8, 10, 8)
        opt_lo.setSpacing(8)
        opt_lo.addWidget(QLabel("<b>3. Muut valinnat:</b>"))

        # ── Plan type selector ───────────────────────────────────
        plan_row = QHBoxLayout()
        plan_row.addWidget(QLabel("Suunnitelmatyyppi:"))
        self._plan_type_combo = QComboBox()
        for pt in PlanType:
            self._plan_type_combo.addItem(pt.label_fi)
        self._plan_type_combo.setCurrentIndex(0)
        self._plan_type_combo.currentIndexChanged.connect(self._on_plan_type_changed)
        plan_row.addWidget(self._plan_type_combo, 1)
        opt_lo.addLayout(plan_row)

        # ── Palliative info label (hidden by default) ────────────
        self._palliative_info = QLabel(
            "<i style='color:#1565c0;'>Palliatiivisessa suunnitelmassa "
            "OAR-päällekkäisyydet eivät ole käytössä.</i>"
        )
        self._palliative_info.setWordWrap(True)
        self._palliative_info.setVisible(False)
        opt_lo.addWidget(self._palliative_info)

        self._niska_cb = QCheckBox("Luo vNiska?")
        self._niska_cb.setToolTip("Luo vNiska-rakenteen (vaatii SpinalCord).")
        opt_lo.addWidget(self._niska_cb)
        opt_lo.addStretch(1)
        grid.addWidget(opt_frame, 1, 0)

        # Generate button
        gen_container = QWidget()
        gen_lo = QVBoxLayout(gen_container)
        gen_lo.setContentsMargins(0, 0, 0, 0)
        self._gen_btn = QPushButton("Generoi Ohjeet")
        self._gen_btn.setObjectName("GenerateButton")
        self._gen_btn.setIconSize(QSize(18, 18))
        self._gen_btn.setEnabled(False)
        self._gen_btn.clicked.connect(self._generate_output)
        gen_lo.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        gen_lo.addWidget(self._gen_btn)
        gen_lo.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding))
        grid.addWidget(gen_container, 1, 1, Qt.AlignVCenter | Qt.AlignHCenter)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowMinimumHeight(0, 200)
        grid.setRowMinimumHeight(1, 150)
        root.addLayout(grid)

        # ── Tabs ─────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_guide_tab(), "Vaiheittainen ohje")
        self._tabs.addTab(self._build_criteria_tab(), "Optimointikriteerit")
        self._tabs.addTab(self._build_crop_summary_tab(), "Crop Yhteenveto")
        root.addWidget(self._tabs, 1)

    def _build_guide_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        # Search bar
        search_row = QHBoxLayout()
        search_row.setContentsMargins(5, 0, 5, 0)
        icon = QLabel(EMOJI_SEARCH)
        icon.setStyleSheet("font-size: 12pt;")
        self._search_input = QLineEdit()
        self._search_input.setObjectName("SearchLineEdit")
        self._search_input.setPlaceholderText("Etsi ohjeista...")
        self._search_input.textChanged.connect(self._on_search_text_changed)
        self._search_input.returnPressed.connect(self._find_next)

        self._find_next_btn = QPushButton("Seuraava")
        self._find_next_btn.setObjectName("FindNextButton")
        self._find_next_btn.setEnabled(False)
        self._find_next_btn.clicked.connect(self._find_next)

        self._find_prev_btn = QPushButton("Edellinen")
        self._find_prev_btn.setObjectName("FindPrevButton")
        self._find_prev_btn.setEnabled(False)
        self._find_prev_btn.clicked.connect(self._find_previous)

        clear_btn = QPushButton("Tyhjennä")
        clear_btn.setObjectName("ClearSearchButton")
        clear_btn.clicked.connect(self._search_input.clear)

        search_row.addWidget(icon)
        search_row.addWidget(self._search_input, 1)
        search_row.addWidget(self._find_prev_btn)
        search_row.addWidget(self._find_next_btn)
        search_row.addWidget(clear_btn)
        layout.addLayout(search_row)

        # Progress label
        prog_row = QHBoxLayout()
        prog_row.setContentsMargins(5, 0, 5, 0)
        prog_row.addStretch(1)
        self._progress_label = QLabel("Vaiheet: 0 / 0")
        self._progress_label.setFont(QFont("Segoe UI", 9))
        self._progress_label.setStyleSheet("QLabel{margin-right:5px; color:#555;}")
        prog_row.addWidget(self._progress_label)
        layout.addLayout(prog_row)

        # Scrollable step area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.NoFrame)

        self._scroll_widget = QWidget()
        self._scroll_widget.setObjectName("ScrollWidget")
        self._steps_layout = QVBoxLayout(self._scroll_widget)
        self._steps_layout.setContentsMargins(5, 5, 10, 5)
        self._steps_layout.setSpacing(0)
        self._steps_layout.addStretch(1)

        self._scroll.setWidget(self._scroll_widget)
        layout.addWidget(self._scroll, 1)
        return tab

    def _build_criteria_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        self._criteria_text = QTextEdit()
        self._criteria_text.setReadOnly(True)
        self._criteria_text.setFont(QFont("Segoe UI", 10))
        layout.addWidget(self._criteria_text)
        return tab

    def _build_crop_summary_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(5, 5, 5, 5)
        self._crop_text = QTextEdit()
        self._crop_text.setReadOnly(True)
        self._crop_text.setFont(QFont("Segoe UI", 9))
        layout.addWidget(self._crop_text)
        return tab

    # ═══════════════════════════════════════════════════════════════
    # Event Handlers
    # ═══════════════════════════════════════════════════════════════

    def _on_plan_type_changed(self, _index: int) -> None:
        """React to plan type combo changes."""
        is_palliative = self.selected_plan_type == PlanType.PALLIATIVE
        self._oar_panel.set_overlaps_enabled(not is_palliative)
        self._palliative_info.setVisible(is_palliative)
        self._clear_output()

    def _on_doses_changed(self) -> None:
        """React to additions/removals in the dose panel."""
        doses = self._dose_panel.doses
        self._gen_btn.setEnabled(len(doses) > 0)
        self._oar_panel.set_available_doses(doses)
        self._oar_panel.refresh_table()
        self._clear_output()

    def _clear_output(self) -> None:
        """Reset all generated output."""
        if self._highlighted_widget:
            self._highlighted_widget.set_highlighted(False)
            self._highlighted_widget = None
        self._current_search_idx = -1

        for w in self._step_widgets:
            w.deleteLater()
        self._step_widgets.clear()

        # Remove everything from the steps layout
        while self._steps_layout.count():
            child = self._steps_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self._steps_layout.addStretch(1)

        self._total_steps = 0
        self._completed_steps = 0
        self._update_progress_label()
        self._criteria_text.clear()
        self._crop_text.clear()
        self._crop_summary = {}
        self._search_input.clear()
        self._find_next_btn.setEnabled(False)
        self._find_prev_btn.setEnabled(False)

    # ═══════════════════════════════════════════════════════════════
    # Generation
    # ═══════════════════════════════════════════════════════════════

    def _generate_output(self) -> None:
        """Run the full generation pipeline: guide + criteria + summary."""
        doses = self._dose_panel.doses
        if not doses:
            QMessageBox.warning(self, "Ei annoksia", "Syötä vähintään yksi PTV-annos.")
            return

        self._clear_output()
        sorted_doses = sorted(doses, reverse=True)
        create_niska = self._niska_cb.isChecked()
        plan_type = self.selected_plan_type

        # For palliative plans, pass empty OAR overlap data
        oars: list[OarEntry] = self._oar_panel.oars_data  # type: ignore[assignment]
        if plan_type == PlanType.PALLIATIVE:
            for oar in oars:
                oar["overlap_with_ptv_doses"] = []

        # Pre-compute crops and final structure names
        calculated_crops: dict[tuple[float, float], dict[str, float]] = {}
        final_names: dict[float, tuple[str, str]] = {}
        ptv_base = f"{V_PREFIX}PTV"
        ctv_base = f"{V_PREFIX}CTV"

        if sorted_doses:
            hd = sorted_doses[0]
            final_names[hd] = (f"{ptv_base}{format_dose(hd)}", f"{ctv_base}{format_dose(hd)}")
            for j in range(1, len(sorted_doses)):
                ld = sorted_doses[j]
                ld_str = format_dose(ld)
                final_names[ld] = (
                    f"{ptv_base}{ld_str}{CROP_SUFFIX}",
                    f"{ctv_base}{ld_str}{CROP_SUFFIX}",
                )
                for i in range(j):
                    hd_i = sorted_doses[i]
                    key = (hd_i, ld)
                    if key not in calculated_crops:
                        calculated_crops[key] = {}
                    calculated_crops[key]["PTV"] = calculate_ptv_crop(hd_i, ld)

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            guide_data, self._crop_summary = generate_guide_steps(
                sorted_doses,
                calculated_crops,
                create_niska,
                oars,
                DEFAULT_RING_PREFIX,
                DEFAULT_DPTV_OAR_CROP_CM,
            )
            self._populate_guide_steps(guide_data)

            criteria_html = generate_optimization_criteria_html(
                sorted_doses,
                final_names,
                create_niska,
                oars,
                DEFAULT_RING_PREFIX,
                plan_type=plan_type,
            )
            self._criteria_text.setHtml(criteria_html)
            self._render_crop_summary()
            self._tabs.setCurrentIndex(0)
            self._update_progress_label()

        except NotImplementedError as exc:
            QMessageBox.information(
                self,
                "Ei vielä toteutettu",
                f"{exc}\n\nKopioi alkuperäisen koodin logiikka uuteen moduulirakenteeseen.",
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Generointivirhe",
                f"Ohjeiden generoinnissa tapahtui virhe:\n{exc}\n\n"
                "Tarkista syötteet ja yritä uudelleen.",
            )
            traceback.print_exc(file=sys.stderr)
            self._clear_output()
        finally:
            QApplication.restoreOverrideCursor()

    def _populate_guide_steps(self, guide_data: list[dict[str, Any]]) -> None:
        """Create StepWidgets from the generated guide data."""
        temp_total = 0
        for i, step in enumerate(guide_data):
            widget = StepWidget(
                step.get("id"),
                step.get("title", "Nimetön vaihe"),
                step.get("details_html", "<p>Ei tarkempia ohjeita.</p>"),
                step.get("emoji", EMOJI_INFO),
                is_alt_row=(i % 2 == 1),
            )
            if "toc_anchor_target_id" in step:
                widget.toc_anchor_target_id = step["toc_anchor_target_id"]

            if step.get("id") == 0:
                # Table-of-contents step: no checkbox, handle anchor links
                widget.checkbox.setVisible(False)
                widget.details_label.setOpenExternalLinks(False)
                widget.details_label.linkActivated.connect(self._handle_toc_link)
            else:
                widget.completionChanged.connect(self._on_step_completion_changed)
                temp_total += 1

            # Insert before the trailing stretch
            idx = max(0, self._steps_layout.count() - 1)
            self._steps_layout.insertWidget(idx, widget)
            self._step_widgets.append(widget)

        self._total_steps = temp_total
        self._completed_steps = 0

    # ═══════════════════════════════════════════════════════════════
    # TOC Navigation
    # ═══════════════════════════════════════════════════════════════

    def _handle_toc_link(self, link: str) -> None:
        """Scroll to the step targeted by a table-of-contents anchor."""
        fragment = QUrl(link).fragment()
        if not fragment:
            return
        for widget in self._step_widgets:
            if getattr(widget, "toc_anchor_target_id", None) == fragment:
                self._scroll.ensureWidgetVisible(widget, 0, 20)
                break

    # ═══════════════════════════════════════════════════════════════
    # Progress Tracking
    # ═══════════════════════════════════════════════════════════════

    def _on_step_completion_changed(self, _is_complete: bool) -> None:
        self._completed_steps = sum(
            1
            for w in self._step_widgets
            if w.is_complete and w.checkbox.isVisible() and w.step_id != 0
        )
        self._update_progress_label()

    def _update_progress_label(self) -> None:
        self._progress_label.setText(f"Vaiheet: {self._completed_steps} / {self._total_steps}")

    # ═══════════════════════════════════════════════════════════════
    # Search
    # ═══════════════════════════════════════════════════════════════

    def _on_search_text_changed(self, text: str) -> None:
        term = text.strip()
        has_widgets = len(self._step_widgets) > 0
        self._find_next_btn.setEnabled(bool(term) and has_widgets)
        self._find_prev_btn.setEnabled(bool(term) and has_widgets)

        if not term and self._highlighted_widget:
            self._highlighted_widget.set_highlighted(False)
            self._highlighted_widget = None

        if term != self._last_search_term:
            self._current_search_idx = -1
            if self._highlighted_widget:
                self._highlighted_widget.set_highlighted(False)
                self._highlighted_widget = None
        self._last_search_term = term

    def _find_next(self) -> None:
        self._find_step(direction=1)

    def _find_previous(self) -> None:
        self._find_step(direction=-1)

    def _find_step(self, direction: int) -> None:
        term = self._search_input.text().strip().lower()
        if not term or not self._step_widgets:
            return

        searchable = [w for w in self._step_widgets if w.step_id != 0]
        if not searchable:
            return
        n = len(searchable)

        start = -1
        if self._highlighted_widget and self._highlighted_widget in searchable:
            start = searchable.index(self._highlighted_widget)

        if self._highlighted_widget:
            self._highlighted_widget.set_highlighted(False)
            self._highlighted_widget = None

        for i in range(n):
            idx = (start + (i * direction) + direction) % n
            widget = searchable[idx]
            if widget.contains_text(term):
                self._scroll.ensureWidgetVisible(widget, 0, 50)
                widget.set_highlighted(True)
                self._highlighted_widget = widget
                self._current_search_idx = idx
                return

        self._current_search_idx = -1
        if start == -1:
            QMessageBox.information(
                self,
                "Etsi",
                f"Tekstiä '{self._search_input.text().strip()}' ei löytynyt ohjeista.",
            )

    # ═══════════════════════════════════════════════════════════════
    # Crop Summary
    # ═══════════════════════════════════════════════════════════════

    def _render_crop_summary(self) -> None:
        if not self._crop_summary:
            self._crop_text.setHtml("<p><i>Ei crop-dataa saatavilla.</i></p>")
            return

        rows: list[str] = []
        for step_id in sorted(self._crop_summary):
            data = self._crop_summary[step_id]
            margin = data.get("margin_cm", "N/A")
            if isinstance(margin, (int, float)) and abs(margin) < 0.001:
                continue  # skip zero-margin entries
            margin_str = f"{margin:.2f}" if isinstance(margin, (int, float)) else str(margin)
            desc = data.get("text", "N/A")
            rows.append(
                f"<tr>"
                f"<td class='step'>{step_id}</td>"
                f"<td class='desc'>{desc}</td>"
                f"<td class='margin'>{margin_str}</td>"
                f"</tr>"
            )

        if not rows:
            self._crop_text.setHtml(
                "<p><i>Ei crop-marginaaleja näytettäväksi "
                "(kaikki olivat 0 cm tai dataa ei ollut).</i></p>"
            )
            return

        html = f"""<style>
            body {{ font-family:'Segoe UI'; font-size:9pt; }}
            h3 {{ color:{COLOR_TITLE}; }}
            table {{ width:100%; border-collapse:collapse; margin-top:5px; }}
            th {{ background-color:#f0f0f0; border:1px solid #d0d0d0;
                  padding:5px; text-align:left; font-weight:bold; }}
            td {{ border:1px solid #e0e0e0; padding:4px 5px; vertical-align:top; }}
            td.step {{ font-weight:bold; text-align:right; width:5%; }}
            td.margin {{ font-weight:bold; color:{COLOR_VALUE};
                         text-align:right; width:15%; }}
            td.desc {{ width:80%; }}
        </style>
        <h3>Generoidut Crop-marginaalit</h3>
        <table>
            <tr><th>Vaihe</th><th>Kuvaus</th><th>Marginaali (cm)</th></tr>
            {"".join(rows)}
        </table>"""
        self._crop_text.setHtml(html)
