from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    nickname = Column(String, primary_key=True, index=True)
    counter = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StartRequest(BaseModel):
    nickname: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/quiz/start")
def start_quiz(request: StartRequest):
    nickname = request.nickname
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.nickname == nickname).first()
        if not user:
            user = User(nickname=nickname, counter=0)
            db.add(user)
        user.counter += 1
        db.commit()
        db.refresh(user)
        return {"counter": user.counter}
    finally:
        db.close()

@app.get("/api/user/{nickname}")
def get_user(nickname: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.nickname == nickname).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"counter": user.counter}
    finally:
        db.close()