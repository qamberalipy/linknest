from fastapi import FastAPI, APIRouter, Depends, HTTPException
import app.user.schema as _schemas
import sqlalchemy.orm as _orm
import app.user.models as _models
import app.user.service as _services
# from main import logger
import app.core.db.session as _database
import pika
import logging

router = APIRouter()

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=_schemas.UserCreate)
async def register_user(user: _schemas.UserCreate, db: _orm.Session = Depends(get_db)):
    print("Here 1", user.email, user.password, user.name)
    db_user = await _services.get_user_by_email(user.email, db)
    print(f"User: {db_user}")
    print("Here 2")
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await _services.create_user(user, db)

@router.post("/login")
async def login(
        user: _schemas.GenerateUserToken,
        db: _orm.Session = Depends(get_db)
    ):
    logger.debug("Here 1", user.email, user.password)
    authenticated_user = await _services.authenticate_user(user.email, user.password, db)
    # if authenticated_user == 'is_verified_false':
    #     raise HTTPException(status_code=403, detail="Account is not verified")
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return await _services.create_token(authenticated_user)

