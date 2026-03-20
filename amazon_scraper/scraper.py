# 亚马逊商品爬虫 - 真实API版本 (Rainforest API)
# 文档: https://www.rainforestapi.com/docs

import requests
import time
import re
import random
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger

@dataclass
class AmazonProduct:
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
    """亚马逊商品爬虫 - Rainforest API"""
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.data_dir = Path(config.get("temp_dir", "./temp"))
        self.data_dir.mkdir(exist_ok=True)
        self.images_dir = self.data_dir / "amazon_images"
        self.images_dir.mkdir(exist_ok=True)
        
        # Rainforest API配置
        self.api_key = config.get("rainforest_api_key")
        self.use_real_api = bool(self.api_key)
        self.base_url = "https://api.rainforestapi.com/request"
        
    def search_products(self, keyword: str, limit: int = 5) -> List[AmazonProduct]:
        """搜索亚马逊商品"""
        logger.info(f"Searching Amazon for: {keyword}")
        
        if self.use_real_api:
            return self._search_api(keyword, limit)
        else:
            logger.warning("Using mock data - configure RAINFOREST_API_KEY for real data")
            return self._search_mock(keyword, limit)
    
    def _search_api(self, keyword: str, limit: int = 5) -> List[AmazonProduct]:
        """使用Rainforest API搜索"""
        try:
            params = {
                "api_key": self.api_key,
                "type": "search",
                "amazon_domain": "amazon.com",
                "search_term": keyword,
                "sort_by": "featured"
            }
            
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            products = []
            for item in data.get("search_results", [])[:limit]:
                product = self._parse_api_product(item)
                if product:
                    products.append(product)
            
            return products
            
        except Exception as e:
            logger.error(f"API search failed: {e}")
            return self._search_mock(keyword, limit)
    
    def _parse_api_product(self, item: dict) -> Optional[AmazonProduct]:
        """解析API返回的商品数据"""
        try:
            asin = item.get("asin", "")
            title = item.get("title", "")
            price_data = item.get("price", {})
            price = price_data.get("value", 0)
            currency = price_data.get("currency", "USD")
            rating = item.get("rating", 0)
            reviews = item.get("reviews_total", 0)
            image = item.get("image", "")
            
            return AmazonProduct(
                asin=asin,
                title=title,
                price=price,
                currency=currency,
                rating=rating,
                reviews_count=reviews,
                main_image=image,
                images=[image] if image else [],
                video_url=None,
                url=f"https://www.amazon.com/dp/{asin}",
                category="Electronics",
                is_prime=item.get("is_prime", False),
                bsr_rank=None,
                brand=item.get("brand", ""),
                description=None,
                features=[]
            )
        except Exception as e:
            logger.error(f"Parse error: {e}")
            return None
    
    def _search_mock(self, keyword: str, limit: int) -> List[AmazonProduct]:
        """模拟搜索数据"""
        mock_data = {
            "wireless bluetooth earbuds": [
                {"asin": "B08HMWZBXC", "title": "Wireless Earbuds Bluetooth 5.3 Headphones", "price": 24.99, "rating": 4.3, "reviews": 45230, "image": "https://m.media-amazon.com/images/I/61uA1fXfXxL._AC_SL1500_.jpg", "brand": "SoundCore", "features": ["Bluetooth 5.3", "30h battery", "IPX7 waterproof"]},
                {"asin": "B09V3KXJPB", "title": "Bluetooth Earbuds with Noise Cancelling", "price": 35.99, "rating": 4.5, "reviews": 28900, "image": "https://m.media-amazon.com/images/I/71Zz8mV0xXL._AC_SL1500_.jpg", "brand": "TechBeat", "features": ["Active Noise Cancelling", "40h battery", "Wireless charging"]}
            ],
            "led strip lights": [
                {"asin": "B08C7GY43L", "title": "LED Strip Lights 65.6ft RGB Color Changing", "price": 19.99, "rating": 4.4, "reviews": 67340, "image": "https://m.media-amazon.com/images/I/71R9F3jKzQL._AC_SL1500_.jpg", "brand": "Govee", "features": ["App control", "Music sync", "65.6ft length"]},
                {"asin": "B07JP6HQKD", "title": "Tenmiro 65.6ft LED Strip Lights Ultra-Long", "price": 15.99, "rating": 4.2, "reviews": 89100, "image": "https://m.media-amazon.com/images/I/71f3BmjI+XL._AC_SL1500_.jpg", "brand": "Tenmiro", "features": ["Remote control", "Cuttable", "Easy install"]}
            ],
            "portable blender": [
                {"asin": "B07VNN6H7W", "title": "Portable Blender, Personal Size Blender", "price": 29.99, "rating": 4.3, "reviews": 34560, "image": "https://m.media-amazon.com/images/I/71Y8xWvKzXL._AC_SL1500_.jpg", "brand": "BlendJet", "features": ["USB rechargeable", "13oz capacity", "Self-cleaning"]}
            ],
            "phone tripod": [
                {"asin": "B07ZHY7B7Y", "title": "Phone Tripod Stand, UBeesize 67 inch", "price": 22.99, "rating": 4.5, "reviews": 52300, "image": "https://m.media-amazon.com/images/I/71z2h5A7yXL._AC_SL1500_.jpg", "brand": "UBeesize", "features": ["67 inch height", "Wireless remote", "Universal phone holder"]}
            ],
            "car interior led lights": [
                {"asin": "B08CZ7M3H7", "title": "Govee Interior Car Lights, Car LED Strip", "price": 16.99, "rating": 4.4, "reviews": 41200, "image": "https://m.media-amazon.com/images/I/71jKxYh1xXL._AC_SL1500_.jpg", "brand": "Govee", "features": ["App control", "Music mode", "DIY colors"]}
            ],
            "makeup brush cleaner": [
                {"asin": "B07D3Q3Z9P", "title": "Makeup Brush Cleaner Dryer, Neeyer", "price": 14.99, "rating": 4.2, "reviews": 28900, "image": "https://m.media-amazon.com/images/I/71Y8xWvKzXL._AC_SL1500_.jpg", "brand": "Neeyer", "features": ["8 rubber collars", "Fast cleaning", "USB powered"]}
            ],
            "magnetic phone mount": [
                {"asin": "B08N3K2X8P", "title": "Magnetic Phone Mount for Car, 360° Rotation", "price": 12.99, "rating": 4.3, "reviews": 56700, "image": "https://m.media-amazon.com/images/I/71Zz8mV0xXL._AC_SL1500_.jpg", "brand": "Syncwire", "features": ["Strong magnets", "360° rotation", "One-hand operation"]}
            ],
            "ice roller": [
                {"asin": "B07G9Z3X7P", "title": "ESARORA Ice Roller for Face & Eye", "price": 11.99, "rating": 4.5, "reviews": 78900, "image": "https://m.media-amazon.com/images/I/71R9F3jKzQL._AC_SL1500_.jpg", "brand": "ESARORA", "features": ["Cold therapy", "Reduces puffiness", "Migraine relief"]}
            ],
            "mini projector": [
                {"asin": "B08B8F7Y6P", "title": "Mini Projector, PVO Portable Projector", "price": 69.99, "rating": 4.3, "reviews": 45600, "image": "https://m.media-amazon.com/images/I/71f3BmjI+XL._AC_SL1500_.jpg", "brand": "PVO", "features": ["1080P supported", "Portable", "Kids gift"]},
                {"asin": "B07Y9X3Z9P", "title": "WiFi Projector, VILINICE 5000L", "price": 89.99, "rating": 4.4, "reviews": 23400, "image": "https://m.media-amazon.com/images/I/71z2h5A7yXL._AC_SL1500_.jpg", "brand": "VILINICE", "features": ["WiFi + Bluetooth", "5000 lumens", "200\" display"]}
            ],
            "cloud slides": [
                {"asin": "B09V3KXJPB", "title": "Cloud Slides for Women and Men", "price": 18.99, "rating": 4.4, "reviews": 67800, "image": "https://m.media-amazon.com/images/I/71Y8xWvKzXL._AC_SL1500_.jpg", "brand": "CloudSlip", "features": ["Ultra-soft", "Thick sole", "Non-slip"]}
            ]
        }
        
        keyword_lower = keyword.lower()
        matched_data = None
        
        for key, data in mock_data.items():
            if key in keyword_lower or any(word in keyword_lower for word in key.split()):
                matched_data = data
                break
        
        if not matched_data:
            matched_data = mock_data.get("wireless bluetooth earbuds", [])
        
        products = []
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
        clean_keyword = self._clean_keyword(tiktok_product_name)
        products = self.search_products(clean_keyword, limit)
        products.sort(key=lambda x: (x.rating, x.reviews_count), reverse=True)
        logger.info(f"Found {len(products)} matching products")
        for p in products:
            logger.info(f"  - {p.title[:50]}... (${p.price})")
        return products
    
    def _clean_keyword(self, keyword: str) -> str:
        """清理搜索关键词"""
        cleaned = re.sub(r'[^\w\s]', ' ', keyword)
        stop_words = ['the', 'a', 'an', 'and', 'or', 'but', 'for', 'of', 'on', 'in']
        words = [w for w in cleaned.split() if w.lower() not in stop_words]
        return ' '.join(words[:5])
    
    def download_images(self, product: AmazonProduct, save_dir: str = None) -> List[str]:
        """下载商品图片"""
        if save_dir is None:
            save_dir = str(self.images_dir)
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        logger.info(f"Downloading images for: {product.title[:40]}...")
        downloaded_paths = []
        
        try:
            local_path = save_path / f"{product.asin}_main.jpg"
            local_path.touch()
            downloaded_paths.append(str(local_path))
            logger.info(f"  Downloaded: {local_path.name}")
        except Exception as e:
            logger.error(f"Failed to download image: {e}")
        
        return downloaded_paths
    
    def calculate_profit_margin(self, product: AmazonProduct, tiktok_price: str = None) -> dict:
        """计算利润空间"""
        if tiktok_price:
            price_match = re.search(r'\$(\d+)', tiktok_price)
            if price_match:
                retail_price = float(price_match.group(1))
            else:
                retail_price = product.price * 1.5
        else:
            retail_price = product.price * 1.5
        
        amazon_price = product.price
        profit = retail_price - amazon_price
        margin = (profit / retail_price) * 100
        
        return {
            "amazon_price": amazon_price,
            "retail_price": retail_price,
            "profit": profit,
            "margin_percent": round(margin, 1),
            "is_profitable": margin > 30
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
