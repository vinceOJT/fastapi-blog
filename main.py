from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates #This is for accessing data from code to html templates, for loops, if else statements etc..
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StartletteHttpException

from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from database import Base, engine, get_db

from schemas import PostCreate, PostResponse, UserCreate, UserResponse

# Type safety dependcy
from typing import Annotated


# Creates the tables from models inherited from base if they dont already exist
Base.metadata.create_all(bind=engine)


app = FastAPI()
app.mount("/static", StaticFiles(directory='static'), name='static')
app.mount("/media", StaticFiles(directory="media"), name="media")


templates = Jinja2Templates(directory="templates") # To access the html templates

# posts: list[dict] = [{
#     'id':1,
#     'author': 'john hickles',
#     'weight': 69.9,
#     'title': 'about me',
#     'content': 'I live in 300 johnson st, at maywood pine groves',
#     'date_posted': '03/04/2023'
# },
# {
#     'id':2,
#     'author': 'mary hickles',
#     'weight': 64.9,
#     'title': 'about me too',
#     'content': 'I live in 200 johnson st, at maywood pine groves',
#     'date_posted': '03/04/2023'

# }
# ]

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )


@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int, db: Annotated[Session, Depends(get_db)]):
    result_post_id = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result_post_id.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
 
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    result_user_id = db.execute(select(models.User).where(models.User.id == user_id))
    user = result_user_id.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )



@app.post("/api/users",
          response_model=UserResponse,
          status_code=status.HTTP_201_CREATED,)

def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result_username = db.execute(select(models.User).where(models.User.username == user.username)) # checks for simillar usernames
    existing_user = result_username.scalars().first() # checks for the first existing username in dba
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username already exists",
        )

    result_email = db.execute(select(models.User).where(models.User.email == user.email)) # checks for simillar emails
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
    db.commit()
    db.refresh()

    return new_user














@app.get("/api/users/posts/{user_id}", response_model=PostResponse)
def get_user(user_id: int, request: Request, db: Annotated[Session, Depends(get_db)]):
    # simillar logic when creating users
    result_id = db.execute(select(models.User).where(models.User.id == user_id))
    existing_id = result_id.scalars().first()
    if existing_id:
        return existing_id
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found", 
    )

@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: Annotated[Session, Depends(get_db)]):
    result_id = db.execute(select(models.User).where(models.User.id == user_id))
    existing_id = result_id.scalars().first()
    if not existing_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = db.execute(select(models.Post).where(models.Post.user_id == user_id))
    posts = result.scalars().all()
    return posts



# By adding the response_model it will now validate each on of our posts
@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result_post = db.execute(select(models.Post))
    posts = result_post.scalars().all()
    return posts
    
@app.post("/api/posts",
          response_model=PostResponse,
          status_code=status.HTTP_201_CREATED,)
@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate, db: Annotated[Session, Depends(get_db)]):
    result_user_id = db.execute(select(models.User).where(models.User.id == post.user_id))
    user = result_user_id.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    new_post = models.Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post



# creating a post retreiver base on id, this is for single posts
# The response model here is validates a single post
@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(models.Post).where(models.Post.id == post_id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    # return templates.TemplateResponse(request, "error.html")


















# error handling for page errors
# this is anything detected by starlette
@app.exception_handler(StartletteHttpException)
def generatl_http_exception_handler(request: Request, exception: StartletteHttpException):
    message = (
        exception.detail
        if exception.detail
        else "An error occured check your Requests"
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


# error handling for validation
# this is anything detected by request validation
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail", exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request, Check input"

        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )


