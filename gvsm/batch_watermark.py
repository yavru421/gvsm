"""
GVSM Batch Watermarking & Forensic Registration Runner
======================================================
Scans all GVSM-related image directories, embeds the Tri-Layer Watermark
(Geodetic Collar + 2D-DCT Spread-Spectrum Steganography + Merkle Provenance),
and registers cryptographic provenance certificates for every asset.
"""

import os
import sys
import shutil
from gvsm.watermark import GVSMWatermarker

def run_batch_watermark():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    images_dir = os.path.join(repo_root, "images")

    targets = [
        # Chuck Miller Soffit
        {
            "dir": "chuck_miller_soffit",
            "job_id": "CHUCK_MILLER_HVAC_SOFFIT",
            "renders": ["gvsm_soffit_cutaway.jpg", "gvsm_foil_mesh_soffit.jpg"],
            "substrate": "before_hvac_cradle.jpg",
        },
        # Lukaszewski Stairs
        {
            "dir": "lukaszewski_stairs",
            "job_id": "LUKASZEWSKI_BASEMENT_STAIRS",
            "renders": ["gvsm_descent.jpg", "gvsm_framing_cutaway.jpg", "gvsm_remodel.jpg"],
            "substrate": "before_descent.jpg",
        },
        # Madden Patio
        {
            "dir": "madden_patio",
            "job_id": "MADDEN_OUTDOOR_PAVILION",
            "renders": [
                "gvsm_work_pavilion.jpg",
                "gvsm_literal_wedge.jpg",
                "gvsm_scrapper_nook.jpg",
                "gvsm_forensic_collapse_infographic.jpg",
            ],
            "substrate": "before_patio.jpg",
        },
        # Prahl Roof Chimney
        {
            "dir": "prahl_roof_chimney",
            "job_id": "PRAHL_ROOF_CHIMNEY_REBUILD",
            "renders": ["gvsm_chimney_ridge_cutaway.jpg", "gvsm_chimney_slope_cutaway.jpg"],
            "substrate": "before_chimney_ridge.jpg",
        },
    ]

    watermarker = GVSMWatermarker()
    results = []

    print("\n" + "="*85)
    print("GVSM REPOSITORY BATCH WATERMARK & CRYPTOGRAPHIC PROVENANCE REGISTRATION")
    print("="*85)

    for item in targets:
        folder = os.path.join(images_dir, item["dir"])
        if not os.path.exists(folder):
            continue

        job_id = item["job_id"]
        substrate_path = os.path.join(folder, item["substrate"]) if item["substrate"] else None

        for render_name in item["renders"]:
            render_path = os.path.join(folder, render_name)
            if not os.path.exists(render_path):
                continue

            # 1. Preserve original unwatermarked render as backup if not already present
            raw_backup_path = os.path.join(folder, f"raw_{render_name}")
            if not os.path.exists(raw_backup_path):
                shutil.copy2(render_path, raw_backup_path)

            # 2. Output paths: create dedicated watermarked file
            base_name, ext = os.path.splitext(render_name)
            watermarked_file_name = f"{base_name}_watermarked{ext}"
            watermarked_path = os.path.join(folder, watermarked_file_name)

            # 3. Apply Tri-Layer Watermark (Geodetic Collar + 2D-DCT + Merkle Manifest)
            res = watermarker.apply_watermark_to_file(
                input_path=raw_backup_path,
                output_path=watermarked_path,
                job_id=job_id,
                add_visible_collar=True,
                add_dct_steganography=True
            )

            # Also update primary render with watermarked version so anyone downloading gets protection
            shutil.copy2(watermarked_path, render_path)

            # 4. Immediate forensic verification
            ver = watermarker.verify_image(render_path, job_id)

            results.append({
                "folder": item["dir"],
                "render": render_name,
                "job_id": job_id,
                "sig": res.get("signature", "OK"),
                "merkle": res.get("merkle_root", "OK")[:12],
                "dct_verified": ver["dct_watermark_verified"],
                "confidence": f"{ver['dct_bit_confidence'] * 100:.1f}%",
                "status": ver["forensic_status"]
            })

    print(f"\n{'ASSET NAME':<38} | {'JOB IDENTIFIER':<26} | {'SIG':<16} | {'DCT CONF':<10} | {'STATUS'}")
    print("-" * 115)
    for r in results:
        asset_str = f"{r['folder']}/{r['render']}"
        print(f"{asset_str:<38} | {r['job_id']:<26} | {r['sig']:<16} | {r['confidence']:<10} | {r['status']}")

    print("="*115)
    print(f"Total GVSM Assets Stamped & Registered: {len(results)}")
    print("All provenance certificates written to .provenance.json files.")
    print("="*115 + "\n")


if __name__ == "__main__":
    run_batch_watermark()
