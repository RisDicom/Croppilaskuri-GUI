# -*- coding: utf-8 -*-
"""
Vastaa optimointikriteerien HTML-muotoilusta Eclipse Contouring Helper -sovellukselle.
"""
from calculations import format_dose
from text_utils import bold, code, value, note # Muut mahdollisesti tarvittavat
from config import COLOR_TITLE, COLOR_INSTRUCTION, COLOR_CODE, COLOR_VALUE, COLOR_NOTE, COLOR_ACTION

def generate_optimization_criteria_html(ptv_doses, final_volume_names_main, create_vniska, oars_data_list, ring_prefix):
    if not ptv_doses: return "<p><b>Ei PTV-annoksia syötetty kriteerien luontiin.</b></p>"
    criteria_html = []
    all_generated_ptv_lower_gy, all_generated_ptv_upper_gy = [], []
    all_generated_ctv_lower_gy, all_generated_ctv_upper_gy = [], []
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
        ul.nto {{ margin-left: 15px; list-style-type: disc; }} li.nto {{ margin-bottom: 4px; }}
    </style>""")
    criteria_html.append("<h2>Optimointikriteerit (Esimerkkiarvot)</h2>")
    criteria_html.append(f"<p class='warning'>HUOM: Optimointikertoimet PTV-rakenteille voivat vaihdella annostasoittain riippuen siitä, onko kyseiselle PTV-annostasolle määritelty {code('dPTV+OAR')} -leikkauksia. {bold('TARKISTA AINA PROTOKOLLA!')}</p>")
    niska_name_html, vptv_kaikki_name_html, vctv_kaikki_name_html = f"<span class='label'>vNiska</span>", f"<span class='label'>vPTVkaikki</span>", f"<span class='label'>vCTVkaikki</span>"
    max_ptv_dose_val = ptv_doses[0]
    dptv_lf, dptv_uf = 0.985, 1.015; ctv_f_lf, ctv_f_uf = 1.00, 1.02
    dptv_oar_lf, dptv_oar_uf = 0.96, 0.99; ring_uf = 0.80
    oar_crop_uf = 0.85 if any(o.get('overlap_with_ptv_doses') for o in oars_data_list) else 0.90

    def fmt_crit(lbl, low=None, upp=None, nt=None):
        ln = f"<p class='crit_item'>{lbl}:"; ind = "    "; det = []
        if upp is not None: det.append(f"{ind}Upper = <span class='value'>{upp:.2f}</span> <span class='unit'>Gy</span>")
        if low is not None: det.append(f"{ind}Lower = <span class='value'>{low:.2f}</span> <span class='unit'>Gy</span>")
        if det: ln += "<br>" + "<br>".join(det)
        if nt: ln += f"<br>{ind}<span class='note'>{nt}</span>"
        ln += "</p>"; return ln

    for dose_xx in ptv_doses:
        dose_s = format_dose(dose_xx)
        fin_ptv_r, fin_ctv_r = final_volume_names_main.get(dose_xx, (f"???PTV{dose_s}", f"???CTV{dose_s}"))
        is_overlap = any(dose_xx in o.get('overlap_with_ptv_doses', []) for o in oars_data_list)
        cur_ptv_f_lf, cur_ptv_f_uf = (0.96, 1.02) if is_overlap else (0.985, 1.02)
        cur_ptv_o_lf = 0.96 if is_overlap else 0.985
        ptv_n = f"({note('Sis. dPTV+OAR')})" if is_overlap else f"({note('Ei dPTV+OAR')})"
        dptv_lbl = f"<span class='label'>dPTV{dose_s}</span>"; fin_ptv_lbl = f"<span class='label'>{fin_ptv_r}</span> {ptv_n}"
        fin_ctv_lbl = f"<span class='label'>{fin_ctv_r}</span>"; orig_vptv_n = f"vPTV{dose_s}"
        orig_vptv_lbl = f"<span class='label'>{orig_vptv_n}</span> <span class='note'>(orig)</span> {ptv_n}"
        ring_lbl = f"<span class='label'>{ring_prefix}{dose_s}</span> <span class='note'>(NT)</span>"
        criteria_html.append(f"<h4>Annostaso {dose_xx} Gy</h4>")
        l_dptv, u_dptv = dptv_lf * dose_xx, dptv_uf * dose_xx
        all_generated_ptv_lower_gy.append(l_dptv); all_generated_ptv_upper_gy.append(u_dptv)
        criteria_html.append(fmt_crit(dptv_lbl, l_dptv, u_dptv))
        l_fin_ptv, u_fin_ptv = cur_ptv_f_lf * dose_xx, cur_ptv_f_uf * dose_xx
        all_generated_ptv_lower_gy.append(l_fin_ptv); all_generated_ptv_upper_gy.append(u_fin_ptv)
        criteria_html.append(fmt_crit(fin_ptv_lbl, l_fin_ptv, u_fin_ptv))
        if fin_ptv_r != orig_vptv_n:
            l_orig_ptv = cur_ptv_o_lf * dose_xx
            u_orig_ptv = max(u_fin_ptv, cur_ptv_f_uf * max_ptv_dose_val) # Tarkistettu logiikka u_orig_ptv:lle
            all_generated_ptv_lower_gy.append(l_orig_ptv); all_generated_ptv_upper_gy.append(u_orig_ptv)
            criteria_html.append(fmt_crit(orig_vptv_lbl, l_orig_ptv, u_orig_ptv))
        l_fin_ctv, u_fin_ctv = ctv_f_lf * dose_xx, ctv_f_uf * dose_xx
        all_generated_ctv_lower_gy.append(l_fin_ctv); all_generated_ctv_upper_gy.append(u_fin_ctv)
        criteria_html.append(fmt_crit(fin_ctv_lbl, l_fin_ctv, u_fin_ctv))
        oars_ov = [o['name'] for o in oars_data_list if dose_xx in o.get('overlap_with_ptv_doses', [])]
        if oars_ov:
            criteria_html.append(f"<h5>    ↳ {code(f'dPTV{dose_s}+OAR')} Leikkaukset</h5>")
            for o_name in oars_ov:
                ov_struct = f"dPTV{dose_s}+{o_name}"; ov_lbl = f"<span class='label'>{ov_struct}</span>"
                l_dptv_oar, u_dptv_oar = dptv_oar_lf * dose_xx, dptv_oar_uf * dose_xx
                all_generated_ptv_lower_gy.append(l_dptv_oar); all_generated_ptv_upper_gy.append(u_dptv_oar)
                criteria_html.append(fmt_crit(ov_lbl, l_dptv_oar, u_dptv_oar))
        criteria_html.append(fmt_crit(ring_lbl, upp=ring_uf * dose_xx))
    criteria_html.append("<h4>Yleiset rakenteet</h4>")
    min_ptv_l = min(all_generated_ptv_lower_gy) if all_generated_ptv_lower_gy else 0.0
    max_ptv_u = max(all_generated_ptv_upper_gy) if all_generated_ptv_upper_gy else 0.0
    min_ctv_l = min(all_generated_ctv_lower_gy) if all_generated_ctv_lower_gy else 0.0
    max_ctv_u = max(all_generated_ctv_upper_gy) if all_generated_ctv_upper_gy else 0.0
    criteria_html.append(fmt_crit(vptv_kaikki_name_html, min_ptv_l, max_ptv_u))
    criteria_html.append(fmt_crit(vctv_kaikki_name_html, min_ctv_l, max_ctv_u))
    if oars_data_list:
        criteria_html.append(f"<h4>Riskielin Cropit ({code('v<OAR>Crop')})</h4>")
        for oar_item in oars_data_list:
            o_crop_lbl = f"<span class='label'>v{oar_item['name']}Crop</span>"
            criteria_html.append(fmt_crit(o_crop_lbl, upp=oar_crop_uf * max_ptv_dose_val))
    if create_vniska:
        n_crit = fmt_crit(niska_name_html, upp=None)
        n_crit = n_crit.replace("</p>", f"<br>    Upper = <span class='value'>???</span> <span class='unit'>Gy</span> <span class='note'>(TÄYTÄ MANUAALISESTI PROTOKOLLAN MUKAAN!)</span></p>")
        criteria_html.append(n_crit)
    criteria_html.append("<h4>Normal Tissue Objective (NTO) Muistutus</h4>")
    criteria_html.append("<p><b>HUOM:</b> Aseta NTO-parametrit manuaalisesti Eclipseen protokollan mukaisesti.</p>")
    criteria_html.append("<p>Yleiset esimerkkiarvot (<span style='color:red; font-weight:bold;'>TARKISTA AINA PAIKALLINEN PROTOKOLLA!</span>):</p>")
    nto_list = ["<ul class='nto'>", f"<li class='nto'>Priority: <span class='value'>~100</span></li>",
                f"<li class='nto'>Distance from Target Border: <span class='value'>0.1 - 0.2</span> <span class='unit'>cm</span></li>"]
    sd_l, sd_u = (0.9*max_ptv_dose_val, 0.95*max_ptv_dose_val) if max_ptv_dose_val > 0 else (0,0)
    ed = 0.5*max_ptv_dose_val if max_ptv_dose_val > 0 else 0
    nto_list.append(f"<li class='nto'>Start Dose [%]: <span class='value'>90 - 95%</span> <span class='note'>(Esim. {sd_l:.1f} - {sd_u:.1f} Gy)</span></li>")
    nto_list.append(f"<li class='nto'>End Dose [%]: <span class='value'>~50%</span> <span class='note'>(Esim. {ed:.1f} Gy)</span></li>")
    nto_list.append(f"<li class='nto'>Fall-off: <span class='value'>0.15 - 0.25</span></li></ul>")
    criteria_html.extend(nto_list)
    return "\n".join(criteria_html)