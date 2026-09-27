"""
GVSM Sovereign Watermarking Subsystem
=====================================
Wisconsin Rapids Geodetic Collar, In-Container EXIF/PNG Text Chunks,
and Autonomous Verification under 17 U.S.C. § 1202.
"""

from .engine import (
    GVSMWatermarker,
    DEFAULT_GEODETIC_ORIGIN,
    DEFAULT_OPERATOR,
    DEFAULT_LICENSE,
    DEFAULT_MASTER_KEY,
    _dct_8x8,
    _idct_8x8,
    _generate_payload_bits,
    _pseudo_random_block_indices,
)
from .batch import run_batch_watermark

__all__ = [
    "GVSMWatermarker",
    "run_batch_watermark",
    "DEFAULT_GEODETIC_ORIGIN",
    "DEFAULT_OPERATOR",
    "DEFAULT_LICENSE",
    "DEFAULT_MASTER_KEY",
]
