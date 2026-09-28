from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

app = FastAPI()


# ==========================================
# PostgreSQL Connection
# ==========================================

import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/fastapi_db"
)
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ==========================================
# Database Table
# ==========================================

class StudentDB(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)


# إنشاء الجدول تلقائياً
Base.metadata.create_all(bind=engine)


# ==========================================
# Pydantic Model
# ==========================================

class Student(BaseModel):
    name: str
    age: int


# ==========================================
# Database Session
# ==========================================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# Routes
# ==========================================

@app.get("/")
def home():
    return {"message": "Hello World"}


@app.get("/students")
def get_students(db: Session = Depends(get_db)):

    students = db.query(StudentDB).all()

    return students


@app.get("/students/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):

    student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return student


@app.get("/search")
def search_student(
    name: str,
    age: int,
    db: Session = Depends(get_db)
):

    students = db.query(StudentDB).filter(
        StudentDB.name == name,
        StudentDB.age == age
    ).all()

    return students


@app.post("/students")
def create_student(
    student: Student,
    db: Session = Depends(get_db)
):

    new_student = StudentDB(
        name=student.name,
        age=student.age
    )

    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    return {
        "message": "Student created",
        "student": new_student
    }


@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db)
):

    student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    db.delete(student)
    db.commit()

    return {
        "message": "Student deleted",
        "student_id": student_id
    }


@app.put("/students/{student_id}")
def update_student(
    student_id: int,
    student: Student,
    db: Session = Depends(get_db)
):

    existing_student = db.query(StudentDB).filter(
        StudentDB.id == student_id
    ).first()

    if existing_student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    existing_student.name = student.name
    existing_student.age = student.age

    db.commit()
    db.refresh(existing_student)

    return {
        "message": "Student updated",
        "student": existing_student
    }