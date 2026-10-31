import asyncio
import io
from pathlib import Path
from PIL import Image
from backend.app.database.session import SessionLocal, init_db
from backend.app.database.repository import ReportRepository
from backend.app.services.analysis_pipeline import analysis_pipeline

async def test_live_e2e_pipeline():
    print("--- 1. Initializing Database ---")
    init_db()
    db = SessionLocal()

    try:
        # Create a synthetic infrastructure test image
        img = Image.new("RGB", (256, 256), color=(60, 60, 60))
        # Draw a bright spot to represent a pothole or streetlight fixture
        for x in range(100, 150):
            for y in range(100, 150):
                img.putpixel((x, y), (20, 20, 20))
        
        test_img_path = Path("backend/uploads/test_live_infrastructure.jpg")
        test_img_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(test_img_path, format="JPEG")

        print("--- 2. Creating Grievance Report Record ---")
        repo = ReportRepository(db)
        report = repo.create_report(
            complaint_text="Large pothole on Bailey Road near Secretariat gate. Water is accumulating and causing traffic slowdowns for two weeks.",
            issue_category="road_damage",
            latitude=25.6090,
            longitude=85.1235,
            address_or_landmark="Bailey Road near Secretariat gate, Patna",
        )
        print(f"Created Report ID: {report.id}")

        print("--- 3. Adding Attachment ---")
        attachment = repo.add_attachment(
            report_id=report.id,
            storage_path=str(test_img_path.resolve()),
            original_filename="bailey_road_pothole.jpg",
            mime_type="image/jpeg",
            file_size=test_img_path.stat().st_size,
        )
        print(f"Attachment stored: {attachment.id}")

        print("--- 4. Executing Multimodal Analysis Pipeline (Qwen2.5-VL & Qwen2.5) ---")
        analyzed_report = await analysis_pipeline.run(report_id=report.id, db=db)

        print("\n=== PIPELINE EXECUTION SUCCESS ===")
        print(f"Report ID: {analyzed_report.id}")
        print(f"Workflow Status: {analyzed_report.workflow_status}")
        print(f"Resolved Issue Category: {analyzed_report.issue_category}")
        print(f"Recommended Review Pathway: {analyzed_report.review_pathway}")
        print(f"Department Recommendation: {analyzed_report.department_recommendation}")
        print(f"Evidence Records Count: {len(analyzed_report.evidence_records)}")

        if analyzed_report.evidence_records:
            rec = analyzed_report.evidence_records[-1]
            print(f"Model Identifiers: {rec.model_identifiers}")
            print(f"Image Candidates: {rec.image_evidence_json.get('issue_candidates')}")
            print(f"Image Quality: {rec.image_evidence_json.get('image_quality')}")
            print(f"Text Category: {rec.text_evidence_json.get('issue_category')}")
            print(f"Text Reported Impacts: {rec.text_evidence_json.get('reported_impacts')}")
            print(f"Fused Evidence Sufficiency: {rec.fused_evidence_json.get('data_sufficiency')}")
            print(f"Fused Conflicts: {rec.fused_evidence_json.get('conflicts')}")
            print(f"Fused Corroborations: {rec.fused_evidence_json.get('corroborations')}")

        print("\n--- 5. Testing Authorized Reviewer State Transition ---")
        updated = repo.update_status(
            report_id=report.id,
            new_status="in_progress",
            actor_type="reviewer",
            actor_id="officer_bihar_pwd_01",
            reason="Pothole repair team dispatched with cold asphalt patch mix.",
        )
        print(f"New Workflow Status: {updated.workflow_status}")
        print(f"Audit Trail Count: {len(updated.status_history)}")

        print("\n--- 6. Testing Live Dashboard Aggregations ---")
        summary = repo.get_dashboard_summary()
        print(f"Total Reports in DB: {summary['total_reports']}")
        print(f"In Progress: {summary['reports_in_progress']}")
        print(f"Categories in DB: {summary['category_distribution']}")
        print(f"Hotspots: {repo.get_hotspots()}")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_live_e2e_pipeline())
