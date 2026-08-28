# app/modules/projects/routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.modules.storage.database import Base, engine
from . import service, schemas
from .models import Project  # noqa: F401 — import registers the table with Base.metadata

router = APIRouter(prefix="/projects", tags=["projects"])

# Idempotent: only creates the "projects" table if it doesn't already exist.
# Safe to call here even though storage.repository also calls create_all elsewhere.
Base.metadata.create_all(bind=engine)


def _to_out(project: Project) -> schemas.ProjectOut:
    return schemas.ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        color=project.color,
        doc_count=0,   # no document-project association exists yet
        chat_count=0,  # no chat persistence exists yet
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/", response_model=list[schemas.ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    try:
        projects = service.list_projects(db)
        return [_to_out(p) for p in projects]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/", response_model=schemas.ProjectOut)
def post_project(payload: schemas.ProjectCreate, db: Session = Depends(get_db)):
    try:
        project = service.create_project(db, name=payload.name, description=payload.description, color=payload.color)
        return _to_out(project)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/{project_id}")
def remove_project(project_id: int, db: Session = Depends(get_db)):
    try:
        deleted = service.delete_project(db, project_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Project not found")
        return {"deleted": True}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))