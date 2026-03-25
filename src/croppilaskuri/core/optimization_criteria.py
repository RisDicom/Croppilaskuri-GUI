"""Optimization criteria HTML generator for Eclipse Contouring Helper.

Refactored to use ``PlanType`` enum and centralised ``PLAN_FACTORS``
instead of hard-coded multipliers.
"""

from __future__ import annotations

from croppilaskuri.config.constants import (
    COLOR_ACTION,
    COLOR_CODE,
    COLOR_INSTRUCTION,
    COLOR_NOTE,
    COLOR_TITLE,
    COLOR_VALUE,
)
from croppilaskuri.core.calculations import format_dose
from croppilaskuri.core.types import PLAN_FACTORS, OarEntry, PlanType
from croppilaskuri.utils.text import bold, code, note


def generate_optimization_criteria_html(
    ptv_doses: list[float],
    final_volume_names_main: dict[float, tuple[str, str]],
    create_vniska: bool,
    oars_data_list: list[OarEntry],
    ring_prefix: str,
    plan_type: PlanType = PlanType.STANDARD,
) -> str:
    """Generate HTML showing example optimization criteria.

    Parameters
    ----------
    plan_type:
        Selects which multiplier set to apply (standard vs palliative).
    """
    if not ptv_doses:
        return "<p><b>Ei PTV-annoksia syötetty kriteerien luontiin.</b></p>"

    factors = PLAN_FACTORS[plan_type]
    criteria_html: list[str] = []
    all_generated_ptv_lower_gy: list[float] = []
    all_generated_ptv_upper_gy: list[float] = []
    all_generated_ctv_lower_gy: list[float] = []
    all_generated_ctv_upper_gy: list[float] = []

    plan_label = plan_type.label_fi

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
        p.plan_badge {{ background-color: #e3f2fd; border: 1px solid #90caf9; border-radius: 4px; padding: 6px 10px; margin-bottom: 10px; font-weight: bold; color: #1565c0; }}
        ul.nto {{ margin-left: 15px; list-style-type: disc; }} li.nto {{ margin-bottom: 4px; }}
    </style>""")
    criteria_html.append("<h2>Optimointikriteerit (Esimerkkiarvot)</h2>")
    criteria_html.append(f"<p class='plan_badge'>Suunnitelmatyyppi: {plan_label}</p>")

    if plan_type == PlanType.STANDARD:
        criteria_html.append(
            f"<p class='warning'>HUOM: Optimointikertoimet PTV-rakenteille voivat vaihdella "
            f"annostasoittain riippuen siitä, onko kyseiselle PTV-annostasolle määritelty "
            f"{code('dPTV+OAR')} -leikkauksia. {bold('TARKISTA AINA PROTOKOLLA!')}</p>"
        )
    else:
        criteria_html.append(
            f"<p class='warning'>{bold('PALLIATIIVINEN SUUNNITELMA')} – "
            f"Optimointiarvot käyttävät palliatiivista kerroinprofiilia. "
            f"{bold('TARKISTA AINA PROTOKOLLA!')}</p>"
        )

    niska_name_html = "<span class='label'>vNiska</span>"
    vptv_kaikki_name_html = "<span class='label'>vPTVkaikki</span>"
    vctv_kaikki_name_html = "<span class='label'>vCTVkaikki</span>"
    max_ptv_dose_val = ptv_doses[0]

    # Unpack factors
    dptv_lf = factors["dptv_lower"]
    dptv_uf = factors["dptv_upper"]
    ctv_f_lf = factors["ctv_lower"]
    ctv_f_uf = factors["ctv_upper"]
    dptv_oar_lf = factors["dptv_oar_lower"]
    dptv_oar_uf = factors["dptv_oar_upper"]
    ring_uf = factors["ring_upper"]
    oar_crop_uf_base = factors["oar_crop_upper"]

    is_palliative = plan_type == PlanType.PALLIATIVE

    def fmt_crit(
        lbl: str,
        low: float | None = None,
        upp: float | None = None,
        nt: str | None = None,
    ) -> str:
        ln = f"<p class='crit_item'>{lbl}:"
        ind = "    "
        det: list[str] = []
        if upp is not None:
            det.append(
                f"{ind}Upper = <span class='value'>{upp:.2f}</span> <span class='unit'>Gy</span>"
            )
        if low is not None:
            det.append(
                f"{ind}Lower = <span class='value'>{low:.2f}</span> <span class='unit'>Gy</span>"
            )
        if det:
            ln += "<br>" + "<br>".join(det)
        if nt:
            ln += f"<br>{ind}<span class='note'>{nt}</span>"
        ln += "</p>"
        return ln

    for dose_xx in ptv_doses:
        dose_s = format_dose(dose_xx)
        fin_ptv_r, fin_ctv_r = final_volume_names_main.get(
            dose_xx, (f"???PTV{dose_s}", f"???CTV{dose_s}")
        )
        is_overlap = any(dose_xx in o.get("overlap_with_ptv_doses", []) for o in oars_data_list)

        if is_palliative:
            # Palliative: use plan-level factors uniformly
            cur_ptv_f_lf = factors["ptv_lower"]
            cur_ptv_f_uf = factors["ptv_upper"]
            cur_ptv_o_lf = factors["ptv_lower"]
        elif is_overlap:
            cur_ptv_f_lf = 0.96
            cur_ptv_f_uf = 1.02
            cur_ptv_o_lf = 0.96
        else:
            cur_ptv_f_lf = 0.985
            cur_ptv_f_uf = 1.02
            cur_ptv_o_lf = 0.985

        ptv_n = (
            f"({note('Sis. dPTV+OAR')})"
            if is_overlap and not is_palliative
            else f"({note('Ei dPTV+OAR')})"
            if not is_palliative
            else ""
        )
        dptv_lbl = f"<span class='label'>dPTV{dose_s}</span>"
        fin_ptv_lbl = f"<span class='label'>{fin_ptv_r}</span> {ptv_n}"
        fin_ctv_lbl = f"<span class='label'>{fin_ctv_r}</span>"
        orig_vptv_n = f"vPTV{dose_s}"
        orig_vptv_lbl = (
            f"<span class='label'>{orig_vptv_n}</span> <span class='note'>(orig)</span> {ptv_n}"
        )
        ring_lbl = (
            f"<span class='label'>{ring_prefix}{dose_s}</span> <span class='note'>(NT)</span>"
        )

        criteria_html.append(f"<h4>Annostaso {dose_xx} Gy</h4>")

        # dPTV criteria
        l_dptv = dptv_lf * dose_xx
        u_dptv = dptv_uf * dose_xx
        all_generated_ptv_lower_gy.append(l_dptv)
        all_generated_ptv_upper_gy.append(u_dptv)
        criteria_html.append(fmt_crit(dptv_lbl, l_dptv, u_dptv))

        # Final PTV criteria
        l_fin_ptv = cur_ptv_f_lf * dose_xx
        u_fin_ptv = cur_ptv_f_uf * dose_xx
        all_generated_ptv_lower_gy.append(l_fin_ptv)
        all_generated_ptv_upper_gy.append(u_fin_ptv)
        criteria_html.append(fmt_crit(fin_ptv_lbl, l_fin_ptv, u_fin_ptv))

        if fin_ptv_r != orig_vptv_n:
            l_orig_ptv = cur_ptv_o_lf * dose_xx
            u_orig_ptv = max(u_fin_ptv, cur_ptv_f_uf * max_ptv_dose_val)
            all_generated_ptv_lower_gy.append(l_orig_ptv)
            all_generated_ptv_upper_gy.append(u_orig_ptv)
            criteria_html.append(fmt_crit(orig_vptv_lbl, l_orig_ptv, u_orig_ptv))

        # CTV criteria
        l_fin_ctv = ctv_f_lf * dose_xx
        u_fin_ctv = ctv_f_uf * dose_xx
        all_generated_ctv_lower_gy.append(l_fin_ctv)
        all_generated_ctv_upper_gy.append(u_fin_ctv)
        criteria_html.append(fmt_crit(fin_ctv_lbl, l_fin_ctv, u_fin_ctv))

        # OAR overlaps (only for standard plans)
        if not is_palliative:
            oars_ov = [
                o["name"] for o in oars_data_list if dose_xx in o.get("overlap_with_ptv_doses", [])
            ]
            if oars_ov:
                criteria_html.append(f"<h5>    ↳ {code(f'dPTV{dose_s}+OAR')} Leikkaukset</h5>")
                for o_name in oars_ov:
                    ov_struct = f"dPTV{dose_s}+{o_name}"
                    ov_lbl = f"<span class='label'>{ov_struct}</span>"
                    l_dptv_oar = dptv_oar_lf * dose_xx
                    u_dptv_oar = dptv_oar_uf * dose_xx
                    all_generated_ptv_lower_gy.append(l_dptv_oar)
                    all_generated_ptv_upper_gy.append(u_dptv_oar)
                    criteria_html.append(fmt_crit(ov_lbl, l_dptv_oar, u_dptv_oar))

        # Ring: upper only
        criteria_html.append(fmt_crit(ring_lbl, upp=ring_uf * dose_xx))

    # ── General structures ──────────────────────────────────────────
    criteria_html.append("<h4>Yleiset rakenteet</h4>")
    min_ptv_l = min(all_generated_ptv_lower_gy) if all_generated_ptv_lower_gy else 0.0
    max_ptv_u = max(all_generated_ptv_upper_gy) if all_generated_ptv_upper_gy else 0.0
    min_ctv_l = min(all_generated_ctv_lower_gy) if all_generated_ctv_lower_gy else 0.0
    max_ctv_u = max(all_generated_ctv_upper_gy) if all_generated_ctv_upper_gy else 0.0
    criteria_html.append(fmt_crit(vptv_kaikki_name_html, min_ptv_l, max_ptv_u))
    criteria_html.append(fmt_crit(vctv_kaikki_name_html, min_ctv_l, max_ctv_u))

    if oars_data_list and not is_palliative:
        criteria_html.append(f"<h4>Riskielin Cropit ({code('v<OAR>Crop')})</h4>")
        for oar_item in oars_data_list:
            o_crop_lbl = f"<span class='label'>v{oar_item['name']}Crop</span>"
            criteria_html.append(fmt_crit(o_crop_lbl, upp=oar_crop_uf_base * max_ptv_dose_val))

    if create_vniska:
        n_crit = fmt_crit(niska_name_html, upp=None)
        n_crit = n_crit.replace(
            "</p>",
            "<br>    Upper = <span class='value'>???</span> <span class='unit'>Gy</span> "
            "<span class='note'>(TÄYTÄ MANUAALISESTI PROTOKOLLAN MUKAAN!)</span></p>",
        )
        criteria_html.append(n_crit)

    # ── NTO reminder ────────────────────────────────────────────────
    criteria_html.append("<h4>Normal Tissue Objective (NTO) Muistutus</h4>")
    criteria_html.append(
        "<p><b>HUOM:</b> Aseta NTO-parametrit manuaalisesti Eclipseen protokollan mukaisesti.</p>"
    )
    criteria_html.append(
        "<p>Yleiset esimerkkiarvot "
        "(<span style='color:red; font-weight:bold;'>TARKISTA AINA PAIKALLINEN PROTOKOLLA!</span>):</p>"
    )
    nto_list = [
        "<ul class='nto'>",
        "<li class='nto'>Priority: <span class='value'>~100</span></li>",
        "<li class='nto'>Distance from Target Border: <span class='value'>0.1 - 0.2</span> "
        "<span class='unit'>cm</span></li>",
    ]
    sd_l = 0.9 * max_ptv_dose_val if max_ptv_dose_val > 0 else 0
    sd_u = 0.95 * max_ptv_dose_val if max_ptv_dose_val > 0 else 0
    ed = 0.5 * max_ptv_dose_val if max_ptv_dose_val > 0 else 0
    nto_list.append(
        f"<li class='nto'>Start Dose [%]: <span class='value'>90 - 95%</span> "
        f"<span class='note'>(Esim. {sd_l:.1f} - {sd_u:.1f} Gy)</span></li>"
    )
    nto_list.append(
        f"<li class='nto'>End Dose [%]: <span class='value'>~50%</span> "
        f"<span class='note'>(Esim. {ed:.1f} Gy)</span></li>"
    )
    nto_list.append("<li class='nto'>Fall-off: <span class='value'>0.15 - 0.25</span></li></ul>")
    criteria_html.extend(nto_list)
    return "\n".join(criteria_html)
