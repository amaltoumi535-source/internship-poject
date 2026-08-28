# app/modules/projects/service.py
"""Service layer for projects: simple CRUD backed by the projects table."""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from .models import Project

logger = logging.getLogger(__name__)


def list_projects(db: Session) -> List[Project]:
    return db.query(Project).order_by(Project.updated_at.desc()).all()


def create_project(db: Session, name: str, description: Optional[str] = None, color: Optional[str] = None) -> Project:
    project = Project(name=name, description=description, color=color)
    db.add(project)
    db.commit()
    db.refresh(project)
    logger.info("Created project %s (%s)", project.id, project.name)
    return project


def delete_project(db: Session, project_id: int) -> bool:
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True