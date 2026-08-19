from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import settings as settings_routes
from models import SettingsUpdate


class FakePersistence:
    database_enabled = True

    def __init__(self):
        self.payload = None

    def get_settings(self):
        return self.payload

    def update_settings(self, payload):
        self.payload = dict(payload)
        return dict(payload)


def fake_settings():
    return SimpleNamespace(
        provider_priority_list=["gemini", "groq"],
        max_upload_mb=25,
    )


def test_settings_patch_persists_and_reads_back(monkeypatch):
    persistence = FakePersistence()
    monkeypatch.setattr(settings_routes, "SupabasePersistence", lambda _settings: persistence)

    updated = settings_routes.update_settings_route(
        SettingsUpdate(workspace_name="David Production", timezone="Europe/London"),
        fake_settings(),
    )
    assert updated.persistence_status == "persisted"
    assert updated.workspace_name == "David Production"

    read_back = settings_routes.get_settings_route(fake_settings())
    assert read_back.persistence_status == "persisted"
    assert read_back.workspace_name == "David Production"
    assert read_back.timezone == "Europe/London"


def test_settings_patch_reports_disabled_persistence(monkeypatch):
    monkeypatch.setattr(
        settings_routes,
        "SupabasePersistence",
        lambda _settings: SimpleNamespace(database_enabled=False),
    )

    with pytest.raises(HTTPException) as error:
        settings_routes.update_settings_route(SettingsUpdate(theme="light"), fake_settings())
    assert error.value.status_code == 503

    read_back = settings_routes.get_settings_route(fake_settings())
    assert read_back.persistence_status == "local-only"
