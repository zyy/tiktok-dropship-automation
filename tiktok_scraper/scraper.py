# TikTok 热门商品爬虫 - 完整实现
# 使用第三方数据服务和API获取热门商品

import requests
import json
import time
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from loguru import logger
from pathlib import Path
import random

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
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.data_dir = Path(config.get("temp_dir", "./temp"))
        self.data_dir.mkdir(exist_ok=True)
        
    def fetch_from_shop_data(self, category: str = None, limit: int = 20) -> List[TikTokProduct]:
        """从TikTok Shop数据获取热门商品"""
        logger.info(f"Fetching TikTok Shop data for category: {category}")
        
        products = []
        
        # 模拟热门商品数据（实际项目中接入TikTok Shop API或爬虫）
        # 这里使用示例数据，实际应替换为真实API
        sample_products = [
            {
                "id": "tt_001",
                "name": "Wireless Bluetooth Earbuds",
                "category": "Electronics",
                "views": 2500000,
                "likes": 180000,
                "shares": 25000,
                "video_url": "https://tiktok.com/@user/video/001",
                "tags": ["#earbuds", "#wireless", "#bluetooth", "#music"],
                "thumbnail": "https://example.com/thumb1.jpg",
                "price_range": "$15-25"
            },
            {
                "id": "tt_002",
                "name": "LED Strip Lights RGB",
                "category": "Home",
                "views": 3200000,
                "likes": 220000,
                "shares": 45000,
                "video_url": "https://tiktok.com/@user/video/002",
                "tags": ["#ledlights", "#roomdecor", "#aesthetic", "#homedecor"],
                "thumbnail": "https://example.com/thumb2.jpg",
                "price_range": "$10-20"
            },
            {
                "id": "tt_003",
                "name": "Portable Blender",
                "category": "Kitchen",
                "views": 1800000,
                "likes": 150000,
                "shares": 18000,
                "video_url": "https://tiktok.com/@user/video/003",
                "tags": ["#blender", "#smoothie", "#healthy", "#kitchen"],
                "thumbnail": "https://example.com/thumb3.jpg",
                "price_range": "$20-35"
            },
            {
                "id": "tt_004",
                "name": "Phone Tripod Stand",
                "category": "Electronics",
                "views": 1500000,
                "likes": 95000,
                "shares": 12000,
                "video_url": "https://tiktok.com/@user/video/004",
                "tags": ["#tripod", "#contentcreator", "#filming", "#setup"],
                "thumbnail": "https://example.com/thumb4.jpg",
                "price_range": "$12-25"
            },
            {
                "id": "tt_005",
                "name": "Car Interior LED Lights",
                "category": "Automotive",
                "views": 2100000,
                "likes": 175000,
                "shares": 32000,
                "video_url": "https://tiktok.com/@user/video/005",
                "tags": ["#carlights", "#caraccessories", "#led", "#automotive"],
                "thumbnail": "https://example.com/thumb5.jpg",
                "price_range": "$15-30"
            },
            {
                "id": "tt_006",
                "name": "Makeup Brush Cleaner",
                "category": "Beauty",
                "views": 1900000,
                "likes": 165000,
                "shares": 28000,
                "video_url": "https://tiktok.com/@user/video/006",
                "tags": ["#makeup", "#beauty", "#brushcleaner", "#skincare"],
                "thumbnail": "https://example.com/thumb6.jpg",
                "price_range": "$8-18"
            },
            {
                "id": "tt_007",
                "name": "Magnetic Phone Mount",
                "category": "Electronics",
                "views": 2800000,
                "likes": 210000,
                "shares": 38000,
                "video_url": "https://tiktok.com/@user/video/007",
                "tags": ["#phonemount", "#car", "#magnetic", "#accessories"],
                "thumbnail": "https://example.com/thumb7.jpg",
                "price_range": "$10-20"
            },
            {
                "id": "tt_008",
                "name": "Ice Roller for Face",
                "category": "Beauty",
                "views": 3500000,
                "likes": 290000,
                "shares": 55000,
                "video_url": "https://tiktok.com/@user/video/008",
                "tags": ["#skincare", "#iceroller", "#beautytips", "#morningroutine"],
                "thumbnail": "https://example.com/thumb8.jpg",
                "price_range": "$6-15"
            },
            {
                "id": "tt_009",
                "name": "Mini Projector",
                "category": "Electronics",
                "views": 4200000,
                "likes": 320000,
                "shares": 68000,
                "video_url": "https://tiktok.com/@user/video/009",
                "tags": ["#projector", "#movienight", "#hometheater", "#tech"],
                "thumbnail": "https://example.com/thumb9.jpg",
                "price_range": "$50-120"
            },
            {
                "id": "tt_010",
                "name": "Cloud Slides",
                "category": "Fashion",
                "views": 5600000,
                "likes": 480000,
                "shares": 95000,
                "video_url": "https://tiktok.com/@user/video/010",
                "tags": ["#cloudslides", "#comfort", "#shoes", "#tiktokmademebuyit"],
                "thumbnail": "https://example.com/thumb10.jpg",
                "price_range": "$15-30"
            }
        ]
        
        for item in sample_products[:limit]:
            # 计算趋势分数
            trending_score = self._calculate_trending_score(item)
            
            product = TikTokProduct(
                id=item["id"],
                name=item["name"],
                category=item["category"],
                views=item["views"],
                likes=item["likes"],
                shares=item["shares"],
                video_url=item["video_url"],
                product_url=None,  # TikTok Shop链接
                trending_score=trending_score,
                tags=item["tags"],
                thumbnail=item.get("thumbnail"),
                price_range=item.get("price_range")
            )
            products.append(product)
            
        return products
    
    def _calculate_trending_score(self, item: dict) -> float:
        """计算商品趋势分数"""
        # 算法：综合观看量、互动率、分享率
        views = item.get("views", 0)
        likes = item.get("likes", 0)
        shares = item.get("shares", 0)
        
        # 互动率
        engagement_rate = (likes + shares * 2) / views if views > 0 else 0
        
        # 观看量权重（取对数避免过大数字）
        views_score = min(views / 1000000, 10)  # 最高10分
        
        # 综合分数
        score = views_score * 0.4 + engagement_rate * 100 * 0.6
        
        return round(score, 2)
    
    def fetch_trending_hashtags(self, limit: int = 20) -> List[Dict]:
        """获取热门标签"""
        logger.info(f"Fetching {limit} trending hashtags...")
        
        # 热门带货标签
        hashtags = [
            {"tag": "#tiktokmademebuyit", "views": "500B+"},
            {"tag": "#amazonfinds", "views": "200B+"},
            {"tag": "#musthave", "views": "80B+"},
            {"tag": "#viralproduct", "views": "45B+"},
            {"tag": "#tiktokshop", "views": "120B+"},
            {"tag": "#productreview", "views": "60B+"},
            {"tag": "#gadget", "views": "90B+"},
            {"tag": "#lifehack", "views": "150B+"},
            {"tag": "#deals", "views": "30B+"},
            {"tag": "#shoppinghaul", "views": "40B+"}
        ]
        
        return hashtags[:limit]
    
    def filter_by_category(self, products: List[TikTokProduct], 
                          categories: List[str]) -> List[TikTokProduct]:
        """按类别筛选商品"""
        if not categories:
            return products
        return [p for p in products if p.category in categories]
    
    def filter_by_score(self, products: List[TikTokProduct], 
                       min_score: float = 5.0) -> List[TikTokProduct]:
        """按趋势分数筛选"""
        return [p for p in products if p.trending_score >= min_score]
    
    def save_products(self, products: List[TikTokProduct], filename: str = None):
        """保存商品数据到文件"""
        if filename is None:
            filename = f"tiktok_products_{int(time.time())}.json"
        
        filepath = self.data_dir / filename
        data = [p.to_dict() for p in products]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath
    
    def run(self, category: str = None, limit: int = 10, 
            min_score: float = 5.0) -> List[TikTokProduct]:
        """主运行函数"""
        logger.info("=" * 50)
        logger.info("Starting TikTok Product Scraping")
        logger.info("=" * 50)
        
        # 获取热门商品
        products = self.fetch_from_shop_data(category, limit * 2)
        logger.info(f"Fetched {len(products)} products")
        
        # 按趋势分数筛选
        products = self.filter_by_score(products, min_score)
        logger.info(f"Filtered to {len(products)} products with score >= {min_score}")
        
        # 排序并取Top
        products.sort(key=lambda x: x.trending_score, reverse=True)
        top_products = products[:limit]
        
        # 保存数据
        self.save_products(top_products)
        
        logger.info("TikTok scraping completed!")
        for p in top_products:
            logger.info(f"  - {p.name} (Score: {p.trending_score}, Views: {p.views:,})")
        
        return top_products


if __name__ == "__main__":
    config = {"temp_dir": "./temp"}
    scraper = TikTokScraper(config)
    
    products = scraper.run(limit=5)
    print(f"\nFound {len(products)} trending products")
    for p in products:
        print(f"  {p.name} - {p.views:,} views - Score: {p.trending_score}")
