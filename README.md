# CivicPulse AI

> **Privacy-Conscious Civic Grievance & Infrastructure Triage Platform**  
> Powered by local multimodal Qwen models running through Ollama.

---

## 1. Core Architectural Principle

> **"AI extracts evidence; deterministic Python rules recommend actions; authorized humans handle consequential decisions."**

CivicPulse AI does **not** allow probabilistic LLMs or VLMs to generate uncalibrated danger scores, claim official government referrals, or present unverified model inferences as established physical facts.

Instead:
- **Qwen2.5-VL:3B** extracts visible observations and notes limitations of visual assessment.
- **Qwen2.5:1.5B** isolates citizen claims, impacts, and missing details.
- **Deterministic Python Engine** fuses evidence, tracks granular provenance, flags contradictions, and applies explicit priority rules.
- **Authorized Human Reviewers** make all consequential state transitions with mandatory audit logging.

---

## 2. Technology Stack

- **AI & Backend**:
  - Python 3.10+
  - FastAPI
  - Pydantic v2 (Strict Schema Validation)
  - Ollama Python Client (Local sequential inference)
  - SQLAlchemy 2.0 (Repository pattern with SQLite default / PostgreSQL support)
  - Pytest (Automated unit and integration testing)
- **Local Models**:
  - Vision Model: `qwen2.5vl:3b`
  - Text Model: `qwen2.5:1.5b`
- **Frontend**:
  - React 19
  - Vite
  - TypeScript
  - Tailwind CSS v4
  - Lucide Icons

---

## 3. Prerequisites

1. **Python 3.10+**: Ensure `python` and `pip` are installed.
2. **Node.js 18+**: Ensure `node` and `npm` are installed.
3. **Ollama**: Download and install [Ollama](https://ollama.com).

Pull the local models:
```bash
ollama pull qwen2.5vl:3b
ollama pull qwen2.5:1.5b
```

Verify that Ollama is running:
```bash
ollama list
```

---

## 4. Setup Instructions

### Backend Setup

1. Open a terminal in the project root:
```bash
cd backend
```

2. (Optional) Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Verify environment configuration:
Copy `.env.example` to `.env` if desired (defaults work out-of-the-box):
```bash
cp .env.example .env
```

5. Run automated tests:
```bash
python -m pytest backend/app/tests -v
```

6. Start the FastAPI backend server:
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
The backend API will be available at: `http://localhost:8000`  
Interactive Swagger docs: `http://localhost:8000/docs`

---

### Frontend Setup

1. In a separate terminal, navigate to the `frontend` directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the Vite development server:
```bash
npm run dev
```
The application will open at: `http://localhost:5173`

---

## 5. End-to-End User Flow

1. **Submit Grievance**:
   - Go to `http://localhost:5173`.
   - Upload a photo (e.g., pothole, leaking pipe, dark streetlight, garbage).
   - Enter a description, location, or attach device coordinates.
   - Click **Submit Grievance**. You receive a permanent Grievance UUID.
2. **AI Multimodal Evidence Analysis**:
   - Inspect the granular breakdown: visible observations from Qwen2.5-VL, claims extracted by Qwen2.5, corroborated points, and detected conflicts.
   - Review the deterministic triage pathway (e.g., `urgent_human_review`, `standard_triage`) and advisory department recommendation.
3. **Reviewer Action**:
   - Municipal case workers enter their reviewer key (`civicpulse-reviewer-dev-key-secure`), select the target status (e.g., `in_progress`), and input an audit justification.
4. **Citizen Tracking**:
   - Citizens search their Complaint UUID to inspect live progress and audit history.
5. **Accountability Dashboard**:
   - Access real-time database-derived metrics, including urgent queue counts, category breakdowns, and resolution durations.

---

## 6. Running Tests

The test suite covers Pydantic schemas, evidence fusion, deterministic triage rules, API endpoints, and benchmark evaluation cases:

```bash
# Run all 27 unit and integration tests
python -m pytest backend/app/tests -v

# Run live end-to-end verification script with Ollama models
python -m backend.app.tests.verify_e2e
```

---

## 7. Known Constraints & Limitations

- **CPU Vision Inference Latency**: On CPU-only laptops, `qwen2.5vl:3b` takes approximately 2-3 minutes per image. A discrete GPU (CUDA / Apple Silicon Metal) reduces this to under 5 seconds.
- **Visual Limitations**: Model prompts strictly prohibit inferring exact physical measurements (depth, width) or subterranean structural integrity from 2D photos alone.
- **Privacy Preservation**: GPS coordinates in dashboard aggregations are clustered and rounded to prevent exposing citizens' private home locations.
- **No Direct Dispatch**: Department suggestions remain clearly marked as recommendations rather than official referrals until verified integration exists.
