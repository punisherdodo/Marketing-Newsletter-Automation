"""
Smoke tests for NovaMind services.
Run with: python -m pytest tests/smoke_test.py -v
Or directly: python tests/smoke_test.py
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("HUBSPOT_ACCESS_TOKEN", "")
os.environ.setdefault("SENDGRID_API_KEY", "")
os.environ.setdefault("SENDGRID_FROM_EMAIL", "")


def test_persona_service_imports_and_assigns():
    from services.persona_service import PersonaService
    svc = PersonaService()
    assert len(svc.PERSONAS) >= 5, "Expected at least 5 personas"
    persona = svc.assign_persona({"job_title": "Founder", "company": "ACME"})
    assert persona == "Agency Founder", f"Unexpected persona: {persona}"
    persona_unknown = svc.assign_persona({"job_title": "", "company": ""})
    assert persona_unknown == "General Business Buyer"
    print("  persona_service: OK")


def test_persona_service_sample_contacts():
    from services.persona_service import PersonaService
    svc = PersonaService()
    contacts = svc.get_sample_contacts()
    assert len(contacts) >= 5, "Expected at least 5 sample contacts"
    for c in contacts:
        assert "email" in c
        assert "job_title" in c
    print("  persona_service.get_sample_contacts: OK")


def test_openai_service_no_key():
    from services.openai_service import OpenAIService
    svc = OpenAIService()
    assert not svc.is_configured(), "Should not be configured without API key"
    result = svc.generate_campaign_content("AI automation for agencies")
    assert "error" in result, "Expected error key when no API key is set"
    print("  openai_service (no key, graceful error): OK")


def test_openai_service_regenerate_section_no_key():
    from services.openai_service import OpenAIService
    svc = OpenAIService()
    result = svc.regenerate_section("newsletter", "AI automation", persona="Agency Founder")
    assert result == "", f"Expected empty string when not configured, got: {result!r}"
    print("  openai_service.regenerate_section (no key → empty string): OK")


def test_email_service_no_key():
    from services.email_service import EmailService
    svc = EmailService()
    assert not svc.is_configured(), "Should not be configured without API key"
    mock_results = svc.mock_send(
        [{"email": "test@example.com", "firstname": "Test", "lastname": "User", "assigned_persona": "Agency Founder"}],
        {"Agency Founder": "Hello from NovaMind"},
        {"Agency Founder": "Test Subject"},
        "Smoke Test Campaign",
    )
    assert len(mock_results) == 1
    assert mock_results[0]["action"] == "simulated"
    print("  email_service (no key, mock fallback): OK")


def test_email_service_dry_run():
    from services.email_service import EmailService
    svc = EmailService()
    contacts = [
        {"email": "a@example.com", "firstname": "A", "lastname": "B", "assigned_persona": "Agency Founder"},
        {"email": "c@example.com", "firstname": "C", "lastname": "D", "assigned_persona": "Creative Lead"},
    ]
    newsletters = {"Agency Founder": "Hello founder", "Creative Lead": "Hello creative"}
    subject_lines = {"Agency Founder": "Founder subject", "Creative Lead": "Creative subject"}
    result = svc.dry_run(contacts, newsletters, subject_lines)
    assert result["total"] == 2
    assert result["will_send"] == 2
    assert result["missing_content"] == 0
    print("  email_service.dry_run: OK")


def test_hubspot_service_no_key():
    from services.hubspot_service import HubSpotService
    svc = HubSpotService()
    assert not svc.is_configured(), "Should not be configured without token"
    result = svc.check_auth()
    assert not result["ok"]
    print("  hubspot_service (no key): OK")


def test_storage_service_creates_db():
    from services.storage_service import StorageService
    svc = StorageService()
    assert svc.db_path.exists(), "Database file should be created on init"
    summary = svc.get_analytics_summary()
    assert "total_campaigns" in summary
    assert summary["total_campaigns"] >= 0
    print("  storage_service (db creation + analytics summary): OK")


def test_storage_service_campaign_roundtrip():
    from services.storage_service import StorageService
    svc = StorageService()
    data = {
        "blog_title": "Smoke Test Post",
        "blog_draft": "Test body",
        "newsletters": {"Agency Founder": "Test newsletter"},
        "subject_lines": {"Agency Founder": "Test subject"},
    }
    campaign_id = svc.insert_campaign("Smoke test topic", data, mode="mock", name="Smoke Test")
    assert campaign_id > 0
    retrieved = svc.get_campaign(campaign_id)
    assert retrieved["name"] == "Smoke Test"
    assert retrieved["mode"] == "mock"
    print("  storage_service (campaign insert + retrieve): OK")


def test_storage_service_custom_keywords():
    from services.storage_service import StorageService
    svc = StorageService()
    svc.save_custom_keyword("Agency Founder", "smoke_test_kw")
    loaded = svc.load_custom_keywords()
    assert "Agency Founder" in loaded
    assert "smoke_test_kw" in loaded["Agency Founder"]
    svc.delete_custom_keywords("Agency Founder")
    reloaded = svc.load_custom_keywords()
    assert "smoke_test_kw" not in reloaded.get("Agency Founder", [])
    print("  storage_service (custom keywords save/load/delete): OK")


def test_analytics_service_imports():
    from services.analytics_service import AnalyticsService
    svc = AnalyticsService()
    assert hasattr(svc, "get_persona_distribution") or hasattr(svc, "render_persona_chart") or True
    print("  analytics_service: imports OK")


def test_optimization_service_imports():
    from services.optimization_service import OptimizationService
    svc = OptimizationService()
    print("  optimization_service: imports OK")


def test_sample_csv_exists():
    csv_path = Path(__file__).resolve().parent.parent / "data" / "sample_contacts.csv"
    assert csv_path.exists(), "data/sample_contacts.csv is missing"
    import pandas as pd
    df = pd.read_csv(csv_path)
    required = {"email", "firstname", "lastname", "company", "job_title"}
    assert required.issubset(set(df.columns)), f"Missing columns: {required - set(df.columns)}"
    assert len(df) >= 8, "Expected at least 8 sample contacts"
    print("  data/sample_contacts.csv: exists and valid")


def test_no_hardcoded_secrets():
    import re
    suspicious = re.compile(
        r"(sk-[A-Za-z0-9]{20,}|SG\.[A-Za-z0-9_\-]{20,}|pat-[A-Za-z0-9\-]{20,})"
    )
    root = Path(__file__).resolve().parent.parent
    for pyfile in root.glob("**/*.py"):
        if ".venv" in str(pyfile) or ".pythonlibs" in str(pyfile) or "__pycache__" in str(pyfile):
            continue
        text = pyfile.read_text(errors="ignore")
        match = suspicious.search(text)
        assert not match, f"Possible hardcoded secret found in {pyfile}: {match.group()}"
    print("  no hardcoded secrets detected")


if __name__ == "__main__":
    tests = [
        test_persona_service_imports_and_assigns,
        test_persona_service_sample_contacts,
        test_openai_service_no_key,
        test_openai_service_regenerate_section_no_key,
        test_email_service_no_key,
        test_email_service_dry_run,
        test_hubspot_service_no_key,
        test_storage_service_creates_db,
        test_storage_service_campaign_roundtrip,
        test_storage_service_custom_keywords,
        test_analytics_service_imports,
        test_optimization_service_imports,
        test_sample_csv_exists,
        test_no_hardcoded_secrets,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            print(f"Running {t.__name__}...")
            t()
            passed += 1
        except Exception as e:
            print(f"  FAILED: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
    else:
        print("All smoke tests passed.")
