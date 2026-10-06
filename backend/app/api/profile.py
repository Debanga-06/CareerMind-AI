"""
/api/profile routes.

Requires auth. A user with no saved profile yet gets a valid, empty-ish
ProfileResponse (not a 404) — an unset profile is a normal state, not an
error.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.session import get_db
from app.models.profile import Profile
from app.models.user import User
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest

router = APIRouter(prefix="/profile", tags=["profile"])


def _to_response(profile: Profile | None) -> ProfileResponse:
    if profile is None:
        return ProfileResponse(skills=[])
    return ProfileResponse(
        target_career=profile.target_career,
        experience_level=profile.experience_level,
        location=profile.location,
        skills=profile.skills or [],
        updated_at=profile.updated_at,
    )


@router.get("", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    return _to_response(profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProfileResponse:
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
    if profile is None:
        profile = Profile(user_id=current_user.id)
        db.add(profile)

    if payload.target_career is not None:
        profile.target_career = payload.target_career
    if payload.experience_level is not None:
        profile.experience_level = payload.experience_level
    if payload.location is not None:
        profile.location = payload.location
    if payload.skills is not None:
        profile.skills = payload.skills

    db.commit()
    db.refresh(profile)
    return _to_response(profile)
