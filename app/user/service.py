from datetime import date,datetime
from typing import List, Dict, Any
from typing import Annotated, List
import jwt
from sqlalchemy import asc, desc, func, or_, text
import sqlalchemy.orm as _orm
from sqlalchemy.sql import and_  
import email_validator as _email_check
import fastapi as _fastapi
import fastapi.security as _security
import app.core.db.session as _database
import app.user.schema as _schemas
import app.user.models as _models
import random
import json
import pika
import time
import os
import bcrypt as _bcrypt
from . import models, schema
import logging
from collections import defaultdict
from app.user.models import StaffStatus
import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter, Depends, HTTPException, Header
from email.mime.multipart import MIMEMultipart
import sendgrid
# import resend
from sendgrid.helpers.mail import Mail, Email, To, Content

# Load environment variables

logger = logging.getLogger("uvicorn.error")
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRY = os.getenv("JWT_EXPIRY")
LOCAL_BASE_URL = os.getenv("LOCAL_BASE_URL")
BASE_URL = os.getenv("BASE_URL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_SERVER = os.getenv("SMTP_SERVER")
# RESEND_API_KEY = os.getenv('RESEND_API_KEY')


oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="api/login")

def create_database():
    # Create database tables
    return _database.Base.metadata.create_all(bind=_database.engine)

def get_db():
    # Dependency to get a database session
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_jwt(token: str):
    # Verify a JWT token
    credentials_exception = _fastapi.HTTPException(
        status_code=_fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Token Expired or Invalid",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = token.split("Bearer ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print("Time Difference", time.time() - payload["token_time"])
        if time.time() - payload["token_time"] > JWT_EXPIRY:
            print("Token Expired")
            raise credentials_exception

        return payload
    except:
        raise credentials_exception

def hash_password(password):
    # Hash a password
    return _bcrypt.hashpw(password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')

async def get_user_by_email(email: str, db: _orm.Session):
    # Retrieve a user by email from the database
    print("Email: ", email)
    return db.query(_models.User).filter(
        and_(
            _models.User.email == email,
            _models.User.is_deleted == False
        )
    ).first()

async def create_user(user: _schemas.UserRegister, db: _orm.Session):
    try:
        valid = _email_check.validate_email(user.email)
        email = valid.email
    except _email_check.EmailNotValidError:
        raise _fastapi.HTTPException(status_code=400, detail="Please enter a valid email")

    hashed_password = hash_password(user.password)
    user_obj = _models.User(
        email=email, 
        first_name=user.first_name, 
        password=hashed_password,
        org_id=user.org_id
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def create_token(user: _models.User):
    # Create a JWT token for authentication
    user_obj = _schemas.User.from_orm(user)
    user_dict = user_obj.dict()
    print(user_dict)
    del user_dict["date_created"]
    user_dict['token_time'] = time.time()
    print("JWT_SECRET", JWT_SECRET)
    print("User Dict: ", user_dict)
    token = jwt.encode(user_dict, JWT_SECRET, algorithm="HS256")
    return dict(access_token=token, token_type="bearer")

async def get_current_user(token: str, db: _orm.Session = _fastapi.Depends(get_db)):
    # Get the current authenticated user from the JWT token
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user = db.query(_models.User).get(payload["id"])
    except:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Email or Password")
    return _schemas.UserSchema.from_orm(user)

def generate_otp():
    # Generate a random OTP
    return str(random.randint(100000, 999999))

async def get_user_by_email(email: str, db: _orm.Session = _fastapi.Depends(get_db)):
    return db.query(_models.User).filter(
        and_(
            _models.User.email == email,
            _models.User.is_deleted == False
        )
    ).first()

async def get_filtered_user_by_email(email: str, db: _orm.Session = _fastapi.Depends(get_db)):
    user =  db.query(models.User).filter(models.User.email == email, _models.User.is_deleted == False).first()
    if user:
        return user
    else: 
        raise HTTPException(status_code=404, detail="It appears there is no account with this email. Please verify the address provided.")


async def get_alluser_data(email: str, db: _orm.Session = _fastapi.Depends(get_db)):
    # Retrieve a user by email from the database
    result = (
        db.query(_models.User, _models.Organization.name)
        .join(_models.Organization, _models.User.org_id == _models.Organization.id)
        .filter(_models.User.email == email)
        .first()
    )
    
    if result:
        user, org_name = result
        return {
            "id": user.id,
            "first_name": user.first_name,
            "email": user.email,
            "date_created": user.created_at,
            "org_id": user.org_id,
            "org_name": org_name,
            "is_deleted": user.is_deleted
        }
    return None

async def update_user_password(user_id: int , org_id : int ,new_password : str, db: _orm.Session = _fastapi.Depends(get_db)):
    user = db.query(_models.User).filter(_models.User.id == user_id, _models.User.org_id == org_id, _models.User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="It appears there is no account with this id. Please verify the details provided.")
    
    user.password = new_password
    db.commit()
    return user
    

async def create_staff(staff: _schemas.CreateStaff,user_id,db: _orm.Session = _fastapi.Depends(get_db)):
    staff_data = staff.dict()
    staff_data['created_by']=user_id
    staff_data['updated_by']=user_id
    staff_data['created_at']=datetime.now()
    staff_data['updated_at']=datetime.now()

    print(staff_data.pop("send_invitation"))
    db_staff = _models.User(**staff_data)
    db.add(db_staff)
    db.commit()
    db.refresh(db_staff)
    return {
            "status_code": "201",
            "id": db_staff.id,
            "message": "Staff created successfully"
        }
        
async def authenticate_user(email: str, password: str, db: _orm.Session):
    # Authenticate a user
    user = await get_user_by_email(email=email, db=db)

    if not user:
       raise HTTPException(status_code=400, detail="No account found associated with the provided email.")

    if not user.verify_password(password):
        return False
    return user

def generate_password_reset_html(name: str ,email :str ,gym_name: str, token: str) -> str:
    return f'''
    <html>
                    <head>
                        <title></title>
                        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <meta http-equiv="X-UA-Compatible" content="IE=edge" />
                        <style type="text/css">
                            /* FONTS */
                            @media screen {{
                                @font-face {{
                                    font-family: 'Lato';
                                    font-style: normal;
                                    font-weight: 400;
                                    src: local('Lato Regular'), local('Lato-Regular'),
                                    url(https://fonts.gstatic.com/s/lato/v11/qIIYRU-oROkIk8vfvxw6QvesZW2xOQ-xsNqO47m55DA.woff) format('woff');
                                }}
                                @font-face {{
                                    font-family: 'Lato';
                                    font-style: normal;
                                    font-weight: 700;
                                    src: local('Lato Bold'), local('Lato-Bold'),
                                    url(https://fonts.gstatic.com/s/lato/v11/qdgUG4U09HnJwhYI-uK18wLUuEpTyoUstqEm5AMlJo4.woff) format('woff');
                                }}
                                @font-face {{
                                    font-family: 'Lato';
                                    font-style: italic;
                                    font-weight: 400;
                                    src: local('Lato Italic'), local('Lato-Italic'),
                                    url(https://fonts.gstatic.com/s/lato/v11/RYyZNoeFgb0l7W3Vu1aSWOvvDin1pK8aKteLpeZ5c0A.woff) format('woff');
                                }}
                                @font-face {{
                                    font-family: 'Lato';
                                    font-style: italic;
                                    font-weight: 700;
                                    src: local('Lato Bold Italic'), local('Lato-BoldItalic'),
                                    url(https://fonts.gstatic.com/s/lato/v11/HkF_qI1x_noxlxhrhMQYELO3LdcAZYWl9Si6vvxL-qU.woff) format('woff');
                                }}
                            }}
                            /* CLIENT-SPECIFIC STYLES */
                            body, table, td, a {{
                                -webkit-text-size-adjust: 100%;
                                -ms-text-size-adjust: 100%;
                                color:#525167!important;
                            }}
                            table, td {{
                                mso-table-lspace: 0pt;
                                mso-table-rspace: 0pt;
                            }}
                            img {{
                                -ms-interpolation-mode: bicubic;
                            }}
                            /* RESET STYLES */
                            img {{
                                border: 0;
                                height: auto;
                                line-height: 100%;
                                outline: none;
                                text-decoration: none;
                            }}
                            table {{
                                border-collapse: collapse !important;
                            }}
                            body {{
                                height: 100% !important;
                                margin: 0 !important;
                                padding: 0 !important;
                                width: 100% !important;
                            }}
                            /* iOS BLUE LINKS */
                            a[x-apple-data-detectors] {{
                                color: inherit !important;
                                text-decoration: none !important;
                                font-size: inherit !important;
                                font-family: inherit !important;
                                font-weight: inherit !important;
                                line-height: inherit !important;
                            }}
                            /* ANDROID CENTER FIX */
                            div[style*="margin: 16px 0;"] {{
                                margin: 0 !important;
                            }}
                        </style>
                    </head>
                    <body style="background-color: #f4f4f4; margin: 0 !important; padding: 0 !important;">
                        <div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: 'Lato', Helvetica, Arial, sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">Hi!</div>
                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                            <tbody>
                                <tr>
                                    <td bgcolor="#77DD77" align="center">
                                        <table border="0" cellpadding="0" cellspacing="0" width="550">
                                            <tbody>
                                                <tr>
                                                    <td align="center" valign="top" style="padding: 40px 10px 40px 10px;">
                                                        <a href="https://pifs.lts.com.fj" target="_blank"></a>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td bgcolor="#77DD77" align="center" style="padding: 0px 10px 0px 10px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="550">
                                            <tbody>
                                                <tr>
                                                    <td bgcolor="#ffffff" align="center" valign="top" style="padding: 40px 20px 20px 20px; border-radius: 4px 4px 0px 0px; color: #111111; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 48px; font-weight: 500; letter-spacing: 2px; line-height: 48px;">
                                                        <h1 style="font-size: 28px; font-weight: 400; margin: 0;">Forgot Your Password?</h1>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td bgcolor="#f4f4f4" align="center" style="padding: 0px 10px 0px 10px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="550">
                                            <tbody>
                                                <tr>
                                                    <td bgcolor="#ffffff" align="left" style="padding: 20px 30px 20px 30px; color: #666666; font-family: 'Lato', Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 400; line-height: 25px;">
                                                        <p style="margin: 0;">Hey {name},<br><br>We received a request to reset the password for your account. To proceed with resetting your password, please click the link below:<br><br>If you did not request this password reset, you can safely ignore this email. Your password will not be changed unless you follow the link and complete the reset process.<br><br>For security reasons, this link will expire in 30 minutes. If you do not reset your password within this time, you will need to request a new password reset.<br><br>If you encounter any issues or need further assistance, please contact our support team at {email}.<br><br>Thank you,<br><br>{gym_name}</p>
                                                    </td>
                                                    
                                                </tr>
                                                <tr>
                                                    <td bgcolor="#ffffff" align="left">
                                                        <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                                            <tbody>
                                                                <tr>
                                                                    <td bgcolor="#ffffff" align="center" style="padding: 0px 30px 30px 30px;">
                                                                        <table border="0" cellspacing="0" cellpadding="0">
                                                                            <tbody>
                                                                                <tr>
                                                                                    <td align="center" style="border-radius: 3px;" bgcolor="#77DD77">
                                                                                        <a href="{LOCAL_BASE_URL if os.getenv("ENV") == "local" else BASE_URL}/reset_password/{token}" target="_blank" style="font-size: 20px; font-family: Helvetica, Arial, sans-serif; color: #ffffff; text-decoration: none; color: #ffffff; text-decoration: none; padding: 15px 25px; border-radius: 2px; border: 1px solid #77DD77; display: inline-block;">Reset Password</a>
                                                                                    </td>
                                                                                </tr>
                                                                            </tbody>
                                                                        </table>
                                                                    </td>
                                                                </tr>
                                                            </tbody>
                                                        </table>
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                                <tr>
                                    <td bgcolor="#f4f4f4" align="center" style="padding: 16px 10px 0px 10px;">
                                        <table border="0" cellpadding="0" cellspacing="0" width="550">
                                            <tbody>
                                                <tr>
                                                    <td bgcolor="#f4f4f4" align="left" style="padding: 0px 30px 16px 30px;color: #666666;font-family: 'Lato', Helvetica, Arial, sans-serif;font-size: 14px;font-weight: 400;line-height: 18px;">
                                                        <p style="margin: 0;">You received this email because your account password is being resetted</p>
                                                    </td>
                                                </tr>
                                               
                                            </tbody>
                                        </table>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </body>
                    </html>
    '''

def send_password_reset_email(recipient_email: str, subject: str, html_body: str) -> bool:
    sender_email = "letsmove.project2024@gmail.com"
    sender_password = SENDER_PASSWORD
    smtp_server = SMTP_SERVER
    smtp_port = SMTP_PORT

    # Create a MIME multipart message
    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Attach the HTML body
    part = MIMEText(html_body, "html")
    msg.attach(part)

    try:
        # Set up the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False

def set_reset_token(id: int, email: str, token: str, db: _orm.Session):
    db.query(_models.User).filter(_models.User.id == id).filter(_models.User.email == email).update({"reset_token": token})
    db.commit()
    return token

def get_reset_token(id: int, db: _orm.Session):
    user = db.query(_models.User).filter(_models.User.id == id, _models.User.reset_token.isnot(None)).first()
    if user is None:
        return None

    return user.reset_token

def delete_reset_token(id: int, db: _orm.Session):
    db.query(_models.User).filter(_models.User.id == id).update({"reset_token": None})
    db.commit()

def get_all_countries( db: _orm.Session):
    return db.query(_models.Country).filter(_models.Country.is_deleted == False).all()

def get_all_sources( db: _orm.Session):
    return db.query(_models.Source).all()

async def get_one_staff(staff_id: int, db: _orm.Session):
    staff_detail = db.query(
        *models.User.__table__.columns,
        _models.Role.name.label("role_name")
        ).join(
            _models.Role, _models.User.role_id == _models.Role.id
        ).filter(
            _models.User.is_deleted == False,
            _models.User.id == staff_id
    ).first()
    print(staff_detail)
    if staff_detail:
        return staff_detail
    else :
        return None
    

async def update_staff(staff_id: int,user_id,staff_update: _schemas.UpdateStaff, db: _orm.Session):
    
    staff = db.query(_models.User).filter(and_(_models.User.id == staff_id,_models.User.is_deleted == False)).first()
    
    if staff is None:
        raise _fastapi.HTTPException(status_code=404, detail="Staff not found")
    
    update_data = staff_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(staff, key, value)
    
    staff.updated_at = datetime.now()
    staff.updated_by=user_id
    db.commit()
    db.refresh(staff)
    return staff


async def delete_staff(staff_id: int,user_id,db: _orm.Session):
    staff = db.query(_models.User).filter(and_(_models.User.id == staff_id,_models.User.is_deleted == False)).first()
    if staff is None:
        raise _fastapi.HTTPException(status_code=404, detail="Staff not found")
    
    staff.is_deleted = True
    staff.updated_by=user_id
    staff.updated_at=datetime.now()
    db.commit()
    return {"status":"201","detail":"Staff deleted successfully"}
