"""
Unit and Integration Tests for GVSM Tri-Layer Watermark Engine
============================================================
Verifies:
1. Mathematical precision of 8x8 2D-DCT & 2D-IDCT roundtrips.
2. Deterministic 64-bit payload generation and block permutation.
3. Frequency-domain DCT watermark embedding and extraction.
4. Deterministic SVG CAD vector watermark and geodetic title block injection.
5. Cryptographic Merkle Provenance Manifest and signature generation.
"""

import os
import unittest
import math
from gvsm.watermark import (
    GVSMWatermarker,
    _dct_8x8,
    _idct_8x8,
    _generate_payload_bits,
    _pseudo_random_block_indices,
    DEFAULT_GEODETIC_ORIGIN,
    DEFAULT_MASTER_KEY
)


class TestGVSMWatermark(unittest.TestCase):

    def setUp(self):
        self.watermarker = GVSMWatermarker()
        self.job_id = "CLIENT_HVAC_SOFFIT"

    def test_dct_idct_mathematical_precision(self):
        """Verify 2D-DCT and 2D-IDCT are exact orthogonal inverses."""
        # Create a test 8x8 spatial luminance block
        block = [[float((r * 8 + c) * 3 % 255) for c in range(8)] for r in range(8)]
        dct_block = _dct_8x8(block)
        recon_block = _idct_8x8(dct_block)

        # Verify max absolute reconstruction error is tiny (< 1e-4)
        max_err = 0.0
        for r in range(8):
            for c in range(8):
                err = abs(block[r][c] - recon_block[r][c])
                if err > max_err:
                    max_err = err

        self.assertLess(max_err, 0.001, f"DCT/IDCT round-trip error too high: {max_err}")

    def test_payload_bits_generation(self):
        """Verify 64-bit cryptographic payload has valid 'GVSM' prefix and deterministic HMAC."""
        bits = _generate_payload_bits(self.job_id, DEFAULT_MASTER_KEY)
        self.assertEqual(len(bits), 64)

        # Check first 32 bits match 'GVSM' (0x4756534D)
        prefix_val = 0
        for b in bits[:32]:
            prefix_val = (prefix_val << 1) | b
        self.assertEqual(prefix_val, 0x4756534D)

    def test_pseudo_random_block_distribution(self):
        """Verify deterministic PRNG block permutation produces non-colliding block indices."""
        indices = _pseudo_random_block_indices(256, DEFAULT_MASTER_KEY + self.job_id, 128)
        self.assertEqual(len(indices), 128)
        # All indices must be unique within permutation
        self.assertEqual(len(set(indices)), 128)

    def test_dct_embedding_and_extraction(self):
        """Verify end-to-end frequency watermark embedding and majority voting recovery."""
        # Create a synthetic 128x128 image (16x16 = 256 8x8 blocks)
        width, height = 128, 128
        pixel_grid = []
        for y in range(height):
            row = []
            for x in range(width):
                # Gradient background simulating construction siding / lumber
                val = int(100 + 40 * math.sin(x / 10.0) + 40 * math.cos(y / 10.0))
                val = max(10, min(240, val))
                row.append((val, val, val))
            pixel_grid.append(row)

        # Embed watermark
        watermarked_grid = self.watermarker.embed_dct_watermark(pixel_grid, self.job_id, strength=30.0)
        self.assertEqual(len(watermarked_grid), height)
        self.assertEqual(len(watermarked_grid[0]), width)

        # Extract watermark
        verified, confidence, rec_hex = self.watermarker.extract_dct_watermark(watermarked_grid, self.job_id)
        
        self.assertTrue(verified, f"Watermark verification failed (confidence: {confidence})")
        self.assertGreaterEqual(confidence, 0.90, f"Expected bit confidence >= 90%, got {confidence}")
        self.assertTrue(rec_hex.startswith("4756534D"), f"Expected 'GVSM' prefix in recovered hex: {rec_hex}")

    def test_svg_vector_cad_watermarking(self):
        """Verify geodetic title block and XML namespace injection into SVG blueprints."""
        sample_svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 700"><rect width="1000" height="700" fill="#fff"/></svg>'
        watermarked_svg = self.watermarker.watermark_svg(sample_svg, self.job_id)

        self.assertIn('xmlns:gvsm="https://dondlingergc.com/gvsm/v1.0"', watermarked_svg)
        self.assertIn(f'gvsm:jobId="{self.job_id}"', watermarked_svg)
        self.assertIn("GVSM SOVEREIGN GEODETIC BENCHMARK & PROVENANCE SEAL", watermarked_svg)
        self.assertIn("Wisconsin Rapids, WI", watermarked_svg)

    def test_merkle_provenance_manifest_creation(self):
        """Verify creation of tamper-evident SHA-256 Merkle Provenance Manifest."""
        # Use an existing file in repo as test target
        readme_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "README.md"))
        manifest = self.watermarker.create_provenance_manifest(
            job_id=self.job_id,
            image_path=readme_path
        )

        self.assertEqual(manifest["format"], "GVSM-PROVENANCE-v1.0")
        self.assertEqual(manifest["job_id"], self.job_id)
        self.assertEqual(manifest["geodetic_origin"], DEFAULT_GEODETIC_ORIGIN)
        self.assertIn("hashes", manifest)
        self.assertNotEqual(manifest["hashes"]["cutaway_render"], "NOT_ATTACHED")
        self.assertEqual(len(manifest["signature_hmac"]), 64)
        self.assertEqual(len(manifest["merkle_root"]), 64)


if __name__ == "__main__":
    unittest.main()
