from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from app.core.storage import JsonStorage
from app.models import ProjectCreate, ProjectItem, TaskCreate, TaskItem


class ProjectService:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def all(self) -> list[ProjectItem]:
        return [ProjectItem(**item) for item in self.storage.read("projects", [])]

    def create(self, payload: ProjectCreate) -> ProjectItem:
        item = ProjectItem(id=str(uuid4()), **payload.model_dump())
        projects = self.storage.read("projects", [])
        projects.append(item.model_dump(mode="json"))
        self.storage.write("projects", projects)
        return item


class TaskService:
    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage

    def all(self) -> list[TaskItem]:
        return [TaskItem(**item) for item in self.storage.read("tasks", [])]

    def create(self, payload: TaskCreate) -> TaskItem:
        item = TaskItem(id=str(uuid4()), **payload.model_dump())
        tasks = self.storage.read("tasks", [])
        tasks.append(item.model_dump(mode="json"))
        self.storage.write("tasks", tasks)
        return item

    def set_status(self, task_id: str, status: str) -> bool:
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
