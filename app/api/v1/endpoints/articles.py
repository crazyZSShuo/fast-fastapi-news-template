from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, get_current_admin_user
# from app.core.response import ResponseSchema
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleQueryParams, Article as ArticleSchema
from app.crud import crud_article
from app.models.user import User
from app.schemas.response import ResponseSchema

router = APIRouter()

@router.post("", response_model=ResponseSchema[ArticleSchema], summary="创建文章")
def create_article(
    *,
    db: Session = Depends(get_db),
    article_in: ArticleCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新文章
    """
    # 检查文章标题是否已存在
    if crud_article.article.get_by_title(db, title=article_in.title):
        raise HTTPException(
            status_code=400,
            detail="文章标题已存在",
        )
    
    article = crud_article.article.create_with_author(
        db=db, obj_in=article_in, author_id=current_user.id
    )
    return ResponseSchema(data=article)

@router.get("", response_model=ResponseSchema[dict], summary="获取文章列表")
def read_articles(
    db: Session = Depends(get_db),
    params: ArticleQueryParams = Depends(),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取文章列表，支持分页和筛选
    """
    articles = crud_article.article.get_multi_by_params(db=db, params=params)
    total = crud_article.article.get_total_count(db=db, params=params)
    
    # 使用 Pydantic 模型序列化文章列表
    articles_data = [ArticleSchema.model_validate(article) for article in articles]
    
    return ResponseSchema(data={
        "total": total,
        "items": articles_data,
        "page": params.page,
        "per_page": params.per_page
    })

@router.get("/{article_id}", response_model=ResponseSchema[ArticleSchema], summary="获取文章详情")
def read_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    通过ID获取文章详情
    """
    article = crud_article.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    # 增加浏览量
    article = crud_article.article.increment_views(db=db, article_id=article_id)
    return ResponseSchema(data=article)

@router.put("/{article_id}", response_model=ResponseSchema[ArticleSchema], summary="更新文章")
def update_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    article_in: ArticleUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新文章
    """
    article = crud_article.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查权限：只有管理员或文章作者可以更新文章
    if current_user.role != 'admin' and article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限更新此文章")
    
    # 如果要更新标题，检查新标题是否已存在（排除当前文章）
    if article_in.title and article_in.title != article.title:
        existing_article = crud_article.article.get_by_title(db, title=article_in.title)
        if existing_article and existing_article.id != article_id:
            raise HTTPException(
                status_code=400,
                detail="文章标题已存在",
            )
    
    # 更新文章，只更新提供的字段
    article = crud_article.article.update(db=db, db_obj=article, obj_in=article_in)
    return ResponseSchema(data=ArticleSchema.model_validate(article))

@router.delete("/{article_id}", response_model=ResponseSchema[ArticleSchema], summary="删除文章")
def delete_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除文章
    """
    article = crud_article.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 检查权限：只有管理员或文章作者可以删除文章
    if current_user.role != 'admin' and article.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限删除此文章")
    
    article = crud_article.article.remove(db=db, id=article_id)
    return ResponseSchema(data=ArticleSchema.model_validate(article))
