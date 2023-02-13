from http.client import HTTPException, HTTPResponse
from fastapi import APIRouter, Request, Form, status, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from fastapi_login import LoginManager
from fastapi import FastAPI, File, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from tortoise.functions import Sum
from slugify import slugify
from datetime import datetime
from passlib.context import CryptContext
import secrets
import uuid
from .models import *


SECRET = 'your-secret-key'
router = APIRouter()
manager = LoginManager(SECRET, token_url='/auth/token')
templates = Jinja2Templates(directory="user/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("registration.html", {
        "request": request, })


@router.get("/welcome/", response_class=HTMLResponse)
async def read_item(request: Request):
    data = await User.all()
    return templates.TemplateResponse("welcome.html", {
        "data":data,
        "request":request})

@router.post('/add_registration/')
async def create_user(request: Request, email: str = Form(...),
                      name: str = Form(...),
                      phone: str = Form(...),
                      password: str = Form(...)):

        user_obj = await User.create(email=email, name=name,
                                     phone=phone, password=get_password_hash(password))
        return RedirectResponse("/login/",  status_code=status.HTTP_302_FOUND)


@router.get("/login/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@manager.user_loader()
async def load_user(email: str):
    if await User.exists(email=email):
        newapil = await User.get(email=email)
        return newapil


@router.post('/login/')
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    email = email

    user = await load_user(email)

    if not User:
        # flash(request,  "User not exist", "danger")
        return RedirectResponse('/login/', status_code=status.HTTP_302_FOUND)
    elif not verify_password(password, user.password):
        # flash(request,  "Faild to login", "danger")
        return RedirectResponse('/login/', status_code=status.HTTP_302_FOUND)
    else:
        # request.session["user_id"] = U.uuid.UUID
        request.session["user_name"] = user.name
        # print(request.session["user_id"])
        print(request.session["user_name"])
        return RedirectResponse('/welcome/', status_code=status.HTTP_302_FOUND)
        

# @router.get("/delete/{id}")
# async def delete(request:Request,id:int):
#     user= await User.get(id=id).delete()
#     return RedirectResponse("/welcome/",  status_code=status.HTTP_302_FOUND)

# @router.get("/update/{id}")
# async def update_user(request:Request,id:int):
#     user=await User.get(id=id)
#     # return templates.TemplateResponse("update.html", {"request": request}, {"user": user})
#     return RedirectResponse("/update/", {"user":user})

# @router.post('/update_user/{id}')
# async def update(request: Request, email: str = Form(...), name: str = Form(...), phone: str = Form(...)):
#     if await User.filter(id=id).exists():
#         user = await filter(id=id).update(name=name, email=email, phone=phone)

#         return RedirectResponse("/welcome/")



@router.get("/del/{id}/")
async def dele(request: Request, id:int):
        await User.get(id=id).delete()
        data=await User.all()
        return templates.TemplateResponse("welcome.html", {"request": request,'data':data})


@router.get("/update/{id}/")
async def read_item(request: Request, id:int):
    user= await User.get(id=id)
    return templates.TemplateResponse("update.html", {"request": request,'user':user})


@router.post("/update_user/", response_class=HTMLResponse)
async def update(request: Request,id:int=Form(...),
                                    name: str =Form(...),
                                   email:str =Form(...),
                                   phone:str =Form(...),
                                   ):
    
    if await User.get(id=id).exists():
        user= await User.filter(id=id).update(name=name,email=email,phone=phone)
        data= await User.all()
        return templates.TemplateResponse("welcome.html", {"request": request,'data':data})