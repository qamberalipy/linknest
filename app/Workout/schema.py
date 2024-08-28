from datetime import datetime
from typing import List, Literal
from typing_extensions import Optional
from pydantic import BaseModel, Field

from ..Exercise.schema import ExerciseBase
from .models import Intensity, ExerciseType, VisibleFor, WorkoutGoal, WorkoutLevel


# class MyBaseModel(BaseModel):
    # class Config:
        # extra = 'forbid'
        # from_attributes = True

class WorkoutDayBase(BaseModel):
    workout_id: int
    day_name: str
    week: int = Field(ge=1)
    day: int = Field(ge=1, le=7)

class WorkoutDayExerciseBase(BaseModel):
    workout_day_id: int
    exercise_id: int
    exercise_type: ExerciseType
    sets: int = Field(ge=1)
    seconds_per_set: Optional[List[int]] = None
    repetitions_per_set: Optional[List[int]] = None
    rest_between_set: Optional[List[int]] = None
    intensity_type: Intensity
    intensity_value: Optional[float] = None
    notes: Optional[str] = None
    distance: Optional[float] = None
    speed: Optional[float] = None
    met_value: Optional[float] = None

class WorkoutDayExerciseRead(WorkoutDayExerciseBase):
    pass
            

class WorkoutDayRead(WorkoutDayBase):
    id: int
    exercises: Optional[List[WorkoutDayExerciseRead]] = []


class WorkoutBase(BaseModel):
    workout_name: str
    org_id:int
    description: Optional[str] = None
    visible_for: VisibleFor
    goals: WorkoutGoal
    level: WorkoutLevel
    notes: Optional[str] = None
    weeks: int = Field(ge=1)
    img_url: str

class WorkoutCreate(WorkoutBase):
    pass

class WorkoutRead(WorkoutBase):
    id: int
    days: Optional[List[WorkoutDayRead]] = []
    created_at: datetime
    updated_at: Optional[datetime]
    create_user_type: str
    update_user_type: Optional[str]
    created_by: int
    updated_by: Optional[int]
    is_deleted: bool


class WorkoutUpdate(BaseModel):
    workout_name: Optional[str] = None
    description: Optional[str] = None
    goals: Optional[WorkoutGoal] = None
    level: Optional[WorkoutLevel] = None
    visible_for: Optional[VisibleFor] = None
    notes: Optional[str] = None
    weeks: Optional[int] = None

class WorkoutFilter(BaseModel):
    goals: Optional[List[WorkoutGoal]] = []
    level: Optional[WorkoutLevel] = None
    search: Optional[str] = None
    include_days: Optional[bool] = False
    include_days_and_exercises: Optional[bool] = False
    created_by_user: Optional[bool] = None
    sort_key: Optional[str] = None
    sort_order: Optional[Literal["asc", "desc"]] = "asc"
    
class WorkoutMobileFilter(BaseModel):
    goals: Optional[WorkoutGoal] = None
    level: Optional[WorkoutLevel] = None
    search: Optional[str] = None
    created_by_user: Optional[bool] = None
    sort_column: Optional[str] = None
    sort_dir: Optional[Literal["asc", "desc"]] = "asc"
    results_per_goal: Optional[int] = 3

class WorkoutDayCreate(WorkoutDayBase):
    pass

class WorkoutDayOptionalBase(BaseModel):
    day_name: Optional[str] = None
    week: Optional[int] = Field(default=None, ge=1)
    day: Optional[int] = Field(default=None, ge=1, le=7)

class WorkoutDayUpdate(WorkoutDayOptionalBase):
    pass

# columns = list(WorkoutDayRead.model_fields.keys())
class WorkoutDayFilter(WorkoutDayOptionalBase):
    workout_id: Optional[int] = None
    include_exercises: Optional[bool] = None
    # sort_column: Optional[Literal[*tuple(columns)]] = None
    sort_dir: Optional[Literal["asc", "desc"]] = "asc"


class WorkoutDayExerciseCreate(WorkoutDayExerciseBase):
    pass

class WorkoutDayExerciseOptionalBase(BaseModel):
    exercise_id: Optional[int] = None
    exercise_type: Optional[ExerciseType] = None
    sets: Optional[int] = Field(default=None, ge=0)
    seconds_per_set: Optional[List[int]] = None
    repetitions_per_set: Optional[List[int]] = None
    rest_between_set: Optional[List[int]] = None
    intensity_type: Optional[Intensity] = None
    percentage_of_1rm: Optional[float] = None
    notes: Optional[str] = None

class WorkoutDayExerciseUpdate(WorkoutDayExerciseOptionalBase):
    pass

class WorkoutDayExerciseFilter(WorkoutDayExerciseOptionalBase):
    workout_day_id: Optional[int] = None

