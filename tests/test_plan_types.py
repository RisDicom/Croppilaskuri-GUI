"""Tests for PlanType and palliative optimization criteria."""

from __future__ import annotations

import pytest

from croppilaskuri.core.types import PLAN_FACTORS, PlanType


class TestPlanType:
    """Tests for the PlanType enum."""

    def test_standard_exists(self) -> None:
        assert PlanType.STANDARD.value == "standard"

    def test_palliative_exists(self) -> None:
        assert PlanType.PALLIATIVE.value == "palliative"

    def test_label_fi_standard(self) -> None:
        assert PlanType.STANDARD.label_fi == "Standardi"

    def test_label_fi_palliative(self) -> None:
        assert PlanType.PALLIATIVE.label_fi == "Palliatiivinen"

    def test_all_plan_types_have_factors(self) -> None:
        for pt in PlanType:
            assert pt in PLAN_FACTORS, f"Missing factors for {pt}"


class TestPlanFactors:
    """Tests for PLAN_FACTORS multiplier consistency."""

    @pytest.mark.parametrize("plan_type", list(PlanType))
    def test_all_keys_present(self, plan_type: PlanType) -> None:
        factors = PLAN_FACTORS[plan_type]
        expected_keys = {
            "dptv_lower",
            "dptv_upper",
            "ctv_lower",
            "ctv_upper",
            "ptv_lower",
            "ptv_upper",
            "ring_upper",
            "dptv_oar_lower",
            "dptv_oar_upper",
            "oar_crop_upper",
        }
        assert set(factors.keys()) == expected_keys

    @pytest.mark.parametrize("plan_type", list(PlanType))
    def test_lower_less_than_upper(self, plan_type: PlanType) -> None:
        f = PLAN_FACTORS[plan_type]
        assert f["dptv_lower"] < f["dptv_upper"]
        assert f["ctv_lower"] < f["ctv_upper"]
        assert f["ptv_lower"] < f["ptv_upper"]
        assert f["dptv_oar_lower"] < f["dptv_oar_upper"]

    def test_palliative_dptv_range(self) -> None:
        f = PLAN_FACTORS[PlanType.PALLIATIVE]
        assert f["dptv_lower"] == pytest.approx(0.92)
        assert f["dptv_upper"] == pytest.approx(0.95)

    def test_palliative_ctv_range(self) -> None:
        f = PLAN_FACTORS[PlanType.PALLIATIVE]
        assert f["ctv_lower"] == pytest.approx(1.00)
        assert f["ctv_upper"] == pytest.approx(1.02)

    def test_palliative_ptv_range(self) -> None:
        f = PLAN_FACTORS[PlanType.PALLIATIVE]
        assert f["ptv_lower"] == pytest.approx(0.92)
        assert f["ptv_upper"] == pytest.approx(1.02)

    def test_palliative_ring_upper(self) -> None:
        f = PLAN_FACTORS[PlanType.PALLIATIVE]
        assert f["ring_upper"] == pytest.approx(0.75)

    def test_standard_ring_upper(self) -> None:
        f = PLAN_FACTORS[PlanType.STANDARD]
        assert f["ring_upper"] == pytest.approx(0.80)


class TestOptimizationCriteriaWithPlanType:
    """Integration-level tests for criteria HTML generation."""

    def test_palliative_html_contains_badge(self) -> None:
        from croppilaskuri.core.optimization_criteria import (
            generate_optimization_criteria_html,
        )

        html = generate_optimization_criteria_html(
            ptv_doses=[30.0],
            final_volume_names_main={30.0: ("vPTV30", "vCTV30")},
            create_vniska=False,
            oars_data_list=[],
            ring_prefix="NT",
            plan_type=PlanType.PALLIATIVE,
        )
        assert "Palliatiivinen" in html

    def test_standard_html_contains_badge(self) -> None:
        from croppilaskuri.core.optimization_criteria import (
            generate_optimization_criteria_html,
        )

        html = generate_optimization_criteria_html(
            ptv_doses=[66.0],
            final_volume_names_main={66.0: ("vPTV66", "vCTV66")},
            create_vniska=False,
            oars_data_list=[],
            ring_prefix="NT",
            plan_type=PlanType.STANDARD,
        )
        assert "Standardi" in html

    def test_palliative_no_oar_overlap_section(self) -> None:
        """Palliative plans should not include OAR overlap criteria."""
        from croppilaskuri.core.optimization_criteria import (
            generate_optimization_criteria_html,
        )

        html = generate_optimization_criteria_html(
            ptv_doses=[30.0],
            final_volume_names_main={30.0: ("vPTV30", "vCTV30")},
            create_vniska=False,
            oars_data_list=[{"name": "Rectum", "overlap_with_ptv_doses": [30.0]}],
            ring_prefix="NT",
            plan_type=PlanType.PALLIATIVE,
        )
        assert "dPTV30+Rectum" not in html
        assert "Riskielin Cropit" not in html

    def test_palliative_ring_value(self) -> None:
        """Ring upper should use 75% for palliative plans."""
        from croppilaskuri.core.optimization_criteria import (
            generate_optimization_criteria_html,
        )

        html = generate_optimization_criteria_html(
            ptv_doses=[30.0],
            final_volume_names_main={30.0: ("vPTV30", "vCTV30")},
            create_vniska=False,
            oars_data_list=[],
            ring_prefix="NT",
            plan_type=PlanType.PALLIATIVE,
        )
        # 75% of 30 = 22.50
        assert "22.50" in html
