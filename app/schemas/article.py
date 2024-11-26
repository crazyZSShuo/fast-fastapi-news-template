from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# 文章基础模型
class ArticleBase(BaseModel):
    title: str
    content: str
    category: str
    tags: List[str]

# 创建文章请求模型
class ArticleCreate(ArticleBase):
    status: str = "draft"

# 更新文章请求模型
class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

# 文章响应模型
class Article(ArticleBase):
    id: int
    status: str
    views: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 文章列表查询参数模型
class ArticleQueryParams(BaseModel):
    page: int = 1
    per_page: int = 10
    category: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
