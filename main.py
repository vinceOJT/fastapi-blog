from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates #This is for accessing data from code to html templates, for loops, if else statements etc..


app = FastAPI()
app.mount("/static", StaticFiles(directory='static'), name='static')

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [{
    'id':1,
    'name': 'john hickles',
    'weight': 69.9,
    'title': 'about me',
    'context': 'I live in 300 johnson st, at maywood pine groves',
    'date_posted': '03/04/2023'
},
{
    'id':2,
    'name': 'mary hickles',
    'weight': 64.9,
    'title': 'about me too',
    'context': 'I live in 200 johnson st, at maywood pine groves',
    'date_posted': '03/04/2023'

}


]

@app.get("/", include_in_schema=False, name='home')
@app.get("/posts", include_in_schema=False, name='posts')
def home(request: Request):
    return templates.TemplateResponse(request, "home.html",{"posts": posts, "title":"N"})

@app.get("/api/posts")
def get_posts():
    return posts










