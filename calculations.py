# -*- coding: utf-8 -*-
"""
Tämä moduuli sisältää puhtaat laskentafunktiot, joita käytetään
Eclipse Contouring Helper -sovelluksessa. Funktiot eivät riipu
käyttöliittymästä ja niitä voidaan testata itsenäisesti.
"""
import math

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