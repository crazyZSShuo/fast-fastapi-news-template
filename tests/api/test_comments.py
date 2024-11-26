import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_comment(client: TestClient, normal_user_token_headers):
    """测试创建评论"""
    # 先创建一篇文章
    article_data = {
        "title": "Test Article",
        "content": "Test content",
        "summary": "Test summary",
        "category": "technology"
    }
    article_response = client.post(
        "/api/v1/articles/",
        json=article_data,
        headers=normal_user_token_headers
    )
    article_id = article_response.json()["data"]["id"]
    
    # 创建评论
    comment_data = {
        "content": "This is a test comment",
        "article_id": article_id
    }
    response = client.post(
        "/api/v1/comments/",
        json=comment_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()["data"]
    assert content["content"] == comment_data["content"]
    assert content["article_id"] == article_id
    assert "id" in content
    assert "created_at" in content
    return content

def test_create_reply(client: TestClient, normal_user_token_headers):
    """测试创建回复评论"""
    # 先创建一个父评论
    parent_comment = test_create_comment(client, normal_user_token_headers)
    
    # 创建回复评论
    reply_data = {
        "content": "This is a reply comment",
        "article_id": parent_comment["article_id"],
        "parent_id": parent_comment["id"]
    }
    response = client.post(
        "/api/v1/comments/",
        json=reply_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()["data"]
    assert content["content"] == reply_data["content"]
    assert content["parent_id"] == parent_comment["id"]
    assert content["article_id"] == parent_comment["article_id"]

def test_get_comment(client: TestClient, normal_user_token_headers):
    """测试获取单个评论"""
    # 先创建一个评论
    comment = test_create_comment(client, normal_user_token_headers)
    
    # 获取这个评论
    response = client.get(f"/api/v1/comments/{comment['id']}")
    assert response.status_code == 200
    content = response.json()["data"]
    assert content["id"] == comment["id"]
    assert content["content"] == comment["content"]

def test_get_nonexistent_comment(client: TestClient):
    """测试获取不存在的评论"""
    response = client.get("/api/v1/comments/99999")
    assert response.status_code == 404
    assert "评论不存在" in response.json()["detail"]

def test_update_comment(client: TestClient, normal_user_token_headers):
    """测试更新评论"""
    # 先创建一个评论
    comment = test_create_comment(client, normal_user_token_headers)
    
    # 更新评论
    update_data = {
        "content": "Updated comment content"
    }
    response = client.put(
        f"/api/v1/comments/{comment['id']}",
        json=update_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()["data"]
    assert content["content"] == update_data["content"]

def test_delete_comment(client: TestClient, normal_user_token_headers):
    """测试删除评论"""
    # 先创建一个评论
    comment = test_create_comment(client, normal_user_token_headers)
    
    # 删除评论
    response = client.delete(
        f"/api/v1/comments/{comment['id']}",
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    
    # 确认评论已被删除
    response = client.get(f"/api/v1/comments/{comment['id']}")
    assert response.status_code == 404

def test_list_article_comments(client: TestClient, normal_user_token_headers):
    """测试获取文章的评论列表"""
    # 先创建一个评论
    comment = test_create_comment(client, normal_user_token_headers)
    
    # 获取文章的评论列表
    response = client.get(f"/api/v1/articles/{comment['article_id']}/comments")
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "total" in content
    assert "page" in content
    assert "size" in content
    assert isinstance(content["data"], list)
    assert len(content["data"]) > 0

def test_unauthorized_comment_operations(client: TestClient):
    """测试未授权的评论操作"""
    # 尝试未登录创建评论
    comment_data = {
        "content": "Test comment",
        "article_id": 1
    }
    response = client.post("/api/v1/comments/", json=comment_data)
    assert response.status_code == 401

def test_invalid_parent_comment(client: TestClient, normal_user_token_headers):
    """测试使用无效的父评论ID"""
    comment_data = {
        "content": "Test reply",
        "article_id": 1,
        "parent_id": 99999  # 不存在的父评论ID
    }
    response = client.post(
        "/api/v1/comments/",
        json=comment_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 404
    assert "父评论不存在" in response.json()["detail"]
