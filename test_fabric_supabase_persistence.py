from david_fabric.core.models import Artifact, ExecutionAttempt, Goal, GoalPlan, PlanStep, Run, Verification
from david_fabric.storage import db


class FakeSupabaseTableClient:
    def __init__(self):
        self.tables: dict[str, list[dict]] = {}

    def upsert(self, table, payload, _on_conflict):
        rows = self.tables.setdefault(table, [])
        key = "goal_id" if table == "david_agent_plans" else "id"
        for index, current in enumerate(rows):
            if current.get(key) == payload.get(key):
                rows[index] = dict(payload)
                return [dict(payload)]
        rows.append(dict(payload))
        return [dict(payload)]

    def insert(self, table, payload):
        rows = self.tables.setdefault(table, [])
        row = dict(payload)
        row.setdefault("id", f"event-{len(rows) + 1}")
        rows.append(row)
        return [row]

    def select(self, table, params):
        rows = [dict(row) for row in self.tables.get(table, [])]
        for field in ("id", "goal_id", "run_id"):
            query = params.get(field)
            if isinstance(query, str) and query.startswith("eq."):
                rows = [row for row in rows if str(row.get(field)) == query[3:]]
        if params.get("order") == "created_at.desc":
            rows.reverse()
        return rows


def test_fabric_records_use_existing_supabase_boundary_when_enabled(monkeypatch):
    remote = FakeSupabaseTableClient()
    monkeypatch.setattr(db, "_remote", lambda: remote)

    goal = Goal(id="goal-1", title="Canonical David", objective="Build one shared run")
    db.save_goal(goal)
    assert db.get_goal(goal.id)["objective"] == "Build one shared run"

    plan = GoalPlan(goal_id=goal.id, steps=[PlanStep(id="step-1", title="Plan", capability="research")])
    db.save_plan(plan)
    assert db.get_plan(goal.id)["steps"][0]["capability"] == "research"

    run = Run(id="run-1", goal_id=goal.id, objective="Build one shared run", selected_provider="canonical")
    db.save_run(run)
    assert db.get_run(run.id)["selected_provider"] == "canonical"

    attempt = ExecutionAttempt(id="attempt-1", run_id=run.id, capability_id="research", status="completed", output={"truthful": True})
    db.save_attempt(attempt)
    assert db.get_attempts(run.id)[0]["output"] == {"truthful": True}

    artifact = Artifact(id="artifact-1", run_id=run.id, attempt_id=attempt.id, name="result", kind="report")
    db.save_artifact(artifact)
    assert db.get_artifacts(run.id)[0]["name"] == "result"

    verification = Verification(id="verification-1", run_id=run.id, status="verified", checks=[{"name": "provenance", "passed": True}])
    db.save_verification(verification)
    assert db.get_verification(run.id)["status"] == "verified"

    db.add_event(run.id, "run.completed", {"status": "completed"})
    assert db.get_events(run.id)[0]["payload"] == {"status": "completed"}
    assert "david_agent_runs" in remote.tables
    assert "david_agent_events" in remote.tables


def test_fabric_does_not_hide_missing_remote_records_with_local_data(monkeypatch):
    remote = FakeSupabaseTableClient()
    monkeypatch.setattr(db, "_remote", lambda: remote)
    monkeypatch.setattr(db, "_find_local", lambda *_args: {"id": "missing", "status": "local-only"})

    assert db.get_run("missing") is None


def test_fabric_uses_local_compatibility_store_only_when_supabase_is_disabled(monkeypatch):
    monkeypatch.setattr(db, "_remote", lambda: None)
    local_records: list[dict] = []

    def read(_name, default):
        return list(local_records) if local_records else default

    def write(_name, value):
        local_records[:] = value

    monkeypatch.setattr(db._STORAGE, "read", read)
    monkeypatch.setattr(db._STORAGE, "write", write)

    run = Run(id="local-run", goal_id="local-goal")
    db.save_run(run)
    assert db.get_run(run.id)["id"] == "local-run"
