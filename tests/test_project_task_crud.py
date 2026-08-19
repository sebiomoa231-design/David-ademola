from project_service import ProjectService, TaskService
from app.core.storage import JsonStorage
from app.models import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate


def test_project_crud_uses_existing_local_storage_contract(tmp_path):
    storage = JsonStorage(tmp_path)
    service = ProjectService(storage)

    created = service.create(ProjectCreate(name="Launch", description="Initial plan"))
    assert service.get(created.id) == created

    updated = service.update(created.id, ProjectUpdate(description="Updated plan", goals=["Ship"]))
    assert updated is not None
    assert updated.description == "Updated plan"
    assert updated.goals == ["Ship"]

    assert service.delete(created.id) is True
    assert service.get(created.id) is None
    assert service.delete(created.id) is False


def test_task_crud_uses_existing_local_storage_contract(tmp_path):
    storage = JsonStorage(tmp_path)
    service = TaskService(storage)

    created = service.create(TaskCreate(project_id="project-1", title="Ship", notes="Verify"))
    assert service.get(created.id) == created

    updated = service.update(created.id, TaskUpdate(status="doing", notes="In progress"))
    assert updated is not None
    assert updated.status == "doing"
    assert updated.notes == "In progress"

    assert service.delete(created.id) is True
    assert service.get(created.id) is None
    assert service.delete(created.id) is False
