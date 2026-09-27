"""
GVSM Deterministic Inline SVG CAD Generator
============================================
Generates millimeter-accurate, vector CAD cross-sections and layout plans
for the 'Fabrication Truth Layer' (Dual-Deliverable Truth Composition).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class StairSpec:
    total_rise_in: float = 85.25
    riser_count: int = 11
    unit_rise_in: float = 7.75
    unit_run_in: float = 10.5
    stringer_stock: str = "2x12 Douglas Fir"
    tread_stock: str = "2x12 Cedartone Timber"
    headroom_min_in: float = 80.0
    bulkhead_cutback_in: float = 28.0


@dataclass
class SoffitSpec:
    width_in: float = 48.0
    drop_in: float = 32.0
    framing_stock: str = "2x4 SPF #2"
    ceiling_grid: str = "15/16-inch Classic X"
    liner_panel: str = "Pro-Rib Bright White 29ga"
    duct_diameter_in: float = 12.0


@dataclass
class LandingSpec:
    width_in: float = 48.0
    length_in: float = 48.0
    joist_spacing_oc_in: float = 16.0
    lumber_stock: str = "2x6 Cedartone"
    post_stock: str = "4x4 AC2 Ground Contact"


class CADGenerator:
    """
    Renders clean, architectural SVG vector blueprints embedded directly into
    proposals, work orders, and HTML deliverables.
    """

    @staticmethod
    def render_stair_cross_section(spec: StairSpec) -> str:
        """Generates an SVG cross-section of a residential staircase with headroom rake lines."""
        svg_w, svg_h = 800, 500
        origin_x, origin_y = 100, 420
        scale = 2.8  # pixels per inch

        step_run_px = spec.unit_run_in * scale
        step_rise_px = spec.unit_rise_in * scale

        # Build stair profile path
        path_d = [f"M {origin_x} {origin_y}"]
        curr_x, curr_y = origin_x, origin_y
        for i in range(spec.riser_count):
            curr_y -= step_rise_px
            path_d.append(f"L {curr_x} {curr_y}")
            if i < spec.riser_count - 1:
                curr_x += step_run_px
                path_d.append(f"L {curr_x} {curr_y}")

        # Stringer back-cut line
        stringer_bottom_x = origin_x
        stringer_bottom_y = origin_y + 15
        stringer_top_x = curr_x
        stringer_top_y = curr_y + 15

        # Headroom rake line (80" clearance above nosings)
        headroom_px = spec.headroom_min_in * scale
        rake_start_x = origin_x
        rake_start_y = origin_y - headroom_px
        rake_end_x = curr_x
        rake_end_y = curr_y - headroom_px

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="auto" style="background:#0f172a; font-family:monospace; border-radius:8px;">
  <!-- Title & Metadata -->
  <text x="30" y="40" fill="#38bdf8" font-size="16" font-weight="bold">DGC ARCHITECTURAL BLUEPRINT — STAIR SECTION &amp; HEADROOM RAKE</text>
  <text x="30" y="60" fill="#94a3b8" font-size="12">Scale: {spec.unit_rise_in}\" Rise &times; {spec.unit_run_in}\" Run | {spec.riser_count} Risers | Wisconsin SPS 321.04 Code</text>

  <!-- Grid lines -->
  <line x1="50" y1="450" x2="750" y2="450" stroke="#334155" stroke-width="2" />
  <text x="750" y="445" fill="#64748b" font-size="10" text-anchor="end">FINISHED CONCRETE SLAB</text>

  <!-- Stringer structural back -->
  <line x1="{stringer_bottom_x}" y1="{stringer_bottom_y}" x2="{stringer_top_x}" y2="{stringer_top_y}" stroke="#d97706" stroke-width="12" stroke-linecap="round" opacity="0.4" />
  
  <!-- Stair Step Profile (Treads & Risers) -->
  <path d="{' '.join(path_d)}" fill="none" stroke="#f59e0b" stroke-width="3" />

  <!-- Code-Compliant 80-inch Headroom Clearance Rake -->
  <line x1="{rake_start_x}" y1="{rake_start_y}" x2="{rake_end_x}" y2="{rake_end_y}" stroke="#22c55e" stroke-width="2" stroke-dasharray="6,4" />
  <text x="{(rake_start_x + rake_end_x)/2 - 40}" y="{(rake_start_y + rake_end_y)/2 - 15}" fill="#4ade80" font-size="12" font-weight="bold">80\" MIN CLEAR HEADROOM RAKE LINE</text>

  <!-- Bulkhead Cutback Area -->
  <rect x="{curr_x - (spec.bulkhead_cutback_in * scale)}" y="70" width="{spec.bulkhead_cutback_in * scale}" height="100" fill="#dc2626" opacity="0.2" stroke="#ef4444" stroke-width="2" stroke-dasharray="4,4" />
  <text x="{curr_x - (spec.bulkhead_cutback_in * scale)/2}" y="125" fill="#f87171" font-size="11" text-anchor="middle" font-weight="bold">BULKHEAD CUTBACK (28\")</text>

  <!-- Kicker Plate Anchor Base -->
  <rect x="{origin_x - 10}" y="{origin_y - 20}" width="40" height="20" fill="#0284c7" stroke="#38bdf8" stroke-width="1.5" />
  <text x="{origin_x + 35}" y="{origin_y - 8}" fill="#38bdf8" font-size="10">AC2 Kicker + Tapcons</text>
</svg>"""
        return svg

    @staticmethod
    def render_soffit_cradle_section(spec: SoffitSpec) -> str:
        """Generates an SVG cross-section of an HVAC soffit enclosure cradle with drop grid."""
        svg_w, svg_h = 600, 450
        scale = 6.0
        cradle_w = spec.width_in * scale
        cradle_h = spec.drop_in * scale
        ox, oy = 100, 80

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="auto" style="background:#0f172a; font-family:monospace; border-radius:8px;">
  <!-- Title -->
  <text x="30" y="35" fill="#38bdf8" font-size="15" font-weight="bold">DGC SOFFIT CRADLE CROSS-SECTION — {spec.width_in}\"W &times; {spec.drop_in}\"D</text>

  <!-- Ceiling Truss Substrate -->
  <line x1="50" y1="{oy}" x2="550" y2="{oy}" stroke="#94a3b8" stroke-width="6" />
  <text x="50" y="{oy - 10}" fill="#94a3b8" font-size="11">EXISTING CEILING TRUSS BOTTOM CHORDS</text>

  <!-- 2x4 Wooden Cradle Frame -->
  <rect x="{ox}" y="{oy}" width="{cradle_w}" height="{cradle_h}" fill="none" stroke="#d97706" stroke-width="4" stroke-dasharray="8,4" />
  <text x="{ox + 10}" y="{oy + 30}" fill="#f59e0b" font-size="11">2x4 Vertical Drop Legs (16\" O.C.)</text>

  <!-- Interior Spiral Duct Round Profile -->
  <circle cx="{ox + cradle_w/2}" cy="{oy + cradle_h/2}" r="{spec.duct_diameter_in * scale / 2}" fill="#334155" stroke="#94a3b8" stroke-width="3" />
  <text x="{ox + cradle_w/2}" y="{oy + cradle_h/2 + 4}" fill="#cbd5e1" font-size="11" text-anchor="middle">{spec.duct_diameter_in}\" SPIRAL DUCT</text>

  <!-- Pro-Rib Vertical Steel Liner (Front Face) -->
  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy + cradle_h}" stroke="#f8fafc" stroke-width="6" />
  <text x="{ox - 15}" y="{oy + cradle_h/2}" fill="#f8fafc" font-size="10" text-anchor="end">Pro-Rib White Steel</text>

  <!-- Suspended 15/16\" Drop Grid Bottom Plane -->
  <line x1="{ox}" y1="{oy + cradle_h}" x2="{ox + cradle_w}" y2="{oy + cradle_h}" stroke="#38bdf8" stroke-width="5" />
  <text x="{ox + cradle_w/2}" y="{oy + cradle_h + 25}" fill="#38bdf8" font-size="11" text-anchor="middle">15/16\" Drop Grid + Foil-Faced Polyiso / 1/2\" PVC</text>
</svg>"""
        return svg
