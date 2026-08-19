from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.core.storage import JsonStorage
from app.models import ProjectCreate, ProjectItem, ProjectUpdate, TaskCreate, TaskItem, TaskUpdate
from app.services.supabase_service import SupabasePersistence


class ProjectService:
    def __init__(self, storage: JsonStorage, persistence: SupabasePersistence | None = None) -> None:
        self.storage = storage
        self.persistence = persistence

    def _remote(self) -> bool:
        return bool(self.persistence and self.persistence.database_enabled)

    def all(self) -> list[ProjectItem]:
        rows = self.persistence.list_projects() if self._remote() else self.storage.read("projects", [])
        return [ProjectItem(**item) for item in rows]

    def create(self, payload: ProjectCreate) -> ProjectItem:
        if self._remote():
            return ProjectItem(**self.persistence.create_project(payload.model_dump(mode="json")))  # type: ignore[union-attr]
        item = ProjectItem(id=str(uuid4()), **payload.model_dump())
        projects = self.storage.read("projects", [])
        projects.append(item.model_dump(mode="json"))
        self.storage.write("projects", projects)
        return item

    def get(self, project_id: str) -> ProjectItem | None:
        if self._remote():
            rows = self.persistence.get_project(project_id)  # type: ignore[union-attr]
            return ProjectItem(**rows) if rows else None
        return next((ProjectItem(**item) for item in self.storage.read("projects", []) if item.get("id") == project_id), None)

    def update(self, project_id: str, payload: ProjectUpdate) -> ProjectItem | None:
        changes = payload.model_dump(exclude_none=True, mode="json")
        if self._remote():
            row = self.persistence.update_project(project_id, changes)  # type: ignore[union-attr]
            return ProjectItem(**row) if row else None
        projects = self.storage.read("projects", [])
        for item in projects:
            if item.get("id") == project_id:
                item.update(changes)
                item["updated_at"] = datetime.utcnow().isoformat()
                self.storage.write("projects", projects)
                return ProjectItem(**item)
        return None

    def delete(self, project_id: str) -> bool:
        if self._remote():
            return self.persistence.delete_project(project_id)  # type: ignore[union-attr]
        projects = self.storage.read("projects", [])
        updated = [item for item in projects if item.get("id") != project_id]
        if len(updated) == len(projects):
            return False
        self.storage.write("projects", updated)
        return True


class TaskService:
    def __init__(self, storage: JsonStorage, persistence: SupabasePersistence | None = None) -> None:
        self.storage = storage
        self.persistence = persistence

    def _remote(self) -> bool:
        return bool(self.persistence and self.persistence.database_enabled)

    def all(self) -> list[TaskItem]:
        rows = self.persistence.list_tasks() if self._remote() else self.storage.read("tasks", [])
        return [TaskItem(**item) for item in rows]

    def create(self, payload: TaskCreate) -> TaskItem:
        if self._remote():
            return TaskItem(**self.persistence.create_task(payload.model_dump(mode="json")))  # type: ignore[union-attr]
        item = TaskItem(id=str(uuid4()), **payload.model_dump())
        tasks = self.storage.read("tasks", [])
        tasks.append(item.model_dump(mode="json"))
        self.storage.write("tasks", tasks)
        return item

    def get(self, task_id: str) -> TaskItem | None:
        if self._remote():
            rows = self.persistence.get_task(task_id)  # type: ignore[union-attr]
            return TaskItem(**rows) if rows else None
        return next((TaskItem(**item) for item in self.storage.read("tasks", []) if item.get("id") == task_id), None)

    def update(self, task_id: str, payload: TaskUpdate) -> TaskItem | None:
        changes = payload.model_dump(exclude_none=True, mode="json")
        if self._remote():
            row = self.persistence.update_task(task_id, changes)  # type: ignore[union-attr]
            return TaskItem(**row) if row else None
        tasks = self.storage.read("tasks", [])
        for item in tasks:
            if item.get("id") == task_id:
                item.update(changes)
                item["updated_at"] = datetime.utcnow().isoformat()
                self.storage.write("tasks", tasks)
                return TaskItem(**item)
        return None

    def set_status(self, task_id: str, status: str) -> bool:
        if status not in {"todo", "doing", "done"}:
            return False
        if self._remote():
            return self.persistence.set_task_status(task_id, status)  # type: ignore[union-attr]
        return self.update(task_id, TaskUpdate(status=status)) is not None

    def delete(self, task_id: str) -> bool:
        if self._remote():
            return self.persistence.delete_task(task_id)  # type: ignore[union-attr]
        tasks = self.storage.read("tasks", [])
        updated = [item for item in tasks if item.get("id") != task_id]
        if len(updated) == len(tasks):
            return False
        self.storage.write("tasks", updated)
        return True
