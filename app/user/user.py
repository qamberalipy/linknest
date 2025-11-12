from typing import Annotated, Dict, List, Optional
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Header, Request, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, DataError
import app.user.schema as _schemas
import sqlalchemy.orm as _orm
import app.user.models as _models
import app.user.service as _services
import app.Shared.schema as _h_schema
import app.core.db.session as _database
import pika
import logging
import datetime
from datetime import datetime as _dt
import fastapi.security as _security
import app.Shared.helpers as _helpers

router = APIRouter()

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

login_attempts: Dict[str, int] = {}
lockout_expiry: Dict[str, datetime.datetime] = {}
MAX_ATTEMPTS = 3
LOCKOUT_TIME = datetime.timedelta(minutes=30)

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @router.post("/organizations", response_model=_schemas.OrganizationRead, tags=["Organizations API"])
# async def create_organization(org: _schemas.OrganizationCreate,request:Request,db: _orm.Session = Depends(get_db)):
#     try:
        
#         if not _helpers.validate_email(org.email):
#             raise HTTPException(status_code=400, detail="Invalid email format")
        
#         user_id=request.state.user.get('id')
#         new_org = await _services.create_organization(org,user_id,db)
#         return new_org
    
#     except IntegrityError as e:
#         db.rollback()
#         logger.error(f"IntegrityError: {e}")
#         raise HTTPException(status_code=400, detail="Duplicate entry or integrity constraint violation")

#     except DataError as e:
#         db.rollback()
#         logger.error(f"DataError: {e}")
#         raise HTTPException(status_code=400, detail="Data error occurred, check your input")
 

# @router.get("/organizations/{id}", response_model=_schemas.OrganizationRead, tags=["Organizations API"])
# async def get_organization(id: int, db: _orm.Session = Depends(get_db)):
#     org = await _services.get_organization(id, db)
#     if org is None:
#         raise HTTPException(status_code=404, detail="Organization not found")
#     return org

# @router.put("/organizations", response_model=_schemas.OrganizationRead, tags=["Organizations API"])
# async def update_organization(org: _schemas.OrganizationUpdate,request:Request,db: _orm.Session = Depends(get_db)):
    
#     if not _helpers.validate_email(org.email):
#         raise HTTPException(status_code=400, detail="Invalid email format")
#     user_id=request.state.user.get('id')
#     updated_org = await _services.update_organization(org.id,user_id,org, db)
#     if updated_org is None:
#         raise HTTPException(status_code=404, detail="Organization not found")
#     return updated_org

# @router.delete("/organizations/{id}", response_model=_schemas.OrganizationRead, tags=["Organizations API"])
# async def delete_organization(id: int,request:Request,db: _orm.Session = Depends(get_db)):
#     user_id=request.state.user.get('id')
#     deleted_org = await _services.delete_organization(id,user_id,db)
#     if deleted_org is None:
#         raise HTTPException(status_code=404, detail="Organization not found")
#     return deleted_org

# @router.get("/opening_hours/{id}", response_model=_schemas.OpeningHoursRead, tags=["Organizations API"])
# async def read_opening_hours(id: int, db: _orm.Session = Depends(get_db)):
#     organization = await _services.get_opening_hours(id, db)
#     if organization:
#         return organization
#     raise HTTPException(status_code=404, detail="Organization not found")

# @router.put("/opening-hours", response_model=_schemas.OpeningHoursRead, tags=["Organizations API"])
# async def update_opening_hours(opening_hours_data: _schemas.OpeningHoursUpdate,request:Request,db: _orm.Session = Depends(get_db)):
    
#     user_id=request.state.user.get('id')
#     updated_organization = await _services.update_opening_hours(opening_hours_data.id,user_id,opening_hours_data, db)
#     if updated_organization:
#         return updated_organization
#     raise HTTPException(status_code=404, detail="Organization not found")

# @router.get("/staff/list",response_model=List[_schemas.getStaff],tags=["Staff APIs"])
# async def get_staff_list(org_id:int, db: _orm.Session= Depends(get_db)):
    
#     filtered_users =  db.query(_models.User.id,func.concat(_models.User.first_name,' ',_models.User.last_name).label('name')).filter(_models.User.org_id == org_id, _models.User.is_deleted == False).all()
#     return filtered_users


# @router.get("/privileges",response_model=List[_schemas.getPrivileges],tags=["Staff APIs"])
# async def get_privileges(org_id:int, db: _orm.Session= Depends(get_db)):
    
    
#     organization_roles=  db.query(_models.Role).filter(_models.Role.org_id == org_id and _models.Role.is_deleted==False).all()
#     return organization_roles


# @router.post("/staff", tags=["Staff APIs"])
# async def register_staff(staff: _schemas.CreateStaff,request:Request,db: _orm.Session = Depends(get_db)):
#     try:
#         user_id=request.state.user.get('id')
#         db_staff = await _services.get_user_by_email(staff.email,db)
#         if db_staff:
#             raise HTTPException(status_code=400, detail="Email already registered")

#         new_staff = await _services.create_staff(staff,user_id,db)
#         return new_staff

#     except IntegrityError as e:
#         db.rollback()
#         logger.error(f"IntegrityError: {e}")
#         raise HTTPException(status_code=400, detail="Duplicate entry or integrity constraint violation")

#     except DataError as e:
#         db.rollback()
#         logger.error(f"DataError: {e}")
#         raise HTTPException(status_code=400, detail="Data error occurred, check your input")

