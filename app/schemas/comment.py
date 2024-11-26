from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# 评论基础模型
class CommentBase(BaseModel):
    content: str = Field(..., max_length=500, description="评论内容")

# 创建评论请求模型
class CommentCreate(CommentBase):
    article_id: int
    parent_id: Optional[int] = None

# 更新评论请求模型
class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=500, description="评论内容")

# 评论用户信息
class CommentUser(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# 评论响应模型
class Comment(CommentBase):
    id: int
    article_id: int
    user_id: int
    parent_id: Optional[int] = None
    status: str = "pending"  # pending, approved, rejected
    created_at: datetime
    updated_at: datetime
    user: Optional[CommentUser] = None
    replies: Optional[List['Comment']] = []
    reply_count: Optional[int] = 0

    class Config:
        from_attributes = True

# 评论列表查询参数模型
class CommentQueryParams(BaseModel):
    page: int = 1
    per_page: int = 10
    parent_id: Optional[int] = None  # None表示查询顶层评论
    status: Optional[str] = None  # 评论状态筛选
    content: Optional[str] = None  # 评论内容筛选
