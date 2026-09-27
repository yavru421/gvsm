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
from .cad import CADGenerator, StairSpec, SoffitSpec, LandingSpec, ChimneySpec
from .validator import GVSMValidator, ValidationError
from .watermark import GVSMWatermarker



class GVSMPipeline:
    """End-to-end execution pipeline for Grounded Visual Site Modeling."""

    def __init__(self):
        self.compiler = GVSMCompiler()
        self.validator = GVSMValidator()
        self.cad = CADGenerator()
        self.watermarker = GVSMWatermarker()

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
        elif scope_type == "chimney" or "chimney" in memo_lower or "masonry" in memo_lower or "soldier" in memo_lower:
            spec = ChimneySpec()
            svg_blueprint = self.cad.render_chimney_elevation(spec)
        else:
            # Default to stair section if unspecified
            spec = StairSpec()
            svg_blueprint = self.cad.render_stair_cross_section(spec)

        cut_schedule = self.cad.generate_cut_schedule(spec)
        labor_h = 24.0 if isinstance(spec, ChimneySpec) else 16.0
        dur_d = 2.5 if isinstance(spec, ChimneySpec) else 2.0
        menards_bom = self.cad.generate_menards_bom(spec, labor_hours=labor_h, duration_days=dur_d)

        job_slug = os.path.basename(os.path.normpath(output_dir)) if output_dir else "GVSM_JOB"
        # Watermark the SVG blueprint with Sovereign Geodetic Benchmark & XML Namespace
        svg_blueprint = self.watermarker.watermark_svg(svg_blueprint, job_id=job_slug)

        # Spatial Verification Specifications (Substrate Grounding Invariants)
        spatial_invariants = {
            "reprojection_error_max_px": 1.20,
            "planar_orthogonality_max_dev_deg": 0.50,
            "scale_closure_max_error_ratio": 0.015,
            "dgc_profit_floor_min_per_day": 350.00,
            "geodetic_origin": "Wisconsin Rapids, WI (44.3933° N, 89.8231° W)",
            "watermark_layers": ["VisibleGeodeticCollar", "2D_DCT_SpreadSpectrum", "SHA256_MerkleProvenance", "DeterministicSVGNamespace"],
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
            prompt_file = os.path.join(output_dir, "gvsm_prompt.txt")
            blueprint_file = os.path.join(output_dir, "blueprint.svg")
            cut_file = os.path.join(output_dir, "cut_schedule.json")
            bom_file = os.path.join(output_dir, "menards_bom.json")

            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(compiled_prompt)
            with open(blueprint_file, "w", encoding="utf-8") as f:
                f.write(svg_blueprint)
            with open(cut_file, "w", encoding="utf-8") as f:
                json.dump(cut_schedule, f, indent=2)
            with open(bom_file, "w", encoding="utf-8") as f:
                json.dump(menards_bom, f, indent=2)

            # Generate Cryptographic Merkle Provenance Manifest
            prov_manifest = self.watermarker.create_provenance_manifest(
                job_id=job_slug,
                image_path=photo_path,
                substrate_photo_path=photo_path,
                svg_blueprint_path=blueprint_file,
                cut_schedule_path=cut_file,
                menards_bom_path=bom_file
            )
            with open(os.path.join(output_dir, "provenance.json"), "w", encoding="utf-8") as f:
                json.dump(prov_manifest, f, indent=2)
            result["provenance_manifest"] = prov_manifest

        return result

