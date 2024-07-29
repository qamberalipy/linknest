from typing import Annotated
from pydantic import EmailStr
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Session

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Request

from .service import get_all_workout, get_workout, save_workout, save_workout_day, update_workout

from .models import Workout
from ..dependencies import get_db, get_user
from .schema import WorkoutCreate, WorkoutDayCreate, WorkoutUpdate
from ..Client import schema as _client_schema


router = APIRouter(tags=["Workout router"])

async def workout_exists(workout_id: Annotated[int,Body()], db: Annotated[Session, Depends(get_db)]):
    return await get_workout(db,workout_id)

@router.post("/")
async def save(
        workout: WorkoutCreate,
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[_client_schema.ClientRead, Depends(get_user)]):
    try:
        return await save_workout(db, workout, user_id=user.id)
    except DataError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data error occurred, check your input") 
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unknown exception occured") 

@router.put("/{workout_id}")
async def update(workout_id: int,
        workout: WorkoutUpdate,
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[_client_schema.ClientRead, Depends(get_user)]):
    try:
        return await update_workout(db, workout_id, workout, user_id=user.id)
    except DataError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data error occurred, check your input") 
    except HTTPException as e:
        db.rollback()
        raise e 


@router.get("/")
async def get_all(db: Annotated[Session, Depends(get_db)]):
    return await get_all_workout(db)

@router.get("/{workout_id}")
async def get_one(workout_id: Annotated[int,Path(description="Id of the workout")], db: Annotated[Session, Depends(get_db)]):
    return await get_workout(db, workout_id)

@router.post("/day")
async def save_day(
        workout_day: WorkoutDayCreate,
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[_client_schema.ClientRead, Depends(get_user)],
        workout: Annotated[Workout, Depends(workout_exists)]):
    try:
        return workout
        # return await save_workout_day(db, workout_day, user_id=user.id)
    except DataError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data error occurred, check your input") 
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Unknown exception occured") 

@router.put("day/{day_id}")
async def update_day(workout_id: int,
        workout: WorkoutUpdate,
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[_client_schema.ClientRead, Depends(get_user)]):
    try:
        return await update_workout(db, workout_id, workout, user_id=user.id)
    except DataError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Data error occurred, check your input") 
    except HTTPException as e:
        db.rollback()
        raise e 
