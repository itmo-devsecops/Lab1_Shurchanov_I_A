from fastapi import FastAPI, HTTPException, Depends, Request, Form, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
import uuid
import logging
from sqlalchemy import create_engine, Column, String, Integer, Table, MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
import jwt
from datetime import datetime, timedelta



REMOVED = "your_secret_key" #ключ к JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


DATABASE_URL = "postgresql://postgres:2004@postgres:5432/web?client_encoding=utf8"  #для теста вместо db нужен localhost, для докера наоборот
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Подключение к существующей таблице "users"
# users_table = Table("users", metadata, autoload_with=engine)
users_table = Table(
    "users", metadata,
    Column('id', UUID(as_uuid=True)),  # Пример колонки для идентификатора
    Column('username', String),  # Пример колонки для имени пользователя
    Column('password', String),
    Column('chat_id', String)   # Пример колонки для пароля
)
#chats_table = Table("chats", metadata, autoload_with=engine)
chats_table = Table(
    "chats", metadata,
    Column('id', Integer),  # Пример колонки для идентификатора
    Column('name', String),  # Пример колонки для имени пользователя
    Column('user_id', UUID(as_uuid=True)),
)
metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_token(username: str):
    data = {
        "sub": username,
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iss": "http://localhost"
    }
    access_token = jwt.encode(data, REMOVED, algorithm=ALGORITHM)
    return {"access_token": access_token}


def get_token_chat(username: str):
    data = {
        "sub": username,
        "iss": "http://localhost"
    }
    access_token = jwt.encode(data, REMOVED, algorithm=ALGORITHM)
    return {"access_token": access_token}



app = FastAPI()
logger = logging.getLogger("uvicorn.info")
templates = Jinja2Templates(directory="Templates")


class UserRequest(BaseModel):
    username: str
    password: str

def get_user(db: Session, user_id: str):
    return db.query(users_table).filter(users_table.c.id == user_id).first()

# Эта функция проверяет, есть ли пользователь в сессии
def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Необходимо войти в систему")
    
    user = get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user



@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.api_route("/register", methods=["GET", "POST"])
async def register(request: Request, db: Session = Depends(get_db), username: str = Form(None), password: str = Form(None)):
    if request.method == "POST":
        db_user = db.query(users_table).filter(users_table.c.username == username).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        user_id = str(uuid.uuid4())
        new_user = {"id": user_id, "username": username, "password": password}
        db.execute(users_table.insert().values(new_user))
        db.commit()
        return templates.TemplateResponse("register_success.html", {"request": request, "msg": "User registered successfully"})

    return templates.TemplateResponse("register.html", {"request": request})


@app.api_route("/login", methods=["GET", "POST"])
async def login(request: Request, db: Session = Depends(get_db), username: str = Form(None), password: str = Form(None)):
    if request.method == "POST":
        user = db.query(users_table).filter(users_table.c.username == username, users_table.c.password == password).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        token =  get_token(username)
        response = RedirectResponse(url="/chats", status_code=303)
        response.set_cookie(key="user_id", value=user.id)
        response.set_cookie(key="JWT", value=token["access_token"])
        return response

    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/chats")
async def get_chats(request: Request, search: Optional[str] = Query(None), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    token = request.cookies.get("JWT")
    if search:
        if len(search) < 6:
            return templates.TemplateResponse("main_page.html", {"request": request, "error": "Название чата должно содержать не менее 6 символов"})
        chats = db.query(chats_table).filter(chats_table.c.name.contains(search)).all()
    else:
        chats = db.query(chats_table).filter(chats_table.c.user_id == current_user.id).all()

    # Формируем ссылки на чаты, без передачи chat_id в шаблон напрямую
    
    chat_links = [{"name": chat.name, "url": f"http://localhost:5001/chat/{get_token_chat(str(chat.id))["access_token"]}"} for chat in chats]

    return templates.TemplateResponse("main_page.html", {"request": request, "chats": chat_links})


@app.post("/chats")
async def create_chat(request: Request, name: str = Form(...), db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_chat = {"name": name, "user_id": current_user.id}
    if len(name) < 6:
         return templates.TemplateResponse("main_page.html", {"request": request, "error": "Название чата должно содержать не менее 6 символов"})
    db.execute(chats_table.insert().values(new_chat))
    db.commit()
    return RedirectResponse(url="/chats", status_code=303)  # Перенаправление на страницу чатов




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)