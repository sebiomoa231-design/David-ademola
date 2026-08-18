from fastapi import APIRouter, Depends

from app.core.storage import JsonStorage
from app.models import ProjectCreate, ProjectItem, TaskCreate, TaskItem
from app.services.project_service import ProjectService, TaskService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service() -> ProjectService:
    return ProjectService(JsonStorage())


def get_task_service() -> TaskService:
    return TaskService(JsonStorage())


@router.get("", response_model=list[ProjectItem])
def list_projects(service: ProjectService = Depends(get_project_service)) -> list[ProjectItem]:
    return service.all()


@router.post("", response_model=ProjectItem)
def create_project(
    payload: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectItem:
    return service.create(payload)


@router.get("/tasks", response_model=list[TaskItem])
def list_tasks(service: TaskService = Depends(get_task_service)) -> list[TaskItem]:
    return service.all()


@router.post("/tasks", response_model=TaskItem)
def create_task(
    payload: TaskCreate,
    service: TaskService = Depends(get_task_service),
) -> TaskItem:
    return service.create(payload)
