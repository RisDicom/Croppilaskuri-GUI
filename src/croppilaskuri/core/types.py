"""Domain types for Croppilaskuri.

Centralised type definitions replace scattered ``dict[str, Any]`` aliases.
Using ``TypedDict`` keeps runtime behaviour identical to plain dicts while
giving mypy full field-level checking.
"""

from __future__ import annotations

from enum import Enum, unique
from typing import TypedDict

# ── Plan type ───────────────────────────────────────────────────────────


@unique
class PlanType(Enum):
    """Supported treatment plan categories."""

    STANDARD = "standard"
    PALLIATIVE = "palliative"

    @property
    def label_fi(self) -> str:
        """Finnish UI label."""
        labels = {
            PlanType.STANDARD: "Standardi",
            PlanType.PALLIATIVE: "Palliatiivinen",
        }
        return labels[self]


# ── Optimization multipliers per plan type ──────────────────────────────


class OptimizationFactors(TypedDict):
    """Multiplier set for a single plan type."""

    dptv_lower: float
    dptv_upper: float
    ctv_lower: float
    ctv_upper: float
    ptv_lower: float
    ptv_upper: float
    ring_upper: float
    # When an OAR overlap exists, these override dptv_lower / dptv_upper:
    dptv_oar_lower: float
    dptv_oar_upper: float
    oar_crop_upper: float


PLAN_FACTORS: dict[PlanType, OptimizationFactors] = {
    PlanType.STANDARD: {
        "dptv_lower": 0.985,
        "dptv_upper": 1.015,
        "ctv_lower": 1.00,
        "ctv_upper": 1.02,
        "ptv_lower": 0.985,
        "ptv_upper": 1.02,
        "ring_upper": 0.80,
        "dptv_oar_lower": 0.96,
        "dptv_oar_upper": 0.99,
        "oar_crop_upper": 0.90,
    },
    PlanType.PALLIATIVE: {
        "dptv_lower": 0.92,
        "dptv_upper": 0.95,
        "ctv_lower": 1.00,
        "ctv_upper": 1.02,
        "ptv_lower": 0.92,
        "ptv_upper": 1.02,
        "ring_upper": 0.75,
        "dptv_oar_lower": 0.92,
        "dptv_oar_upper": 0.95,
        "oar_crop_upper": 0.85,
    },
}


# ── Typed dicts for data flowing between modules ────────────────────────


class OarEntry(TypedDict, total=False):
    """Single organ-at-risk record."""

    name: str
    overlap_with_ptv_doses: list[float]


class StepData(TypedDict, total=False):
    """Single guide step."""

    id: int
    title: str
    details_html: str
    emoji: str
    toc_anchor_target_id: str


class CropSummaryEntry(TypedDict, total=False):
    """One row in the crop-margin summary table."""

    text: str
    margin_cm: float
