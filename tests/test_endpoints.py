import json
import os
from pathlib import Path
import pytest


def test_companies_returns_list(client):
    resp = client.get("/api/companies")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "companies" in data
    assert isinstance(data["companies"], list)


def test_companies_excludes_template(client):
    resp = client.get("/api/companies")
    data = resp.get_json()
    slugs = [c["value"] for c in data["companies"]]
    assert "template" not in slugs


def test_new_company_creates_file(client, tmp_path, monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module, "BEDRIJVEN_DIR", tmp_path)
    (tmp_path / "template.md").write_text("# Template")

    resp = client.post(
        "/api/new-company",
        data=json.dumps({"name": "Test Bedrijf BV"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["slug"] == "test_bedrijf_bv"
    assert (tmp_path / "test_bedrijf_bv.md").exists()


def test_new_company_empty_name_returns_400(client):
    resp = client.post(
        "/api/new-company",
        data=json.dumps({"name": ""}),
        content_type="application/json",
    )
    assert resp.status_code == 400


def test_new_company_idempotent(client, tmp_path, monkeypatch):
    import app as app_module
    monkeypatch.setattr(app_module, "BEDRIJVEN_DIR", tmp_path)
    (tmp_path / "template.md").write_text("# Template")
    (tmp_path / "bestaand_bedrijf.md").write_text("# Existing")

    resp = client.post(
        "/api/new-company",
        data=json.dumps({"name": "Bestaand Bedrijf"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert (tmp_path / "bestaand_bedrijf.md").read_text() == "# Existing"
