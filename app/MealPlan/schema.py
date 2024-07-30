from pydantic import BaseModel
import datetime
from typing import Optional, List
from app.MealPlan.models import VisibleForEnum, MealTimeEnum


class MealBase(BaseModel):
    meal_time: MealTimeEnum
    food_id: int
    quantity: float

class CreateMeal(MealBase):
    pass

class ReadMeal(MealBase):
    id: int

class UpdateMeal(MealBase):
    id: int
    updated_by: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None

class DeleteMeal(MealBase):
    is_deleted: bool

class MealPlanBase(BaseModel):
    name: str
    profile_img: Optional[str]
    visible_for: VisibleForEnum
    description: Optional[str]

class CreateMealPlan(MealPlanBase):
    meals: List[CreateMeal]
    created_at: Optional[datetime.datetime] = datetime.datetime.now()

    class Config:
        from_attributes = True

class ReadMealPlan(MealPlanBase):
    id: int

class UpdateMealPlan(BaseModel):
    id: int
    name: Optional[str] = None
    profile_img: Optional[str] = None
    visible_for: Optional[VisibleForEnum] = None
    description: Optional[str] = None
    meals: Optional[List[CreateMeal]] = []
    updated_by: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None

class DeleteMealPlan(BaseModel):
    id: int

class ShowMealPlan(BaseModel):
    id: int
    name: Optional[str] = None
    profile_img: Optional[str] = None
    visible_for: Optional[VisibleForEnum] = None
    description: Optional[str] = None
    meals: Optional[List[CreateMeal]] = []
    created_by: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_by: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None
