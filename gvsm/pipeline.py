"""
GVSM Orchestration Pipeline
============================
Coordinates the complete voice-to-deliverable execution:
1. Validates physical substrate and pre-flight rules.
2. Compiles voice memos into 5-layer prompt specifications.
3. Generates deterministic inline SVG vector CAD blueprints.
4. Assembles dual-deliverable presentation packages.
"""

from typing import Dict, Any, List, Optional
import os
from .compiler import GVSMCompiler, PromptSpec
from .cad import CADGenerator, StairSpec, SoffitSpec, LandingSpec
from .validator import GVSMValidator, ValidationError


class GVSMPipeline:
    """End-to-end execution pipeline for Grounded Visual Site Modeling."""

    def __init__(self):
        self.compiler = GVSMCompiler()
        self.validator = GVSMValidator()
        self.cad = CADGenerator()

    def run(
        self,
        photo_path: str,
        voice_memo: str,
        scope_type: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the GVSM compilation and dual-deliverable synthesis.
        """
        # 1. Pre-flight Validation
        self.validator.validate_substrate_photo(photo_path)
        warning = self.validator.check_multi_element_scope(voice_memo, photo_count=1)

        # 2. Compile 5-Layer Prompt Specification
        prompt_spec = self.compiler.parse_voice_memo(voice_memo, [photo_path])
        compiled_prompt = prompt_spec.compile()

        # 3. Generate Deterministic SVG CAD Blueprint, Cut Schedule, and Menards BOM
        svg_blueprint = ""
        memo_lower = voice_memo.lower()
        if scope_type == "stairs" or "stair" in memo_lower:
            spec = StairSpec()
            svg_blueprint = self.cad.render_stair_cross_section(spec)
        elif scope_type == "soffit" or "hvac" in memo_lower or "cradle" in memo_lower:
            spec = SoffitSpec()
            svg_blueprint = self.cad.render_soffit_cradle_section(spec)
        else:
            # Default to stair section if unspecified
            spec = StairSpec()
            svg_blueprint = self.cad.render_stair_cross_section(spec)

        cut_schedule = self.cad.generate_cut_schedule(spec)
        menards_bom = self.cad.generate_menards_bom(spec, labor_hours=16.0, duration_days=2.0)

        # Spatial Verification Specifications (Substrate Grounding Invariants)
        spatial_invariants = {
            "reprojection_error_max_px": 1.20,
            "planar_orthogonality_max_dev_deg": 0.50,
            "scale_closure_max_error_ratio": 0.015,
            "dgc_profit_floor_min_per_day": 350.00,
            "geodetic_origin": "Wisconsin Rapids, WI (44.3933° N, 89.8231° W)",
        }

        result = {
            "substrate_photo": photo_path,
            "voice_memo": voice_memo,
            "warning": warning,
            "prompt_spec": {
                "substrate": prompt_spec.substrate,
                "cladding": prompt_spec.cladding,
                "finish": prompt_spec.finish,
                "cutaway": prompt_spec.cutaway,
                "macro_inset": prompt_spec.macro_inset,
                "preservations": prompt_spec.preservations,
            },
            "compiled_diffusion_prompt": compiled_prompt,
            "cad_svg_blueprint": svg_blueprint,
            "cut_schedule": cut_schedule,
            "menards_bom": menards_bom,
            "spatial_invariants": spatial_invariants,
        }

        # 4. Save Bundle if output_dir requested
        if output_dir:
            import json
            os.makedirs(output_dir, exist_ok=True)
            with open(os.path.join(output_dir, "gvsm_prompt.txt"), "w", encoding="utf-8") as f:
                f.write(compiled_prompt)
            with open(os.path.join(output_dir, "blueprint.svg"), "w", encoding="utf-8") as f:
                f.write(svg_blueprint)
            with open(os.path.join(output_dir, "cut_schedule.json"), "w", encoding="utf-8") as f:
                json.dump(cut_schedule, f, indent=2)
            with open(os.path.join(output_dir, "menards_bom.json"), "w", encoding="utf-8") as f:
                json.dump(menards_bom, f, indent=2)

        return result

