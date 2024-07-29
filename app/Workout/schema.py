from typing_extensions import Optional
from pydantic import BaseModel

from app.Workout.models import WorkoutGoal, WorkoutLevel

class WorkoutCreate(BaseModel):
    workout_name: str
    description: Optional[str] = None
    goals: WorkoutGoal
    level: WorkoutLevel
    notes: Optional[str] = None
    weeks: int

class WorkoutUpdate(BaseModel):
    workout_name: Optional[str] = None
    description: Optional[str] = None
    goals: Optional[WorkoutGoal] = None
    level: Optional[WorkoutLevel] = None
    notes: Optional[str] = None
    weeks: Optional[int] = None

class WorkoutDayCreate(BaseModel):
    workout_id: int
    day_name: str
    week: int
    day: int
