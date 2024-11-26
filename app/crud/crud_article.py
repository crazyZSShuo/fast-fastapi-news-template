from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleQueryParams

class CRUDArticle(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    def get_by_title(self, db: Session, *, title: str) -> Optional[Article]:
        """
        通过标题获取文章
        """
        return db.query(self.model).filter(Article.title == title).first()

    def create_with_author(
        self, db: Session, *, obj_in: ArticleCreate, author_id: int
    ) -> Article:
        """
        创建文章，并设置作者ID
        """
        obj_in_data = obj_in.dict()
        db_obj = Article(**obj_in_data, author_id=author_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_author(
        self, db: Session, *, author_id: int, skip: int = 0, limit: int = 100
    ) -> List[Article]:
        return (
            db.query(self.model)
            .filter(Article.author_id == author_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_by_params(
        self, db: Session, *, params: ArticleQueryParams
    ) -> List[Article]:
        query = db.query(self.model)
        
        # 应用过滤条件
        if params.category:
            query = query.filter(Article.category == params.category)
        if params.status:
            query = query.filter(Article.status == params.status)
        if params.search:
            search = f"%{params.search}%"
            query = query.filter(
                or_(
                    Article.title.like(search),
                    Article.content.like(search)
                )
            )
        
        # 计算分页
        skip = (params.page - 1) * params.per_page
        
        return query.offset(skip).limit(params.per_page).all()

    def get_total_count(self, db: Session, *, params: Optional[ArticleQueryParams] = None) -> int:
        query = db.query(self.model)
        
        if params:
            if params.category:
                query = query.filter(Article.category == params.category)
            if params.status:
                query = query.filter(Article.status == params.status)
            if params.search:
                search = f"%{params.search}%"
                query = query.filter(
                    or_(
                        Article.title.like(search),
                        Article.content.like(search)
                    )
                )
        
        return query.count()

    def increment_views(self, db: Session, *, article_id: int) -> Article:
        article = self.get(db, id=article_id)
        if article:
            article.views += 1
            db.add(article)
            db.commit()
            db.refresh(article)
        return article

article = CRUDArticle(Article)
