from pydantic import BaseModel
import datetime
from typing import Optional, List
from app.MealPlan.models import VisibleForEnum, MealTimeEnum


class MealBase(BaseModel):
    meal_time: Optional[MealTimeEnum] = None
    food_id: Optional[int] = None
    quantity: Optional[float] = None

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
    org_id : int
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
    org_id : Optional[int] = None
    name: Optional[str] = None
    profile_img: Optional[str] = None
    visible_for: Optional[VisibleForEnum] = None
    description: Optional[str] = None
    meals: Optional[List[CreateMeal]] = []
    updated_by: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None

class DeleteMealPlan(BaseModel):
    id: int

class MealPlanFilterParams(BaseModel):
    org_id: int
    search_key: Optional[str] = None
    sort_by: Optional[str] = None
    status: Optional[str] = None
    limit:Optional[int] = None
    offset:Optional[int] = None

class ShowMealPlan(BaseModel):
    id: int
    org_id : int
    name: Optional[str] = None
    profile_img: Optional[str] = None
    visible_for: Optional[VisibleForEnum] = None
    description: Optional[str] = None
    meals: Optional[List[CreateMeal]] = []
    created_by: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_by: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None
