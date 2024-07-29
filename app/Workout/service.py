from typing import Literal
from fastapi import Depends, HTTPException
from sqlalchemy import Column
from sqlalchemy.orm import Session
from starlette.types import HTTPExceptionHandler
from app.Workout.models import Workout, WorkoutDay
from app.Workout.schema import WorkoutCreate, WorkoutDayCreate, WorkoutUpdate


async def update_workout(db: Session, workout_id: int, workout: WorkoutUpdate, user_id: int):
    model = db.query(Workout).filter(Workout.id == workout_id, Workout.is_deleted == False).first()
    if not model:
        raise HTTPException(status_code=404, detail="Workout doesn't exist")
    data = workout.model_dump(exclude_unset=True)
    data["updated_by"] = user_id
    for key, value in data.items():
        setattr(model, key, value)
    db.commit()
    db.refresh(model)
    return model

async def save_workout(db: Session, workout: WorkoutCreate, user_id: int):
    data = workout.model_dump()
    data["created_by"] = user_id
    db_workout = Workout(**data)
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout

async def get_workout(db: Session, workout_id: int):
    workout = db.query(Workout).filter(Workout.id == workout_id, Workout.is_deleted == False).first()  
    if not workout:
            raise HTTPException(status_code=404, detail="Workout not found")
    return workout

async def get_all_workout(db: Session):
    return db.query(Workout).filter(Workout.is_deleted == False).all()  

async def save_workout_day(db: Session, workout: WorkoutDayCreate, user_id: int):
    data = workout.model_dump()
    data["created_by"] = user_id
    db_workout_day = WorkoutDay(**data)
    db.add(db_workout_day)
    db.commit()
    db.refresh(db_workout_day)
    return db_workout_day
