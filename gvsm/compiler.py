"""
GVSM 5-Layer Semantic Prompt Compiler
======================================
Transforms unstructured voice field notes and tradesman specifications into
strict, multimodal latent diffusion prompts anchored to physical site substrates.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import re


@dataclass
class PromptSpec:
    """Structured representation of a 5-layer GVSM prompt specification."""
    substrate: str
    cladding: str
    finish: str
    cutaway: Optional[str] = None
    macro_inset: Optional[str] = None
    preservations: List[str] = field(default_factory=list)
    aspect_ratio: str = "16:9"
    image_paths: List[str] = field(default_factory=list)
    style: str = "Photorealistic architectural visualization, professional contractor presentation style, crisp architectural lighting, zero geometric distortion"
    geodetic_origin: str = "Wisconsin Rapids, WI (44°23'36\" N, 89°49'23\" W)"

    def compile(self) -> str:
        """Compile the 5 layers into a single cohesive multimodal prompt."""
        parts = []
        
        # Base Framing Directives
        parts.append(
            f"Photorealistic architectural cutaway visualization built directly onto the exact visible substrate shown in the reference image."
        )
        
        # Layer 1: Substrate Grounding & Preservations
        if self.preservations:
            pres_str = ", ".join(self.preservations)
            parts.append(
                f"[SUBSTRATE GROUNDING]: Maintain authentic existing {pres_str} exactly as photographed without alteration or repainting. {self.substrate}"
            )
        else:
            parts.append(f"[SUBSTRATE GROUNDING]: {self.substrate}")
            
        # Layer 2: Cladding & Trade Specifications
        parts.append(f"[CLADDING & PROFILES]: {self.cladding}")
        
        # Layer 3: Finish & Underside Assemblies
        parts.append(f"[FINISH ASSEMBLIES]: {self.finish}")
        
        # Layer 4: Architectural Cutaway
        if self.cutaway:
            parts.append(f"[ARCHITECTURAL CUTAWAY]: {self.cutaway}")
            
        # Layer 5: Macro Detail Inset
        if self.macro_inset:
            parts.append(f"[MACRO DETAIL INSET]: {self.macro_inset}")
            
        # Style & Lighting Guardrails
        parts.append(f"[PRESENTATION]: {self.style}.")
        
        return " ".join(parts)


class GVSMCompiler:
    """
    Parses natural field voice notes and builds hardened GVSM prompt specifications.
    Enforces the 'Anti-Hallucination Invariant' (Rule 11).
    """

    # Trade Material Keywords & SKU Mappings
    TRADE_KEYWORDS = {
        "prorib": "vertical Bright White 29-gauge Pro-Rib ribbed steel liner panels with color-matched hex washer screws on rib flats and white J-trim perimeters",
        "cedartone": "premium solid 2x12 Cedartone wood treads with smooth bullnosed front edges, satin white risers, and matching Cedartone skirt trim",
        "drop_grid": "15/16-inch heavy-duty white suspended ceiling grid holding 1/2-inch solid smooth white PVC panels (Menards SKU 1429329)",
        "polyiso": "suspended Classic X 15/16-inch drop ceiling grid with custom-cut 1-inch foil-faced rigid polyiso insulation panels",
        "polycarbonate": "low-profile architectural canopy with bronze/smoke semi-translucent polycarbonate twin-wall roof panels in aluminum glazing bars",
        "craftsman_rail": "modern 2x2 craftsman-profile eased stained wood handrail mounted at 36-inch height with code-compliant 90-degree wall returns",
        "grk_screws": "structural framing joined with GRK RSS 5/16x4-inch heavy-duty structural timber screws and PL Premium polyurethane adhesive",
        "tapcon_anchors": "AC2 treated bottom kicker plate secured into concrete slab with 1/4x3-1/4-inch hex head Tapcon concrete anchors",
        "simpson_angles": "cradle perimeter corners and drop legs reinforced with Simpson Strong-Tie A35 structural framing angles",
    }


    def __init__(self):
        pass

    def parse_voice_memo(self, transcript: str, photo_paths: List[str]) -> PromptSpec:
        """
        Parses a raw voice memo transcript into a structured PromptSpec.
        Extracts existing elements, new scopes, materials, and cutaways.
        """
        lower = transcript.lower()

        # 1. Detect Preservations (Things to keep untouched)
        preservations = []
        if "door" in lower:
            if "red" in lower or "9-lite" in lower:
                preservations.append("red 9-lite entry door")
            elif "preserve" in lower or "keep" in lower:
                preservations.append("existing doorway and jamb")
        if "concrete" in lower or "slab" in lower or "patio" in lower:
            if "stamped" in lower:
                preservations.append("stamped concrete patio slab")
            else:
                preservations.append("concrete floor slab")
        if "window" in lower:
            preservations.append("house window and casing")
        if "fence" in lower:
            preservations.append("wooden privacy fence")
        if "truss" in lower or "rafter" in lower or "joist" in lower:
            preservations.append("ceiling trusses and rafters")
        if "wall" in lower or "siding" in lower:
            if "vinyl" in lower:
                preservations.append("vinyl siding house wall")
            else:
                preservations.append("existing walls")

        # 2. Extract or Synthesize Substrate Grounding
        substrate = "Build onto the visible framing members and spatial boundaries."
        if "stair" in lower:
            substrate = "Anchor to the exact staircase footprint, wall partitions, and floor openings visible in the reference photo."
        elif "soffit" in lower or "cradle" in lower or "hvac" in lower:
            substrate = "Built directly onto the suspended 2x4 wooden framing cradle and ceiling joists visible in the reference photo."
        elif "patio" in lower or "canopy" in lower or "roof" in lower:
            substrate = "Freestanding timber structure anchored on the patio slab bounded between the house wall and perimeter fence."

        # 3. Detect Cladding & Materials
        cladding = "Finished with high-grade commercial trade materials and clean trim terminations."
        if "pro-rib" in lower or "rib" in lower or "metal" in lower or "steel" in lower:
            cladding = self.TRADE_KEYWORDS["prorib"]
        elif "cedar" in lower or "cedartone" in lower or "tread" in lower:
            cladding = self.TRADE_KEYWORDS["cedartone"]
        elif "timber" in lower or "pavilion" in lower or "post" in lower:
            cladding = "heavy-timber 6x6 pressure-treated posts with diagonal 4x4 structural knee braces and horizontal header beams"

        # 4. Detect Finish & Underside
        finish = "Clean architectural transitions with color-matched hardware and clean perimeter seals."
        if "polyiso" in lower or "foil" in lower:
            finish = self.TRADE_KEYWORDS["polyiso"]
        elif "polycarbonate" in lower or "translucent" in lower:
            finish = self.TRADE_KEYWORDS["polycarbonate"]
        elif "drop ceiling" in lower or "grid" in lower or "tile" in lower or "pvc" in lower:
            finish = self.TRADE_KEYWORDS["drop_grid"]
        elif "riser" in lower or "stair" in lower:
            finish = "satin white solid risers, matching side skirts scribed tight to walls, and craftsman handrail"

        # 5. Detect Cutaway Directive
        cutaway = None
        if "cutaway" in lower or "peel" in lower or "reveal" in lower or "rough" in lower or "inside" in lower or "x-ray" in lower:
            if "stair" in lower:
                cutaway = "Peel back drywall along the right mid-flight partition to reveal triple 2x12 cut stringers, heavy subfloor adhesive bedding, and Tapcon-anchored AC2 treated kicker plate on the slab."
            elif "hvac" in lower or "furnace" in lower or "duct" in lower or "soffit" in lower:
                cutaway = "A clean diagonal 45-degree cutaway on the front face peels back the steel liner to reveal the horizontal furnace unit, spiral supply ductwork, and electrical rough-ins inside the cradle."
            elif "header" in lower or "headroom" in lower:
                cutaway = "Upper ceiling bulkhead cutaway exposes the double 2x10 SPF header with Simpson Strong-Tie face-mount joist hangers creating 80-inch clear vertical headroom."

        # 6. Detect Macro Inset
        macro_inset = None
        if "detail" in lower or "zoom" in lower or "inset" in lower or "callout" in lower:
            if "stair" in lower:
                macro_inset = "Circular 10x architectural zoom inset highlighting the countersunk GRK RSS structural timber screw and polyurethane adhesive bed between tread and stringer notch."
            elif "soffit" in lower or "grid" in lower:
                macro_inset = "Circular 10x architectural zoom callout illustrating the closed-cell EPDM gasket tape compressed between the steel grid flange and PVC panel."
            else:
                macro_inset = "Circular 10x detail inset showing post-to-slab Simpson Strong-Tie anchor base connection."

        return PromptSpec(
            substrate=substrate,
            cladding=cladding,
            finish=finish,
            cutaway=cutaway,
            macro_inset=macro_inset,
            preservations=preservations,
            image_paths=photo_paths,
        )
