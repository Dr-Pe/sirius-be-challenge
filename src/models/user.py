from sqlmodel import Field, SQLModel
from pydantic import BaseModel

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str
    password: str
    is_admin: bool = Field(default=False)

    def clean(self):
        self.password = '********'
        return self
    
class CreateUserDTO(BaseModel):
    username: str
    password: str
    is_admin: bool = False