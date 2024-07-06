import pydantic
import datetime
from typing import Optional

class MembershipPlanBase(pydantic.BaseModel):
    name: str
    price: str
    org_id: int

class MembershipPlanCreate(MembershipPlanBase):
    pass

class MembershipPlanRead(MembershipPlanBase):
    id: int
    is_deleted: bool

    class Config:
        from_attributes = True
        
class CreditBase(pydantic.BaseModel):
    name: Optional[str] = None
    org_id: Optional[int] = None
    min_limit: Optional[int] = None
    status: Optional[bool] = True

class CreditDelete(pydantic.BaseModel):
    id: int  # Correctly annotated with the type int

    class Config:
        from_attributes = True
    
class CreditCreate(CreditBase):
    created_by: Optional[int] = None

class CreditUpdate(CreditBase):
    id:int
    updated_by: Optional[int] = None

class CreditRead(CreditBase):
    id: int
    is_deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
