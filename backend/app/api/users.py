"""
User management endpoints: profile, update, delete
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Get information about the currently authenticated user.
    """
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update user profile (username, bio).

    Validations:
    - Username must be unique (if changed)
    """
    # Check if username is being changed and if it's already taken
    if update_data.username and update_data.username != current_user.username:
        result = await db.execute(
            select(User).where(User.username == update_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        current_user.username = update_data.username

    # Update bio if provided
    if update_data.bio is not None:
        current_user.bio = update_data.bio

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user account.

    Cascade delete:
    - Refresh tokens (automatically via CASCADE)
    - Reviews: Keep them but mark reviewer as deleted (or delete based on business logic)

    For now, we'll just deactivate the user instead of hard delete
    to preserve data integrity.
    """
    # Soft delete: deactivate user
    current_user.is_active = False
    await db.commit()

    # Alternatively, for hard delete:
    # await db.delete(current_user)
    # await db.commit()

    return None
