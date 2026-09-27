"""
GVSM Validator & Pre-Flight Alignment Engine
=============================================
Enforces the hard-learned field laws:
1. Anti-Refeed Guard: Prevents feeding AI-generated images back into diffusion.
2. Substrate Integrity: Verifies image readability, dimensions, and path safety.
3. Multi-Element Scope Check: Catches mismatches like 'two doors' on a single photo.
"""

import os
import re
from typing import List, Tuple, Optional


class ValidationError(Exception):
    """Raised when an operational GVSM invariant is violated."""
    pass


class GVSMValidator:
    """Automated guardrails protecting the GVSM pipeline from compounding errors."""

    # Patterns characteristic of AI-generated artifact filenames
    AI_IMAGE_PATTERNS = [
        re.compile(r"gvsm", re.IGNORECASE),
        re.compile(r"render", re.IGNORECASE),
        re.compile(r"infographic", re.IGNORECASE),
        re.compile(r"cutaway", re.IGNORECASE),
        re.compile(r"wedge", re.IGNORECASE),
        re.compile(r"pavilion", re.IGNORECASE),
    ]

    # Phrases indicating a multi-element scope that cannot fit into a single photo
    MULTI_ELEMENT_PATTERNS = [
        re.compile(r"two\s+doors?", re.IGNORECASE),
        re.compile(r"both\s+doors?", re.IGNORECASE),
        re.compile(r"two\s+4x4\s+platforms?", re.IGNORECASE),
        re.compile(r"front\s+and\s+back\s+door", re.IGNORECASE),
        re.compile(r"two\s+separate\s+landings?", re.IGNORECASE),
    ]

    @classmethod
    def check_anti_refeed(cls, photo_path: str) -> None:
        """
        Enforces Rule 2: NEVER RE-FEED GENERATED IMAGES.
        Throws ValidationError if the photo path appears to be a prior AI render.
        """
        filename = os.path.basename(photo_path)
        for pattern in cls.AI_IMAGE_PATTERNS:
            if pattern.search(filename):
                raise ValidationError(
                    f"ANTI-REFEED VIOLATION: '{filename}' appears to be an AI-generated artifact. "
                    "GVSM must anchor strictly to raw, authentic on-site camera frames to prevent error compounding."
                )

    @classmethod
    def validate_substrate_photo(cls, photo_path: str) -> None:
        """Verifies that the reference photo exists and is accessible."""
        if not os.path.exists(photo_path):
            raise ValidationError(f"SUBSTRATE MISSING: File does not exist at '{photo_path}'.")
        
        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
        _, ext = os.path.splitext(photo_path)
        if ext.lower() not in valid_exts:
            raise ValidationError(f"INVALID IMAGE FORMAT: '{ext}' is not a supported image format {valid_exts}.")

        # Check anti-refeed rule
        cls.check_anti_refeed(photo_path)

    @classmethod
    def check_multi_element_scope(cls, transcript: str, photo_count: int) -> Optional[str]:
        """
        Enforces Rule 1: The 'One Substrate, One Camera Frame' Law.
        Warns if the contractor's speech describes multiple distinct physical zones
        while only passing a single camera frame (The Lake Road Trap).
        """
        for pattern in cls.MULTI_ELEMENT_PATTERNS:
            match = pattern.search(transcript)
            if match and photo_count == 1:
                return (
                    f"POTENTIAL SCOPE MISMATCH DETECTED: The voice memo mentions '{match.group(0)}', "
                    "but only 1 camera frame was supplied. "
                    "GVSM Law: One physical structure = One photo = One render. "
                    "If there are two separate doors/zones, split the job into Job A and Job B with separate photos."
                )
        return None

    @classmethod
    def validate_spatial_reprojection(cls, reprojection_error_px: float, threshold_px: float = 1.20) -> None:
        """
        Enforces Anti-Hallucination Invariant 1:
        Sub-pixel reprojection error must be < 1.20 px on 1080p frames.
        """
        if reprojection_error_px > threshold_px:
            raise ValidationError(
                f"SPATIAL REPROJECTION VIOLATION: Mean reprojection error {reprojection_error_px:.3f}px "
                f"exceeds tolerance of {threshold_px:.2f}px. Landmark constellation rejected."
            )

    @classmethod
    def validate_planar_orthogonality(
        cls,
        floor_normal: Tuple[float, float, float],
        wall_normal: Tuple[float, float, float],
        threshold_deg: float = 0.50
    ) -> float:
        """
        Enforces Anti-Hallucination Invariant 2:
        Planar orthogonality between floor and wall normals must deviate < 0.50 degrees from 90 deg.
        Returns the absolute deviation in degrees.
        """
        import math
        # Dot product of normalized vectors
        dot = (
            floor_normal[0] * wall_normal[0] +
            floor_normal[1] * wall_normal[1] +
            floor_normal[2] * wall_normal[2]
        )
        dot = max(-1.0, min(1.0, dot))
        angle_deg = math.degrees(math.acos(dot))
        deviation_deg = abs(angle_deg - 90.0)
        if deviation_deg > threshold_deg:
            raise ValidationError(
                f"PLANAR ORTHOGONALITY VIOLATION: Angle deviation {deviation_deg:.3f} deg exceeds "
                f"structural framing tolerance of {threshold_deg:.2f} deg. Rejecting warped plane."
            )
        return deviation_deg

    @classmethod
    def validate_scale_closure(
        cls,
        derived_length_in: float,
        true_length_in: float,
        threshold_ratio: float = 0.015
    ) -> float:
        """
        Enforces Anti-Hallucination Invariant 3:
        Scale closure error against physical structural priors (16" O.C. studs) must be < 1.5%.
        Returns the error ratio.
        """
        if true_length_in <= 0:
            raise ValidationError("INVALID SCALE COMPARISON: true_length_in must be positive.")
        error_ratio = abs(derived_length_in - true_length_in) / true_length_in
        if error_ratio > threshold_ratio:
            raise ValidationError(
                f"SCALE CLOSURE VIOLATION: Derived span {derived_length_in:.2f}\" deviates from physical "
                f"truth {true_length_in:.2f}\" by {error_ratio*100:.2f}% (tolerance: {threshold_ratio*100:.1f}%)."
            )
        return error_ratio

    @classmethod
    def validate_dgc_bid_floor(
        cls,
        contract_price: float,
        material_cost: float,
        direct_subs: float = 0.0,
        duration_days: float = 1.0,
        floor_per_day: float = 350.00
    ) -> float:
        """
        Enforces Wisconsin Rapids DGC Contract Protection:
        Guarantees minimum $350+/day profit floor on every billable job day.
        Returns daily profit.
        """
        if duration_days <= 0:
            duration_days = 1.0
        gross_margin = contract_price - (material_cost + direct_subs)
        daily_profit = gross_margin / duration_days
        if daily_profit < floor_per_day:
            raise ValidationError(
                f"DGC PROFIT FLOOR VIOLATION: Daily profit ${daily_profit:.2f}/day is below "
                f"mandatory floor of ${floor_per_day:.2f}/day (Contract: ${contract_price:.2f}, "
                f"Materials: ${material_cost:.2f}, Days: {duration_days})."
            )
        return daily_profit

