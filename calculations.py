# -*- coding: utf-8 -*-
"""
Tämä moduuli sisältää puhtaat laskentafunktiot, joita käytetään
Eclipse Contouring Helper -sovelluksessa. Funktiot eivät riipu
käyttöliittymästä ja niitä voidaan testata itsenäisesti.
"""
import math

def calculate_ptv_crop(higher_dose, lower_dose):
    """
    Calculates PTV crop margin in cm.
    Ensures a minimum of 0.1cm if a crop is applicable due to dose difference.
    """
    if higher_dose <= 0: return 0.0
    if lower_dose >= higher_dose: return 0.0 # No crop if lower dose is not actually lower

    # Original calculation logic
    ratio = lower_dose / higher_dose
    percentage = ratio * 100
    rounded_percentage_down = math.floor(percentage / 5) * 5
    steps = 0 if rounded_percentage_down >= 95 else (95 - rounded_percentage_down) / 5
    calculated_crop_cm = int(steps) / 10.0

    # Apply minimum 0.1 cm if the formula results in 0.0 for a valid cropping scenario
    if calculated_crop_cm == 0.0:
        return 0.1
    return calculated_crop_cm

def calculate_ctv_crop_margin(ptv_crop_cm):
    """Calculates CTV crop margin based on PTV crop margin, ensuring a minimum of 0.1 cm."""
    return max(0.1, ptv_crop_cm)

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

def get_ring_body_outside_crop_margin():
    """Returns the standard crop margin for Ring vs Body (outside)."""
    return 0.0

def get_dptv_ctv_inside_crop_margin():
    """Returns the standard crop margin for dPTV vs CTV (inside)."""
    return 0.1 # 1 mm

def get_voar_vptvall_inside_crop_margin():
    """Returns the standard crop margin for vOARcrop vs vPTVkaikki (inside)."""
    return 0.1 # 1 mm

def get_vniska_vptvall_inside_crop_margin():
    """Returns the standard crop margin for vNiska vs vPTVkaikki (inside)."""
    return 1.0 # 10 mm

def get_vniska_body_outside_crop_margin():
    """Returns the standard crop margin for vNiska vs Body (outside)."""
    return 0.0

def convert_cm_to_mm(value_cm):
    """Converts a value from centimeters to millimeters."""
    return value_cm * 10.0