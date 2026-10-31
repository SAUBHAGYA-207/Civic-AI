import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from PIL import Image

from backend.app.main import app
from backend.app.config import settings
from backend.app.database.models import Base
from backend.app.database.session import get_db

# Use in-memory SQLite database with StaticPool for test isolation
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def client():
    return TestClient(app)

def create_dummy_jpeg() -> bytes:
    img = Image.new("RGB", (32, 32), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def test_api_create_report_success(client):
    img_bytes = create_dummy_jpeg()
    response = client.post(
        "/api/reports",
        data={
            "complaint_text": "Large pothole in front of community hall causing traffic snarls.",
            "latitude": 25.5941,
            "longitude": 85.1376,
            "address_or_landmark": "Near Community Hall, Ward 4",
            "citizen_category": "road_damage",
        },
        files={
            "images": ("test_road.jpg", img_bytes, "image/jpeg"),
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "report_id" in data
    assert data["processing_status"] == "pending"

def test_api_create_report_invalid_coordinates(client):
    response = client.post(
        "/api/reports",
        data={
            "complaint_text": "Invalid coordinate report test",
            "latitude": 150.0,  # Invalid latitude (> 90)
            "longitude": 85.0,
        }
    )
    assert response.status_code == 400
    assert "Invalid latitude" in response.json()["detail"]

def test_api_create_report_invalid_file_type(client):
    response = client.post(
        "/api/reports",
        data={
            "complaint_text": "Valid text with malicious file attachment",
        },
        files={
            "images": ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-dosexec"),
        }
    )
    assert response.status_code == 400
    assert "Invalid file extension" in response.json()["detail"]

def test_api_create_report_empty_text(client):
    response = client.post(
        "/api/reports",
        data={
            "complaint_text": "",  # Empty
        }
    )
    assert response.status_code == 422

def test_api_get_report_not_found(client):
    response = client.get("/api/reports/non-existent-uuid-12345")
    assert response.status_code == 404

def test_api_dashboard_empty_db(client):
    response = client.get("/api/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_reports"] == 0
    assert data["reports_awaiting_review"] == 0
    assert data["avg_response_time_hours"] is None

def test_api_reviewer_update_unauthorized(client):
    # Create a report first
    create_resp = client.post(
        "/api/reports",
        data={"complaint_text": "Water leaking from underground pipeline on 4th cross."}
    )
    report_id = create_resp.json()["report_id"]

    # Try updating without header
    update_resp = client.post(
        f"/api/reports/{report_id}/updates",
        json={
            "new_status": "in_progress",
            "actor_type": "reviewer",
            "actor_id": "officer_1",
            "reason": "Team deployed to fix leak.",
        }
    )
    assert update_resp.status_code == 401

def test_api_reviewer_update_invalid_transition(client):
    create_resp = client.post(
        "/api/reports",
        data={"complaint_text": "Garbage dump near primary school entrance."}
    )
    report_id = create_resp.json()["report_id"]

    # submitted cannot directly jump to 'resolved' without investigation
    update_resp = client.post(
        f"/api/reports/{report_id}/updates",
        headers={"x-reviewer-token": settings.REVIEWER_SECRET_KEY},
        json={
            "new_status": "resolved",
            "actor_type": "reviewer",
            "actor_id": "officer_1",
            "reason": "Premature closure attempt.",
        }
    )
    assert update_resp.status_code == 400
    assert "Invalid state transition" in update_resp.json()["detail"]

def test_api_reviewer_update_valid_transition_and_history(client):
    create_resp = client.post(
        "/api/reports",
        data={"complaint_text": "Garbage dump near primary school entrance."}
    )
    report_id = create_resp.json()["report_id"]

    # Transition from 'submitted' to 'awaiting_review'
    update_resp = client.post(
        f"/api/reports/{report_id}/updates",
        headers={"x-reviewer-token": settings.REVIEWER_SECRET_KEY},
        json={
            "new_status": "awaiting_review",
            "actor_type": "reviewer",
            "actor_id": "supervisor_patna_101",
            "reason": "Assigned to Ward 10 sanitation inspection roster.",
        }
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["workflow_status"] == "awaiting_review"
    assert len(data["status_history"]) >= 2
    assert data["status_history"][-1]["reason"] == "Assigned to Ward 10 sanitation inspection roster."
