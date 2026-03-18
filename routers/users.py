
from typing import Annotated


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


import models
from database import get_db
from schemas import PostResponse, UserCreate, UserPublic, UserPrivate, UserUpdate


from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm


from auth import create_access_token, hash_password, oauth2_scheme, verify_access_token, verify_password

from config import settings

router = APIRouter()


# main.py will have a route of /api/users, so this users.py will contain an 
# Empty route because it will inherit the /api/users from mainAsyncSession

@router.post("",
          response_model=UserPrivate,
          status_code=status.HTTP_201_CREATED,)

async def create_user(user: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result_username = await db.execute(select(models.User).where(models.User.username == user.username)) # checks for simillar usernames
    existing_user = result_username.scalars().first() # checks for the first existing username in dba
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username already exists",
        )

    result_email = await db.execute(select(models.User).where(models.User.email == user.email)) # checks for simillar emails
    existing_email = result_email.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email already exists",
        )
    new_user = models.User(
        username=user.username,
        email=user.email,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    db.refresh(new_user)

    return new_user



@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result_user_id = await db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    user = result_user_id.scalars().first()
    if user:
        return user
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")




@router.get("/{user_id}/posts", response_model=list[PostResponse])
async def get_user_posts(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result_user_post = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result_user_post.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result =await db.execute(select(models.Post)
                            .options(selectinload(models.Post.author))
                            .where(models.Post.user_id == user_id)
                            .order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return posts





@router.patch("/{user_id}", response_model=UserPublic)
async def update_user(user_id: int, user_update:UserUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result_user_id =await db.execute(
        select(models.User).where(models.User.id == user_id),
    )
    user = result_user_id.scalars().first()
    # Checks if user does not exist
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
    )
    # Checks for similar usernames
    if user_update.username is not None and user_update.username != user.username:
        result_same_username = db.execute(
        select(models.User).where(models.User.username == user_update.username)
        )
        existing_username = result_same_username.scalars().first()
        if existing_username:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
             )

    # Checks for similar emails
    if user_update.email is not None and user_update.email != user.email:
        result_same_email = db.execute(
        select(models.User).where(models.User.email == user_update.email)
        )
        existing_email = result_same_email.scalars().first()
        if existing_email:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
                )

    # Check if email and name doesn't have similarities
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.image_file is not None:
            user.image_file = user_update.image_file

    await db.commit()
    await db.refresh(user)
    return user



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result_to_be_deleted = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result_to_be_deleted.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()





































