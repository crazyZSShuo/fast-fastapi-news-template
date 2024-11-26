from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(50), nullable=False)
    location = Column(String(200))  # 存储IP地理位置信息
    user_agent = Column(String(500))  # 存储用户浏览器信息
    path = Column(String(200))  # 访问的路径
    created_at = Column(DateTime(timezone=True), server_default=func.now())
