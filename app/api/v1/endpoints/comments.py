from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, get_current_admin_user
from app.crud import crud_comment, crud_article
from app.models.user import User
from app.schemas.comment import (
    Comment as CommentSchema,
    CommentCreate,
    CommentQueryParams,
)
from app.schemas.response import ResponseSchema

router = APIRouter()

@router.post("", response_model=ResponseSchema[CommentSchema], summary="创建评论")
def create_comment(
    *,
    db: Session = Depends(get_db),
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新评论或回复其他评论
    """
    # 检查文章是否存在
    article = crud_article.article.get(db=db, id=comment_in.article_id)
    if not article:
        raise HTTPException(
            status_code=404,
            detail=f"文章 {comment_in.article_id} 不存在"
        )
    
    # 如果是回复其他评论，检查父评论是否存在且属于同一篇文章
    if comment_in.parent_id:
        parent_comment = crud_comment.comment.get(db=db, id=comment_in.parent_id)
        if not parent_comment:
            raise HTTPException(status_code=404, detail="父评论不存在")
        if parent_comment.article_id != comment_in.article_id:
            raise HTTPException(status_code=400, detail="父评论不属于该文章")
        # 不允许嵌套回复（只允许二级评论）
        if parent_comment.parent_id is not None:
            raise HTTPException(status_code=400, detail="不支持嵌套回复")
    
    comment = crud_comment.comment.create_with_user(
        db=db, obj_in=comment_in, user_id=current_user.id
    )
    return ResponseSchema(data=CommentSchema.model_validate(comment))

@router.get("/article/{article_id}", response_model=ResponseSchema[dict], summary="获取文章评论")
def read_article_comments(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    params: CommentQueryParams = Depends(),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定文章的评论列表
    
    - parent_id为None时获取顶层评论
    - parent_id不为None时获取指定评论的回复
    """
    # 检查文章是否存在
    article = crud_article.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(
            status_code=404,
            detail=f"文章 {article_id} 不存在"
        )
    
    # 如果指定了parent_id，检查父评论是否存在
    if params.parent_id is not None:
        parent_comment = crud_comment.comment.get(db=db, id=params.parent_id)
        if not parent_comment:
            raise HTTPException(status_code=404, detail="父评论不存在")
        if parent_comment.article_id != article_id:
            raise HTTPException(status_code=400, detail="父评论不属于该文章")
    
    skip = (params.page - 1) * params.per_page
    comments = crud_comment.comment.get_multi_by_article(
        db=db,
        article_id=article_id,
        skip=skip,
        limit=params.per_page,
        parent_id=params.parent_id
    )
    total = crud_comment.comment.get_total_count_by_article(
        db=db,
        article_id=article_id,
        parent_id=params.parent_id
    )
    
    # 获取每个评论的回复数和最新回复
    comments_data = []
    for comment in comments:
        comment_data = CommentSchema.model_validate(comment)
        if params.parent_id is None:  # 只为顶层评论获取回复信息
            # 获取最新的5条回复
            comment_with_replies = crud_comment.comment.get_with_replies(
                db=db, comment_id=comment.id, reply_limit=5
            )
            if comment_with_replies:
                comment_data.replies = [
                    CommentSchema.model_validate(reply)
                    for reply in comment_with_replies.replies
                ]
                comment_data.reply_count = crud_comment.comment.get_reply_count(
                    db=db, comment_id=comment.id
                )
        comments_data.append(comment_data)
    
    return ResponseSchema(data={
        "total": total,
        "items": comments_data,
        "page": params.page,
        "per_page": params.per_page
    })

@router.get("", response_model=ResponseSchema[dict], summary="管理员获取所有评论")
def read_comments(
    *,
    db: Session = Depends(get_db),
    params: CommentQueryParams = Depends(),
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    管理员获取所有评论列表
    """
    skip = (params.page - 1) * params.per_page
    comments = crud_comment.comment.get_multi(
        db=db,
        skip=skip,
        limit=params.per_page,
        status=params.status,
        content=params.content
    )
    total = crud_comment.comment.get_total_count(
        db=db,
        status=params.status,
        content=params.content
    )
    
    return ResponseSchema(data={
        "total": total,
        "items": [CommentSchema.model_validate(comment) for comment in comments],
        "page": params.page,
        "per_page": params.per_page
    })

@router.post("/{comment_id}/review", response_model=ResponseSchema[CommentSchema], summary="审核评论")
def review_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int,
    status: str,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """
    审核评论
    
    - 只有管理员可以审核评论
    - status可选值：approved（通过）、rejected（拒绝）
    """
    if status not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    comment = crud_comment.comment.get(db=db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    comment = crud_comment.comment.update(
        db=db,
        db_obj=comment,
        obj_in={"status": status}
    )
    return ResponseSchema(data=CommentSchema.model_validate(comment))

@router.delete("/article/{article_id}/comment/{comment_id}", response_model=ResponseSchema[CommentSchema], summary="删除评论")
def delete_comment(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除评论
    
    - 需要验证评论属于指定的文章
    - 只有管理员或评论作者可以删除评论
    - 删除评论时会同时删除其所有回复
    """
    # 检查文章是否存在
    article = crud_article.article.get(db=db, id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail=f"文章 {article_id} 不存在")
    
    # 检查评论是否存在
    comment = crud_comment.comment.get(db=db, id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    
    # 验证评论是否属于该文章
    if comment.article_id != article_id:
        raise HTTPException(status_code=400, detail="该评论不属于此文章")
    
    # 检查权限：只有管理员或评论作者可以删除评论
    if current_user.role != 'admin' and comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="没有权限删除此评论")
    
    comment = crud_comment.comment.remove(db=db, id=comment_id)
    return ResponseSchema(data=CommentSchema.model_validate(comment))
