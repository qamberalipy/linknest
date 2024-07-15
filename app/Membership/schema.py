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

class SaleTaxBase(pydantic.BaseModel):
    name: Optional[str] = None
    percentage: Optional[float] = None
    org_id: Optional[int] = None

class SaleTaxCreate(SaleTaxBase):
    created_by: Optional[int] = None

class SaleTaxUpdate(SaleTaxBase):
    id: Optional[int] = None
    updated_by: Optional[int] = None

class SaleTaxRead(SaleTaxBase):
    id: Optional[int] = None
    is_deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True

class SaleTaxDelete(pydantic.BaseModel):
    id: int 

    class Config:
        from_attributes = True


class GroupCreate(pydantic.BaseModel):
    org_id: int
    name: str
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

class GroupRead(pydantic.BaseModel):
    id: int
    name: str
    org_id: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class GroupUpdate(pydantic.BaseModel):
    id: int
    name: Optional[str] = None