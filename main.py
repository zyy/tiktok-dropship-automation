"""
TikTok 无货源带货自动化系统 - 完整实现
全自动流程: TikTok热门商品 → 亚马逊匹配 → AI生成视频 → TikTok发布
"""

import os
import sys
import json
import time
import schedule
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

# 加载环境变量
load_dotenv()

# 导入各模块
from tiktok_scraper.scraper import TikTokScraper, TikTokProduct
from amazon_scraper.scraper import AmazonScraper, AmazonProduct
from ai_video_generator.generator import AIVideoGenerator, GeneratedVideo
from tiktok_publisher.publisher import TikTokPublisher, PublishResult

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/automation_{time:YYYYMMDD}.log",
    rotation="10 MB",
    retention="30 days",
    level="DEBUG"
)

class DropshipAutomation:
    """无货源带货自动化主控制器"""
    
    def __init__(self):
        self.config = {
            # API Keys
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "rainforest_api_key": os.getenv("RAINFOREST_API_KEY"),
            "tiktok_data_api_key": os.getenv("TIKTOK_DATA_API_KEY"),
            "tiktok_data_api_url": os.getenv("TIKTOK_DATA_API_URL"),
            
            # TikTok配置
            "tiktok_access_token": os.getenv("TIKTOK_ACCESS_TOKEN"),
            "tiktok_open_id": os.getenv("TIKTOK_OPEN_ID"),
            "tiktok_username": os.getenv("TIKTOK_USERNAME"),
            "tiktok_password": os.getenv("TIKTOK_PASSWORD"),
            
            # 目录配置
            "output_dir": os.getenv("OUTPUT_DIR", "./output"),
            "temp_dir": os.getenv("TEMP_DIR", "./temp"),
            "logs_dir": "./logs",
            
            # 自动化配置
            "max_products_per_run": int(os.getenv("MAX_PRODUCTS_PER_RUN", "3")),
            "min_profit_margin": float(os.getenv("MIN_PROFIT_MARGIN", "30")),
            "schedule_interval_hours": int(os.getenv("SCHEDULE_INTERVAL_HOURS", "6")),
        }
        
        # 检查API配置状态
        self._check_api_status()
        
        # 初始化各模块
        self.tiktok_scraper = TikTokScraper(self.config)
        self.amazon_scraper = AmazonScraper(self.config)
        self.ai_generator = AIVideoGenerator(self.config)
        self.tiktok_publisher = TikTokPublisher(self.config)
        
        # 创建目录
        for dir_path in [self.config["output_dir"], self.config["temp_dir"], self.config["logs_dir"]]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            "runs": 0,
            "products_found": 0,
            "videos_generated": 0,
            "videos_published": 0,
            "errors": []
        }
    
    def _check_api_status(self):
        """检查API配置状态"""
        logger.info("=" * 60)
        logger.info("API Configuration Status")
        logger.info("=" * 60)
        
        apis = {
            "OpenAI (AI Script)": bool(self.config["openai_api_key"]),
            "Rainforest (Amazon)": bool(self.config["rainforest_api_key"]),
            "TikTok Data": bool(self.config["tiktok_data_api_key"]),
            "TikTok API": bool(self.config["tiktok_access_token"]),
        }
        
        for name, configured in apis.items():
            status = "✅ Configured" if configured else "⚠️  Not configured (using mock)"
            logger.info(f"  {name}: {status}")
        
        logger.info("=" * 60)
    
    def run_single_product(self, keyword: str = None) -> dict:
        """为单个商品运行完整流程"""
        logger.info("=" * 60)
        logger.info("Running Single Product Pipeline")
        logger.info("=" * 60)
        
        result = {
            "success": False,
            "tiktok_product": None,
            "amazon_product": None,
            "video": None,
            "publish_result": None,
            "error": None
        }
        
        try:
            # Step 1: 获取TikTok热门商品
            if keyword:
                logger.info(f"Using provided keyword: {keyword}")
                tiktok_product = TikTokProduct(
                    id=f"manual_{int(time.time())}",
                    name=keyword,
                    category="General",
                    views=1000000,
                    likes=50000,
                    shares=5000,
                    video_url="",
                    product_url=None,
                    trending_score=8.5,
                    tags=["#viral", "#trending"],
                    thumbnail=None,
                    price_range="$15-30"
                )
            else:
                logger.info("Fetching trending TikTok products...")
                tiktok_products = self.tiktok_scraper.run(limit=1)
                if not tiktok_products:
                    raise Exception("No trending products found")
                tiktok_product = tiktok_products[0]
            
            result["tiktok_product"] = tiktok_product.to_dict()
            logger.info(f"Selected product: {tiktok_product.name}")
            
            # Step 2: 亚马逊商品匹配
            logger.info("Matching Amazon products...")
            amazon_products = self.amazon_scraper.find_similar_products(
                tiktok_product.name, limit=3
            )
            
            if not amazon_products:
                raise Exception("No matching Amazon products found")
            
            amazon_product = amazon_products[0]
            result["amazon_product"] = amazon_product.to_dict()
            logger.info(f"Found Amazon product: {amazon_product.title[:50]}...")
            
            # 计算利润
            profit_info = self.amazon_scraper.calculate_profit_margin(
                amazon_product, tiktok_product.price_range
            )
            logger.info(f"Profit margin: {profit_info['margin_percent']}% (${profit_info['profit']:.2f})")
            
            # Step 3: 下载商品图片
            logger.info("Downloading product images...")
            images = self.amazon_scraper.download_images(amazon_product)
            logger.info(f"Downloaded {len(images)} images")
            
            # Step 4: AI生成视频
            logger.info("Generating AI video...")
            video = self.ai_generator.run(
                product_name=tiktok_product.name,
                product_images=images,
                product_price=amazon_product.price,
                product_features=amazon_product.features
            )
            
            result["video"] = video.to_dict()
            logger.info(f"Video generated: {video.title}")
            logger.info(f"Script: {video.script.voiceover_text[:80]}...")
            
            # Step 5: 发布到TikTok
            logger.info("Publishing to TikTok...")
            publish_result = self.tiktok_publisher.upload_video(
                video_path=video.video_path,
                title=video.title,
                description=video.description,
                hashtags=video.hashtags
            )
            
            result["publish_result"] = publish_result.to_dict()
            result["success"] = publish_result.success
            
            if publish_result.success:
                logger.info(f"✅ Published successfully!")
                logger.info(f"   Video ID: {publish_result.video_id}")
                logger.info(f"   URL: {publish_result.url}")
            else:
                logger.error(f"❌ Publish failed: {publish_result.error}")
            
            self._save_run_result(result, tiktok_product.id)
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            result["error"] = str(e)
            self.stats["errors"].append(str(e))
        
        return result
    
    def run_full_pipeline(self, max_products: int = None) -> dict:
        """运行完整自动化流程"""
        if max_products is None:
            max_products = self.config["max_products_per_run"]
        
        logger.info("=" * 60)
        logger.info("Starting Full Automation Pipeline")
        logger.info(f"Time: {datetime.now()}")
        logger.info("=" * 60)
        
        self.stats["runs"] += 1
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "products_processed": [],
            "summary": {"total": 0, "successful": 0, "failed": 0}
        }
        
        try:
            # Step 1: 抓取TikTok热门商品
            logger.info("[Step 1/5] Fetching TikTok trending products...")
            tiktok_products = self.tiktok_scraper.run(limit=max_products)
            
            if not tiktok_products:
                logger.warning("No trending products found")
                return results
            
            self.stats["products_found"] += len(tiktok_products)
            logger.info(f"Found {len(tiktok_products)} trending products")
            
            # 处理每个商品
            for idx, tiktok_product in enumerate(tiktok_products, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"Processing product {idx}/{len(tiktok_products)}: {tiktok_product.name}")
                logger.info(f"{'='*60}")
                
                try:
                    # Step 2: 亚马逊商品匹配
                    logger.info("[Step 2/5] Matching Amazon products...")
                    amazon_products = self.amazon_scraper.find_similar_products(
                        tiktok_product.name, limit=3
                    )
                    
                    if not amazon_products:
                        logger.warning("No matching Amazon products, skipping...")
                        continue
                    
                    amazon_product = amazon_products[0]
                    
                    # 检查利润率
                    profit_info = self.amazon_scraper.calculate_profit_margin(
                        amazon_product, tiktok_product.price_range
                    )
                    
                    if not profit_info["is_profitable"]:
                        logger.warning(f"Low profit margin ({profit_info['margin_percent']}%), skipping...")
                        continue
                    
                    logger.info(f"Amazon product: {amazon_product.title[:50]}...")
                    logger.info(f"Profit: ${profit_info['profit']:.2f} ({profit_info['margin_percent']}%)")
                    
                    # Step 3: 下载商品图片
                    logger.info("[Step 3/5] Downloading product images...")
                    images = self.amazon_scraper.download_images(amazon_product)
                    
                    # Step 4: AI生成视频
                    logger.info("[Step 4/5] Generating AI video...")
                    video = self.ai_generator.run(
                        product_name=tiktok_product.name,
                        product_images=images,
                        product_price=amazon_product.price,
                        product_features=amazon_product.features
                    )
                    
                    self.stats["videos_generated"] += 1
                    
                    # Step 5: 发布到TikTok
                    logger.info("[Step 5/5] Publishing to TikTok...")
                    publish_result = self.tiktok_publisher.upload_video(
                        video_path=video.video_path,
                        title=video.title,
                        description=video.description,
                        hashtags=video.hashtags
                    )
                    
                    if publish_result.success:
                        self.stats["videos_published"] += 1
                        results["summary"]["successful"] += 1
                        logger.info(f"✅ Successfully published: {publish_result.url}")
                    else:
                        results["summary"]["failed"] += 1
                        logger.error(f"❌ Publish failed: {publish_result.error}")
                    
                    results["products_processed"].append({
                        "tiktok_product": tiktok_product.name,
                        "amazon_product": amazon_product.title,
                        "video_title": video.title,
                        "published": publish_result.success,
                        "video_id": publish_result.video_id
                    })
                    
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing {tiktok_product.name}: {e}")
                    results["summary"]["failed"] += 1
                    continue
            
            results["summary"]["total"] = len(tiktok_products)
            self._save_pipeline_report(results)
            
            logger.info("=" * 60)
            logger.info("Pipeline completed!")
            logger.info(f"  Total: {results['summary']['total']}")
            logger.info(f"  Successful: {results['summary']['successful']}")
            logger.info(f"  Failed: {results['summary']['failed']}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            results["error"] = str(e)
        
        return results
    
    def _save_run_result(self, result: dict, product_id: str):
        """保存单次运行结果"""
        filename = f"run_{product_id}_{int(time.time())}.json"
        filepath = Path(self.config["output_dir"]) / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"Result saved to: {filepath}")
    
    def _save_pipeline_report(self, results: dict):
        """保存批量运行报告"""
        filename = f"pipeline_report_{int(time.time())}.json"
        filepath = Path(self.config["output_dir"]) / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Pipeline report saved to: {filepath}")
    
    def print_stats(self):
        """打印运行统计"""
        logger.info("=" * 60)
        logger.info("Automation Statistics")
        logger.info("=" * 60)
        logger.info(f"Total runs: {self.stats['runs']}")
        logger.info(f"Products found: {self.stats['products_found']}")
        logger.info(f"Videos generated: {self.stats['videos_generated']}")
        logger.info(f"Videos published: {self.stats['videos_published']}")
        logger.info(f"Errors: {len(self.stats['errors'])}")


def main():
    """主入口"""
    logger.info("=" * 60)
    logger.info("TikTok Dropship Automation System")
    logger.info("=" * 60)
    
    automation = DropshipAutomation()
    
    import argparse
    parser = argparse.ArgumentParser(description='TikTok Dropship Automation')
    parser.add_argument('--single', type=str, help='Process single product by keyword')
    parser.add_argument('--batch', type=int, help='Number of products to process')
    parser.add_argument('--schedule', action='store_true', help='Run in scheduled mode')
    parser.add_argument('--interval', type=int, help='Hours between runs')
    args = parser.parse_args()
    
    if args.single:
        result = automation.run_single_product(args.single)
        print("\n" + "=" * 60)
        print("RESULT:")
        print(json.dumps(result, indent=2))
        
    elif args.schedule:
        interval = args.interval or automation.config["schedule_interval_hours"]
        logger.info(f"Schedule mode: running every {interval} hours")
        
        schedule.every(interval).hours.do(automation.run_full_pipeline)
        automation.run_full_pipeline()
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped.")
            automation.print_stats()
    else:
        result = automation.run_full_pipeline(args.batch)
        print("\n" + "=" * 60)
        print("PIPELINE RESULT:")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
