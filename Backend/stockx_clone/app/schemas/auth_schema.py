from pydantic import BaseModel, EmailStr, Field 
from typing import Optional 

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str 
    name: str 
    
class Token(BaseModel):
    access_token: str 
    token_type: str 
    
class TokenData(BaseModel):
        email: Optional[str] = None 
        user_id: Optional[str] = None 
        
class PasswordReset(BaseModel):
        email: EmailStr
        
class PasswordUpdate(BaseModel): 
        token: str 
        new_password: str = Field(..., min_length=8)
        