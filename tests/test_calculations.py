"""Tests for croppilaskuri.core.calculations."""

from __future__ import annotations

import pytest

from croppilaskuri.core.calculations import (
    calculate_ctv_crop_margin,
    calculate_ptv_crop,
    calculate_ring_crop,
    convert_cm_to_mm,
    format_dose,
    get_dptv_ctv_inside_crop_margin,
    get_ring_body_outside_crop_margin,
    get_vniska_body_outside_crop_margin,
    get_vniska_vptvall_inside_crop_margin,
    get_voar_vptvall_inside_crop_margin,
)


class TestCalculatePtvCrop:
    """Tests for the PTV crop margin formula."""

    def test_same_dose_returns_zero(self) -> None:
        assert calculate_ptv_crop(66, 66) == 0.0

    def test_lower_greater_returns_zero(self) -> None:
        assert calculate_ptv_crop(50, 66) == 0.0

    def test_zero_higher_returns_zero(self) -> None:
        assert calculate_ptv_crop(0, 50) == 0.0

    def test_minimum_margin(self) -> None:
        """Even near-equal doses should yield at least 0.1 cm."""
        result = calculate_ptv_crop(66, 64)
        assert result >= 0.1

    def test_large_difference(self) -> None:
        result = calculate_ptv_crop(66, 30)
        assert result > 0.1

    def test_typical_h_and_n(self) -> None:
        """66 Gy vs 54 Gy — a common head-and-neck scenario."""
        result = calculate_ptv_crop(66, 54)
        assert isinstance(result, float)
        assert result >= 0.1

    def test_returns_float(self) -> None:
        assert isinstance(calculate_ptv_crop(66, 50), float)


class TestCalculateCtcCropMargin:
    def test_minimum_enforced(self) -> None:
        assert calculate_ctv_crop_margin(0.0) == 0.1

    def test_passthrough(self) -> None:
        assert calculate_ctv_crop_margin(0.5) == 0.5


class TestCalculateRingCrop:
    def test_equal_doses(self) -> None:
        assert calculate_ring_crop(66, 66) == 0.1

    def test_target_zero(self) -> None:
        assert calculate_ring_crop(66, 0) == 0.0


class TestFormatDose:
    def test_integer_dose(self) -> None:
        assert format_dose(66.0) == "66"

    def test_float_dose_comma(self) -> None:
        assert format_dose(50.4) == "50,4"

    def test_integer_like(self) -> None:
        assert format_dose(30.0) == "30"


class TestFixedMargins:
    def test_ring_body_outside(self) -> None:
        assert get_ring_body_outside_crop_margin() == 0.0

    def test_dptv_ctv_inside(self) -> None:
        assert get_dptv_ctv_inside_crop_margin() == 0.1

    def test_voar_vptvall_inside(self) -> None:
        assert get_voar_vptvall_inside_crop_margin() == 0.1

    def test_vniska_vptvall_inside(self) -> None:
        assert get_vniska_vptvall_inside_crop_margin() == 1.0

    def test_vniska_body_outside(self) -> None:
        assert get_vniska_body_outside_crop_margin() == 0.0


class TestConvertCmToMm:
    def test_basic(self) -> None:
        assert convert_cm_to_mm(1.0) == 10.0

    @pytest.mark.parametrize("cm,mm", [(0.1, 1.0), (0.5, 5.0), (2.5, 25.0)])
    def test_parametrized(self, cm: float, mm: float) -> None:
        assert convert_cm_to_mm(cm) == pytest.approx(mm)
