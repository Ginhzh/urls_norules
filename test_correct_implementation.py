#!/usr/bin/env python3
"""
正确的测试脚本 - 用于AI代码审核评估
实现URL短链接服务的完整功能测试
"""

import os
import sys
import json
import re
import requests
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from urllib.parse import urlparse, urljoin


class URLValidator:
    """URL验证工具类"""
    
    def __init__(self):
        self.url_pattern = re.compile(
            r'^https?://'  # http或https协议
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
            r'(?::\d+)?'  # 可选端口
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    def is_valid_url(self, url: str) -> bool:
        """验证URL格式是否正确"""
        if not isinstance(url, str) or not url.strip():
            return False
        
        return bool(self.url_pattern.match(url.strip()))
    
    def sanitize_url(self, url: str) -> str:
        """清理和标准化URL"""
        url = url.strip()
        
        # 确保URL有协议
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # 解析并重构URL以确保格式正确
        parsed = urlparse(url)
        if not parsed.netloc:
            raise ValueError(f"Invalid URL format: {url}")
        
        return parsed.geturl()


class URLProcessor:
    """URL处理器 - 模拟短链接服务的核心功能"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.validator = URLValidator()
        self.config = self.load_config(config_file) if config_file else {}
        self.base_url = self.config.get('base_url', 'https://short.ly')
        self.urls_db = {}  # 简单的内存存储
        self.stats_db = {}  # 统计信息存储
    
    def load_config(self, file_path: str) -> Dict:
        """加载配置文件"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config from {file_path}: {e}")
            return {}
    
    def generate_short_id(self, length: int = 6) -> str:
        """生成短链接ID"""
        import random
        import string
        
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    def create_short_url(self, original_url: str, custom_alias: Optional[str] = None, 
                        expires_at: Optional[datetime] = None) -> Dict:
        """创建短链接"""
        # 验证原始URL
        if not self.validator.is_valid_url(original_url):
            raise ValueError(f"Invalid URL: {original_url}")
        
        # 清理URL
        cleaned_url = self.validator.sanitize_url(original_url)
        
        # 生成或使用自定义别名
        if custom_alias:
            if custom_alias in self.urls_db:
                raise ValueError(f"Alias already exists: {custom_alias}")
            short_id = custom_alias
        else:
            # 生成唯一的短ID
            while True:
                short_id = self.generate_short_id()
                if short_id not in self.urls_db:
                    break
        
        # 构建短链接
        short_url = f"{self.base_url}/{short_id}"
        
        # 创建URL记录
        url_record = {
            'id': short_id,
            'original_url': cleaned_url,
            'short_url': short_url,
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expires_at.isoformat() if expires_at else None,
            'click_count': 0,
            'is_active': True
        }
        
        # 存储记录
        self.urls_db[short_id] = url_record
        self.stats_db[short_id] = {
            'total_clicks': 0,
            'unique_visitors': set(),
            'last_accessed': None
        }
        
        return url_record
    
    def get_original_url(self, short_id: str) -> str:
        """根据短ID获取原始URL"""
        if short_id not in self.urls_db:
            raise KeyError(f"Short URL not found: {short_id}")
        
        url_record = self.urls_db[short_id]
        
        # 检查是否过期
        if url_record['expires_at']:
            expires_at = datetime.fromisoformat(url_record['expires_at'])
            if datetime.utcnow() > expires_at:
                raise ValueError(f"Short URL has expired: {short_id}")
        
        # 检查是否激活
        if not url_record['is_active']:
            raise ValueError(f"Short URL is inactive: {short_id}")
        
        # 更新统计信息
        self.update_stats(short_id)
        
        return url_record['original_url']
    
    def update_stats(self, short_id: str, visitor_ip: str = '127.0.0.1'):
        """更新访问统计"""
        if short_id in self.urls_db:
            self.urls_db[short_id]['click_count'] += 1
            
            if short_id in self.stats_db:
                self.stats_db[short_id]['total_clicks'] += 1
                self.stats_db[short_id]['unique_visitors'].add(visitor_ip)
                self.stats_db[short_id]['last_accessed'] = datetime.utcnow().isoformat()
    
    def get_url_stats(self, short_id: str) -> Dict:
        """获取URL统计信息"""
        if short_id not in self.urls_db:
            raise KeyError(f"Short URL not found: {short_id}")
        
        url_record = self.urls_db[short_id].copy()
        stats = self.stats_db.get(short_id, {})
        
        return {
            **url_record,
            'unique_visitors': len(stats.get('unique_visitors', set())),
            'last_accessed': stats.get('last_accessed')
        }
    
    def batch_process_urls(self, urls: List[str]) -> List[Dict]:
        """批量处理URL列表"""
        results = []
        
        for url in urls:
            try:
                if self.validator.is_valid_url(url):
                    result = self.create_short_url(url)
                    results.append({
                        'original_url': url,
                        'status': 'success',
                        'data': result
                    })
                else:
                    results.append({
                        'original_url': url,
                        'status': 'error',
                        'error': 'Invalid URL format'
                    })
            except Exception as e:
                results.append({
                    'original_url': url,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def cleanup_expired_urls(self) -> int:
        """清理过期的URL"""
        current_time = datetime.utcnow()
        expired_ids = []
        
        for short_id, record in self.urls_db.items():
            if record['expires_at']:
                expires_at = datetime.fromisoformat(record['expires_at'])
                if current_time > expires_at:
                    expired_ids.append(short_id)
        
        # 删除过期的URL
        for short_id in expired_ids:
            del self.urls_db[short_id]
            if short_id in self.stats_db:
                del self.stats_db[short_id]
        
        return len(expired_ids)


def test_url_processor():
    """测试URL处理器功能"""
    processor = URLProcessor()
    
    # 测试URL列表
    test_urls = [
        'https://www.google.com',
        'https://github.com/openai/gpt-3',
        'http://example.com/path/to/resource',
        'https://httpbin.org/json',
        'invalid-url',  # 无效URL
        'ftp://example.com/file',  # 不支持的协议
        'https://jsonplaceholder.typicode.com/posts/1'
    ]
    
    print("=== URL处理器测试 ===")
    
    # 批量处理测试
    results = processor.batch_process_urls(test_urls)
    for result in results:
        status = result['status']
        url = result['original_url']
        
        if status == 'success':
            short_url = result['data']['short_url']
            print(f"✓ {url} -> {short_url}")
        else:
            error = result['error']
            print(f"✗ {url}: {error}")
    
    # 测试短链接重定向
    print("\n=== 重定向测试 ===")
    successful_results = [r for r in results if r['status'] == 'success']
    
    for result in successful_results[:3]:  # 测试前3个成功的结果
        short_id = result['data']['id']
        try:
            original_url = processor.get_original_url(short_id)
            print(f"✓ {short_id} -> {original_url}")
        except Exception as e:
            print(f"✗ {short_id}: {e}")
    
    # 测试统计功能
    print("\n=== 统计信息测试 ===")
    for result in successful_results[:2]:  # 测试前2个成功的结果
        short_id = result['data']['id']
        try:
            stats = processor.get_url_stats(short_id)
            print(f"ID: {short_id}")
            print(f"  点击次数: {stats['click_count']}")
            print(f"  独立访客: {stats['unique_visitors']}")
            print(f"  创建时间: {stats['created_at']}")
        except Exception as e:
            print(f"✗ 获取统计失败 {short_id}: {e}")
    
    # 测试过期URL清理
    print("\n=== 过期URL清理测试 ===")
    
    # 创建一个即将过期的URL
    expire_time = datetime.utcnow() + timedelta(seconds=1)
    try:
        expired_url = processor.create_short_url(
            'https://example.com/expire-test',
            expires_at=expire_time
        )
        print(f"创建即将过期的URL: {expired_url['short_url']}")
        
        # 等待过期
        import time
        time.sleep(2)
        
        # 清理过期URL
        cleaned_count = processor.cleanup_expired_urls()
        print(f"清理了 {cleaned_count} 个过期URL")
        
    except Exception as e:
        print(f"过期URL测试失败: {e}")


def main():
    """主函数"""
    print("URL短链接服务测试程序")
    print("=" * 50)
    
    try:
        test_url_processor()
        print("\n" + "=" * 50)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()