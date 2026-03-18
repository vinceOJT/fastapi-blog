from contextlib import asynccontextmanager


# Type safety dependcy
from typing import Annotated


from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi import FastAPI, Request, HTTPException, status, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates #This is for accessing data from code to html templates, for loops, if else statements etc..
from fastapi.exceptions import RequestValidationError
# from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StartletteHttpException


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


from database import Base, engine, get_db
import models


from routers import posts, users

from schemas import PostResponse 


















# Creates the tables from models inherited from base if they dont already exist
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory='static'), name='static')
app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="templates") # To access the html templates

# Every api route ("") or (/user_id) or (/post_id), is being appended here
# Becoming a fully functional api route
 
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])



# Landing page
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    result =await db.execute(select(models.Post)
                                #  Switched from lazy loading to eager loading
                                # Lazy is when data is fetched 1 by 1 when neede, eager fetches everything even uneeded data
                              .options(selectinload(models.Post.author))
                               .order_by(models.Post.date_posted.desc()),
                             )
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {"posts": posts, "title": "Home"},
    )
 


















@app.get("/posts/{post_id}", include_in_schema=False)
async def post_page(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result_post_id =await db.execute(select(models.Post)
                .options(selectinload(models.Post.author))
                .where(models.Post.id == post_id))
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
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result_user_id = await db.execute(select(models.User) # does not need a selectinload because its not accessing a relationships in User
                                 .where(models.User.id == user_id))
    user = result_user_id.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    result = await db.execute(select(models.Post).where(models.Post.user_id == user_id)
                              .order_by(models.Post.date_posted.desc()))
    posts = result.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_post.html",
        {"posts": posts, "user": user, "title": f"{user.username}'s Posts"},
    )




@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )


@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )


































# error handling for page errors
# this is anything detected by starlette
@app.exception_handler(StartletteHttpException)
async def generatl_http_exception_handler(request: Request, exception: StartletteHttpException):

    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exception)
    message = (
    exception.detail
    if exception.detail
    else "An error occured check your Requests"
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
async def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exception)

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


