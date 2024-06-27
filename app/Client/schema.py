import pydantic
import datetime
from datetime import date
from typing import Optional

class ClientBase(pydantic.BaseModel):
    profile_img: str
    own_member_id: str
    first_name: str
    last_name: str
    gender: str
    dob: date
    email_address: str
    phone: Optional[str] = None
    mobile_number: Optional[str] = None
    notes: Optional[str] = None
    source_id: Optional[int] = None
    language: Optional[str] = None
    is_business: bool = False
    country_id: Optional[int] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    client_since: Optional[date] = None
    created_at: Optional[date] = None
    created_by: Optional[int] = None
    
class ClientCreate(ClientBase):
    org_id:int
    coach_id:int
    membership_id:int
    class Config:
        from_attributes=True

class RegisterClient(ClientBase):
    pass

class ClientRead(ClientBase):
    id: int
    
    class Config:
        from_attributes=True

class Client_Organization(pydantic.BaseModel):
    client_id: int
    org_id: int

class CreateClient_Organization(Client_Organization):
    pass
    
class Client_membership(pydantic.BaseModel):
    client_id: int
    membership_plan_id: int

class CreateClient_membership(Client_membership):
    pass

class Client_coach(pydantic.BaseModel):
    client_id: int
    coach_id: int

class CreateClient_coach(Client_coach):
    pass
    
class ClientLogin(pydantic.BaseModel):
    email_address: str
    wallet_address: str
    
class BusinessBase(pydantic.BaseModel):
    name: str
    address: str
    email: str
    org_id: int


class BusinessRead(BusinessBase):
    id: int
    date_created: date

    class Config:
        from_attributes = True  
