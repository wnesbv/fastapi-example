
import uvicorn
from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

# ..
#from config.db import on_app_startup
# ..

from routes.urls import routes
from account import route_auth
from comment import route_comment
from item import route_item
from reserve import route_reserve
from trivia import route_trivia
from user import route_user
from vote import route_vote
from api import auth, user, item as tm_item, comment as tm_comment, reserve as tm_reserve
from dump_csv import router_csv


app = FastAPI(
    # ..
    #on_startup=[on_app_startup],
    # ..
    routes=routes
)


app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(route_auth.router)
app.include_router(route_comment.router)
app.include_router(route_item.router)
app.include_router(route_reserve.router)
app.include_router(route_trivia.router)
app.include_router(route_user.router)
app.include_router(route_vote.router)
app.include_router(router_csv.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(tm_item.router)
app.include_router(tm_comment.router)
app.include_router(tm_reserve.router)


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)
