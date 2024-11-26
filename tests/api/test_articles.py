import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

def test_create_article(client: TestClient, normal_user_token_headers):
    """测试创建文章"""
    data = {
        "title": "Test Article",
        "content": "This is a test article content",
        "summary": "Test summary",
        "category": "technology"
    }
    response = client.post(
        "/api/v1/articles/", 
        json=data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()["data"]
    assert content["title"] == data["title"]
    assert content["content"] == data["content"]
    assert content["summary"] == data["summary"]
    assert content["category"] == data["category"]
    assert "id" in content
    assert "created_at" in content
    return content

def test_get_article(client: TestClient, normal_user_token_headers):
    """测试获取单个文章"""
    # 先创建一篇文章
    article = test_create_article(client, normal_user_token_headers)
    
    # 获取这篇文章
    response = client.get(f"/api/v1/articles/{article['id']}")
    assert response.status_code == 200
    content = response.json()["data"]
    assert content["id"] == article["id"]
    assert content["title"] == article["title"]
    assert content["content"] == article["content"]

def test_get_nonexistent_article(client: TestClient):
    """测试获取不存在的文章"""
    response = client.get("/api/v1/articles/99999")
    assert response.status_code == 404
    assert "文章不存在" in response.json()["detail"]

def test_update_article(client: TestClient, normal_user_token_headers):
    """测试更新文章"""
    # 先创建一篇文章
    article = test_create_article(client, normal_user_token_headers)
    
    # 更新文章
    update_data = {
        "title": "Updated Title",
        "content": "Updated content",
        "summary": "Updated summary",
        "category": "science"
    }
    response = client.put(
        f"/api/v1/articles/{article['id']}", 
        json=update_data,
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    content = response.json()["data"]
    assert content["title"] == update_data["title"]
    assert content["content"] == update_data["content"]
    assert content["summary"] == update_data["summary"]
    assert content["category"] == update_data["category"]

def test_delete_article(client: TestClient, normal_user_token_headers):
    """测试删除文章"""
    # 先创建一篇文章
    article = test_create_article(client, normal_user_token_headers)
    
    # 删除文章
    response = client.delete(
        f"/api/v1/articles/{article['id']}", 
        headers=normal_user_token_headers
    )
    assert response.status_code == 200
    
    # 确认文章已被删除
    response = client.get(f"/api/v1/articles/{article['id']}")
    assert response.status_code == 404

def test_list_articles(client: TestClient):
    """测试获取文章列表"""
    response = client.get("/api/v1/articles/")
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "total" in content
    assert "page" in content
    assert "size" in content
    assert isinstance(content["data"], list)

def test_search_articles(client: TestClient, normal_user_token_headers):
    """测试搜索文章"""
    # 先创建一篇包含特定关键词的文章
    data = {
        "title": "Python Programming",
        "content": "Learn Python programming language",
        "summary": "A guide to Python",
        "category": "technology"
    }
    client.post("/api/v1/articles/", json=data, headers=normal_user_token_headers)
    
    # 搜索文章
    response = client.get("/api/v1/articles/?search=Python")
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) > 0
    assert any("Python" in article["title"] for article in content["data"])

def test_filter_articles_by_category(client: TestClient, normal_user_token_headers):
    """测试按分类筛选文章"""
    # 创建一篇特定分类的文章
    data = {
        "title": "Science News",
        "content": "Latest science news",
        "summary": "Science summary",
        "category": "science"
    }
    client.post("/api/v1/articles/", json=data, headers=normal_user_token_headers)
    
    # 按分类筛选
    response = client.get("/api/v1/articles/?category=science")
    assert response.status_code == 200
    content = response.json()
    assert len(content["data"]) > 0
    assert all(article["category"] == "science" for article in content["data"])
