
import uvicorn
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from config import settings

#from config.db import on_app_startup

from account import route_auth
from comment import route_comment
from item import route_item
from trivia import route_trivia
from user import route_user
from vote import route_vote
from api import router_api


app = FastAPI(
    #on_startup=[on_app_startup]
)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(route_auth.router)
app.include_router(route_comment.router)
app.include_router(route_item.router)
app.include_router(route_trivia.router)
app.include_router(route_user.router)
app.include_router(route_vote.router)
app.include_router(router_api.router)


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000, debug=settings.DEBUG)
