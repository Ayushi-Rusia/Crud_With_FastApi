from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from user import routes as AdminRoute
from tortoise.contrib.fastapi import register_tortoise
from configs.connection import DATABASE_URL
from user import api as apiroute
from starlette.middleware.sessions import SessionMiddleware



db_url=DATABASE_URL()
app=FastAPI()
app.add_middleware(SessionMiddleware, secret_key="some-random-string", max_age=None)

app.mount('/static', StaticFiles(directory="static"), name="static")
app.include_router(AdminRoute.router,tags=["Admin"])
# app.include_router(apiRoute.router,prefix="api/")


register_tortoise(
    app,
    db_url=db_url,
    modules={'models':['user.models']},
    generate_schemas  = True,
    add_exception_handlers =True
)
