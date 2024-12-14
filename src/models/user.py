from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str
    password: str
    is_admin: bool = Field(default=False)
    quota: int = Field(default=0)


class CreateUserDTO(BaseModel):
    username: str
    password: str
    is_admin: bool = False


class GetUserDTO(BaseModel):
    username: str
    is_admin: bool
    quota: int

    class Config:
        from_attributes = True
