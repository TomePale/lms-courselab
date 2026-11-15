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
from app.schemas.enrollment import EnrollmentRead
from app.services import enrollment_service

# Bez prefiksa: rute ovog routera žive pod /courses/..., /me/... i /enrollments/...
router = APIRouter(tags=["enrollments"])


@router.post(
    "/courses/{course_id}/enrollments/", response_model=EnrollmentRead, status_code=201
)
async def enroll(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("student")),
):
    return await enrollment_service.enroll(db, course_id, user)


@router.get("/courses/{course_id}/enrollments/", response_model=Page[EnrollmentRead])
async def list_course_enrollments(
    course_id: int,
    page: PageParams = Depends(get_page_params),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("trainer", "admin")),
):
    items, total = await enrollment_service.list_course_enrollments(
        db, course_id, user, page.limit, page.offset
    )
    return {"items": items, "total": total, "limit": page.limit, "offset": page.offset}


@router.get("/me/enrollments/", response_model=Page[EnrollmentRead])
async def list_my_enrollments(
    page: PageParams = Depends(get_page_params),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("student")),
):
    items, total = await enrollment_service.list_my_enrollments(
        db, user, page.limit, page.offset
    )
    return {"items": items, "total": total, "limit": page.limit, "offset": page.offset}


@router.get("/enrollments/{enrollment_id}", response_model=EnrollmentRead)
async def get_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await enrollment_service.get_enrollment(db, enrollment_id, user)


@router.post("/enrollments/{enrollment_id}/accept", response_model=EnrollmentRead)
async def accept(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("trainer", "admin")),
):
    return await enrollment_service.accept(db, enrollment_id, user)


@router.post("/enrollments/{enrollment_id}/reject", response_model=EnrollmentRead)
async def reject(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("trainer", "admin")),
):
    return await enrollment_service.reject(db, enrollment_id, user)
