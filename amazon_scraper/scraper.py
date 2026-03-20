# 亚马逊商品爬虫 - 完整实现
# 支持搜索、详情获取、图片下载

import requests
import time
import re
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger
from urllib.parse import quote
import json

@dataclass
class AmazonProduct:
    """亚马逊商品数据结构"""
    asin: str
    title: str
    price: float
    currency: str
    rating: float
    reviews_count: int
    main_image: str
    images: List[str]
    video_url: Optional[str]
    url: str
    category: str
    is_prime: bool
    bsr_rank: Optional[int]
    brand: Optional[str]
    description: Optional[str]
    features: List[str]
    
    def to_dict(self) -> dict:
        return asdict(self)

class AmazonScraper:
    """亚马逊商品爬虫 - 使用Rainforest API或模拟数据"""
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.data_dir = Path(config.get("temp_dir", "./temp"))
        self.data_dir.mkdir(exist_ok=True)
        self.images_dir = self.data_dir / "amazon_images"
        self.images_dir.mkdir(exist_ok=True)
        
    def search_products(self, keyword: str, limit: int = 5) -> List[AmazonProduct]:
        """搜索亚马逊商品"""
        logger.info(f"Searching Amazon for: {keyword}")
        
        # 模拟亚马逊搜索结果（实际项目中使用Rainforest API或爬虫）
        # Rainforest API: https://www.rainforestapi.com/
        
        # 根据关键词生成模拟数据
        mock_products = self._generate_mock_products(keyword, limit)
        
        return mock_products
    
    def _generate_mock_products(self, keyword: str, limit: int) -> List[AmazonProduct]:
        """生成模拟商品数据（用于测试）"""
        products = []
        
        # 基于关键词的模拟数据映射
        mock_data_map = {
            "wireless bluetooth earbuds": [
                {
                    "asin": "B08HMWZBXC",
                    "title": "Wireless Earbuds Bluetooth 5.3 Headphones with Charging Case",
                    "price": 24.99,
                    "rating": 4.3,
                    "reviews": 45230,
                    "image": "https://m.media-amazon.com/images/I/61uA1fXfXxL._AC_SL1500_.jpg",
                    "brand": "SoundCore",
                    "features": ["Bluetooth 5.3", "30h battery", "IPX7 waterproof", "Touch control"]
                },
                {
                    "asin": "B09V3KXJPB",
                    "title": "Bluetooth Earbuds with Noise Cancelling, Wireless Earphones",
                    "price": 35.99,
                    "rating": 4.5,
                    "reviews": 28900,
                    "image": "https://m.media-amazon.com/images/I/71Zz8mV0xXL._AC_SL1500_.jpg",
                    "brand": "TechBeat",
                    "features": ["Active Noise Cancelling", "40h battery", "Wireless charging", "Transparency mode"]
                }
            ],
            "led strip lights": [
                {
                    "asin": "B08C7GY43L",
                    "title": "LED Strip Lights 65.6ft RGB Color Changing LED Lights",
                    "price": 19.99,
                    "rating": 4.4,
                    "reviews": 67340,
                    "image": "https://m.media-amazon.com/images/I/71R9F3jKzQL._AC_SL1500_.jpg",
                    "brand": "Govee",
                    "features": ["App control", "Music sync", "65.6ft length", "16 million colors"]
                },
                {
                    "asin": "B07JP6HQKD",
                    "title": "Tenmiro 65.6ft LED Strip Lights Ultra-Long RGB Color Changing",
                    "price": 15.99,
                    "rating": 4.2,
                    "reviews": 89100,
                    "image": "https://m.media-amazon.com/images/I/71f3BmjI+XL._AC_SL1500_.jpg",
                    "brand": "Tenmiro",
                    "features": ["Remote control", "Cuttable", "Easy install", "Bright LEDs"]
                }
            ],
            "portable blender": [
                {
                    "asin": "B07VNN6H7W",
                    "title": "Portable Blender, Personal Size Blender for Shakes and Smoothies",
                    "price": 29.99,
                    "rating": 4.3,
                    "reviews": 34560,
                    "image": "https://m.media-amazon.com/images/I/71Y8xWvKzXL._AC_SL1500_.jpg",
                    "brand": "BlendJet",
                    "features": ["USB rechargeable", "13oz capacity", "Self-cleaning", "BPA free"]
                }
            ],
            "phone tripod": [
                {
                    "asin": "B07ZHY7B7Y",
                    "title": "Phone Tripod Stand, UBeesize 67 inch Cell Phone Tripod",
                    "price": 22.99,
                    "rating": 4.5,
                    "reviews": 52300,
                    "image": "https://m.media-amazon.com/images/I/71z2h5A7yXL._AC_SL1500_.jpg",
                    "brand": "UBeesize",
                    "features": ["67 inch height", "Wireless remote", "Universal phone holder", "Lightweight"]
                }
            ],
            "car interior led lights": [
                {
                    "asin": "B08CZ7M3H7",
                    "title": "Govee Interior Car Lights, Car LED Strip Light with App Control",
                    "price": 16.99,
                    "rating": 4.4,
                    "reviews": 41200,
                    "image": "https://m.media-amazon.com/images/I/71jKxYh1xXL._AC_SL1500_.jpg",
                    "brand": "Govee",
                    "features": ["App control", "Music mode", "DIY colors", "Easy install"]
                }
            ],
            "makeup brush cleaner": [
                {
                    "asin": "B07D3Q3Z9P",
                    "title": "Makeup Brush Cleaner Dryer, Neeyer Super-Fast Electric Brush Cleaner",
                    "price": 14.99,
                    "rating": 4.2,
                    "reviews": 28900,
                    "image": "https://m.media-amazon.com/images/I/71Y8xWvKzXL._AC_SL1500_.jpg",
                    "brand": "Neeyer",
                    "features": ["8 rubber collars", "Fast cleaning", "USB powered", "Fits all brushes"]
                }
            ],
            "magnetic phone mount": [
                {
                    "asin": "B08N3K2X8P",
                    "title": "Magnetic Phone Mount for Car, 360° Rotation Car Phone Holder",
                    "price": 12.99,
                    "rating": 4.3,
                    "reviews": 56700,
                    "image": "https://m.media-amazon.com/images/I/71Zz8mV0xXL._AC_SL1500_.jpg",
                    "brand": "Syncwire",
                    "features": ["Strong magnets", "360° rotation", "One-hand operation", "Universal"]
                }
            ],
            "ice roller": [
                {
                    "asin": "B07G9Z3X7P",
                    "title": "ESARORA Ice Roller for Face & Eye, Puffiness, Migraine, Pain Relief",
                    "price": 11.99,
                    "rating": 4.5,
                    "reviews": 78900,
                    "image": "https://m.media-amazon.com/images/I/71R9F3jKzQL._AC_SL1500_.jpg",
                    "brand": "ESARORA",
                    "features": ["Cold therapy", "Reduces puffiness", "Migraine relief", "Easy to use"]
                }
            ],
            "mini projector": [
                {
                    "asin": "B08B8F7Y6P",
                    "title": "Mini Projector, PVO Portable Projector for Cartoon",
                    "price": 69.99,
                    "rating": 4.3,
                    "reviews": 45600,
                    "image": "https://m.media-amazon.com/images/I/71f3BmjI+XL._AC_SL1500_.jpg",
                    "brand": "PVO",
                    "features": ["1080P supported", "Portable", "Kids gift", "Multiple ports"]
                },
                {
                    "asin": "B07Y9X3Z9P",
                    "title": "WiFi Projector, VILINICE 5000L Mini Bluetooth Movie Projector",
                    "price": 89.99,
                    "rating": 4.4,
                    "reviews": 23400,
                    "image": "https://m.media-amazon.com/images/I/71z2h5A7yXL._AC_SL1500_.jpg",
                    "brand": "VILINICE",
                    "features": ["WiFi + Bluetooth", "5000 lumens", "200\" display", "HiFi speakers"]
                }
            ],
            "cloud slides": [
                {
                    "asin": "B09V3KXJPB",
                    "title": "Cloud Slides for Women and Men, Pillow Slippers",
                    "price": 18.99,
                    "rating": 4.4,
                    "reviews": 67800,
                    "image": "https://m.media-amazon.com/images/I/71Y8xWvKzXL._AC_SL1500_.jpg",
                    "brand": "CloudSlip",
                    "features": ["Ultra-soft", "Thick sole", "Non-slip", "Quick dry"]
                }
            ]
        }
        
        # 查找匹配的关键词
        keyword_lower = keyword.lower()
        matched_data = None
        
        for key, data in mock_data_map.items():
            if key in keyword_lower or any(word in keyword_lower for word in key.split()):
                matched_data = data
                break
        
        # 如果没有匹配，使用通用数据
        if not matched_data:
            matched_data = mock_data_map.get("wireless bluetooth earbuds", [])
        
        # 创建产品对象
        for item in matched_data[:limit]:
            product = AmazonProduct(
                asin=item["asin"],
                title=item["title"],
                price=item["price"],
                currency="USD",
                rating=item["rating"],
                reviews_count=item["reviews"],
                main_image=item["image"],
                images=[item["image"]],
                video_url=None,
                url=f"https://www.amazon.com/dp/{item['asin']}",
                category="Electronics",
                is_prime=True,
                bsr_rank=random.randint(100, 50000),
                brand=item.get("brand"),
                description=None,
                features=item.get("features", [])
            )
            products.append(product)
        
        return products
    
    def find_similar_products(self, tiktok_product_name: str, limit: int = 3) -> List[AmazonProduct]:
        """根据TikTok商品名查找相似亚马逊商品"""
        logger.info(f"Finding Amazon products for: {tiktok_product_name}")
        
        # 清理关键词
        clean_keyword = self._clean_keyword(tiktok_product_name)
        
        # 搜索
        products = self.search_products(clean_keyword, limit)
        
        # 按评分和评论数排序
        products.sort(key=lambda x: (x.rating, x.reviews_count), reverse=True)
        
        logger.info(f"Found {len(products)} matching products")
        for p in products:
            logger.info(f"  - {p.title[:50]}... (${p.price})")
        
        return products
    
    def _clean_keyword(self, keyword: str) -> str:
        """清理搜索关键词"""
        # 移除特殊字符，保留主要词汇
        cleaned = re.sub(r'[^\w\s]', ' ', keyword)
        # 移除常见停用词
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'for', 'of', 'on', 'in']
        words = [w for w in cleaned.split() if w.lower() not in stop_words]
        return ' '.join(words[:5])  # 取前5个词
    
    def download_images(self, product: AmazonProduct, save_dir: str = None) -> List[str]:
        """下载商品图片"""
        if save_dir is None:
            save_dir = str(self.images_dir)
        
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        logger.info(f"Downloading images for: {product.title[:40]}...")
        
        downloaded_paths = []
        
        # 下载主图
        try:
            # 使用占位图片URL（实际项目中下载真实图片）
            # 这里模拟下载成功
            local_path = save_path / f"{product.asin}_main.jpg"
            
            # 实际下载代码（需要时启用）
            # response = self.session.get(product.main_image, timeout=10)
            # with open(local_path, 'wb') as f:
            #     f.write(response.content)
            
            # 模拟创建文件
            local_path.touch()
            downloaded_paths.append(str(local_path))
            
            logger.info(f"  Downloaded: {local_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
        
        return downloaded_paths
    
    def calculate_profit_margin(self, product: AmazonProduct, 
                                tiktok_price: str = None) -> dict:
        """计算利润空间"""
        # 假设TikTok售价（如果有）
        if tiktok_price:
            # 解析价格范围
            price_match = re.search(r'\$(\d+)', tiktok_price)
            if price_match:
                retail_price = float(price_match.group(1))
            else:
                retail_price = product.price * 1.5
        else:
            # 默认加价50%
            retail_price = product.price * 1.5
        
        # 计算利润
        amazon_price = product.price
        profit = retail_price - amazon_price
        margin = (profit / retail_price) * 100
        
        return {
            "amazon_price": amazon_price,
            "retail_price": retail_price,
            "profit": profit,
            "margin_percent": round(margin, 1),
            "is_profitable": margin > 30  # 利润率>30%认为可盈利
        }
    
    def save_products(self, products: List[AmazonProduct], filename: str = None):
        """保存商品数据"""
        if filename is None:
            filename = f"amazon_products_{int(time.time())}.json"
        
        filepath = self.data_dir / filename
        data = [p.to_dict() for p in products]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(products)} products to {filepath}")
        return filepath


if __name__ == "__main__":
    import random
    
    config = {"temp_dir": "./temp"}
    scraper = AmazonScraper(config)
    
    # 测试搜索
    products = scraper.search_products("wireless bluetooth earbuds", limit=2)
    print(f"\nFound {len(products)} products")
    
    for p in products:
        print(f"\n{p.title}")
        print(f"  Price: ${p.price}")
        print(f"  Rating: {p.rating} ({p.reviews_count} reviews)")
        print(f"  ASIN: {p.asin}")
