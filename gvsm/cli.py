"""
GVSM Command-Line Interface (CLI)
==================================
Usage:
  python -m gvsm.cli compile --photo <path> --memo "<text>"
  python -m gvsm.cli cad --type <stairs|soffit> --out <path.svg>
  python -m gvsm.cli validate --photo <path>
  python -m gvsm.cli serve [--port 8080]
"""

import argparse
import sys
import os
import json
from .compiler import GVSMCompiler
from .cad import CADGenerator, StairSpec, SoffitSpec, ChimneySpec
from .validator import GVSMValidator, ValidationError

from .pipeline import GVSMPipeline


def main():
    parser = argparse.ArgumentParser(
        prog="gvsm",
        description="Grounded Visual Site Modeling (GVSM) Engine"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Compile Command
    compile_parser = subparsers.add_parser("compile", help="Compile a voice memo and photo into a 5-layer GVSM prompt")
    compile_parser.add_argument("--photo", required=True, help="Path to raw on-site photo")
    compile_parser.add_argument("--memo", required=True, help="Contractor voice memo or field description")
    compile_parser.add_argument("--scope", choices=["stairs", "soffit", "landing", "chimney"], default=None, help="Explicit scope type override")
    compile_parser.add_argument("--out", default=None, help="Output directory to save bundle artifacts")

    # 2. CAD Command
    cad_parser = subparsers.add_parser("cad", help="Generate deterministic inline SVG CAD blueprints")
    cad_parser.add_argument("--type", choices=["stairs", "soffit", "chimney"], default="stairs", help="CAD drawing type")
    cad_parser.add_argument("--out", default="blueprint.svg", help="Output SVG filepath")

    # 3. Cut Schedule Command
    sched_parser = subparsers.add_parser("schedule", help="Generate piece-by-piece fabrication cut schedule")
    sched_parser.add_argument("--type", choices=["stairs", "soffit", "chimney"], default="stairs", help="Framing spec type")
    sched_parser.add_argument("--out", default=None, help="Output JSON filepath")

    # 4. BOM Command
    bom_parser = subparsers.add_parser("bom", help="Generate single-supplier Menards SKU BOM and DGC contract economics")
    bom_parser.add_argument("--type", choices=["stairs", "soffit", "chimney"], default="stairs", help="Framing spec type")
    bom_parser.add_argument("--hours", type=float, default=16.0, help="Labor hours ($80/hr calibration)")
    bom_parser.add_argument("--days", type=float, default=2.0, help="Job duration in days ($350+/day profit floor)")
    bom_parser.add_argument("--out", default=None, help="Output JSON filepath")

    # 5. Validate Command
    val_parser = subparsers.add_parser("validate", help="Pre-flight check photo and memo for GVSM invariants")
    val_parser.add_argument("--photo", required=True, help="Path to photo")
    val_parser.add_argument("--memo", default="", help="Optional memo string to check for multi-element mismatches")

    # 6. Watermark Command (Tri-Layer Protection)
    wm_parser = subparsers.add_parser("watermark", help="Apply Tri-Layer Watermark (Geodetic Collar + Invisible 2D-DCT + Merkle Provenance)")
    wm_parser.add_argument("--input", required=True, help="Path to input image to watermark")
    wm_parser.add_argument("--out", required=True, help="Path to save watermarked image")
    wm_parser.add_argument("--job", default="GVSM_JOB", help="Job identifier or client code")
    wm_parser.add_argument("--no-collar", action="store_true", help="Omit outer geodetic calibration collar")
    wm_parser.add_argument("--no-dct", action="store_true", help="Omit invisible frequency DCT steganography")

    # 7. Verify Command (Forensic Watermark & Provenance Extraction)
    ver_parser = subparsers.add_parser("verify", help="Forensically verify GVSM watermark, DCT bits, and Merkle provenance")
    ver_parser.add_argument("--input", required=True, help="Path to image to verify")
    ver_parser.add_argument("--job", default="GVSM_JOB", help="Expected Job identifier")

    # 8. Serve Command
    serve_parser = subparsers.add_parser("serve", help="Launch interactive before/after split-curtain comparison viewer")
    serve_parser.add_argument("--port", type=int, default=8080, help="Local HTTP port")

    args = parser.parse_args()

    if args.command == "compile":
        pipeline = GVSMPipeline()
        try:
            result = pipeline.run(
                photo_path=args.photo,
                voice_memo=args.memo,
                scope_type=args.scope,
                output_dir=args.out
            )
            print("\n" + "="*80)
            print("GVSM 5-LAYER PROMPT COMPILATION RECEIPT")
            print("="*80)
            if result["warning"]:
                print(f"\n[WARNING]: {result['warning']}\n")
            print(f"\n[COMPILED PROMPT]:\n{result['compiled_diffusion_prompt']}\n")
            print(f"[CAD BLUEPRINT GENERATED]: {len(result['cad_svg_blueprint'])} bytes of inline SVG")
            print(f"[CUT SCHEDULE]: {len(result['cut_schedule'])} pieces itemized")
            bom = result["menards_bom"]
            print(f"[DGC MENARDS TAKEOFF]: Turnkey Proposal ${bom['turnkey_contract_proposal_price']:.2f} "
                  f"(Materials: ${bom['material_client_price']:.2f}, Labor: ${bom['labor_client_total']:.2f}, "
                  f"Daily Profit: ${bom['daily_profit']:.2f}/day - Floor Protected: {bom['profit_floor_protected']})")
            if args.out:
                print(f"[SAVED BUNDLE]: {args.out}")
            print("="*80 + "\n")
        except ValidationError as e:
            print(f"\n[ERROR - GVSM INVARIANT VIOLATION]: {e}\n", file=sys.stderr)
            sys.exit(1)

    elif args.command == "cad":
        cad = CADGenerator()
        if args.type == "stairs":
            svg = cad.render_stair_cross_section(StairSpec())
        elif args.type == "soffit":
            svg = cad.render_soffit_cradle_section(SoffitSpec())
        else:
            svg = cad.render_chimney_elevation(ChimneySpec())
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated {args.type} blueprint saved to: {args.out}")

    elif args.command == "schedule":
        cad = CADGenerator()
        if args.type == "stairs":
            spec = StairSpec()
        elif args.type == "soffit":
            spec = SoffitSpec()
        else:
            spec = ChimneySpec()
        sched = cad.generate_cut_schedule(spec)
        sched_json = json.dumps(sched, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(sched_json)
            print(f"Cut schedule saved to: {args.out}")
        else:
            print(sched_json)

    elif args.command == "bom":
        cad = CADGenerator()
        if args.type == "stairs":
            spec = StairSpec()
        elif args.type == "soffit":
            spec = SoffitSpec()
        else:
            spec = ChimneySpec()
        bom = cad.generate_menards_bom(spec, labor_hours=args.hours, duration_days=args.days)
        bom_json = json.dumps(bom, indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(bom_json)
            print(f"Menards BOM takeoff saved to: {args.out}")
        else:
            print(bom_json)


    elif args.command == "validate":
        validator = GVSMValidator()
        try:
            validator.validate_substrate_photo(args.photo)
            print(f"[OK]: Substrate photo '{args.photo}' passed all GVSM invariants.")
            if args.memo:
                warn = validator.check_multi_element_scope(args.memo, photo_count=1)
                if warn:
                    print(f"[WARNING]: {warn}")
                else:
                    print("[OK]: Scope matches single camera frame.")
        except ValidationError as e:
            print(f"[VALIDATION FAILED]: {e}", file=sys.stderr)
            sys.exit(1)


    elif args.command == "watermark":
        from .watermark import GVSMWatermarker
        wm = GVSMWatermarker()
        res = wm.apply_watermark_to_file(
            input_path=args.input,
            output_path=args.out,
            job_id=args.job,
            add_visible_collar=not args.no_collar,
            add_dct_steganography=not args.no_dct
        )
        print("\n" + "="*80)
        print("GVSM TRI-LAYER WATERMARK RECEIPT")
        print("="*80)
        print(f"Input:        {args.input}")
        print(f"Output Image: {res.get('output_image', args.out)}")
        print(f"Job ID:       {res.get('job_id', args.job)}")
        print(f"Signature:    {res.get('signature', 'GENERATED')}")
        print(f"Merkle Root:  {res.get('merkle_root', 'COMPUTED')}")
        print(f"Provenance:   {res.get('provenance_path', 'SAVED')}")
        print("="*80 + "\n")


    elif args.command == "verify":
        from .watermark import GVSMWatermarker
        wm = GVSMWatermarker()
        ver = wm.verify_image(args.input, args.job)
        print("\n" + "="*80)
        print("GVSM FORENSIC PROVENANCE VERIFICATION")
        print("="*80)
        print(f"Target Image:      {ver['image_path']}")
        print(f"Target Job ID:     {ver['job_id']}")
        print(f"DCT Bit Verified:  {ver['dct_watermark_verified']}")
        print(f"Bit Confidence:    {ver['dct_bit_confidence'] * 100:.1f}%")
        print(f"Recovered Payload: {ver['recovered_payload_hex']}")
        print(f"Provenance JSON:   {ver['has_provenance_file']}")
        print(f"Forensic Status:   {ver['forensic_status']}")
        print("="*80 + "\n")


    elif args.command == "serve":
        import http.server
        import socketserver
        import webbrowser
        web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
        os.chdir(web_dir)
        handler = http.server.SimpleHTTPRequestHandler
        print(f"Serving GVSM Interactive Viewer at http://localhost:{args.port}")
        webbrowser.open(f"http://localhost:{args.port}")
        with socketserver.TCPServer(("", args.port), handler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nServer stopped.")


if __name__ == "__main__":
    main()
