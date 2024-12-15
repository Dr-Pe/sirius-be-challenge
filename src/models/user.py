from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel
from datetime import date


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str
    password: str
    is_admin: bool = Field(default=False)
    quota: int = Field(default=0)
    daily_usage: "DailyUsage" = Relationship(back_populates="user")


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


class GetUserStatsDTO(BaseModel):
    username: str
    daily_usage: Optional["DailyUsageDTO"]

    class Config:
        from_attributes = True

class DailyUsage(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship(back_populates="daily_usage") # type: ignore
    date: date
    usage: int = Field(default=0)


class DailyUsageDTO(BaseModel):
    date: date
    usage: int

    class Config:
        from_attributes = True
