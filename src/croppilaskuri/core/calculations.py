"""Pure calculation functions for crop margins and dose formatting.

These functions have no UI dependencies and can be tested independently.
"""

from __future__ import annotations

import math


def calculate_ptv_crop(higher_dose: float, lower_dose: float) -> float:
    """Calculate PTV crop margin in cm.

    Uses a stepped formula based on the dose ratio, rounding down to the
    nearest 5% step.  Guarantees a minimum of 0.1 cm when a crop is
    applicable.

    Args:
        higher_dose: The higher PTV dose in Gy (must be > 0).
        lower_dose: The lower PTV dose in Gy.

    Returns:
        Crop margin in cm (always >= 0.1 for valid inputs).
    """
    if higher_dose <= 0 or lower_dose >= higher_dose:
        return 0.0

    ratio = lower_dose / higher_dose
    rounded_pct = math.floor(ratio * 100 / 5) * 5
    steps = max(0, (95 - rounded_pct) / 5)
    crop_cm = int(steps) / 10.0

    return max(0.1, crop_cm)


def calculate_ctv_crop_margin(ptv_crop_cm: float) -> float:
    """Calculate CTV crop margin, minimum 0.1 cm."""
    return max(0.1, ptv_crop_cm)


def calculate_ring_crop(ring_ptv_dose: float, target_ptv_dose: float) -> float:
    """Calculate ring (NT) crop margin in cm.

    Args:
        ring_ptv_dose: Dose level associated with the ring structure.
        target_ptv_dose: Target PTV dose to crop against.

    Returns:
        Crop margin in cm.
    """
    if ring_ptv_dose == target_ptv_dose:
        return 0.1
    if target_ptv_dose <= 0:
        return 0.0

    effective_dose = ring_ptv_dose * 0.8
    if effective_dose >= target_ptv_dose:
        return 0.1

    ratio = effective_dose / target_ptv_dose
    rounded_pct = math.floor(ratio * 100 / 5) * 5
    steps = max(0, (95 - rounded_pct) / 5)
    crop_mm = max(1.0, float(int(steps)))

    return crop_mm / 10.0


def format_dose(dose: float) -> str:
    """Format a dose value for display.

    Integers are shown without decimals; floats use a comma as the
    decimal separator (Finnish locale convention).

    Examples:
        >>> format_dose(66.0)
        '66'
        >>> format_dose(50.4)
        '50,4'
    """
    if dose == int(dose):
        return str(int(dose))
    return str(dose).replace(".", ",")


# ── Fixed margin accessors ──────────────────────────────────────────────


def get_ring_body_outside_crop_margin() -> float:
    """Standard crop margin for Ring vs Body (outside): 0 cm."""
    return 0.0


def get_dptv_ctv_inside_crop_margin() -> float:
    """Standard crop margin for dPTV vs CTV (inside): 0.1 cm = 1 mm."""
    return 0.1


def get_voar_vptvall_inside_crop_margin() -> float:
    """Standard crop margin for vOARcrop vs vPTVkaikki (inside): 0.1 cm."""
    return 0.1


def get_vniska_vptvall_inside_crop_margin() -> float:
    """Standard crop margin for vNiska vs vPTVkaikki (inside): 1.0 cm."""
    return 1.0


def get_vniska_body_outside_crop_margin() -> float:
    """Standard crop margin for vNiska vs Body (outside): 0 cm."""
    return 0.0


def convert_cm_to_mm(value_cm: float) -> float:
    """Convert centimeters to millimeters."""
    return value_cm * 10.0
