from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserProfileUpdate
from app.api import deps

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(deps.get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    if payload.financial:
        for field, value in payload.financial.model_dump(exclude_none=True).items():
            setattr(current_user, field, value)

    if payload.labor:
        for field, value in payload.labor.model_dump(exclude_none=True).items():
            setattr(current_user, field, value)

    if payload.debt:
        for field, value in payload.debt.model_dump(exclude_none=True).items():
            setattr(current_user, field, value)

    if payload.housing:
        for field, value in payload.housing.model_dump(exclude_none=True).items():
            setattr(current_user, field, value)

    if payload.household:
        for field, value in payload.household.model_dump(exclude_none=True).items():
            setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user
