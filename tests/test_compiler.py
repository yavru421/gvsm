"""
Unit and Integration Tests for GVSM Engine
===========================================
Verifies:
1. 5-Layer Prompt Specification Compiler
2. Voice Memo Semantic Parsing
3. Anti-Refeed Guardrail (Rule 2)
4. Multi-Element Scope Mismatch Detector (Rule 1)
5. Deterministic SVG CAD Blueprint Generator (Rule 11)
6. End-to-End GVSMPipeline Execution
"""

import os
import unittest
from gvsm.compiler import GVSMCompiler, PromptSpec
from gvsm.validator import GVSMValidator, ValidationError
from gvsm.cad import CADGenerator, StairSpec, SoffitSpec
from gvsm.pipeline import GVSMPipeline


class TestGVSMCompiler(unittest.TestCase):

    def setUp(self):
        self.compiler = GVSMCompiler()
        self.test_photo = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "images", "chuck_miller_soffit", "before_hvac_cradle.jpg")
        )

    def test_5_layer_prompt_compilation(self):
        """Verify the 5-layer prompt structure adheres to Rule 11."""
        spec = PromptSpec(
            substrate="Existing 2x4 framing cradle around spiral duct and heater",
            cladding="Vertical Bright White 29-gauge Pro-Rib steel panels with white J-trim",
            finish="Flush 15/16-inch drop grid with 1-inch foil-faced polyiso insulation",
            cutaway="Exposed 2x4 SPF framing cradle, threaded rod hangers, and 12-inch spiral duct",
            macro_inset="Corner junction showing J-trim receiver and hex washer screw penetration",
            preservations=["concrete floor", "overhead metal trusses"]
        )
        compiled = spec.compile()
        
        self.assertIn("[SUBSTRATE GROUNDING]:", compiled)
        self.assertIn("Maintain authentic existing concrete floor, overhead metal trusses", compiled)
        self.assertIn("[CLADDING & PROFILES]:", compiled)
        self.assertIn("Vertical Bright White 29-gauge Pro-Rib", compiled)
        self.assertIn("[FINISH ASSEMBLIES]:", compiled)
        self.assertIn("[ARCHITECTURAL CUTAWAY]:", compiled)
        self.assertIn("[MACRO DETAIL INSET]:", compiled)
        self.assertIn("[PRESENTATION]:", compiled)

    def test_voice_memo_parsing(self):
        """Verify parsing authentic contractor voice memos extracts materials and scope."""
        memo = (
            "We're doing Chuck Miller's shop. I want vertical prorib steel panels on the vertical drop "
            "with J-trim at the bottom. The bottom needs polyiso insulation in a drop grid. Keep the concrete "
            "floor and the overhead ductwork visible, and do a cutaway showing the framing cradle inside."
        )
        spec = self.compiler.parse_voice_memo(memo, [self.test_photo])
        
        self.assertIsNotNone(spec)
        self.assertIn("Pro-Rib", spec.cladding)
        self.assertIn("polyiso", spec.finish.lower())
        self.assertIsNotNone(spec.cutaway)

    def test_anti_refeed_guard(self):
        """Verify that passing an AI render filename triggers Anti-Refeed ValidationError."""
        ai_paths = [
            "images/chuck_miller_soffit/gvsm_soffit_cutaway.jpg",
            "render_output_final.png",
            "madden_patio_work_pavilion.jpg",
            "infographic_diagram.jpg"
        ]
        for path in ai_paths:
            with self.assertRaises(ValidationError) as ctx:
                GVSMValidator.check_anti_refeed(path)
            self.assertIn("ANTI-REFEED VIOLATION", str(ctx.exception))

    def test_authentic_substrate_passes_validator(self):
        """Verify that authentic site photos pass validation."""
        self.assertTrue(os.path.exists(self.test_photo))
        # Should not raise
        GVSMValidator.check_anti_refeed(self.test_photo)
        GVSMValidator.validate_substrate_photo(self.test_photo)

    def test_multi_element_scope_detector(self):
        """Verify detector catches 'two doors / platforms' on a single camera frame (Lake Rd law)."""
        memo_two_doors = "Customer wants two 4x4 platforms and stairs at both doors."
        warning = GVSMValidator.check_multi_element_scope(memo_two_doors, photo_count=1)
        self.assertIsNotNone(warning)
        self.assertIn("SCOPE MISMATCH DETECTED", warning)

        memo_single_stair = "Build 11-riser staircase down to basement with cedartone treads."
        warning_none = GVSMValidator.check_multi_element_scope(memo_single_stair, photo_count=1)
        self.assertIsNone(warning_none)

    def test_cad_stair_generation(self):
        """Verify deterministic inline SVG CAD generation for stairs."""
        spec = StairSpec(total_rise_in=85.25, riser_count=11, unit_rise_in=7.75, unit_run_in=10.5)
        svg = CADGenerator.render_stair_cross_section(spec)
        
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("11 Risers", svg)
        self.assertIn("80\" MIN CLEAR HEADROOM", svg)
        self.assertIn("BULKHEAD CUTBACK", svg)

    def test_cad_soffit_generation(self):
        """Verify deterministic inline SVG CAD generation for soffit cradle."""
        spec = SoffitSpec(width_in=48.0, drop_in=32.0)
        svg = CADGenerator.render_soffit_cradle_section(spec)
        
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("48.0\"W", svg)
        self.assertIn("32.0\"D", svg)
        self.assertIn("12.0\" SPIRAL DUCT", svg)

    def test_end_to_end_pipeline(self):
        """Verify end-to-end pipeline produces complete dual-deliverable package."""
        pipeline = GVSMPipeline()
        memo = "Wrap this cradle with prorib steel and a drop grid, show cutaway of the heater and duct."
        result = pipeline.run(photo_path=self.test_photo, voice_memo=memo, scope_type="soffit")
        
        self.assertEqual(result["substrate_photo"], self.test_photo)
        self.assertIn("[CLADDING & PROFILES]:", result["compiled_diffusion_prompt"])
        self.assertTrue(result["cad_svg_blueprint"].startswith("<svg"))
        self.assertIn("SPIRAL DUCT", result["cad_svg_blueprint"])


if __name__ == "__main__":
    unittest.main()
