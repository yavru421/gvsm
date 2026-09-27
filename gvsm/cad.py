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

    @staticmethod
    def generate_cut_schedule(spec: Any) -> List[Dict[str, Any]]:
        """
        Generates a piece-by-piece fabrication cut schedule for field carpenters.
        Part of Layer 2: Fabrication Truth.
        """
        import math
        schedule = []
        if isinstance(spec, StairSpec):
            total_run_in = (spec.riser_count - 1) * spec.unit_run_in
            stringer_len_in = math.sqrt(spec.total_rise_in**2 + total_run_in**2)
            plumb_cut_deg = math.degrees(math.atan2(spec.unit_rise_in, spec.unit_run_in))
            seat_cut_deg = 90.0 - plumb_cut_deg

            for idx in range(1, 4):
                schedule.append({
                    "mark": f"STR-0{idx}",
                    "name": f"Stair Stringer #{idx} (Left/Center/Right)",
                    "stock": spec.stringer_stock + " 16-ft",
                    "cut_length_in": round(stringer_len_in + 12.0, 2),
                    "plumb_cut_angle_deg": round(plumb_cut_deg, 1),
                    "seat_cut_angle_deg": round(seat_cut_deg, 1),
                    "step_count": spec.riser_count,
                    "fasteners": "GRK RSS 5/16x4\" Timber Screws + PL Premium Polyurethane",
                })

            for idx in range(1, spec.riser_count):
                schedule.append({
                    "mark": f"TRD-{idx:02d}",
                    "name": f"Stair Tread #{idx}",
                    "stock": spec.tread_stock + " (Bullnosed)",
                    "cut_length_in": 36.0,
                    "plumb_cut_angle_deg": 0.0,
                    "seat_cut_angle_deg": 0.0,
                    "fasteners": "3x GRK TopStar / 3\" Deck Screws per stringer bearing",
                })

            schedule.append({
                "mark": "KCK-01",
                "name": "Base Kicker Plate",
                "stock": "2x4 AC2 Ground Contact Pressure-Treated 8-ft",
                "cut_length_in": 36.0,
                "plumb_cut_angle_deg": 0.0,
                "seat_cut_angle_deg": 0.0,
                "fasteners": "4x 1/4\"x3-1/4\" Tapcon Concrete Screw Anchors into slab",
            })

        elif isinstance(spec, SoffitSpec):
            run_in = 192.0  # Default 16-ft run
            stud_count = int(run_in // 16.0) + 1

            for idx in range(1, stud_count + 1):
                schedule.append({
                    "mark": f"DROP-{idx:02d}",
                    "name": f"Cradle Vertical Drop Leg #{idx}",
                    "stock": spec.framing_stock + " 8-ft",
                    "cut_length_in": spec.drop_in,
                    "plumb_cut_angle_deg": 0.0,
                    "seat_cut_angle_deg": 0.0,
                    "fasteners": "3x 16d Paslode framing nails into truss bottom chord",
                })
                schedule.append({
                    "mark": f"TIE-{idx:02d}",
                    "name": f"Cradle Horizontal Bottom Tie #{idx}",
                    "stock": spec.framing_stock + " 8-ft",
                    "cut_length_in": spec.width_in,
                    "plumb_cut_angle_deg": 0.0,
                    "seat_cut_angle_deg": 0.0,
                    "fasteners": "2x 16d nails each corner + Simpson Strong-Tie A35 angle",
                })

            schedule.append({
                "mark": "RUN-01",
                "name": "Continuous Bottom Plate Runner (Left)",
                "stock": spec.framing_stock + " 16-ft",
                "cut_length_in": run_in,
                "plumb_cut_angle_deg": 0.0,
                "seat_cut_angle_deg": 0.0,
                "fasteners": "16d nails into drop leg bottoms",
            })
            schedule.append({
                "mark": "RUN-02",
                "name": "Continuous Bottom Plate Runner (Right)",
                "stock": spec.framing_stock + " 16-ft",
                "cut_length_in": run_in,
                "plumb_cut_angle_deg": 0.0,
                "seat_cut_angle_deg": 0.0,
                "fasteners": "16d nails into drop leg bottoms",
            })

        return schedule

    @staticmethod
    def generate_menards_bom(
        spec: Any,
        labor_hours: float = 16.0,
        duration_days: float = 2.0
    ) -> Dict[str, Any]:
        """
        Compiles an itemized single-supplier Menards Bill of Materials (Store #3107 catalog),
        applies 15% material markup, $80/hr labor calibration, and enforces $350+/day profit floor.
        Part of DGC Core Four Contract Suite coupling.
        """
        items = []
        if isinstance(spec, StairSpec):
            items = [
                {"sku": "1112836", "desc": "2x12-16' #2 Douglas Fir Lumber (Stringers)", "qty": 3, "unit_price": 28.99},
                {"sku": "1112108", "desc": "2x12-12' Cedartone Premium Wood Treads", "qty": 4, "unit_price": 24.49},
                {"sku": "1111620", "desc": "2x4-8' AC2 Ground Contact Pressure-Treated", "qty": 1, "unit_price": 6.89},
                {"sku": "1041443", "desc": "1x8-8' Primed White Wood Risers", "qty": 5, "unit_price": 14.99},
                {"sku": "2301211", "desc": "GRK RSS 5/16\" x 4\" Structural Timber Screws (50ct)", "qty": 1, "unit_price": 31.98},
                {"sku": "2321890", "desc": "Tapcon 1/4\" x 3-1/4\" Hex Concrete Anchors (25ct)", "qty": 1, "unit_price": 18.49},
                {"sku": "5201505", "desc": "Loctite PL Premium Max Polyurethane Subfloor Adhesive (28oz)", "qty": 2, "unit_price": 12.98},
            ]
        elif isinstance(spec, SoffitSpec):
            items = [
                {"sku": "1110815", "desc": "2x4-8' Premium SPF Studs (Cradle framing)", "qty": 18, "unit_price": 4.28},
                {"sku": "1110828", "desc": "2x4-16' Premium SPF Plate Runners", "qty": 4, "unit_price": 9.98},
                {"sku": "1561021", "desc": "Pro-Rib Bright White 29-gauge Steel Liner Panel 36\"x8'", "qty": 6, "unit_price": 26.50},
                {"sku": "1564205", "desc": "Pro-Rib Bright White J-Trim 10-ft", "qty": 4, "unit_price": 11.25},
                {"sku": "1429329", "desc": "1/2\" x 2' x 4' Solid Smooth White PVC Ceiling Tile", "qty": 8, "unit_price": 14.99},
                {"sku": "1421015", "desc": "15/16\" Classic X White Main Runner 12-ft", "qty": 4, "unit_price": 18.50},
                {"sku": "1421028", "desc": "15/16\" Classic X White Cross Tee 4-ft", "qty": 10, "unit_price": 5.25},
                {"sku": "2301540", "desc": "Pro-Rib #10 x 1-1/2\" Hex Washer Head Metal Screws (250ct)", "qty": 1, "unit_price": 19.99},
                {"sku": "2181050", "desc": "Simpson Strong-Tie A35 Framing Angles (50ct box)", "qty": 1, "unit_price": 42.50},
            ]
        else:
            items = [
                {"sku": "1110815", "desc": "2x4-8' Premium SPF Studs", "qty": 10, "unit_price": 4.28},
            ]

        # Calculate line totals
        material_retail = 0.0
        bom_rows = []
        for it in items:
            line_total = round(it["qty"] * it["unit_price"], 2)
            material_retail += line_total
            bom_rows.append({
                "sku": it["sku"],
                "description": it["desc"],
                "quantity": it["qty"],
                "unit_price": it["unit_price"],
                "total_price": line_total
            })

        material_retail = round(material_retail, 2)
        # DGC 15% Material Markup
        material_marked_up = round(material_retail * 1.15, 2)
        material_markup_profit = round(material_marked_up - material_retail, 2)

        # DGC $80/hr Labor Calibration
        labor_rate_hourly = 80.00
        labor_total = round(labor_hours * labor_rate_hourly, 2)

        # Turnkey Proposal Contract Price
        contract_proposal_price = round(material_marked_up + labor_total, 2)

        # Gross margin & Daily profit check
        gross_margin = round(contract_proposal_price - material_retail, 2)
        if duration_days <= 0:
            duration_days = 1.0
        daily_profit = round(gross_margin / duration_days, 2)

        profit_floor_met = daily_profit >= 350.00

        return {
            "supplier": "Menards (Wisconsin Rapids Store #3107)",
            "line_items": bom_rows,
            "material_retail_subtotal": material_retail,
            "material_markup_rate": 0.15,
            "material_client_price": material_marked_up,
            "labor_hours": labor_hours,
            "labor_rate_hourly": labor_rate_hourly,
            "labor_client_total": labor_total,
            "turnkey_contract_proposal_price": contract_proposal_price,
            "gross_margin": gross_margin,
            "duration_days": duration_days,
            "daily_profit": daily_profit,
            "profit_floor_min_per_day": 350.00,
            "profit_floor_protected": profit_floor_met
        }

