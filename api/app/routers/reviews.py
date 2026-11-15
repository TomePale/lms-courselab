from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import PageParams, get_current_user, get_db, get_page_params, require_role
from app.models.user import User
from app.schemas.common import Page
from app.schemas.review import ReviewCreate, ReviewRead
from app.services import review_service

# Recenzije pripadaju tečaju, pa su ugniježđene pod njega
router = APIRouter(prefix="/courses/{course_id}/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewRead, status_code=201)
async def create_review(
    course_id: int,
    body: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("student")),
):
    return await review_service.create_review(db, course_id, body, user)


@router.get("/", response_model=Page[ReviewRead])
async def list_reviews(
    course_id: int,
    page: PageParams = Depends(get_page_params),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    items, total = await review_service.list_reviews(
        db, course_id, user, page.limit, page.offset
    )
    return {"items": items, "total": total, "limit": page.limit, "offset": page.offset}
