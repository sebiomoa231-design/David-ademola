from project_service import ProjectService, TaskService
from models import ProjectCreate, ProjectUpdate, TaskCreate, TaskUpdate


class FakeStorage:
    def __init__(self):
        self.values = {}

    def read(self, name, default):
        return self.values.get(name, default)

    def write(self, name, value):
        self.values[name] = value


class FakePersistence:
    database_enabled = True

    def __init__(self):
        self.projects = {}
        self.tasks = {}

    def list_projects(self):
        return list(self.projects.values())

    def get_project(self, project_id):
        return self.projects.get(project_id)

    def create_project(self, payload):
        row = {"id": "project-1", **payload}
        self.projects[row["id"]] = row
        return row

    def update_project(self, project_id, payload):
        if project_id not in self.projects:
            return None
        self.projects[project_id].update(payload)
        return self.projects[project_id]

    def delete_project(self, project_id):
        return self.projects.pop(project_id, None) is not None

    def list_tasks(self):
        return list(self.tasks.values())

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def create_task(self, payload):
        row = {"id": "task-1", **payload}
        self.tasks[row["id"]] = row
        return row

    def update_task(self, task_id, payload):
        if task_id not in self.tasks:
            return None
        self.tasks[task_id].update(payload)
        return self.tasks[task_id]

    def delete_task(self, task_id):
        return self.tasks.pop(task_id, None) is not None

    def set_task_status(self, task_id, status):
        return bool(self.update_task(task_id, {"status": status}))


def test_project_crud_has_read_back_and_truthful_delete():
    persistence = FakePersistence()
    service = ProjectService(FakeStorage(), persistence)

    created = service.create(ProjectCreate(name="David AI"))
    assert service.get(created.id).name == "David AI"

    updated = service.update(created.id, ProjectUpdate(description="Persistent operating system"))
    assert updated.description == "Persistent operating system"
    assert service.get(created.id).description == "Persistent operating system"

    assert service.delete(created.id) is True
    assert service.get(created.id) is None
    assert service.delete(created.id) is False


def test_task_crud_supports_update_complete_retrieve_and_delete():
    persistence = FakePersistence()
    service = TaskService(FakeStorage(), persistence)

    created = service.create(TaskCreate(title="Verify persistence"))
    assert service.get(created.id).status == "todo"

    updated = service.update(created.id, TaskUpdate(notes="read back from database", status="doing"))
    assert updated.status == "doing"
    assert service.get(created.id).notes == "read back from database"

    assert service.set_status(created.id, "done") is True
    assert service.get(created.id).status == "done"
    assert service.delete(created.id) is True
    assert service.get(created.id) is None
    assert service.delete(created.id) is False
