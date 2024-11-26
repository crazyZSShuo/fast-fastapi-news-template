from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

# 用户基础模型
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True

# 创建用户请求模型
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str

# 更新用户请求模型
class UserUpdate(UserBase):
    password: Optional[str] = None

# 用户登录请求模型
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token响应模型
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

# Token数据模型
class TokenData(BaseModel):
    email: Optional[str] = None

# 用户数据库模型
class UserInDBBase(UserBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# 用户模型
class User(UserInDBBase):
    pass

# 用户数据库模型（包含hashed_password）
class UserInDB(UserInDBBase):
    hashed_password: str

# 用户响应模型
class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
