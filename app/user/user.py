from typing import Dict, List
from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError, DataError
import app.user.schema as _schemas
import sqlalchemy.orm as _orm
import app.user.models as _models
import app.user.service as _services
# from main import logger
import app.core.db.session as _database
import logging, os
import datetime
from datetime import datetime as _dt
import fastapi.security as _security

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET")
oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/login")

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


@router.post("/login")
async def login(
        user: _security.OAuth2PasswordRequestForm = Depends(_schemas.GenerateUserToken),
        db: _orm.Session = Depends(get_db)
    ):
    
    if user.email in lockout_expiry and datetime.datetime.now() < lockout_expiry[user.email]:
        raise HTTPException(status_code=403, detail="Account locked. Try again later.")

    authenticated_user = await _services.authenticate_user(user.email, user.password, db)
    if not authenticated_user:
        login_attempts[user.email] = login_attempts.get(user.email, 0) + 1

        if login_attempts[user.email] >= MAX_ATTEMPTS:
            # Lock the account if maximum attempts are reached
            lockout_expiry[user.email] = datetime.datetime.now() + LOCKOUT_TIME
            raise HTTPException(status_code=403, detail="Account locked. Try again later.")

        raise HTTPException(status_code=401, detail="Invalid email or password")

    login_attempts[user.email] = 0
    token = await _services.create_token(authenticated_user)
    user_data = await _services.get_alluser_data(email=user.email, db=db)
    return {
        "user": user_data,
        "token": token
    }


@router.post("/test_token")
async def test_token(
        token: str,
        db: _orm.Session = Depends(get_db)
    ):
    print("Token 1: ", token)
    payload = _services.verify_jwt(token)
    return payload

@router.get("/get_all_countries/", response_model=List[_schemas.CountryRead])
async def read_countries(db: _orm.Session = Depends(get_db)):
    countries = _services.get_all_countries(db=db)
    if not countries:
        raise HTTPException(status_code=404, detail="No countries found")
    return countries

@router.get("/get_all_sources/", response_model=List[_schemas.SourceRead])
async def read_sources(db: _orm.Session = Depends(get_db)):
    sources = _services.get_all_sources(db=db)
    if not sources:
        raise HTTPException(status_code=404, detail="No sources found")
    return sources

@router.get("/get_staff",response_model=List[_schemas.getStaff])
async def get_staff(user: _schemas.getStaff, db: _orm.Session):
    filtered_users=db.query(_models.User).filter(_models.User.org_id == user.org_id).all()
    response_users = [map_lead_to_response(lead) for lead in filtered_users]
    return response_users

def map_lead_to_response(user) -> _schemas.getStaff:
    return _schemas.getStaff(
        first_name=user.username,
        id=user.id,
        org_id=user.org_id
        )
    