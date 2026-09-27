# GROUNDED VISUAL SITE MODELING (GVSM)
## System Formalization, Spatial Grounding Kinematics & Mathematical Specification

**Document Version**: 2.0.0-PROD  
**Geodetic Benchmark Origin**: $44^\circ 23' 36''\text{ N}, 89^\circ 49' 23''\text{ W}$ (Wisconsin Rapids, Wood County, WI, USA)  
**Host Hardware Target**: NVIDIA Ada Lovelace AD107 (GeForce RTX 4060 Laptop GPU, SM_89, 8GB GDDR6, 32MB L2 Cache)  
**Underlying C-ABI Acceleration Core**: `cu_vision_lite_sm89.dll`, `cu_dense_stereo.dll`, `turbo_cuda.dll`  
**Operational Standard**: Zero-Liability Architecture (ZLA), Rule 11 (Dual-Deliverable Truth Composition), DGC Core Four Contract Suite  
**Statutory Framework**: Wisconsin Uniform Dwelling Code (SPS Chapters 320–325), Wisconsin Commercial Building Code (SPS Chapters 361–366)

---

## 1. Executive Vision & Foundational Paradigm

### 1.1 The Operational Paradox of Construction Visualization
In contracting and remodeling, bidding accuracy and customer comprehension represent the primary failure points of small and mid-sized enterprises. The traditional paradigm forces contractors into one of three dead ends:
1. **The Abstract Estimate**: Written text descriptions or QuickBooks line items (`"Frame soffit, hang steel liner — $5,400"`). Clients cannot visualize spatial volume, resulting in decision paralysis, sticker shock, or contentious post-build disputes.
2. **Traditional ArchViz Meshing**: Revit, Lumion, SketchUp, or 3ds Max workflows requiring 12 to 30 hours of manual poly modeling, texture mapping, and lighting setup per scene—economically non-viable for rapid $2,000 to $25,000 contracting proposals.
3. **Unanchored Text-to-Image AI**: Monolithic diffusion models (Midjourney, DALL-E, unguided Stable Diffusion) that synthesize imagery from pure Gaussian noise without spatial substrates. These systems warp structural framing, invent non-existent walls, violate load paths, hallucinate non-code stairs, and destroy legal and technical credibility.

### 1.2 The GVSM Solution: Grounded Physical Invariance
**Grounded Visual Site Modeling (GVSM)** establishes a mathematically rigorous, hardware-accelerated pipeline that synthesizes **two complementary layers of truth** from authentic on-site camera frames:
- **Layer 1: The Client Visualization & Excitement Layer**: Photorealistic architectural cutaway imagery anchored to the physical perspective lines, lighting vectors, and substrate geometry of the real room.
- **Layer 2: The Fabrication & Dimensional Truth Layer**: Millimeter-accurate vector CAD drawings (SVG/DXF), itemized cut schedules, and Menards single-supplier Bill of Materials (BOM) for John's field crew.

```
+--------------------------------------------------------------------------------------------------+
|                                  THE GVSM DUAL-DELIVERABLE MATRIX                                |
+------------------------------------+-------------------------------------------------------------+
| LAYER 1: CLIENT EXCITEMENT         | LAYER 2: FABRICATION TRUTH                                  |
| - Photorealistic finish cutaway    | - Millimeter-accurate SVG/DXF cross-sections & elevations   |
| - Anchored directly to site photo  | - Itemized framing cut schedules (lengths, angles, stock)   |
| - Trade materials (Pro-Rib, Cedar) | - Menards SKU-coded procurement BOM                         |
| - Visualizes rough-ins & MEP       | - SPS 321 code compliance citations & load path verification|
| - Approved on sight with zero hes. | - Direct handoff to carpenter on the jobsite                |
+------------------------------------+-------------------------------------------------------------+
```

---

## 2. Mathematical Formalization of the Spatial Perception Engine

The GVSM spatial perception engine ingests 2D camera frames and recovers metric 3D scene structure using AD107 CUDA-accelerated feature tracking and non-linear optimization.

```
+--------------------------------------------------------------------------------------------------+
|                              END-TO-END GVSM SPATIAL PIPELINE                                    |
+--------------------------------------------------------------------------------------------------+
                                                 |
                                                 v
  +----------------------------------------------------------------------------------------------+
  | 1. RAW SUBSTRATE INGESTION & PRE-FLIGHT VALIDATION                                           |
  |    - Image verification, EXIF focal length extraction, resolution normalization              |
  |    - Anti-Refeed Guard: `is_ai_artifact(path) == False` (Prevents generative recursive drift)|
  |    - One Substrate, One Frame Law: Detect multi-element scope mismatches                     |
  +----------------------------------------------------------------------------------------------+
                                                 |
                                                 v
  +----------------------------------------------------------------------------------------------+
  | 2. AD107 CUDA LANDMARK EXTRACTION & GEOPIN TRACKING (`cu_vision_lite_sm89.dll`)              |
  |    - FAST-16 / Harris corner detection on 16x16 macroblock grids                             |
  |    - Normalized Cross-Correlation (NCC) sub-pixel patch matching ($r = 15\text{ px}$)        |
  |    - Bi-directional forward-backward temporal consistency gate ($\Delta < 0.25\text{ px}$)   |
  +----------------------------------------------------------------------------------------------+
                                                 |
                                                 v
  +----------------------------------------------------------------------------------------------+
  | 3. 6-DoF LEVENBERG-MARQUARDT PERSPECTIVE-N-POINT (PnP) SOLVER                                |
  |    - Substrate ground-plane & wall normal estimation ($\hat{n}_{\text{floor}}, \hat{n}_{\text{wall}}$)              |
  |    - Metric scale calibration via physical structural priors (16" O.C. studs, 48" Baker deck) |
  |    - Sub-pixel reprojection error gate: $\epsilon_{\text{reproj}} < 1.2\text{ px}$            |
  |    - Planar orthogonality constraint: $|\arccos(\hat{n}_w \cdot \hat{n}_f) - 90^\circ| < 0.5^\circ$|
  +----------------------------------------------------------------------------------------------+
                                                 |
                                                 v
  +----------------------------------------------------------------------------------------------+
  | 4. PARAMETRIC STRUCTURAL CAD COMPILER (`gvsm.cad`)                                           |
  |    - Extraction of boundary conditions, total rise/run, spans, clearances                    |
  |    - Synthesis of vector geometry: stringer profiles, drop cradles, timber posts             |
  |    - SPS 321.04 headroom rake verification ($h_{\text{clear}} \ge 80.0''$)                   |
  +----------------------------------------------------------------------------------------------+
                                                 |
                        +------------------------+------------------------+
                        |                                                 |
                        v                                                 v
  +-------------------------------------------+     +-------------------------------------------+
  | LAYER 1: CLIENT EXCITEMENT (DIFFUSION)    |     | LAYER 2: FABRICATION TRUTH (BLUEPRINT)    |
  | - 5-Layer Semantic Prompt Compilation     |     | - Inline SVG & DXF Vector Schematics      |
  | - Physical substrate image anchoring      |     | - Piece-by-piece cut schedule JSON        |
  | - Latent cutaway revealing internal MEP   |     | - Menards single-supplier itemized BOM    |
  | - Macro-inset corner joint details        |     | - DGC Core Four contract documents        |
  +-------------------------------------------+     +-------------------------------------------+
```

### 2.1 Pinhole Camera Model & Intrinsic Calibration
Let a physical 3D scene point in world Euclidean coordinates be denoted by:
$$P_w = \begin{bmatrix} X_w \\ Y_w \\ Z_w \\ 1 \end{bmatrix} \in \mathbb{P}^3$$

The calibrated camera matrix $K \in \mathbb{R}^{3 \times 3}$ projects 3D camera coordinates $P_c = [X_c, Y_c, Z_c]^T$ onto the 2D image plane:
$$K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$
where:
- $f_x, f_y$ are the focal lengths expressed in pixel dimensions (derived from physical sensor width $S_w$, image width $W$, and optical focal length $F_{\text{mm}}$: $f_x = \frac{F_{\text{mm}} \cdot W}{S_w}$).
- $c_x, c_y$ is the principal point, centered at $(W/2, H/2)$ for zero-decenter optical systems.

The rigid-body transformation from the world frame to the camera coordinate frame is parameterized by the Special Euclidean group Lie algebra $\mathbf{T} = [R | t] \in \mathbb{SE}(3)$, where $R \in \mathbb{SO}(3)$ is a $3 \times 3$ orthonormal rotation matrix and $t \in \mathbb{R}^3$ is the 3D translation vector:
$$P_c = \begin{bmatrix} X_c \\ Y_c \\ Z_c \end{bmatrix} = R P_w + t$$

The homogeneous projection onto the 2D pixel coordinate $p = [u, v]^T$ is given by:
$$s \begin{bmatrix} u \\ v \\ 1 \end{bmatrix} = K \left( R \begin{bmatrix} X_w \\ Y_w \\ Z_w \end{bmatrix} + t \right), \quad s = Z_c$$
$$\pi(K, R, t, P_w) = \begin{bmatrix} f_x \frac{X_c}{Z_c} + c_x \\ f_y \frac{Y_c}{Z_c} + c_y \end{bmatrix} = \begin{bmatrix} u \\ v \end{bmatrix}$$

---

### 2.2 AD107 CUDA Levenberg-Marquardt PnP Optimization
Given $N \ge 4$ 2D observed feature landmarks $p_i = [u_i, v_i]^T$ and their corresponding 3D structural model landmarks $P_{w,i} = [X_{w,i}, Y_{w,i}, Z_{w,i}]^T$ extracted from known jobsite framing geometry, the 6-DoF pose $\xi \in \mathfrak{se}(3)$ is solved by minimizing the non-linear reprojection error:
$$E(\xi) = \frac{1}{2} \sum_{i=1}^N \| r_i(\xi) \|^2_2 = \frac{1}{2} \sum_{i=1}^N \| p_i - \pi(K, \exp(\hat{\xi}), P_{w,i}) \|^2_2$$

Where $\xi = [\omega_1, \omega_2, \omega_3, \nu_1, \nu_2, \nu_3]^T \in \mathbb{R}^6$ represents the twist coordinates mapped to $\mathbb{SE}(3)$ via the exponential map:
$$\exp(\hat{\xi}) = \begin{bmatrix} \exp(\hat{\omega}) & V \nu \\ 0 & 1 \end{bmatrix}$$

The iterative Levenberg-Marquardt step solves the damped normal equations:
$$(J^T J + \lambda \, \text{diag}(J^T J)) \Delta \xi = -J^T r$$
where:
- $J \in \mathbb{R}^{2N \times 6}$ is the stacked Jacobian matrix of partial derivatives $\frac{\partial r_i}{\partial \xi}$.
- $r \in \mathbb{R}^{2N}$ is the stacked residual vector.
- $\lambda \in \mathbb{R}^+$ is the adaptive damping parameter adjusted according to the Marquardt gain ratio:
  $$\rho = \frac{\|r(\xi)\|^2 - \|r(\xi + \Delta \xi)\|^2}{2 \Delta \xi^T (\lambda \Delta \xi - J^T r)}$$

When $\rho > 0$, the step is accepted and $\lambda \leftarrow \lambda \cdot \max(1/3, 1 - (2\rho - 1)^3)$; otherwise, the step is rejected and $\lambda \leftarrow \lambda \cdot 2$.

---

### 2.3 Physical Substrate Ground-Plane & Vanishing Point Extraction
Jobsite substrates define dominant planar surfaces (concrete slabs, subfloors, plumb stud walls, ceiling truss bottom chords).

A physical plane $\Pi$ in camera space satisfies:
$$n^T P_c + d = 0, \quad \hat{n} = \begin{bmatrix} n_x \\ n_y \\ n_z \end{bmatrix}, \quad \|\hat{n}\|_2 = 1$$
where $\hat{n}$ is the unit normal vector and $d$ is the perpendicular distance from the camera optical center to the plane.

#### Orthogonal Vanishing Point Triad
From Manhattan world structures (16" O.C. stud walls, level ceiling joists, plumb vertical drop legs), three mutually orthogonal vanishing points $V_x, V_y, V_z \in \mathbb{P}^2$ emerge from parallel line clusters in the image:
$$V_k = K R e_k, \quad k \in \{x, y, z\}, \quad e_x = \begin{bmatrix} 1 \\ 0 \\ 0 \end{bmatrix}, \, e_y = \begin{bmatrix} 0 \\ 1 \\ 0 \end{bmatrix}, \, e_z = \begin{bmatrix} 0 \\ 0 \\ 1 \end{bmatrix}$$

Because the world coordinate axes are mutually orthogonal ($e_j^T e_k = 0$ for $j \neq k$):
$$V_j^T \omega V_k = 0 \quad (\forall j \neq k)$$
where $\omega = (K K^T)^{-1}$ is the Image of the Absolute Conic (IAC). This allows instantaneous closed-form verification of camera focal length and optical axis tilt directly from jobsite framing lines.

---

## 3. Anti-Hallucination & Grounding Invariants

To guarantee that generative visual layers never corrupt physical reality, GVSM enforces four non-negotiable mathematical and operational invariants:

```
+--------------------------------------------------------------------------------------------------+
|                               GVSM HARDWARE & MATHEMATICAL GATES                                 |
+------------------------------------+------------------------------------+------------------------+
| INVARIANT                          | MATHEMATICAL TOLERANCE             | FAILURE RECOVERY       |
+------------------------------------+------------------------------------+------------------------+
| 1. Sub-pixel Reprojection Error    | $\epsilon_{\text{reproj}} < 1.20\text{ px}$ | Discard ungrounded pin |
| 2. Planar Orthogonality Tolerance  | $\Delta\theta_{\text{ortho}} < 0.50^\circ$  | Reject warped normals  |
| 3. Metric Scale Closure Tolerance  | $\eta_{\text{scale}} < 1.50\%$     | Re-index physical stud |
| 4. Anti-Refeed Guard               | $P(\text{AI artifact}) == 0.0$     | Hard halt / Reset raw  |
+------------------------------------+------------------------------------+------------------------+
```

### 3.1 Sub-Pixel Reprojection Error Invariant ($\epsilon_{\text{reproj}} < 1.2\text{ px}$)
The mean reprojection error across all calibrated substrate landmarks must not exceed $1.2$ pixels on a $1920 \times 1080$ frame:
$$\epsilon_{\text{reproj}} = \frac{1}{N} \sum_{i=1}^N \sqrt{(u_i - \hat{u}_i)^2 + (v_i - \hat{v}_i)^2} < 1.20\text{ px}$$
- If $\epsilon_{\text{reproj}} \ge 1.20\text{ px}$, the landmark constellation is rejected for poor conditioning. Outliers with individual residuals $e_i > 2.5\text{ px}$ are pruned via RANSAC before re-solving.

### 3.2 Planar Orthogonality Invariant ($\Delta\theta_{\text{ortho}} < 0.5^\circ$)
In structural framing, walls must be plumb to gravity and orthogonal to level subfloors. Let $\hat{n}_{\text{floor}}$ be the estimated normal of the floor plane and $\hat{n}_{\text{wall}}$ be the normal of an adjacent bearing wall. The orthogonality deviation is strictly bounded:
$$\Delta\theta_{\text{ortho}} = \left| \arccos\left(\hat{n}_{\text{floor}} \cdot \hat{n}_{\text{wall}}\right) - 90.00^\circ \right| < 0.50^\circ$$
- If the estimated angle deviates by $\ge 0.5^\circ$, the system triggers a plane normal re-projection using gravity vector alignment derived from vertical door jambs and corner studs.

### 3.3 Metric Scale Closure Invariant ($\eta_{\text{scale}} < 1.5\%$)
Scale cannot be recovered from monocular vision alone without physical substrate anchors. GVSM binds scale using known construction constants:
- Standard wall stud center-to-center spacing: $16.00''$ ($406.4\text{ mm}$) or $24.00''$ ($609.6\text{ mm}$).
- Standard drop grid runner spacing: $24.00''$ or $48.00''$.
- Standard Baker scaffold frame height: $72.00''$ ($1828.8\text{ mm}$) with $29.00''$ width.
- Standard exterior door rough opening width: $38.00''$ for a $36''$ door.

The metric scale closure ratio $\eta_{\text{scale}}$ is computed against a secondary ground-truth span:
$$\eta_{\text{scale}} = \frac{\left| L_{\text{derived}} - L_{\text{physical}} \right|}{L_{\text{physical}}} < 0.015 \quad (1.5\%)$$
- If $\eta_{\text{scale}} \ge 1.5\%$, the framing model will not mate with physical components; the scale multiplier is locked to the primary physical anchor before generating cut schedules.

### 3.4 Anti-Refeed & Single-Substrate Invariants
1. **Rule 2: Anti-Refeed Guard**: Generative AI renders must NEVER be passed as inputs into subsequent diffusion turns. Recursive re-feeding creates hallucination compounding, softens edges, and drifts dimensional accuracy. Inputs MUST be raw photographic captures.
2. **Rule 1: One Substrate, One Camera Frame Law (The Lake Road Trap)**: A single camera frame cannot represent two disconnected physical workspaces (e.g. front entry landing and back garage steps). If a field note describes multi-zone structures, the pipeline decomposes the job into Job A and Job B with independent camera anchors.

---

## 4. The 5-Layer Semantic Prompt Engine (Layer 1: Client Excitement)

To steer generative diffusion models with engineering precision, prompts are synthesized through a deterministic 5-layer hierarchy:

```
+--------------------------------------------------------------------------------------------------+
|                            THE 5-LAYER SEMANTIC PROMPT STACK                                     |
+--------------------------------------------------------------------------------------------------+
| LAYER 1: SUBSTRATE GROUNDING & PRESERVATIONS                                                     |
| Anchor: "Built onto the exact framing cradle shown in the reference image..."                    |
| Preserves: Raw concrete slab, door jambs, vinyl siding, ceiling trusses untouched.               |
+--------------------------------------------------------------------------------------------------+
| LAYER 2: CLADDING & TRADE MATERIAL SPECIFICATIONS                                                |
| Trade SKUs: 29-gauge Bright White Pro-Rib ribbed steel liner panels, #10 color-matched hex screws|
| Finish: Cedartone 2x12 solid treads, bullnosed edges, satin white risers, 2x2 craftsman handrail. |
+--------------------------------------------------------------------------------------------------+
| LAYER 3: FINISH & UNDERSIDE ASSEMBLIES                                                           |
| Assemblies: 15/16" heavy-duty suspended drop grid holding 1/2" solid smooth white PVC panels     |
| (Menards SKU 1429329), 1" foil-faced rigid polyiso insulation, bronze polycarbonate panels.      |
+--------------------------------------------------------------------------------------------------+
| LAYER 4: ARCHITECTURAL CUTAWAY SECTION (THE X-RAY)                                               |
| Perspective Slice: 45-degree diagonal section peeling back surface cladding to expose internal   |
| 2x4 framing cradle, 12" spiral ductwork, furnace unit, wiring rough-ins, or triple 2x12 stringers|
+--------------------------------------------------------------------------------------------------+
| LAYER 5: MACRO DETAIL INSET (THE CRAFTSMAN ZOOM)                                                 |
| Microscopic Joint: 100mm circular callout showing J-trim termination, neoprene washer gasket    |
| seal, Simpson Strong-Tie A35 framing angle, or Tapcon anchor into concrete slab.                 |
+--------------------------------------------------------------------------------------------------+
```

---

## 5. Parametric Structural CAD & Cut Schedules (Layer 2: Fabrication Truth)

Layer 2 translates validated geometry into deterministic vector blueprints and fabrication schedules.

### 5.1 Wisconsin SPS 321.04 Stair Geometry Formulation
For any interior or exterior stairway, total vertical rise $R_{\text{total}}$ is partitioned into $N$ equal risers:
$$N = \text{round}\left( \frac{R_{\text{total}}}{7.75} \right), \quad R_{\text{unit}} = \frac{R_{\text{total}}}{N}$$
subject to statutory constraints under Wisconsin SPS 321.04:
- Maximum riser height: $R_{\text{unit}} \le 8.00''$ ($203.2\text{ mm}$).
- Minimum tread run: $T_{\text{run}} \ge 9.00''$ ($228.6\text{ mm}$) with nosing, standard $10.50''$ for commercial/residential comfort.
- Uniformity tolerance: $\max(R_i) - \min(R_i) \le 0.375''$ ($9.5\text{ mm}$) across the entire flight.
- Minimum clear headroom rake line: $H_{\text{clear}} \ge 80.00''$ ($2032\text{ mm}$) measured vertically from the leading edge plane of all tread nosings:
  $$y_{\text{bulkhead}}(x) - y_{\text{tread}}(x) \ge 80.00'' \quad (\forall x \in [0, X_{\text{total}}])$$

### 5.2 Deterministic Cut Schedule Compilation
From the structural model, GVSM outputs a piece-by-piece cut schedule JSON specifying:
1. **Component Name & Type** (e.g., `Stringer #1`, `Kicker Plate`, `Drop Leg #4`).
2. **Raw Stock Material** (e.g., `2x12x16' Douglas Fir #2`, `2x4x8' SPF`, `6x6x10' AC2 Ground Contact`).
3. **Finish Cut Length** in decimal inches and fractional 1/16ths.
4. **Bevel / Miter Angles** (e.g., $36.4^\circ$ plumb cut, $53.6^\circ$ seat cut).
5. **Fastener & Anchor Callout** (e.g., `GRK RSS 5/16x4" Timber Screws`, `3/8x4" Concrete Wedge Anchors`).

---

## 6. Wisconsin Rapids Jobsite Integration & DGC Core Four Contract Suite

GVSM connects directly into John Dondlinger's DGC operational engine in Wisconsin Rapids, WI.

```
+--------------------------------------------------------------------------------------------------+
|                                DGC CORE FOUR CONTRACT SUITE MATRIX                               |
+--------------------------------------------------------------------------------------------------+
| 1. CLIENT PROPOSAL               | Turnkey, non-itemized lump sum price. Beautiful GVSM Layer 1  |
|                                  | cutaway render + Layer 2 blueprint preview. SPS code citations.|
+----------------------------------+----------------------------------------------------------------+
| 2. INTERNAL WORK ORDER           | Strictly confidential. Complete Menards SKU itemized BOM,     |
|                                  | crew hours, piece-by-piece cut schedule, safety hazards.       |
+----------------------------------+----------------------------------------------------------------+
| 3. PRODUCTION TIMELINE           | Day-by-day milestone schedule, inspection holds, concrete      |
|                                  | cure times, weather contingencies, subcontractor handoffs.    |
+----------------------------------+----------------------------------------------------------------+
| 4. FINAL INVOICE & CHANGE ORDERS | Milestone payment triggers, Change Order (CO) tracking,        |
|                                  | SHA-256 digital signature seal via Cloudflare Edge (`/sign`).  |
+----------------------------------+----------------------------------------------------------------+
```

### 6.1 DGC Economic Constraints & Pricing Equations
Every takeoff and estimate compiled through GVSM must strictly enforce DGC financial rules:
1. **Labor Rate Calibration**:
   $$C_{\text{labor}} = H_{\text{crew}} \times \$80.00/\text{hr}$$
2. **Material Procurement**:
   $$C_{\text{material}} = \sum_{j=1}^M \left( Q_j \times P_{\text{retail}, j} \right)$$
   Procured exclusively from Menards Wisconsin Rapids (Store #3107) catalog.
3. **Material Markup Protection**:
   $$P_{\text{material}} = C_{\text{material}} \times 1.15 \quad (15\%\text{ markup})$$
4. **Daily Profit Floor Invariant**:
   $$\Pi_{\text{daily}} = \frac{P_{\text{contract}} - (C_{\text{material}} + C_{\text{direct\_subs}})}{D_{\text{duration}}} \ge \$350.00/\text{day}$$
   If $\Pi_{\text{daily}} < \$350.00/\text{day}$, the compilation engine automatically adjusts labor contingency hours to guarantee the contractor profit floor.

---

## 7. Real-World Proof-of-Performance Benchmarks

| Project Identifier | Physical Substrate | GVSM Intervention | Client Outcome |
| :--- | :--- | :--- | :--- |
| **Chuck Miller Shop** | Suspended 2x4 framing cradle, unit heater, spiral duct | Dual-Deliverable Cutaway: Bright White Pro-Rib vertical liner, Classic X drop grid, polyiso, cutaway revealing equipment | **Change Order CO-02 ($1,850.85)** approved on sight by Chuck & Sharon Miller with **zero questions asked**. |
| **Lukaszewski Stairs** | Dark green carpet, dangerous 5'9" ceiling pinch bulkhead | Safe Headroom Descent: Solid 2x12 Cedartone treads, satin risers, 82" clear rake line, framing cutaway with Tapcons | Bulkhead cutback verified against SPS 321.04; immediate client signing. |
| **Madden Patio Shelter** | Open stamped patio, 6-ft privacy fence, house vinyl wall | Forensic Failure Infographic: Proved unbraced wedge snaps fence posts under 3,500 lb snowpack; presented heavy timber pavilion | Client abandoned dangerous DIY plan; opted for engineered freestanding structure. |

---

## 8. Verification & Test Suite Specifications

The GVSM system is validated via automated integration suites verifying both spatial and financial logic:
1. `TestGVSMCompiler`: 5-layer prompt grammar compilation, SKU keyword mapping, preservation extraction.
2. `TestGVSMValidator`: Substrate image accessibility, anti-refeed rejection, single-frame scope guards.
3. `TestCADGenerator`: SVG coordinate accuracy, headroom rake angle calculation, dimension string integrity.
4. `TestDGCCoreFour`: Menards BOM calculation, 15% material markup, $80/hr labor rate, $350+/day profit floor.
5. `TestSpatialInvariants`: Reprojection error $< 1.2\text{ px}$, planar orthogonality $< 0.5^\circ$, scale closure $< 1.5\%$.
6. `TestGVSMWatermark`: 2D-DCT orthogonal inverse precision, 64-bit payload preservation, majority-voting bit recovery, SVG XML namespace signing, and SHA-256 Merkle Provenance Manifest verification.

---

## 9. Tri-Layer Forensic Watermark & Merkle Provenance Specification

To prevent technological expropriation and guarantee non-repudiation of GVSM assets, every deliverable is stamped with an immutable, multi-domain provenance signature:

```
+--------------------------------------------------------------------------------------------------+
| LAYER 1: SOVEREIGN GEODETIC COLLAR & THEODOLITE RETICLE (Visible Framing Layer)                 |
| Outer calibration collar burned into border: Datum coordinates (Wisconsin Rapids, WI),           |
| contractor identity (John Dondlinger / DGC), ZLA license, Job ID, and SHA-256 signature prefix. |
| Four-corner theodolite crosshair reticles tie directly into structural vanishing axes.           |
+--------------------------------------------------------------------------------------------------+
| LAYER 2: 2D-DCT MID-FREQUENCY SPREAD-SPECTRUM STEGANOGRAPHY (Invisible Frequency Layer)         |
| Luminance Y channel transformed via 8x8 2D-DCT. 64-bit cryptographic payload ('GVSM' + HMAC-32)  |
| modulated across mid-frequency pairs (3,2) and (2,3). Tiled redundantly across hundreds of       |
| pseudo-random blocks. Survives JPEG 60% recompression, web downsampling, screenshots, inpainting.|
+--------------------------------------------------------------------------------------------------+
| LAYER 3: DUAL-DELIVERABLE CRYPTOGRAPHIC MERKLE HASH BINDING (Proof of Possession Layer)         |
| Merkle root binds the visual cutaway render to: (1) raw substrate on-site camera frame,         |
| (2) deterministic inline SVG CAD blueprint, (3) carpenter cut schedule, (4) Menards BOM.        |
| An attacker possessing only the image CANNOT fabricate the matching offline engineering bundle. |
+--------------------------------------------------------------------------------------------------+
| LAYER 4: DETERMINISTIC SVG CAD EMBEDDED BENCHMARK & XML NAMESPACE (Vector Layer)                 |
| Geodetic survey medallion embedded in SVG with xmlns:gvsm attributes, legal statutory citations  |
| (17 U.S.C. § 1202 - Criminalization of Copyright Management Information removal/tampering).     |
+--------------------------------------------------------------------------------------------------+
```

### 9.1 Mathematical Formulation of 2D-DCT Watermark Modulation
For an $8 \times 8$ spatial luminance block $B(x, y)$, the 2D-DCT is defined as:
$$D(u, v) = \frac{1}{4} C(u) C(v) \sum_{x=0}^7 \sum_{y=0}^7 B(x, y) \cos\left[\frac{(2x+1)u\pi}{16}\right] \cos\left[\frac{(2y+1)v\pi}{16}\right]$$
where $C(w) = \frac{1}{\sqrt{2}}$ for $w=0$, and $1$ for $w > 0$.

For bit $b_k \in \{0, 1\}$ at sequence index $k$:
- If $b_k = 1$: modulate coefficients such that $D(3, 2) - D(2, 3) \ge \Delta$
- If $b_k = 0$: modulate coefficients such that $D(2, 3) - D(3, 2) \ge \Delta$
where $\Delta = 28.0$ represents the robust watermark embedding strength.

Inverse DCT (2D-IDCT) reconstructs the spatial domain with bounded luminance drift $|\delta Y| \le 3.5\text{ IRE}$, imperceptible to the human eye but statistically recoverable via majority-voting over $N_{\text{blocks}} \ge 256$.

