from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta

from app.core.deps import get_db, get_current_active_user
from app.crud import crud_article, crud_user, crud_comment
from app.models.user import User
from app.models.article import Article
from app.models.comment import Comment
from app.schemas.response import ResponseSchema

router = APIRouter()

@router.get("/stats", summary="获取仪表盘统计数据")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取仪表盘统计和趋势数据
    """
    # 基础统计数据
    article_count = db.query(func.count(Article.id)).scalar()
    comment_count = db.query(func.count(Comment.id)).scalar()
    user_count = db.query(func.count(User.id)).scalar()

    # 获取最近7天的日期列表
    today = datetime.now().date()
    dates = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

    # 获取最近7天的文章数据
    articles_trend = []
    for date in dates:
        count = db.query(func.count(Article.id)).filter(
            func.date(Article.created_at) == date
        ).scalar()
        articles_trend.append(count)

    # 获取最近7天的评论数据
    comments_trend = []
    for date in dates:
        count = db.query(func.count(Comment.id)).filter(
            func.date(Comment.created_at) == date
        ).scalar()
        comments_trend.append(count)

    return ResponseSchema(data={
        "article_count": article_count,
        "comment_count": comment_count,
        "user_count": user_count,
        "trend_data": {
            "dates": dates,
            "articles": articles_trend,
            "comments": comments_trend
        }
    })
