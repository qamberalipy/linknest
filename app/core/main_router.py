import datetime
from typing import Dict, List
from urllib import request
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DataError, IntegrityError
import app.Shared.helpers as _helpers
import sqlalchemy.orm as _orm

from app.Shared.schema import UserBase
from ..Shared.dependencies import get_db
import app.user.schema as _schemas
import app.user.models as _models
import app.user.service as _services
import app.core.db.session as _database
import json
import logging
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)

router = APIRouter()
login_attempts: Dict[str, int] = {}
lockout_expiry: Dict[str, datetime.datetime] = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = datetime.timedelta(minutes=30)


@router.get("/healthcheck", status_code=200)
def healthcheck():
    return JSONResponse(content=jsonable_encoder({"status": "Healthy yayy!"}))

@router.post("/refresh_token", tags=["Auth"])
async def refresh_token(token_body:_schemas.verify_token):
 
    print("This is my refresh token:", token_body.token)
    return _helpers.refresh_jwt(token_body.token)

@router.post("/register/admin")
async def register_user(user: _schemas.UserCreate, db: _orm.Session = Depends(get_db)):
    print("Here 1", user.email, user.password, user.first_name)
    db_user = await _services.get_user_by_email(user.email, db)
    print(f"User: {db_user}")
    print("Here 2")
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    organization_details = _schemas.OrganizationCreateTest(name=user.org_name)
    organization = await _services.create_organizationtest(organization_details, db)

    user_data = user.dict()
    user_data['org_id'] = organization.id
    user_data.pop('org_name')

    user_register = _schemas.UserRegister(**user_data, created_at=datetime.datetime.utcnow())
    new_user = await _services.create_user(user_register, db)
    
    return new_user

@router.post("/login")
async def login(user: _schemas.GenerateUserToken,db: _orm.Session = Depends(get_db)):
    if not _helpers.validate_email(user.email):
        raise HTTPException(status_code=400, detail="Incorrect email format")
    
    print("user: ",user,"lockout_expiry: ",lockout_expiry,"login_attempts: ",login_attempts)
    if user.email in lockout_expiry and datetime.datetime.now() < lockout_expiry[user.email]:
        raise HTTPException(status_code=403, detail="Your account has been locked due to multiple unsuccessful sign-in attempts. Please reset your password.")

    authenticated_user = await _services.authenticate_user(user.email, user.password, db)
    if not authenticated_user:
        login_attempts[user.email] = login_attempts.get(user.email, 0) + 1

        if login_attempts[user.email] >= MAX_ATTEMPTS:
            # Lock the account if maximum attempts are reached
            lockout_expiry[user.email] = datetime.datetime.now() + LOCKOUT_TIME
            login_attempts[user.email] = 0
            raise HTTPException(status_code=403, detail="Your account has been locked due to multiple unsuccessful sign-in attempts. Please reset your password.")

        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    login_attempts[user.email] = 0
    user_obj = UserBase.model_validate(authenticated_user)
    user_obj = user_obj.model_dump()
    token = _helpers.create_token(user_obj, "Staff")
    user_data = await _services.get_alluser_data(email=user.email, db=db)
    return {
        "user": user_data,
        "token": token
    }

@router.post("/forget_password")
async def forget_password(staff : _schemas.ForgetPasswordRequest ,db: _orm.Session = Depends(get_db)):
    
    org_name,org_id, org_email, user = await _services.get_user_gym(staff.email, db)
    
    user_data = {
        "id": user.id,
        "email": user.email,
        "org_id" : org_id
    }
    # Convert to JSON
    user_json = json.dumps(user_data)

    # Generate a password reset token
    token = _helpers.generate_password_reset_token(user_json)
    
    set_token = _services.set_reset_token(user.id, user.email, token, db)
    html_body = _services.generate_password_reset_html(user.first_name, org_email, org_name, token)

    # Send the password reset email
    email_sent = _services.send_password_reset_email(user.email, "Password Reset Request", html_body)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send email")

    return JSONResponse(content={"message": f"An e-mail with a password reset link has been sent to {user.email}. If you did not receive the email, please check your spam/junk mail folder."}, status_code=200)

@router.get("/reset_password/{token}")
async def verify_token(token: str, db: _orm.Session = Depends(get_db)):

    payload = _helpers.verify_password_reset_token(token)
    payload = json.loads(payload)

    if _services.get_reset_token(payload['id'], db) == token:
        return JSONResponse(content=payload, status_code=200)
    else:
        raise HTTPException(status_code=401, detail="The reset link is invalid or has expired. Please request a new password reset link.")
     
@router.post("/reset_password")
async def reset_password(user : _schemas.ResetPasswordRequest, db: _orm.Session = Depends(get_db)):
    
    token = _services.get_reset_token(user.id, db)
    if token == user.token:
        data = _helpers.verify_password_reset_token(user.token)
        
        if data is None or any(key not in data for key in ["id","org_id"]):
            raise HTTPException(status_code=400, detail="The reset link is invalid or has expired. Please request a new password reset link.")
        
        if user.new_password != user.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        password = _services.hash_password(user.new_password)
        # Update the user's password
        user = await _services.update_user_password(user.id, user.org_id ,password, db)
        _services.delete_reset_token(user.id, db)
        if not user:
            raise HTTPException(status_code=404, detail="It appears there is no account with this id. Please verify the details provided.")
        return JSONResponse(content={"message": "Your password has been reset successfully. You can now log in with your new password."}, status_code=200)
    else:
        raise HTTPException(status_code=400, detail="The reset link is invalid or has expired. Please request a new password reset link.")

@router.post("/test_token")
async def test_token(
        token: str,
        db: _orm.Session = Depends(get_db)
    ):
    print("Token 1: ", token)
    payload = _helpers.verify_jwt(token, "User")
    return payload

@router.get("/countries", response_model=List[_schemas.CountryRead])
async def read_countries(db: _orm.Session = Depends(get_db)):
    countries = _services.get_all_countries(db=db)
    if not countries:
        raise HTTPException(status_code=404, detail="No countries found")
    return countries


@router.get("/sources", response_model=List[_schemas.SourceRead])
async def read_sources(db: _orm.Session = Depends(get_db)):
    sources = _services.get_all_sources(db=db)
    if not sources:
        raise HTTPException(status_code=404, detail="No sources found")
    return sources
