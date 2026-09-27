"""
Grounded Visual Site Modeling (GVSM)
=====================================
Zero-Hallucination Architectural Site Modeling & Persuasive Engineering Visualization.
Anchored directly to physical jobsite substrate.
"""

from .compiler import GVSMCompiler, PromptSpec
from .cad import CADGenerator, StairSpec, SoffitSpec, LandingSpec
from .validator import GVSMValidator, ValidationError
from .pipeline import GVSMPipeline

__version__ = "1.0.0"
__all__ = [
    "GVSMCompiler",
    "PromptSpec",
    "CADGenerator",
    "StairSpec",
    "SoffitSpec",
    "LandingSpec",
    "GVSMValidator",
    "ValidationError",
    "GVSMPipeline",
]
