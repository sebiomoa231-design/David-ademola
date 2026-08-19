from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.core.storage import JsonStorage
from app.models import ProjectCreate, ProjectItem, ProjectUpdate, TaskCreate, TaskItem, TaskUpdate
from app.services.project_service import ProjectService, TaskService
from app.services.supabase_service import SupabasePersistence

router = APIRouter(prefix="/projects", tags=["projects"])


def get_persistence(settings: Settings = Depends(get_settings)) -> SupabasePersistence:
    return SupabasePersistence(settings)


def get_project_service(
    settings: Settings = Depends(get_settings),
) -> ProjectService:
    return ProjectService(JsonStorage(), SupabasePersistence(settings))


def get_task_service(
    settings: Settings = Depends(get_settings),
) -> TaskService:
    return TaskService(JsonStorage(), SupabasePersistence(settings))


@router.get("", response_model=list[ProjectItem])
def list_projects(service: ProjectService = Depends(get_project_service)) -> list[ProjectItem]:
    return service.all()


@router.post("", response_model=ProjectItem)
def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectItem:
    return service.create(payload)


# Static task collection routes must remain before the dynamic project-ID routes.
@router.get("/tasks", response_model=list[TaskItem])
def list_tasks(service: TaskService = Depends(get_task_service)) -> list[TaskItem]:
    return service.all()


@router.post("/tasks", response_model=TaskItem)
def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskItem:
    return service.create(payload)


@router.get("/tasks/{task_id}", response_model=TaskItem)
def get_task(task_id: str, service: TaskService = Depends(get_task_service)) -> TaskItem:
    task = service.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskItem)
def update_task(
    task_id: str,
    payload: TaskUpdate,
    service: TaskService = Depends(get_task_service),
) -> TaskItem:
    task = service.update(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: str, service: TaskService = Depends(get_task_service)) -> dict[str, bool]:
    if not service.delete(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"deleted": True}


@router.get("/{project_id}", response_model=ProjectItem)
def get_project(project_id: str, service: ProjectService = Depends(get_project_service)) -> ProjectItem:
    project = service.get(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectItem)
def update_project(
    project_id: str,
    payload: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectItem:
    project = service.update(project_id, payload)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}")
def delete_project(project_id: str, service: ProjectService = Depends(get_project_service)) -> dict[str, bool]:
    if not service.delete(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return {"deleted": True}
