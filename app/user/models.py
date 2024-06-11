import datetime as _dt
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from app.core.auth import Base , engine
import app.core.auth as _database
import bcrypt as _bcrypt

Base.metadata.create_all(engine)

class User(_database.Base):
    __tablename__ = "users"
    id = _sql.Column(_sql.Integer, primary_key=True, index=True)
    username = _sql.Column(_sql.String)
    password = _sql.Column(_sql.String)
    email = _sql.Column(_sql.String, unique=True, index=True)
    otp = _sql.Column(_sql.Integer)
    date_created = _sql.Column(_sql.DateTime, default=_dt.datetime.utcnow)
    is_verified = _sql.Column(_sql.Boolean , default=False)
    role_id = _sql.Column(_sql.Integer ,index=True)
    organization_id = _sql.Column(_sql.Integer, index=True)
    
    def verify_password(self, password: bytes):
        print("In Verify Password", password, self.hashed_password.encode('utf-8'))
        return _bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))