from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.core.storage import JsonStorage
from app.models import ProjectCreate, ProjectItem, TaskCreate, TaskItem
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

    def set_status(self, task_id: str, status: str) -> bool:
        if self._remote():
            return self.persistence.set_task_status(task_id, status)  # type: ignore[union-attr]
        tasks = self.storage.read("tasks", [])
        found = False
        for item in tasks:
            if item.get("id") == task_id:
                item["status"] = status
                item["updated_at"] = datetime.utcnow().isoformat()
                found = True
                break
        if found:
            self.storage.write("tasks", tasks)
        return found
