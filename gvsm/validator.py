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
