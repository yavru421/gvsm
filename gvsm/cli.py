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


def interactive_asset_mode(image_path: str):
    """
    Direct Interactive Mode for single asset execution:
      gvsm "<image_path>"
    Presents:
      1.) watermarker
      2.) verifier
      3.) info
    """
    from PIL import Image
    from .watermark import GVSMWatermarker

    image_path = image_path.strip('\'"')
    if not os.path.exists(image_path):
        print(f"\n[ERROR]: Target file does not exist: {image_path}\n", file=sys.stderr)
        sys.exit(1)

    base_name = os.path.basename(image_path)
    stem, ext = os.path.splitext(base_name)
    parent_dir = os.path.dirname(os.path.abspath(image_path))
    parent_folder = os.path.basename(parent_dir)
    default_job = parent_folder if parent_folder and parent_folder != "." else "GVSM_JOB"

    # Check for adjacent provenance manifest
    prov_path = os.path.join(parent_dir, f"{stem}.provenance.json")
    if not os.path.exists(prov_path):
        orig_stem = stem.replace("_watermarked", "")
        alt_prov = os.path.join(parent_dir, f"{orig_stem}.provenance.json")
        if os.path.exists(alt_prov):
            prov_path = alt_prov

    manifest_data = None
    if os.path.exists(prov_path):
        try:
            with open(prov_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                if "job_id" in manifest_data:
                    default_job = manifest_data["job_id"]
        except Exception:
            pass

    print("\n" + "=" * 80)
    print(f"GVSM ASSET INTERACTIVE WORKFLOW: {base_name}")
    print("=" * 80)
    print(f"Path: {image_path}\n")
    print("1.) watermarker")
    print("2.) verifier")
    print("3.) info\n")

    try:
        choice = input("Select option [1-3]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        sys.exit(0)

    wm = GVSMWatermarker()

    if choice in ("1", "watermarker", "watermark"):
        print("\n--- [1] GVSM TRI-LAYER WATERMARKER ---")
        job_prompt = input(f"Job ID [{default_job}]: ").strip()
        job_id = job_prompt if job_prompt else default_job

        default_out_dir = parent_dir
        out_prompt = input(f"Output directory or file [{default_out_dir}]: ").strip()
        out_target = out_prompt if out_prompt else default_out_dir

        if os.path.isdir(out_target):
            out_file = os.path.join(out_target, f"{stem}_watermarked{ext if ext else '.png'}")
        else:
            out_file = out_target

        print(f"\nProcessing watermark with Wisconsin Rapids geodetic collar & 2D-DCT frequency stego...")
        res = wm.apply_watermark_to_file(
            input_path=image_path,
            output_path=out_file,
            job_id=job_id,
            add_visible_collar=True,
            add_dct_steganography=True
        )

        print("\n" + "=" * 80)
        print("GVSM TRI-LAYER WATERMARK RECEIPT")
        print("=" * 80)
        print(f"Input:        {image_path}")
        print(f"Output Image: {res['output_image']}")
        print(f"Job ID:       {res['job_id']}")
        print(f"Signature:    {res['signature']}")
        print(f"Merkle Root:  {res['merkle_root']}")
        print(f"Provenance:   {res['provenance_path']}")
        print("=" * 80 + "\n")

    elif choice in ("2", "verifier", "verify"):
        print("\n--- [2] GVSM AUTONOMOUS VERIFIER ---")
        print("Inspecting visible geodetic collar & embedded 17 U.S.C. § 1202 metadata...")
        ver = wm.verify_image(image_path)

        print("\n" + "=" * 80)
        print("GVSM FORENSIC PROVENANCE VERIFICATION")
        print("=" * 80)
        print(f"Target Image:        {ver.get('image_path', image_path)}")
        print(f"Job ID:              {ver.get('job_id', 'N/A')}")
        print(f"Visible Collar:      {'DETECTED' if ver.get('has_visible_collar') else 'NOT DETECTED'}")
        print(f"Embedded Author:     {ver.get('embedded_author', 'None')}")
        print(f"Embedded Scope:      {ver.get('embedded_description', 'None')}")
        print(f"Provenance File:     {'FOUND' if ver.get('has_provenance_file') else 'NONE (Self-Contained in Image)'}")
        print(f"Statutory Shield:    {ver.get('statutory_shield', 'None')}")
        print(f"Forensic Status:     {ver.get('forensic_status', 'UNKNOWN')}")
        print("=" * 80 + "\n")

    elif choice in ("3", "info", "information"):
        print("\n--- [3] GVSM ASSET METADATA & TELEMETRY ---")
        file_size = os.path.getsize(image_path)
        img = Image.open(image_path)
        w, h = img.size
        mp = (w * h) / 1_000_000.0

        print(f"Filename:            {base_name}")
        print(f"Full Path:           {os.path.abspath(image_path)}")
        print(f"File Size:           {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
        print(f"Dimensions:          {w} x {h} px ({mp:.2f} Megapixels)")
        print(f"Aspect Ratio:        {w/h:.3f} ({w}:{h})")
        print(f"Image Format:        {img.format} ({img.mode})")

        has_prov = os.path.exists(prov_path)
        print(f"Provenance Manifest: {'FOUND (' + prov_path + ')' if has_prov else 'NOT FOUND'}")
        if manifest_data:
            print(f"  • Format:          {manifest_data.get('format', 'N/A')}")
            print(f"  • Job ID:          {manifest_data.get('job_id', 'N/A')}")
            print(f"  • Timestamp:       {manifest_data.get('timestamp_iso', 'N/A')}")
            print(f"  • Operator:        {manifest_data.get('operator', 'N/A')}")
            print(f"  • Datum:           {manifest_data.get('geodetic_origin', 'N/A')}")
            print(f"  • Merkle Root:     {manifest_data.get('merkle_root', 'N/A')[:16]}...")
            print(f"  • Signature:       {manifest_data.get('signature_hmac', 'N/A')[:16]}...")

        print(f"Statutory Shield:    17 U.S.C. § 1202 Protection Protocol Active")
        print("=" * 80 + "\n")

    else:
        print("Exiting.")
        sys.exit(0)


def main():
    KNOWN_COMMANDS = {"compile", "cad", "schedule", "bom", "validate", "watermark", "verify", "catalog", "serve", "-h", "--help"}

    # Intercept direct image argument: gvsm "<path>"
    if len(sys.argv) >= 2:
        arg1 = sys.argv[1].strip('\'"')
        if arg1 not in KNOWN_COMMANDS and not arg1.startswith("-"):
            ext = os.path.splitext(arg1)[1].lower()
            if os.path.isfile(arg1) or ext in (".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"):
                interactive_asset_mode(arg1)
                return

    # If invoked with no args at all: gvsm
    if len(sys.argv) == 1:
        try:
            print("\n" + "=" * 80)
            print("GVSM (Grounded Visual Site Modeling) Sovereign Engine")
            print("=" * 80)
            path_input = input("Enter path to image asset (or press Enter for CLI help): ").strip('\'" \t')
            if path_input:
                interactive_asset_mode(path_input)
                return
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

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
    compile_parser.add_argument("--out", "--output", dest="out", default=None, help="Output directory to save bundle artifacts")

    # 2. CAD Command
    cad_parser = subparsers.add_parser("cad", help="Generate deterministic inline SVG CAD blueprints")
    cad_parser.add_argument("--type", choices=["stairs", "soffit", "chimney"], default="stairs", help="CAD drawing type")
    cad_parser.add_argument("--out", "--output", dest="out", default="blueprint.svg", help="Output SVG filepath")

    # 3. Cut Schedule Command
    sched_parser = subparsers.add_parser("schedule", help="Generate piece-by-piece fabrication cut schedule")
    sched_parser.add_argument("--type", choices=["stairs", "soffit", "chimney"], default="stairs", help="Framing spec type")
    sched_parser.add_argument("--out", "--output", dest="out", default=None, help="Output JSON filepath")

    # 4. BOM Command
    bom_parser = subparsers.add_parser("bom", help="Generate single-supplier Menards SKU BOM and DGC contract economics")
    bom_parser.add_argument("--type", choices=["stairs", "soffit", "chimney"], default="stairs", help="Framing spec type")
    bom_parser.add_argument("--hours", type=float, default=16.0, help="Labor hours ($80/hr calibration)")
    bom_parser.add_argument("--days", type=float, default=2.0, help="Job duration in days ($350+/day profit floor)")
    bom_parser.add_argument("--out", "--output", dest="out", default=None, help="Output JSON filepath")

    # 5. Validate Command
    val_parser = subparsers.add_parser("validate", help="Pre-flight check photo and memo for GVSM invariants")
    val_parser.add_argument("--photo", required=True, help="Path to photo")
    val_parser.add_argument("--memo", default="", help="Optional memo string to check for multi-element mismatches")

    # 6. Watermark Command (Tri-Layer Protection)
    wm_parser = subparsers.add_parser("watermark", help="Apply Tri-Layer Watermark (Geodetic Collar + Invisible 2D-DCT + Merkle Provenance)")
    wm_parser.add_argument("--input", required=True, help="Path to input image to watermark")
    wm_parser.add_argument("--out", "--output", dest="out", required=True, help="Path to save watermarked image or directory")
    wm_parser.add_argument("--job", default="GVSM_JOB", help="Job identifier or client code")
    wm_parser.add_argument("--no-collar", action="store_true", help="Omit outer geodetic calibration collar")
    wm_parser.add_argument("--no-dct", action="store_true", help="Omit invisible frequency DCT steganography")

    # 7. Verify Command (Forensic Watermark & Provenance Extraction)
    ver_parser = subparsers.add_parser("verify", help="Forensically verify GVSM watermark, DCT bits, and Merkle provenance")
    ver_parser.add_argument("--input", required=True, help="Path to image to verify")
    ver_parser.add_argument("--job", default="GVSM_JOB", help="Expected Job identifier")

    # 8. Catalog Command
    cat_parser = subparsers.add_parser("catalog", help="Catalog GVSM watermark specification into persistent mind.duckdb")
    cat_parser.add_argument("--db", default=None, help="Target DuckDB database path")

    # 9. Serve Command
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
        out_path = args.out
        if os.path.isdir(out_path):
            base_name = os.path.basename(args.input)
            stem, ext = os.path.splitext(base_name)
            out_path = os.path.join(out_path, f"{stem}_watermarked{ext if ext else '.png'}")

        res = wm.apply_watermark_to_file(
            input_path=args.input,
            output_path=out_path,
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
        print(f"Target Image:        {ver.get('image_path', args.input)}")
        print(f"Job ID:              {ver.get('job_id', 'N/A')}")
        print(f"Visible Collar:      {'DETECTED' if ver.get('has_visible_collar') else 'NOT DETECTED'}")
        print(f"Embedded Author:     {ver.get('embedded_author', 'None')}")
        print(f"Embedded Scope:      {ver.get('embedded_description', 'None')}")
        print(f"Provenance File:     {'FOUND' if ver.get('has_provenance_file') else 'NONE (Self-Contained in Image)'}")
        print(f"Statutory Shield:    {ver.get('statutory_shield', 'None')}")
        print(f"Forensic Status:     {ver.get('forensic_status', 'UNKNOWN')}")
        print("="*80 + "\n")


    elif args.command == "catalog":
        from .watermark import GVSMWatermarker
        wm = GVSMWatermarker()
        res = wm.catalog_to_duckdb(args.db)
        print("\n" + "="*80)
        print("GVSM WATERMARK SPECIFICATION CATALOGED TO DUCKDB")
        print("="*80)
        print(f"Database:      {res['database']}")
        print(f"Spec ID:       {res['spec_id']}")
        print(f"Registered At: {res['registered_at']}")
        print(f"Datum Origin:  {res['datum_origin']}")
        print(f"Operator:      {res['operator']}")
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
