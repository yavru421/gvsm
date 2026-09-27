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
        self.assertGreater(len(result["cut_schedule"]), 0)
        self.assertIn("menards_bom", result)
        self.assertEqual(result["menards_bom"]["supplier"], "Menards (Wisconsin Rapids Store #3107)")
        self.assertTrue(result["menards_bom"]["profit_floor_protected"])

    def test_spatial_reprojection_validation(self):
        """Verify sub-pixel reprojection error invariant (< 1.20 px)."""
        # Should pass
        GVSMValidator.validate_spatial_reprojection(0.85, threshold_px=1.20)
        GVSMValidator.validate_spatial_reprojection(1.19, threshold_px=1.20)
        
        # Should fail
        with self.assertRaises(ValidationError) as ctx:
            GVSMValidator.validate_spatial_reprojection(1.35, threshold_px=1.20)
        self.assertIn("SPATIAL REPROJECTION VIOLATION", str(ctx.exception))

    def test_planar_orthogonality_validation(self):
        """Verify planar orthogonality invariant (< 0.50 deg deviation from 90 deg)."""
        # Perfect orthogonal floor [0, 1, 0] and wall [1, 0, 0] -> dot = 0 -> angle = 90 deg
        floor = (0.0, 1.0, 0.0)
        wall = (1.0, 0.0, 0.0)
        dev = GVSMValidator.validate_planar_orthogonality(floor, wall, threshold_deg=0.50)
        self.assertAlmostEqual(dev, 0.0, places=3)

        # Slight tilt (within 0.5 deg)
        import math
        rad = math.radians(90.3)
        wall_tilted = (math.sin(rad), math.cos(rad), 0.0)
        dev_tilted = GVSMValidator.validate_planar_orthogonality(floor, wall_tilted, threshold_deg=0.50)
        self.assertAlmostEqual(dev_tilted, 0.3, places=2)

        # Excessive tilt (0.8 deg deviation) -> should fail
        rad_fail = math.radians(90.8)
        wall_fail = (math.sin(rad_fail), math.cos(rad_fail), 0.0)
        with self.assertRaises(ValidationError) as ctx:
            GVSMValidator.validate_planar_orthogonality(floor, wall_fail, threshold_deg=0.50)
        self.assertIn("PLANAR ORTHOGONALITY VIOLATION", str(ctx.exception))

    def test_scale_closure_validation(self):
        """Verify metric scale closure invariant (< 1.5% against physical framing truth)."""
        # 16.0" stud spacing measured as 16.15" -> error = 0.15/16 = 0.93% -> passes
        GVSMValidator.validate_scale_closure(16.15, 16.0, threshold_ratio=0.015)

        # 16.0" stud spacing measured as 16.4" -> error = 0.4/16 = 2.5% -> fails
        with self.assertRaises(ValidationError) as ctx:
            GVSMValidator.validate_scale_closure(16.4, 16.0, threshold_ratio=0.015)
        self.assertIn("SCALE CLOSURE VIOLATION", str(ctx.exception))

    def test_dgc_bid_floor_validation(self):
        """Verify DGC $350+/day profit floor protection invariant."""
        # Contract $2,500, materials $1,000, 2 days -> $1,500 / 2 = $750/day -> passes
        daily_profit = GVSMValidator.validate_dgc_bid_floor(
            contract_price=2500.0,
            material_cost=1000.0,
            direct_subs=0.0,
            duration_days=2.0,
            floor_per_day=350.0
        )
        self.assertEqual(daily_profit, 750.0)

        # Contract $1,500, materials $1,000, 2 days -> $500 / 2 = $250/day -> fails
        with self.assertRaises(ValidationError) as ctx:
            GVSMValidator.validate_dgc_bid_floor(
                contract_price=1500.0,
                material_cost=1000.0,
                direct_subs=0.0,
                duration_days=2.0,
                floor_per_day=350.0
            )
        self.assertIn("DGC PROFIT FLOOR VIOLATION", str(ctx.exception))

    def test_cut_schedule_and_menards_bom(self):
        """Verify cut schedule and single-supplier Menards BOM generation."""
        stair_spec = StairSpec()
        sched = CADGenerator.generate_cut_schedule(stair_spec)
        self.assertGreater(len(sched), 5)
        self.assertEqual(sched[0]["mark"], "STR-01")

        bom = CADGenerator.generate_menards_bom(stair_spec, labor_hours=16.0, duration_days=2.0)
        self.assertIn("Menards", bom["supplier"])
        self.assertEqual(bom["material_markup_rate"], 0.15)
        self.assertEqual(bom["labor_rate_hourly"], 80.00)
        self.assertTrue(bom["profit_floor_protected"])
        self.assertGreaterEqual(bom["daily_profit"], 350.00)


if __name__ == "__main__":
    unittest.main()

