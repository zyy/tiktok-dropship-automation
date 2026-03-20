"""
TikTok 无货源带货自动化系统 - 主程序
全自动流程: TikTok热门商品 → 亚马逊匹配 → AI生成视频 → TikTok发布
"""

import os
import schedule
from loguru import logger
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入各模块
from tiktok_scraper.scraper import TikTokScraper
from amazon_scraper.scraper import AmazonScraper
from ai_video_generator.generator import AIVideoGenerator
from tiktok_publisher.publisher import TikTokPublisher

logger.add(
    "logs/automation_{time}.log",
    rotation="500 MB",
    retention="7 days",
    level="INFO"
)

class DropshipAutomation:
    """无货源带货自动化主控制器"""
    
    def __init__(self):
        self.config = {
            # TikTok配置
            "tiktok_access_token": os.getenv("TIKTOK_ACCESS_TOKEN"),
            "tiktok_open_id": os.getenv("TIKTOK_OPEN_ID"),
            
            # OpenAI配置
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            
            # 目录配置
            "output_dir": os.getenv("OUTPUT_DIR", "./output"),
            "temp_dir": os.getenv("TEMP_DIR", "./temp"),
        }
        
        # 初始化各模块
        self.tiktok_scraper = TikTokScraper(self.config)
        self.amazon_scraper = AmazonScraper(self.config)
        self.ai_generator = AIVideoGenerator(self.config)
        self.tiktok_publisher = TikTokPublisher(self.config)
        
        # 创建目录
        os.makedirs(self.config["output_dir"], exist_ok=True)
        os.makedirs(self.config["temp_dir"], exist_ok=True)
        
    def run_full_pipeline(self) -> dict:
        """运行完整自动化流程"""
        logger.info("=" * 50)
        logger.info("Starting Dropship Automation Pipeline")
        logger.info(f"Time: {datetime.now()}")
        logger.info("=" * 50)
        
        results = {
            "tiktok_products": [],
            "amazon_products": [],
            "videos": [],
            "published": [],
            "errors": []
        }
        
        try:
            # Step 1: 抓取TikTok热门商品
            logger.info("[Step 1/5] Fetching TikTok trending products...")
            tiktok_products = self.tiktok_scraper.run()
            results["tiktok_products"] = tiktok_products
            logger.info(f"Found {len(tiktok_products)} trending products")
            
            # Step 2: 亚马逊商品匹配
            logger.info("[Step 2/5] Matching Amazon products...")
            for tiktok_product in tiktok_products:
                amazon_products = self.amazon_scraper.find_similar_products(
                    tiktok_product.name
                )
                results["amazon_products"].extend(amazon_products)
                
                if amazon_products:
                    # Step 3: 下载亚马逊图片
                    logger.info("[Step 3/5] Downloading product images...")
                    images = self.amazon_scraper.download_images(
                        amazon_products[0],
                        self.config["temp_dir"]
                    )
                    
                    # Step 4: AI生成视频
                    logger.info("[Step 4/5] Generating AI video...")
                    video = self.ai_generator.run(
                        product_name=tiktok_product.name,
                        product_images=images
                    )
                    results["videos"].append(video)
                    
                    # Step 5: 发布到TikTok
                    logger.info("[Step 5/5] Publishing to TikTok...")
                    publish_result = self.tiktok_publisher.run({
                        "video_path": video.video_path,
                        "title": video.title,
                        "description": video.description,
                        "hashtags": video.hashtags
                    })
                    results["published"].append(publish_result)
                    
            logger.info("=" * 50)
            logger.info("Pipeline completed!")
            logger.info(f"Published: {len(results['published'])} videos")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            results["errors"].append(str(e))
            
        return results
    
    def run_single_product(self, keyword: str) -> dict:
        """为单个商品运行完整流程"""
        logger.info(f"Processing single product: {keyword}")
        
        # 亚马逊搜索
        amazon_products = self.amazon_scraper.search_products(keyword)
        if not amazon_products:
            return {"error": "No Amazon products found"}
        
        # 下载图片
        images = self.amazon_scraper.download_images(
            amazon_products[0],
            self.config["temp_dir"]
        )
        
        # 生成视频
        video = self.ai_generator.run(keyword, images)
        
        # 发布
        result = self.tiktok_publisher.run({
            "video_path": video.video_path,
            "title": video.title,
            "description": video.description,
            "hashtags": video.hashtags
        })
        
        return {"video": video, "publish_result": result}


def main():
    """主入口"""
    logger.info("Initializing Dropship Automation System...")
    
    automation = DropshipAutomation()
    
    # 检查是否单次运行
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--single" and len(sys.argv) > 2:
            result = automation.run_single_product(sys.argv[2])
            print(result)
        return
    
    # 定时任务模式
    # 每天早上8点运行（美区时间）
    schedule.every().day.at("08:00").do(automation.run_full_pipeline)
    
    # 也可以设置为每6小时运行一次
    # schedule.every(6).hours.do(automation.run_full_pipeline)
    
    logger.info("Scheduler started. Running daily at 08:00")
    logger.info("Press Ctrl+C to exit")
    
    # 立即运行一次
    automation.run_full_pipeline()
    
    # 保持运行
    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
