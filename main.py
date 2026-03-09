from fastapi import FastAPI, Request, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates #This is for accessing data from code to html templates, for loops, if else statements etc..
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StartletteHttpException



app = FastAPI()
app.mount("/static", StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [{
    'id':1,
    'author': 'john hickles',
    'weight': 69.9,
    'title': 'about me',
    'content': 'I live in 300 johnson st, at maywood pine groves',
    'date_posted': '03/04/2023'
},
{
    'id':2,
    'author': 'mary hickles',
    'weight': 64.9,
    'title': 'about me too',
    'content': 'I live in 200 johnson st, at maywood pine groves',
    'date_posted': '03/04/2023'

}


]

@app.get("/", include_in_schema=False, name='home')
@app.get("/posts", include_in_schema=False, name='posts')
def home(request: Request):
    return templates.TemplateResponse(request, "home.html",{"posts": posts, "title":"N"})



@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(post_id: int, request: Request):
    for post in posts:
        if post.get("id") == post_id:
            post_title = post['title'][:50] # get the first 50 characters of the title 
            return templates.TemplateResponse(request, "post.html",{"post": post, "title":post_title})
    raise HTTPException(status_code=404, detail=f"Post: '{post_id}' not found")



@app.get("/api/posts")
def get_posts():
    return posts


# creating a post retreiver base on id
@app.get("/api/posts/{post_id}")
def get_posts(post_id: int, request: Request):
    for post in posts:
        if post.get("id") == post_id:
            return post
        else:
            raise HTTPException(status_code=404, detail=f"Post: '{post_id}' not found")
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
            "message": message
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


