# CivicPulse AI — System Architecture

## 1. Architectural Philosophy

**Core Principle:**
> *AI extracts evidence; deterministic Python rules recommend actions; authorized humans handle consequential decisions.*

CivicPulse AI is engineered around strict boundaries between probabilistic model inference and municipal administrative authority. LLMs and VLMs are never permitted to declare real-world danger levels, decide legal liability, invent measurements, or pretend to submit official municipal dispatch orders.

```
Citizen Submission (Photo + Text + Location)
      │
      ▼
Input Validation & Secure Storage (MIME inspection, UUID filenames)
      │
      ▼
Sequential Evidence Extraction
   ├─► Qwen2.5-VL:3B (Vision-Language Model)  ──► ImageEvidence Pydantic Record
   └─► Qwen2.5:1.5B  (Text-Only Instruct)     ──► TextEvidence Pydantic Record
      │
      ▼
Deterministic Evidence Fusion Engine (Pure Python)
   ├─► Provenance Tracking (visually_observed vs citizen_reported vs corroborated vs conflict)
   └─► Conflict & Unknown Detection
      │
      ▼
Deterministic Triage Engine (Priority Rules v1.0.0)
   ├─► Immediate Danger Indicators
   ├─► Critical Access Obstruction (Hospitals, Schools)
   ├─► Evidence Sufficiency & Conflict Escalation
   └─► Waiting-Time Escalation (>24h, >72h)
      │
      ▼
Department Recommendation Router (Advisory routing with referral disclaimers)
      │
      ▼
Database Persistence (SQLite/PostgreSQL Repository Layer)
      │
      ├─► Citizen Tracking View (Transparent Audit History)
      └─► Live Accountability Dashboard (Real Aggregates)
```

---

## 2. End-to-End Pipeline Stages

### Stage A: Citizen Submission
- Accepts multipart form uploads: photograph(s), grievance text narrative, optional GPS coordinates, optional landmark or street address, and an optional issue category hint.
- **Security Validations**:
  - Magic byte / file signature verification (JPEG, PNG, WebP) to prevent executable spoofing.
  - File size bounded to 10 MB per image.
  - Path traversal defense: randomized server-side UUID filenames.
  - Coordinate range enforcement (-90 to 90 lat, -180 to 180 lon).
  - Grievance narrative length constraints (5 to 4000 characters).

### Stage B: Image Evidence Extraction (`app/services/image_extractor.py`)
- Powered locally by **Qwen2.5-VL:3B** via Ollama.
- Preprocesses images to a standardized resolution (max 1024px) to preserve memory on resource-constrained environments (e.g. 8 GB RAM / CPU-only setups).
- **Anti-Hallucination System Prompt Rules**:
  1. Prohibited from inventing physical measurements (depth, width, volume).
  2. Prohibited from asserting vehicular accidents or injuries without directly visible wreckage.
  3. Prohibited from declaring structures "structurally safe" or "structurally unsafe" from photos alone.
  4. Prohibited from treating citizen narrative claims as confirmed visual facts.
  5. Prohibited from inferring subterranean or hidden structural conditions.
- Validates model output against `ImageEvidence` Pydantic schema using structured JSON decoding.

### Stage C: Text Claim Extraction (`app/services/text_extractor.py`)
- Powered locally by **Qwen2.5:1.5B** Instruct via Ollama.
- Isolates citizen allegations, reported impacts, reported durations, and claimed safety hazards.
- Identifies missing municipal action details (e.g. absent landmark, unspecified sewage vs potable water).
- Validates output against `TextEvidence` Pydantic schema.

### Stage D: Structured Output & Resilient Execution (`app/services/ollama_client.py`)
- Uses an asynchronous sequential concurrency lock (`asyncio.Lock`) to ensure only one local model runs at any time, preventing out-of-memory crashes on consumer laptops and edge servers.
- Bounded retries (2 attempts) with timeout handling (120 seconds).
- Robust JSON sanitization stripping markdown codeblocks or preambles.

### Stage E: Evidence Fusion Engine (`app/services/evidence_fusion.py`)
- Implemented purely in Python without external model calls.
- Preserves atomic evidence items with strict provenance:
  - `visually_observed`: Model visual observation (not independent ground truth).
  - `citizen_reported`: Citizen allegation.
  - `corroborated`: Compatible visual and textual details.
  - `conflict`: Category or condition divergence between image and text.
  - `unknown`: Missing or unverifiable information.
  - `reviewer_verified`: Human-certified item with reviewer ID and timestamp.

### Stage F: Deterministic Triage (`app/triage/priority_rules.py`)
- Routes complaints into four distinct workflow pathways:
  - `urgent_human_review`: Credible danger signals (live wires, open manholes, gas leaks) or critical access blockage (hospital/school route).
  - `human_review`: Category divergence, evidence conflicts, or poor image quality.
  - `request_clarification`: Insufficient location or evidence gaps.
  - `standard_triage`: Routine verifiable maintenance issues.
- Supports administrative reviewer overrides with mandatory justification and audit logging.

### Stage G: Department Recommendation (`app/triage/department_router.py`)
- Maps verified issues to municipal departments (Roads, Water, Drainage, Waste, Lighting).
- Enforces `is_official_referral = False` to prevent misleading citizens into believing an external authority has already confirmed receipt.

---

## 3. Concurrency & Performance Controls for Low-Resource Environments

- **Sequential Execution**: A process-wide lock prevents concurrent inference, allowing smooth operation on CPU-only machines with 8 GB RAM.
- **Image Downsampling**: High-resolution mobile phone photos (e.g. 12 MP) are scaled down to 1024px prior to VLM encoding.
- **Configurable Timeouts**: Environment-variable overrides allow scaling limits for slower hardware.
