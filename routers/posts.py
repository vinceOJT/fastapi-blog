
from typing import Annotated


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


import models
from database import get_db
from schemas import PostResponse, PostCreate, PostUpdate

from auth import CurrentUser




router = APIRouter()






# By adding the response_model it will now validate each on of our posts
@router.get("", response_model=list[PostResponse])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result_post = await db.execute(select(models.Post)
                                   .options(selectinload(models.Post.author))
                                   .order_by(models.Post.date_posted.desc()))
    posts = result_post.scalars().all()
    return posts
    
@router.post("",
          response_model=PostResponse,
          status_code=status.HTTP_201_CREATED,)
@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)

# CurrentUser is added, now only users can edit their own posts because its required
# In the paramerers to user their own token
async def create_post(post: PostCreate, current_user: CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
    )
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post


# creating a post retreiver base on id, this is for single posts
# The response model here is validates a single post
@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int,     db: Annotated[AsyncSession, Depends(get_db)]):
    result_post_id =   await db.execute(select(models.Post)
                                        .options(selectinload(models.Post.author))
                                        .where(models.Post.id == post_id))
    post = result_post_id.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    # return templates.TemplateResponse(request, "error.html")



# Updates all fields title & content is a need to change else it'll have a default value when updating
@router.put("/{post_id}", response_model=PostResponse)
async def update_post_full(post_id: int, post_data:PostCreate,   db: Annotated[AsyncSession, Depends(get_db)]):
    result_post_id =    await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result_post_id.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    # Returns an error status code when a post doesn't exist

    # If the author is being changed, verify the new user exists to maintain database integrity
    if post_data.user_id != post.user_id:
        result_user_id =    await db.execute(select(models.User).where(models.User.id == post_data.user_id))
        user = result_user_id.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
        )
    
    # Updates the current post with the latest post data
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    await db.commit()
    await db.refresh(post,  attribute_names=["author"])
    return post



# Update on a post can be title or content, one can change without the other having to be override by default values
@router.patch("/{post_id}", response_model=PostResponse)
async def update_post_partial(post_id: int, post_data:PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result_post_id =    await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result_post_id.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    update_data = post_data.model_dump(exclude_unset=True)  
    for field, value in update_data.items():
        setattr(post, field, value)


    await db.commit()
    await db.refresh(post,  attribute_names=["author"])
    return post




@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT )
async def delete_post(post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result_post_id =    await db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result_post_id.scalars().first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    

    await db.delete(post)
    await db.commit()































