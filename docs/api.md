# CivicPulse AI — API Documentation

Interactive OpenAPI / Swagger documentation is available at `/docs` when the backend is running.

All endpoints adhere to REST conventions, JSON responses, and standard HTTP status codes.

---

## Base URL
Default local development endpoint: `http://localhost:8000`

---

## Endpoints

### 1. Submit Grievance
- **Method:** `POST /api/reports`
- **Content-Type:** `multipart/form-data`
- **Payload:**
  - `complaint_text` (string, required, 5-4000 chars): Detailed description of civic issue.
  - `images` (file array, optional): One or more image files (JPEG, PNG, WebP, max 10MB each).
  - `latitude` (float, optional): Between -90.0 and 90.0.
  - `longitude` (float, optional): Between -180.0 and 180.0.
  - `address_or_landmark` (string, optional): Physical location description.
  - `citizen_category` (string, optional): Advisory category hint.
- **Response (201 Created):**
```json
{
  "report_id": "ac733ddf-6867-492f-9cc0-62ea6254e070",
  "processing_status": "pending",
  "message": "Grievance submitted successfully. Evidence extraction ready to run.",
  "created_at": "2026-10-31T18:20:00Z"
}
```

---

### 2. Run Multimodal Analysis Pipeline
- **Method:** `POST /api/reports/{report_id}/analyze`
- **Description:** Triggers local Qwen2.5-VL and Qwen2.5 models sequentially, executes Python evidence fusion, evaluates triage priority rules, and persists structured evidence records.
- **Response (200 OK):**
```json
{
  "id": "ac733ddf-6867-492f-9cc0-62ea6254e070",
  "complaint_text": "Large pothole on Bailey Road...",
  "issue_category": "road_damage",
  "workflow_status": "awaiting_review",
  "review_pathway": "human_review",
  "department_recommendation": {
    "department_name": "Road Maintenance & Public Works Division",
    "department_status": "recommended",
    "jurisdiction_level": "Urban Local Body / Municipal Corporation",
    "rationale": "Potholes, surface cracks, and asphalt degradation...",
    "is_official_referral": false
  },
  "evidence_record": {
    "image_evidence": { ... },
    "text_evidence": { ... },
    "fused_evidence": {
      "issue_category": "road_damage",
      "conflicts": [],
      "unknowns": ["Visual limitation: Depth cannot be confirmed"],
      "corroborations": ["Both photograph and complaint text substantiate issue category: road_damage"],
      "requires_human_review": true,
      "data_sufficiency": "partial"
    }
  },
  "triage_decision": {
    "rule_version": "v1.0.0",
    "recommended_pathway": "human_review",
    "reason_codes": ["POOR_IMAGE_QUALITY"]
  }
}
```

---

### 3. Get Report Detail
- **Method:** `GET /api/reports/{report_id}`
- **Description:** Returns complaint details, evidence record, department recommendation, and complete status history audit log.

---

### 4. List Grievances
- **Method:** `GET /api/reports`
- **Query Parameters:**
  - `page` (int, default 1)
  - `limit` (int, default 20)
  - `category` (string, optional)
  - `pathway` (string, optional)
  - `status` (string, optional)
- **Response (200 OK):** Paginated summaries excluding private device information.

---

### 5. Reviewer Status Update (Authorized)
- **Method:** `POST /api/reports/{report_id}/updates`
- **Headers:**
  - `X-Reviewer-Token`: Configured administrative secret token.
- **Payload:**
```json
{
  "new_status": "in_progress",
  "actor_type": "reviewer",
  "actor_id": "officer_bihar_pwd_01",
  "reason": "Repair crew dispatched with cold asphalt mix."
}
```
- **Response (200 OK):** Updated report with new audit trail entry.

---

### 6. Live Dashboard Metrics
- **Method:** `GET /api/dashboard/summary`
- **Description:** Real database-derived statistics (total reports, awaiting review, urgent review, in progress, resolved, overdue, category distributions, and response times).

---

### 7. Geographic Hotspots
- **Method:** `GET /api/dashboard/hotspots`
- **Description:** Geographically clustered and rounded complaint concentrations preserving citizen privacy.

---

### 8. System Health
- **Method:** `GET /api/dashboard/health`
- **Description:** Local Ollama connectivity and model readiness (`qwen2.5vl:3b` & `qwen2.5:1.5b`).
