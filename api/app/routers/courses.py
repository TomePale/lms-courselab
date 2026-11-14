from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import (
    PageParams,
    get_current_user,
    get_db,
    get_page_params,
    require_role,
)
from app.models.user import User
from app.schemas.common import Page
from app.schemas.course import CourseCreate, CourseRead, CourseUpdate
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=Page[CourseRead])
async def list_courses(
    page: PageParams = Depends(get_page_params),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = await course_service.list_courses(db, user, page.limit, page.offset)
    return {"items": items, "total": total, "limit": page.limit, "offset": page.offset}


@router.post("/", response_model=CourseRead, status_code=201)
async def create_course(
    body: CourseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("trainer", "admin")),
):
    return await course_service.create_course(db, body, user)


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await course_service.get_visible_course(db, course_id, user)


@router.patch("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    body: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("trainer", "admin")),
):
    return await course_service.update_course(db, course_id, body, user)


# Status se ne mijenja PATCH-om nego zasebnim radnjama: svaka ima svoje pravilo
@router.post("/{course_id}/publish", response_model=CourseRead)
async def publish_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("trainer", "admin")),
):
    return await course_service.change_status(db, course_id, "publish", user)


@router.post("/{course_id}/archive", response_model=CourseRead)
async def archive_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("trainer", "admin")),
):
    return await course_service.change_status(db, course_id, "archive", user)


# Brisati se smije tečaj na koji nitko nije upisan
@router.delete("/{course_id}", status_code=204)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("trainer", "admin")),
):
    await course_service.delete_course(db, course_id, user)