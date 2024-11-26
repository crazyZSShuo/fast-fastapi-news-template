from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate

class CRUDComment(CRUDBase[Comment, CommentCreate, CommentUpdate]):
    def create_with_user(
        self, db: Session, *, obj_in: CommentCreate, user_id: int
    ) -> Comment:
        """
        创建评论，并设置用户ID
        """
        obj_in_data = obj_in.dict()
        db_obj = Comment(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_article(
        self, db: Session, *, article_id: int, skip: int = 0, limit: int = 100, parent_id: Optional[int] = None
    ) -> List[Comment]:
        """
        获取指定文章的评论列表
        
        :param parent_id: 如果指定，则获取指定父评论的回复；如果为None，则获取顶层评论
        """
        query = db.query(self.model).filter(Comment.article_id == article_id)
        
        if parent_id is None:
            # 获取顶层评论（没有父评论的评论）
            query = query.filter(Comment.parent_id.is_(None))
        else:
            # 获取指定父评论的回复
            query = query.filter(Comment.parent_id == parent_id)
        
        return query.order_by(Comment.created_at.desc()).offset(skip).limit(limit).all()

    def get_total_count_by_article(
        self, db: Session, *, article_id: int, parent_id: Optional[int] = None
    ) -> int:
        """
        获取指定文章的评论总数
        
        :param parent_id: 如果指定，则获取指定父评论的回复数；如果为None，则获取顶层评论数
        """
        query = db.query(func.count(self.model.id)).filter(Comment.article_id == article_id)
        
        if parent_id is None:
            query = query.filter(Comment.parent_id.is_(None))
        else:
            query = query.filter(Comment.parent_id == parent_id)
        
        return query.scalar()

    def get_reply_count(self, db: Session, *, comment_id: int) -> int:
        """
        获取指定评论的回复数量
        """
        return db.query(func.count(self.model.id)).filter(
            Comment.parent_id == comment_id
        ).scalar()

    def get_with_replies(
        self, db: Session, *, comment_id: int, reply_limit: int = 5
    ) -> Optional[Comment]:
        """
        获取评论及其回复
        """
        comment = db.query(self.model).filter(self.model.id == comment_id).first()
        if comment:
            # 获取最新的几条回复
            replies = (
                db.query(self.model)
                .filter(Comment.parent_id == comment_id)
                .order_by(Comment.created_at.desc())
                .limit(reply_limit)
                .all()
            )
            setattr(comment, "replies", replies)
            setattr(comment, "reply_count", len(replies))
        return comment

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100,
        status: Optional[str] = None, content: Optional[str] = None
    ) -> List[Comment]:
        """
        获取评论列表，支持按状态和内容筛选
        """
        query = db.query(self.model)
        
        if status:
            query = query.filter(self.model.status == status)
        if content:
            query = query.filter(self.model.content.ilike(f"%{content}%"))
        
        return query.order_by(self.model.created_at.desc()).offset(skip).limit(limit).all()

    def get_total_count(
        self, db: Session, *, status: Optional[str] = None,
        content: Optional[str] = None
    ) -> int:
        """
        获取评论总数，支持按状态和内容筛选
        """
        query = db.query(func.count(self.model.id))
        
        if status:
            query = query.filter(self.model.status == status)
        if content:
            query = query.filter(self.model.content.ilike(f"%{content}%"))
        
        return query.scalar()

    def is_admin(self, user) -> bool:
        return user.role == "admin"

comment = CRUDComment(Comment)
