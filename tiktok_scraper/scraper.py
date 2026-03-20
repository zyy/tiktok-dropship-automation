# TikTok 热门商品爬虫 - 真实API版本
# 支持 FastMoss / Kalodata / EchoTik / 官方API

import requests
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from loguru import logger
from pathlib import Path
import os

@dataclass
class TikTokProduct:
    """TikTok商品数据结构"""
    id: str
    name: str
    category: str
    views: int
    likes: int
    shares: int
    video_url: str
    product_url: Optional[str]
    trending_score: float
    tags: List[str]
    thumbnail: Optional[str]
    price_range: Optional[str]
    
    def to_dict(self) -> dict:
        return asdict(self)

class TikTokScraper:
    """TikTok热门商品爬虫 - 多数据源方案"""
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.data_dir = Path(config.get("temp_dir", "./temp"))
        self.data_dir.mkdir(exist_ok=True)
        
        # API配置
        self.api_key = config.get("tiktok_data_api_key")
        self.api_url = config.get("tiktok_data_api_url")
        self.use_real_api = bool(self.api_key and self.api_url)
        
    def fetch_trending_products(self, category: str = None, limit: int = 20) -> List[TikTokProduct]:
        """获取热门商品"""
        if self.use_real_api:
            return self._fetch_from_api(category, limit)
        else:
            logger.warning("Using mock data - configure TIKTOK_DATA_API_KEY for real data")
            return self._fetch_mock_data(category, limit)
    
    def _fetch_from_api(self, category: str = None, limit: int = 20) -> List[TikTokProduct]:
        """从真实API获取数据"""
        logger.info(f"Fetching from TikTok Data API: {self.api_url}")
        
        try:
            # FastMoss API 示例
            # 文档: https://www.fastmoss.com/api-docs
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            params = {
                "limit": limit,
                "category": category or "all",
                "sort_by": "sales",  # sales, views, likes
                "time_range": "7d"   # 7d, 30d, 90d
            }
            
            response = self.session.get(
                f"{self.api_url}/products/trending",
                headers=headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for item in data.get("data", []):
                product = TikTokProduct(
                    id=item.get("product_id", ""),
                    name=item.get("product_name", ""),
                    category=item.get("category", "General"),
                    views=item.get("views", 0),
                    likes=item.get("likes", 0),
                    shares=item.get("shares", 0),
                    video_url=item.get("video_url", ""),
                    product_url=item.get("product_url"),
                    trending_score=self._calculate_trending_score(item),
                    tags=item.get("tags", []),
                    thumbnail=item.get("thumbnail"),
                    price_range=item.get("price_range")
                )
                products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"API fetch failed: {e}")
            logger.info("Falling back to mock data")
            return self._fetch_mock_data(category, limit)
    
    def _fetch_mock_data(self, category: str = None, limit: int = 20) -> List[TikTokProduct]:
        """模拟数据（用于测试）"""
        logger.info(f"Fetching mock TikTok Shop data")
        
        sample_products = [
            {
                "id": "tt_001", "name": "Wireless Bluetooth Earbuds",
                "category": "Electronics", "views": 2500000, "likes": 180000, "shares": 25000,
                "video_url": "https://tiktok.com/@user/video/001",
                "tags": ["#earbuds", "#wireless", "#bluetooth", "#music"],
                "thumbnail": "https://example.com/thumb1.jpg", "price_range": "$15-25"
            },
            {
                "id": "tt_002", "name": "LED Strip Lights RGB",
                "category": "Home", "views": 3200000, "likes": 220000, "shares": 45000,
                "video_url": "https://tiktok.com/@user/video/002",
                "tags": ["#ledlights", "#roomdecor", "#aesthetic", "#homedecor"],
                "thumbnail": "https://example.com/thumb2.jpg", "price_range": "$10-20"
            },
            {
                "id": "tt_003", "name": "Portable Blender",
                "category": "Kitchen", "views": 1800000, "likes": 150000, "shares": 18000,
                "video_url": "https://tiktok.com/@user/video/003",
                "tags": ["#blender", "#smoothie", "#healthy", "#kitchen"],
                "thumbnail": "https://example.com/thumb3.jpg", "price_range": "$20-35"
            },
            {
                "id": "tt_004", "name": "Phone Tripod Stand",
                "category": "Electronics", "views": 1500000, "likes": 95000, "shares": 12000,
                "video_url": "https://tiktok.com/@user/video/004",
                "tags": ["#tripod", "#contentcreator", "#filming", "#setup"],
                "thumbnail": "https://example.com/thumb4.jpg", "price_range": "$12-25"
            },
            {
                "id": "tt_005", "name": "Car Interior LED Lights",
                "category": "Automotive", "views": 2100000, "likes": 175000, "shares": 32000,
                "video_url": "https://tiktok.com/@user/video/005",
                "tags": ["#carlights", "#caraccessories", "#led", "#automotive"],
                "thumbnail": "https://example.com/thumb5.jpg", "price_range": "$15-30"
            },
            {
                "id": "tt_006", "name": "Makeup Brush Cleaner",
                "category": "Beauty", "views": 1900000, "likes": 165000, "shares": 28000,
                "video_url": "https://tiktok.com/@user/video/006",
                "tags": ["#makeup", "#beauty", "#brushcleaner", "#skincare"],
                "thumbnail": "https://example.com/thumb6.jpg", "price_range": "$8-18"
            },
            {
                "id": "tt_007", "name": "Magnetic Phone Mount",
                "category": "Electronics", "views": 2800000, "likes": 210000, "shares": 38000,
                "video_url": "https://tiktok.com/@user/video/007",
                "tags": ["#phonemount", "#car", "#magnetic", "#accessories"],
                "thumbnail": "https://example.com/thumb7.jpg", "price_range": "$10-20"
            },
            {
                "id": "tt_008", "name": "Ice Roller for Face",
                "category": "Beauty", "views": 3500000, "likes": 290000, "shares": 55000,
                "video_url": "https://tiktok.com/@user/video/008",
                "tags": ["#skincare", "#iceroller", "#beautytips", "#morningroutine"],
                "thumbnail": "https://example.com/thumb8.jpg", "price_range": "$6-15"
            },
            {
                "id": "tt_009", "name": "Mini Projector",
                "category": "Electronics", "views": 4200000, "likes": 320000, "shares": 68000,
                "video_url": "https://tiktok.com/@user/video/009",
                "tags": ["#projector", "#movienight", "#hometheater", "#tech"],
                "thumbnail": "https://example.com/thumb9.jpg", "price_range": "$50-120"
            },
            {
                "id": "tt_010", "name": "Cloud Slides",
                "category": "Fashion", "views": 5600000, "likes": 480000, "shares": 95000,
                "video_url": "https://tiktok.com/@user/video/010",
                "tags": ["#cloudslides", "#comfort", "#shoes", "#tiktokmademebuyit"],
                "thumbnail": "https://example.com/thumb10.jpg", "price_range": "$15-30"
            }
        ]
        
        products = []
        for item in sample_products[:limit]:
            trending_score = self._calculate_trending_score(item)
            product = TikTokProduct(
                id=item["id"], name=item["name"], category=item["category"],
                views=item["views"], likes=item["likes"], shares=item["shares"],
                video_url=item["video_url"], product_url=None,
                trending_score=trending_score, tags=item["tags"],
                thumbnail=item.get("thumbnail"), price_range=item.get("price_range")
            )
            products.append(product)
            
        return products
    
    def _calculate_trending_score(self, item: dict) -> float:
        """计算商品趋势分数"""
        views = item.get("views", 0)
        likes = item.get("likes", 0)
        shares = item.get("shares", 0)
        engagement_rate = (likes + shares * 2) / views if views > 0 else 0
        views_score = min(views / 1000000, 10)
        score = views_score * 0.4 + engagement_rate * 100 * 0.6
        return round(score, 2)
    
    def save_products(self, products: List[TikTokProduct], filename: str = None):
        """保存商品数据"""
        if filename is None:
            filename = f"tiktok_products_{int(time.time())}.json"
        filepath = self.data_dir / filename
        data = [p.to_dict() for p in products]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath
    
    def run(self, category: str = None, limit: int = 10, min_score: float = 5.0) -> List[TikTokProduct]:
        """主运行函数"""
        logger.info("=" * 50)
        logger.info("Starting TikTok Product Scraping")
        logger.info("=" * 50)
        
        products = self.fetch_trending_products(category, limit * 2)
        logger.info(f"Fetched {len(products)} products")
        
        products = [p for p in products if p.trending_score >= min_score]
        products.sort(key=lambda x: x.trending_score, reverse=True)
        top_products = products[:limit]
        
        self.save_products(top_products)
        
        logger.info("TikTok scraping completed!")
        for p in top_products:
            logger.info(f"  - {p.name} (Score: {p.trending_score}, Views: {p.views:,})")
        
        return top_products
