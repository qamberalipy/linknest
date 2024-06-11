from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(example="Joe")
    password: str = Field(example="123456")
    email: str = Field(example="joe@gmail.com")


class UserSchema(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str = Field(example="joe@gmail.com")
    password: str = Field(example="123456")
