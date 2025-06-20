import pytest
from datetime import datetime, timedelta


class TestURLAPI:
    """URL API测试"""
    
    def test_root_endpoint(self, client):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        assert "欢迎使用URL短链接生成器" in response.json()["message"]
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_create_short_url_basic(self, client):
        """测试创建基本短链接"""
        payload = {
            "original_url": "https://www.example.com"
        }
        
        response = client.post("/shorten", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_url"] == "https://www.example.com"
        assert len(data["id"]) == 8
        assert data["click_count"] == 0
        assert data["is_active"] is True
        assert data["short_url"].endswith(data["id"])
    
    def test_create_short_url_with_alias(self, client):
        """测试创建带自定义别名的短链接"""
        payload = {
            "original_url": "https://www.google.com",
            "custom_alias": "google"
        }
        
        response = client.post("/shorten", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "google"
        assert data["original_url"] == "https://www.google.com"
    
    def test_create_short_url_with_expiry(self, client):
        """测试创建带过期时间的短链接"""
        expires_at = (datetime.utcnow() + timedelta(days=1)).isoformat()
        payload = {
            "original_url": "https://www.example.com",
            "expires_at": expires_at
        }
        
        response = client.post("/shorten", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["expires_at"] is not None
    
    def test_create_short_url_invalid_url(self, client):
        """测试创建无效URL的短链接"""
        payload = {
            "original_url": "not-a-valid-url"
        }
        
        response = client.post("/shorten", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_short_url_duplicate_alias(self, client):
        """测试创建重复别名的短链接"""
        payload = {
            "original_url": "https://www.example1.com",
            "custom_alias": "test"
        }
        
        # 第一次创建应该成功
        response1 = client.post("/shorten", json=payload)
        assert response1.status_code == 200
        
        # 第二次创建相同别名应该失败
        payload2 = {
            "original_url": "https://www.example2.com",
            "custom_alias": "test"
        }
        response2 = client.post("/shorten", json=payload2)
        assert response2.status_code == 409  # Conflict
    
    def test_redirect_to_original_url(self, client):
        """测试重定向到原始URL"""
        # 先创建一个短链接
        payload = {
            "original_url": "https://www.example.com"
        }
        create_response = client.post("/shorten", json=payload)
        short_id = create_response.json()["id"]
        
        # 测试重定向
        response = client.get(f"/{short_id}", follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "https://www.example.com"
    
    def test_redirect_nonexistent_url(self, client):
        """测试重定向不存在的短链接"""
        response = client.get("/nonexistent", follow_redirects=False)
        assert response.status_code == 404
    
    def test_get_all_urls(self, client):
        """测试获取所有短链接"""
        # 先创建几个短链接
        for i in range(3):
            payload = {
                "original_url": f"https://www.example{i}.com"
            }
            client.post("/shorten", json=payload)
        
        response = client.get("/api/urls")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3
        assert all("original_url" in url for url in data)
    
    def test_get_url_info(self, client):
        """测试获取短链接信息"""
        # 先创建一个短链接
        payload = {
            "original_url": "https://www.example.com"
        }
        create_response = client.post("/shorten", json=payload)
        short_id = create_response.json()["id"]
        
        response = client.get(f"/api/urls/{short_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == short_id
        assert data["original_url"] == "https://www.example.com"
    
    def test_get_url_info_nonexistent(self, client):
        """测试获取不存在短链接的信息"""
        response = client.get("/api/urls/nonexistent")
        assert response.status_code == 404
    
    def test_get_url_stats(self, client):
        """测试获取短链接统计信息"""
        # 先创建一个短链接
        payload = {
            "original_url": "https://www.example.com"
        }
        create_response = client.post("/shorten", json=payload)
        short_id = create_response.json()["id"]
        
        # 访问几次短链接
        client.get(f"/{short_id}", follow_redirects=False)
        client.get(f"/{short_id}", follow_redirects=False)
        
        response = client.get(f"/api/urls/{short_id}/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == short_id
        assert data["click_count"] == 2
    
    def test_update_url(self, client):
        """测试更新短链接"""
        # 先创建一个短链接
        payload = {
            "original_url": "https://www.example.com"
        }
        create_response = client.post("/shorten", json=payload)
        short_id = create_response.json()["id"]
        
        # 更新短链接
        update_payload = {
            "original_url": "https://www.updated.com",
            "is_active": False
        }
        response = client.put(f"/api/urls/{short_id}", json=update_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["original_url"] == "https://www.updated.com"
        assert data["is_active"] is False
    
    def test_update_url_nonexistent(self, client):
        """测试更新不存在的短链接"""
        update_payload = {
            "is_active": False
        }
        response = client.put("/api/urls/nonexistent", json=update_payload)
        assert response.status_code == 404
    
    def test_delete_url(self, client):
        """测试删除短链接"""
        # 先创建一个短链接
        payload = {
            "original_url": "https://www.example.com"
        }
        create_response = client.post("/shorten", json=payload)
        short_id = create_response.json()["id"]
        
        # 删除短链接
        response = client.delete(f"/api/urls/{short_id}")
        
        assert response.status_code == 200
        assert "删除成功" in response.json()["message"]
        
        # 验证短链接已被删除
        get_response = client.get(f"/api/urls/{short_id}")
        assert get_response.status_code == 404
    
    def test_delete_url_nonexistent(self, client):
        """测试删除不存在的短链接"""
        response = client.delete("/api/urls/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_json_payload(self, client):
        """测试无效的JSON负载"""
        response = client.post("/shorten", data="invalid json")
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """测试缺少必需字段"""
        payload = {}  # 缺少 original_url
        response = client.post("/shorten", json=payload)
        assert response.status_code == 422
    
    def test_expired_url_access(self, client):
        """测试访问已过期的短链接"""
        expired_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        payload = {
            "original_url": "https://www.example.com",
            "expires_at": expired_time
        }
        
        create_response = client.post("/shorten", json=payload)
        short_id = create_response.json()["id"]
        
        # 尝试访问已过期的短链接
        response = client.get(f"/{short_id}", follow_redirects=False)
        assert response.status_code == 410  # Gone
    
    def test_alias_validation(self, client):
        """测试别名验证"""
        test_cases = [
            ("valid-alias", 200),
            ("valid_alias", 200),
            ("ValidAlias123", 200),
            ("invalid alias", 400),  # 包含空格
            ("invalid@alias", 400),  # 包含特殊字符
            ("", 422),  # 空别名
        ]
        
        for alias, expected_status in test_cases:
            payload = {
                "original_url": "https://www.example.com",
                "custom_alias": alias
            }
            response = client.post("/shorten", json=payload)
            
            if expected_status == 200:
                assert response.status_code in [200, 409]  # 可能因重复而冲突
            else:
                assert response.status_code == expected_status 