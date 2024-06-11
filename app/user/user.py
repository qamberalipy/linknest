from fastapi import FastAPI, APIRouter, Depends, HTTPException
import schema as _schemas
import sqlalchemy.orm as _orm
import models as _models
import service as _services
import logging
import core.db as _database
import pika

router = APIRouter()

def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=_schemas.UserSchema)
async def register_user(user: _schemas.UserCreate, db: _orm.Session = Depends(get_db)):
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await _services.create_user(user, db)

@router.post("/login")
async def login(user: _schemas.UserLogin, db: _orm.Session = Depends(get_db)):
    authenticated_user = await _services.authenticate_user(user.email, user.password, db)
    if authenticated_user == 'is_verified_false':
        raise HTTPException(status_code=403, detail="Account is not verified")
    if not authenticated_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    return await _services.create_token(authenticated_user)

# Main application setup
app = FastAPI()
logging.basicConfig(level=logging.INFO)

app.include_router(router, prefix="/api/users", tags=["users"])

_models.Base.metadata.create_all(_models.engine)
