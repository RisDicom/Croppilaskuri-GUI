# -*- coding: utf-8 -*-
"""
Tämä moduuli vastaa vaiheittaisten ohjeiden generoinnista
Eclipse Contouring Helper -sovellukselle.
"""
from calculations import calculate_ptv_crop, calculate_ring_crop, format_dose
from text_utils import bold, code, value, tool, action, note
from config import (
    EMOJI_COPY, EMOJI_CROP_IN, EMOJI_CROP_OUT, EMOJI_UNION, EMOJI_RING,
    EMOJI_MARGIN, EMOJI_BOOLEAN, EMOJI_CHECK, EMOJI_INFO, EMOJI_DONE
)

# --- Guide Step Generation (Uudelleenjärjestetty Workflow) ---
def generate_guide_steps(ptv_doses, calculated_crops_dict, create_vniska, oars_data_list, ring_prefix, dptv_oar_crop_margin_cm):
    steps = []
    crop_summary_data = {}
    if not ptv_doses: return steps, crop_summary_data
    step_num = 0
    v = "v"; ptv_prefix = f"{v}PTV"; ctv_prefix = f"{v}CTV";
    dptv_base_prefix = "dPTV"; crop_suffix = "crop"
    body_name_raw = "Body"; spinal_cord_raw = "SpinalCord"
    vptv_kaikki_raw = f"{v}PTVkaikki"; vctv_kaikki_raw = f"{v}CTVkaikki"

    all_original_ptv_raw = {d: f"PTV{format_dose(d)}" for d in ptv_doses}
    all_original_ctv_raw = {d: f"CTV{format_dose(d)}" for d in ptv_doses}
    all_vptv_raw = {d: f"{v}PTV{format_dose(d)}" for d in ptv_doses}
    all_vctv_raw = {d: f"{v}CTV{format_dose(d)}" for d in ptv_doses}

    highest_dose = ptv_doses[0]
    is_multi_dose = len(ptv_doses) > 1
    final_volume_raw_names = {}
    all_ring_raw_names = {}

    toc_entries = []
    current_section_char_code = ord('A')

    def generate_toc_anchor_id_and_register(title_for_toc):
        nonlocal current_section_char_code
        anchor_id = f"toc_section_{chr(current_section_char_code)}"
        toc_entries.append({"anchor": anchor_id, "title": title_for_toc})
        current_section_char_code += 1
        return anchor_id

    # --- Vaihe A: Alkuvalmistelut ---
    section_a_title_for_toc = "A. Alkuvalmistelut"
    toc_target_id_a = generate_toc_anchor_id_and_register(section_a_title_for_toc)

    step_num += 1
    step1_details = f"""<a id='{toc_target_id_a}'></a><ul><li>{action('Kopioi')} PTV:t: {', '.join([code(n) for n in all_original_ptv_raw.values()])} → {', '.join([code(n) for n in all_vptv_raw.values()])}</li>
                         <li>{action('Kopioi')} CTV:t: {', '.join([code(n) for n in all_original_ctv_raw.values()])} → {', '.join([code(n) for n in all_vctv_raw.values()])}</li>
                         <li>{note('Alkuperäisiä OAR:ja ja Bodya hyödynnetään suoraan, ellei alla toisin ohjeisteta.')}</li></ul>"""
    steps.append({
        "id": step_num, "title": "A.1: Kopioi alkuperäiset PTV/CTV rakenteet", "details_html": step1_details,
        "emoji": EMOJI_COPY, "toc_anchor_target_id": toc_target_id_a
    })

    final_volume_raw_names[highest_dose] = (all_vptv_raw[highest_dose], all_vctv_raw[highest_dose])
    step_num += 1
    step2_high_details = f"<p>Korkeimman annostason ({value(highest_dose)} Gy) rakenteet {code(all_vptv_raw[highest_dose])} ja {code(all_vctv_raw[highest_dose])} ovat sellaisenaan lopulliset.</p>{note('Ei croppeja tälle tasolle.')}"
    steps.append({"id": step_num, "title": f"A.2: Tarkista korkein annostaso ({value(highest_dose)} Gy)", "details_html": step2_high_details, "emoji": EMOJI_INFO})

    # --- Vaihe B: Alemman annostason PTV/CTV-parien käsittely ---
    if is_multi_dose:
        step_num += 1
        section_b_title_for_toc = "B: Alemman annostason PTV/CTV-rakenteiden muokkaus"
        toc_target_id_b = generate_toc_anchor_id_and_register(section_b_title_for_toc)
        steps.append({
            "id": step_num, "title": section_b_title_for_toc,
            "details_html": f"<a id='{toc_target_id_b}'></a><p>Seuraavaksi käsitellään alemman annostason PTV- ja CTV-rakenteet {action('kopioimalla')} ja {action('croppaamalla')} niitä ylempiarvoisilla PTV-rakenteilla.</p>",
            "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_b
        })
        # ... (koko B-osion sisältö ennallaan) ...
        for j in range(1, len(ptv_doses)): # Indeksi j viittaa käsiteltävään alempaan annostasoon
            lower_dose = ptv_doses[j]
            lower_dose_str_fmt = format_dose(lower_dose)

            original_vptv_lower_raw_name = all_vptv_raw[lower_dose]
            original_vctv_lower_raw_name = all_vctv_raw[lower_dose]

            vptv_crop_raw_name = f"{ptv_prefix}{lower_dose_str_fmt}{crop_suffix}"
            vctv_crop_raw_name = f"{ctv_prefix}{lower_dose_str_fmt}{crop_suffix}"
            final_volume_raw_names[lower_dose] = (vptv_crop_raw_name, vctv_crop_raw_name)

            step_num += 1
            steps.append({"id": step_num, "title": f"B.{j}.1: Luo {code(vptv_crop_raw_name)} ({value(lower_dose_str_fmt)} Gy)",
                          "details_html": f"<p>{action('Kopioi')} {code(original_vptv_lower_raw_name)} → {code(vptv_crop_raw_name)}.</p>{note('Tätä muokataan seuraavaksi.')}",
                          "emoji": EMOJI_COPY})
            step_num += 1
            steps.append({"id": step_num, "title": f"B.{j}.2: Luo {code(vctv_crop_raw_name)} ({value(lower_dose_str_fmt)} Gy)",
                          "details_html": f"<p>{action('Kopioi')} {code(original_vctv_lower_raw_name)} → {code(vctv_crop_raw_name)}.</p>{note('Tätä muokataan seuraavaksi.')}",
                          "emoji": EMOJI_COPY})

            for i in range(j): # Indeksi i viittaa ylempään annostasoon
                higher_dose_i = ptv_doses[i]
                vptv_high_tool_raw_name = all_vptv_raw[higher_dose_i]
                crop_key = (higher_dose_i, lower_dose)
                ptv_crop_cm = calculated_crops_dict.get(crop_key, {}).get('PTV', 0.0)

                step_num += 1
                crop_ptv_details = f"<p>{action('Croppaa')} {code(vptv_crop_raw_name)} rakenteella {code(vptv_high_tool_raw_name)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{ptv_crop_cm:.1f} cm')}</li><li>Kohde: {code(vptv_crop_raw_name)} {note('(korvaa)')}</li></ul>"
                steps.append({"id": step_num, "title": f"B.{j}.{3+i*2}: Crop {code(vptv_crop_raw_name)} vs {code(vptv_high_tool_raw_name)}", "details_html": crop_ptv_details, "emoji": EMOJI_CROP_IN})
                crop_summary_data[step_num] = {"text": f"Crop {vptv_crop_raw_name} vs {vptv_high_tool_raw_name} (inside)", "margin_cm": ptv_crop_cm}

                step_num += 1
                ctv_crop_cm = max(0.1, ptv_crop_cm)
                crop_ctv_details = f"<p>{action('Croppaa')} {code(vctv_crop_raw_name)} rakenteella {code(vptv_high_tool_raw_name)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{ctv_crop_cm:.1f} cm')}</li><li>Kohde: {code(vctv_crop_raw_name)} {note('(korvaa)')}</li></ul>"
                steps.append({"id": step_num, "title": f"B.{j}.{4+i*2}: Crop {code(vctv_crop_raw_name)} vs {code(vptv_high_tool_raw_name)}", "details_html": crop_ctv_details, "emoji": EMOJI_CROP_IN})
                crop_summary_data[step_num] = {"text": f"Crop {vctv_crop_raw_name} vs {vptv_high_tool_raw_name} (inside)", "margin_cm": ctv_crop_cm}

    # --- Vaihe C: Yhdistelmärakenteet ---
    section_c_title_for_toc = "C: Yhdistelmärakenteet"
    toc_target_id_c = generate_toc_anchor_id_and_register(section_c_title_for_toc)
    
    step_num += 1
    step3_details = f"<a id='{toc_target_id_c}'></a><p>{action('Yhdistä')} {bold('alkuperäiset')} vPTV:t: {', '.join([code(n) for n in all_vptv_raw.values()])}</p><ul><li>Työkalu: {tool('Boolean Operators')}</li><li>Operaatio: Union {note('( | )')}</li><li>Kohde: {code(vptv_kaikki_raw)} {note('(Luo uusi)')}</li></ul>"
    steps.append({
        "id": step_num, "title": f"C.1: Luo {code(vptv_kaikki_raw)}", "details_html": step3_details,
        "emoji": EMOJI_UNION, "toc_anchor_target_id": toc_target_id_c
    })

    step_num += 1
    # Varmistetaan, että final_volume_raw_names sisältää avaimet ennen käyttöä
    final_vctv_names_to_union = [code(final_volume_raw_names[dose][1]) for dose in ptv_doses if dose in final_volume_raw_names and len(final_volume_raw_names[dose]) > 1]
    step4_details = f"<p>{action('Yhdistä')} {bold('lopulliset')} vCTV:t: {', '.join(final_vctv_names_to_union)}</p><ul><li>Työkalu: {tool('Boolean Operators')}</li><li>Operaatio: Union {note('( | )')}</li><li>Kohde: {code(vctv_kaikki_raw)} {note('(Luo uusi)')}</li></ul>"
    steps.append({"id": step_num, "title": f"C.2: Luo {code(vctv_kaikki_raw)}", "details_html": step4_details, "emoji": EMOJI_UNION})


    # --- Vaihe D: Ring/NT-rakenteet ---
    step_num += 1
    section_d_title_for_toc = f"D: Luo ja muokkaa {ring_prefix}-rakenteet"
    toc_target_id_d = generate_toc_anchor_id_and_register(section_d_title_for_toc)
    steps.append({
        "id": step_num, "title": section_d_title_for_toc,
        "details_html": f"<a id='{toc_target_id_d}'></a><p>Seuraavaksi luodaan {ring_prefix}-rakenteet ({note('Normal Tissue Objectives, NTO')}) jokaiselle PTV-tasolle ja muokataan niitä.</p>",
        "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_d
    })
    # ... (koko D-osion sisältö ennallaan) ...
    for idx, dose_r in enumerate(ptv_doses):
        dose_str_fmt = format_dose(dose_r)
        vptv_original_raw_name = all_vptv_raw[dose_r]
        ring_raw_name = f"{ring_prefix}{dose_str_fmt}"
        all_ring_raw_names[dose_r] = ring_raw_name

        step_num += 1
        create_ring_details = f"<p>{action('Luo')} {code(ring_raw_name)} pohjana {code(vptv_original_raw_name)}.</p><ul><li>Työkalu: {tool('Create Ring Structure')}</li><li>Sisäraja: {value('-0.5 cm')}</li><li>Ulkoraja: {value('2.5 - 3.0 cm')} {note('(Säädä tarv.)')}</li><li>Kohde: {code(ring_raw_name)} {note('(Luo uusi)')}</li></ul>"
        steps.append({"id": step_num, "title": f"D.1.{idx+1}: Luo {code(ring_raw_name)}", "details_html": create_ring_details, "emoji": EMOJI_RING})

        step_num += 1
        crop_ring_body_margin_cm = 0.0
        crop_ring_body_details = f"<p>{action('Croppaa')} {code(ring_raw_name)} vs {code(body_name_raw)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part outside:')}</li><li>Työkalurakenne: {code(body_name_raw)}</li><li>Marginaali: {value(f'{crop_ring_body_margin_cm:.1f} cm')}</li><li>Kohde: {code(ring_raw_name)} {note('(korvaa)')}</li></ul>"
        steps.append({"id": step_num, "title": f"D.1.{idx+1}b: Crop {code(ring_raw_name)} vs {code(body_name_raw)}", "details_html": crop_ring_body_details, "emoji": EMOJI_CROP_OUT})
        crop_summary_data[step_num] = {"text": f"Crop {ring_raw_name} vs {body_name_raw} (outside)", "margin_cm": crop_ring_body_margin_cm}

    if is_multi_dose:
        step_num += 1
        steps.append({"id": step_num, "title": f"D.2: Crop {ring_prefix}-rakenteita muilla PTV-tasoilla", 
                      "details_html": f"<p>Varmistetaan, että {ring_prefix}-rakenteet eivät ulotu muiden PTV-alueiden sisälle määritellyllä marginaalilla.</p>",
                      "emoji": EMOJI_INFO})
        for ring_dose_idx, dose_r in enumerate(ptv_doses): 
            ring_to_crop_raw_name = all_ring_raw_names[dose_r]
            for ptv_tool_idx, dose_p in enumerate(ptv_doses): 
                if dose_r == dose_p: continue 
                ptv_tool_raw_name = all_vptv_raw[dose_p] 
                ring_crop_cm = calculate_ring_crop(dose_r, dose_p)

                step_num += 1
                crop_ring_details = f"<p>{action('Croppaa')} {code(ring_to_crop_raw_name)} vs {code(ptv_tool_raw_name)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{ring_crop_cm:.1f} cm')}</li><li>Kohde: {code(ring_to_crop_raw_name)} {note('(korvaa)')}</li></ul>"
                steps.append({"id": step_num, "title": f"D.2.{ring_dose_idx+1}.{ptv_tool_idx+1}: Crop {code(ring_to_crop_raw_name)} vs {code(ptv_tool_raw_name)}", "details_html": crop_ring_details, "emoji": EMOJI_CROP_IN})
                crop_summary_data[step_num] = {"text": f"Crop {ring_to_crop_raw_name} vs {ptv_tool_raw_name} (inside)", "margin_cm": ring_crop_cm}

    # --- Vaihe E: dPTV-rakenteiden luonti ja CTV-cropit ---
    section_e_title_for_toc = f"E: Luo {dptv_base_prefix}-rakenteet ja perus-cropit CTV:llä"
    toc_target_id_e = generate_toc_anchor_id_and_register(section_e_title_for_toc)
    
    if ptv_doses:
        step_num += 1
        steps.append({
            "id": step_num, "title": section_e_title_for_toc,
            "details_html": f"<a id='{toc_target_id_e}'></a><p>Luodaan {dptv_base_prefix}-rakenteet optimointia varten. Nämä ovat PTV:n ja CTV:n välinen kuori.</p>",
            "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_e
        })

    for idx, dose_xx in enumerate(ptv_doses):
        dose_str_fmt = format_dose(dose_xx)
        ptv_ctv_name_tuple = final_volume_raw_names.get(dose_xx)
        if not ptv_ctv_name_tuple or len(ptv_ctv_name_tuple) < 2:
            print(f"VAROITUS: final_volume_raw_names puuttuu tai on epäkelpo annokselle {dose_xx} E-vaiheessa.")
            final_ptv_raw_name = all_vptv_raw.get(dose_xx, f"vPTV{dose_str_fmt}_ERROR")
            final_ctv_raw_name = all_vctv_raw.get(dose_xx, f"vCTV{dose_str_fmt}_ERROR")
        else:
            final_ptv_raw_name = ptv_ctv_name_tuple[0]
            final_ctv_raw_name = ptv_ctv_name_tuple[1]
            
        dptv_for_ctv_crop_raw_name = f"{dptv_base_prefix}{dose_str_fmt}"
        step_num += 1
        steps.append({"id": step_num, "title": f"E.{idx+1}.1: Luo {code(dptv_for_ctv_crop_raw_name)} kopioimalla",
                      "details_html": f"<p>{action('Kopioi')} {code(final_ptv_raw_name)} → {code(dptv_for_ctv_crop_raw_name)}.</p>", "emoji": EMOJI_COPY})
        step_num += 1
        dptv_vs_ctv_crop_cm = 0.1
        crop_dptv_details = f"<p>{action('Croppaa')} {code(dptv_for_ctv_crop_raw_name)} vs {code(final_ctv_raw_name)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{dptv_vs_ctv_crop_cm:.1f} cm')} {note('(1 mm)')}</li><li>Kohde: {code(dptv_for_ctv_crop_raw_name)} {note('(korvaa)')}</li></ul>"
        steps.append({"id": step_num, "title": f"E.{idx+1}.2: Crop {code(dptv_for_ctv_crop_raw_name)} vs {code(final_ctv_raw_name)}", "details_html": crop_dptv_details, "emoji": EMOJI_CROP_IN})
        crop_summary_data[step_num] = {"text": f"Crop {dptv_for_ctv_crop_raw_name} vs {final_ctv_raw_name} (inside)", "margin_cm": dptv_vs_ctv_crop_cm}

    # --- Vaihe F: OAR Crop -rakenteiden käsittely ---
    section_f_title_for_toc = "F: Riskielinten (OAR) Crop-rakenteiden käsittely"
    toc_target_id_f = generate_toc_anchor_id_and_register(section_f_title_for_toc)
    step_num += 1
    if oars_data_list:
        oar_titles = ", ".join([code(o['name']) for o in oars_data_list])
        oar_processing_intro_details = f"<a id='{toc_target_id_f}'></a><p>{bold(f'Käsittele seuraavat syötetyt riskielimet (OAR): {oar_titles}')}</p><p>Luodaan {code('v<OAR>Crop')}-rakenteet, jotka ovat OAR:n ja {code(vptv_kaikki_raw)}:n ulkopuolinen osa.</p>"
        steps.append({
            "id": step_num, "title": section_f_title_for_toc, "details_html": oar_processing_intro_details,
            "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_f
        })
        # ... (koko F-osion sisältö ennallaan) ...
        for oar_idx, oar_item in enumerate(oars_data_list):
            oar_name = oar_item['name']
            oar_name_code_fmt = code(oar_name)
            voar_crop_name_raw = f"v{oar_name}Crop"
            voar_crop_name_code_fmt = code(voar_crop_name_raw)

            step_num += 1
            copy_oar_details = f"<p>{action('Kopioi')} alkuperäinen {oar_name_code_fmt} → {voar_crop_name_code_fmt}.</p>"
            steps.append({"id": step_num, "title": f"F.{oar_idx+1}.1: Kopioi {oar_name_code_fmt} → {voar_crop_name_code_fmt}", "details_html": copy_oar_details, "emoji": EMOJI_COPY})

            step_num += 1
            voar_vs_vptvall_crop_cm = 0.1 
            crop_oar_details = f"<p>{action('Croppaa')} {voar_crop_name_code_fmt} vs {code(vptv_kaikki_raw)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{voar_vs_vptvall_crop_cm:.1f} cm')} {note('(1 mm)')}</li><li>Kohde: {voar_crop_name_code_fmt} {note('(korvaa)')}</li></ul>"
            steps.append({"id": step_num, "title": f"F.{oar_idx+1}.2: Crop {voar_crop_name_code_fmt} vs {code(vptv_kaikki_raw)}", "details_html": crop_oar_details, "emoji": EMOJI_CROP_IN})
            crop_summary_data[step_num] = {"text": f"Crop {voar_crop_name_raw} vs {vptv_kaikki_raw} (inside)", "margin_cm": voar_vs_vptvall_crop_cm}
    else:
        no_oar_details = f"<a id='{toc_target_id_f}'></a><p>Ei määriteltyjä OAReja erilliseen {code('v<OAR>Crop')}-käsittelyyn.</p>"
        steps.append({
            "id": step_num, "title": section_f_title_for_toc, "details_html": no_oar_details,
            "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_f
        })

    # --- Vaihe G: dPTV+OAR Overlap -rakenteiden käsittely ---
    section_g_title_for_toc = f"G: Luo {dptv_base_prefix}+OAR Overlapit ja tee cropit"
    toc_target_id_g = generate_toc_anchor_id_and_register(section_g_title_for_toc)
    step_num += 1
    any_oar_has_ptv_overlap_config = any(oar_item.get('overlap_with_ptv_doses') for oar_item in oars_data_list)
    if any_oar_has_ptv_overlap_config and any(oar_item.get('overlap_with_ptv_doses') for oar_item in oars_data_list): # Tarkempi ehto
        oars_involved_in_any_overlap = [oar_item['name'] for oar_item in oars_data_list if oar_item.get('overlap_with_ptv_doses')]
        if oars_involved_in_any_overlap: # Varmistetaan, että lista ei ole tyhjä
            overlap_intro_list_str = "<ul>"
            for o_name in oars_involved_in_any_overlap:
                current_oar_item = next((o for o in oars_data_list if o['name'] == o_name), None)
                if current_oar_item and current_oar_item.get('overlap_with_ptv_doses'):
                    sorted_overlap_doses = sorted(current_oar_item['overlap_with_ptv_doses'], reverse=True)
                    ptv_levels_str = ', '.join([format_dose(d) + ' Gy' for d in sorted_overlap_doses])
                    overlap_intro_list_str += f"<li>{code(o_name)} (PTV-tasot: {ptv_levels_str})</li>"
            overlap_intro_list_str += "</ul>"
            overlap_info_details = f"<a id='{toc_target_id_g}'></a><p>{bold(f'LUO {dptv_base_prefix}+OAR OVERLAPIT')} seuraaville OAR:eille ja PTV-tasoille:</p>{overlap_intro_list_str}<p>Näillä luoduilla rakenteilla cropataan vastaavia {dptv_base_prefix}-rakenteita.</p>"
            steps.append({
                "id": step_num, "title": section_g_title_for_toc, "details_html": overlap_info_details,
                "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_g
            })
            # ... (koko G-osion sisältö ennallaan) ...
            overlap_sub_step_counter = 0
            for oar_item in oars_data_list:
                oar_name = oar_item['name']
                oar_name_code_fmt = code(oar_name)
                ptv_doses_for_this_oar_overlap = oar_item.get('overlap_with_ptv_doses', [])
                if not ptv_doses_for_this_oar_overlap: continue

                sorted_ptv_doses_for_overlap = sorted(ptv_doses_for_this_oar_overlap, reverse=True)

                for ptv_dose_value in sorted_ptv_doses_for_overlap:
                    if ptv_dose_value not in ptv_doses: continue
                    overlap_sub_step_counter +=1

                    ptv_dose_str_fmt = format_dose(ptv_dose_value)
                    # Varmistetaan, että source_ptv_for_boolean_raw_name haetaan oikein
                    ptv_name_tuple_g = final_volume_raw_names.get(ptv_dose_value)
                    if not ptv_name_tuple_g or len(ptv_name_tuple_g) < 1:
                        print(f"VAROITUS: final_volume_raw_names puuttuu tai on epäkelpo annokselle {ptv_dose_value} G-vaiheessa.")
                        source_ptv_for_boolean_raw_name = all_vptv_raw.get(ptv_dose_value, f"vPTV{ptv_dose_str_fmt}_ERROR")
                    else:
                        source_ptv_for_boolean_raw_name = ptv_name_tuple_g[0]
                        
                    if not source_ptv_for_boolean_raw_name: continue 
                    target_dptv_to_crop_raw_name = f"{dptv_base_prefix}{ptv_dose_str_fmt}"
                    overlap_tool_raw_name = f"{dptv_base_prefix}{ptv_dose_str_fmt}+{oar_name}"
                    overlap_tool_code_fmt = code(overlap_tool_raw_name)

                    step_num += 1
                    create_overlap_details = f"<p>{action('Luo leikkaus')} {code(source_ptv_for_boolean_raw_name)} ja {oar_name_code_fmt} välillä.</p><ul><li>Työkalu: {tool('Boolean Operators')}</li><li>Operaatio: {value('AND')} {note('(&)')}</li><li>Kohde: {overlap_tool_code_fmt} {note('(Luo uusi työkalu)')}</li></ul>"
                    steps.append({"id": step_num, "title": f"G.{overlap_sub_step_counter}.1: Luo {overlap_tool_code_fmt}", "details_html": create_overlap_details, "emoji": EMOJI_BOOLEAN})

                    step_num += 1
                    dptv_vs_overlap_crop_mm_str = f"{dptv_oar_crop_margin_cm * 10:.1f}".replace('.0', '') + " mm"
                    crop_dptv_overlap_details = f"<p>{action('Croppaa')} {code(target_dptv_to_crop_raw_name)} vs {overlap_tool_code_fmt}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{dptv_oar_crop_margin_cm:.2f} cm')} {note(f'({dptv_vs_overlap_crop_mm_str})')}</li><li>Kohde: {code(target_dptv_to_crop_raw_name)} {note('(korvaa)')}</li></ul>"
                    steps.append({"id": step_num, "title": f"G.{overlap_sub_step_counter}.2: Crop {code(target_dptv_to_crop_raw_name)} vs {overlap_tool_code_fmt}", "details_html": crop_dptv_overlap_details, "emoji": EMOJI_CROP_IN})
                    crop_summary_data[step_num] = {"text": f"Crop {target_dptv_to_crop_raw_name} vs {overlap_tool_raw_name} (inside)", "margin_cm": dptv_oar_crop_margin_cm}
        else: # Jos ei mitään overlap-määrityksiä (oars_involved_in_any_overlap oli tyhjä)
            steps.append({
                "id": step_num, "title": section_g_title_for_toc, 
                "details_html": f"<a id='{toc_target_id_g}'></a><p>Ei määriteltyjä OAR PTV -päällekkäisyyksiä {dptv_base_prefix}+OAR -rakenteiden luomiseksi.</p>",
                "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_g
            })
    else: # Jos oars_data_list on tyhjä tai ei yhtään overlap-asetusta
        steps.append({
            "id": step_num, "title": section_g_title_for_toc, 
            "details_html": f"<a id='{toc_target_id_g}'></a><p>Ei määriteltyjä riskielimiä tai OAR PTV -päällekkäisyyksiä {dptv_base_prefix}+OAR -rakenteiden käsittelyyn.</p>",
            "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_g
        })

    # --- Vaihe H: vNiska ---
    section_h_title_for_toc = "H: vNiska"
    toc_target_id_h = generate_toc_anchor_id_and_register(section_h_title_for_toc)
    
    step_num +=1 
    if create_vniska:
        v_niska_raw_name = "vNiska"
        steps.append({
            "id": step_num, "title": f"H.1: Tarkista {code(spinal_cord_raw)}",
            "details_html": f"<a id='{toc_target_id_h}'></a><p>{action('Tarkista')} {code(spinal_cord_raw)} piirto.</p>",
            "emoji": EMOJI_CHECK, "toc_anchor_target_id": toc_target_id_h
        })
        # ... (koko H-osion sisältö ennallaan) ...
        step_num += 1
        create_niska_details = f"<p>{action('Luo')} {code(v_niska_raw_name)} laajentamalla {code(spinal_cord_raw)}.</p><ul><li>Työkalu: {tool('Margin Geometry')}</li><li>Marginaalit: Ant {value('1.0')}, Post {value('5.0')}, L/R {value('3.0 cm')}</li><li>Kohde: {code(v_niska_raw_name)} {note('(Luo uusi)')}</li></ul> {note('Tarkista ja muokkaa rajat manuaalisesti.')}"
        steps.append({"id": step_num, "title": f"H.2: Luo {code(v_niska_raw_name)}", "details_html": create_niska_details, "emoji": EMOJI_MARGIN})

        step_num += 1
        niska_vs_ptvall_crop_cm = 1.0
        crop_niska_ptv_details = f"<p>{action('Croppaa')} {code(v_niska_raw_name)} vs {code(vptv_kaikki_raw)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part extending inside:')}</li><li>Marginaali: {value(f'{niska_vs_ptvall_crop_cm:.1f} cm')}</li><li>Kohde: {code(v_niska_raw_name)} {note('(korvaa)')}</li></ul>"
        steps.append({"id": step_num, "title": f"H.3: Crop {code(v_niska_raw_name)} vs {code(vptv_kaikki_raw)}", "details_html": crop_niska_ptv_details, "emoji": EMOJI_CROP_IN})
        crop_summary_data[step_num] = {"text": f"Crop {v_niska_raw_name} vs {vptv_kaikki_raw} (inside)", "margin_cm": niska_vs_ptvall_crop_cm}

        step_num += 1
        niska_vs_body_crop_cm = 0.0
        crop_niska_body_details = f"<p>{action('Croppaa')} {code(v_niska_raw_name)} vs {code(body_name_raw)}.</p><ul><li>Työkalu: {tool('Crop Structure')}</li><li>Asetus: {value('Remove part outside:')}</li><li>Marginaali: {value(f'{niska_vs_body_crop_cm:.1f} cm')}</li><li>Kohde: {code(v_niska_raw_name)} {note('(korvaa)')}</li></ul>"
        steps.append({"id": step_num, "title": f"H.4: Crop {code(v_niska_raw_name)} vs {code(body_name_raw)}", "details_html": crop_niska_body_details, "emoji": EMOJI_CROP_OUT})
        crop_summary_data[step_num] = {"text": f"Crop {v_niska_raw_name} vs {body_name_raw} (outside)", "margin_cm": niska_vs_body_crop_cm}

    else:
        steps.append({
            "id":step_num, "title": f"{section_h_title_for_toc} (ei valittu)",
            "details_html": f"<a id='{toc_target_id_h}'></a><p>vNiska-rakenteen luontia ei valittu.</p>",
            "emoji": EMOJI_INFO, "toc_anchor_target_id": toc_target_id_h
        })

    # --- Vaihe I: Lopputarkistus ---
    section_i_title_for_toc = "I: Lopullinen tarkistus"
    toc_target_id_i = generate_toc_anchor_id_and_register(section_i_title_for_toc)
    step_num += 1
    final_check_details = f"<a id='{toc_target_id_i}'></a><p>{action('Tarkista')} kaikki luodut rakenteet huolellisesti.</p>"
    steps.append({
        "id": step_num, "title": section_i_title_for_toc, "details_html": final_check_details,
        "emoji": EMOJI_DONE, "toc_anchor_target_id": toc_target_id_i
    })

    toc_html = "<p><b>Sisällysluettelo</b></p><ul>"
    for entry in toc_entries:
        toc_html += f"<li><a href=\"#{entry['anchor']}\">{entry['title']}</a></li>"
    toc_html += "</ul><hr>"
    toc_html += "<p><small><i>Huom: Linkit vaativat toimiakseen sovelluksen sisäisen käsittelyn. Klikkaaminen ei välttämättä vieritä näkymää ilman sitä.</i></small></p>"

    toc_step = {
        "id": 0, "title": "Sisällysluettelo", "details_html": toc_html, "emoji": EMOJI_INFO
        # Ei toc_anchor_target_id:tä tälle, koska se ei ole kohde
    }
    final_steps = [toc_step] + steps
    return final_steps, crop_summary_data