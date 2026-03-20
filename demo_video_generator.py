# AI视频生成器 - 演示版本（无需API费用）
# 使用本地生成脚本和示例音频

import os
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from loguru import logger

@dataclass
class VideoScript:
    """视频脚本"""
    hook: str
    problem: str
    solution: str
    cta: str
    duration: int
    voiceover_text: str
    
    def to_dict(self) -> dict:
        return asdict(self)

@dataclass
class GeneratedVideo:
    """生成的视频"""
    video_path: str
    thumbnail_path: str
    title: str
    description: str
    hashtags: List[str]
    script: VideoScript
    product_name: str
    duration: int
    
    def to_dict(self) -> dict:
        return {
            "video_path": self.video_path,
            "thumbnail_path": self.thumbnail_path,
            "title": self.title,
            "description": self.description,
            "hashtags": self.hashtags,
            "script": self.script.to_dict(),
            "product_name": self.product_name,
            "duration": self.duration
        }

class DemoVideoGenerator:
    """演示视频生成器 - 无需API费用"""
    
    def __init__(self, config: dict):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "./output"))
        self.videos_dir = self.output_dir / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        
        # 脚本模板库
        self.script_templates = {
            "hook": [
                "Stop scrolling! You need to see this {product}!",
                "I can't believe this {product} is only {price}!",
                "This {product} just changed my life!",
                "POV: You finally found the perfect {product}",
                "Wait for it... This {product} is INSANE!",
            ],
            "problem": [
                "Tired of overpriced products that don't work?",
                "Sick of wasting money on cheap knockoffs?",
                "Struggling to find a good quality option?",
                "Frustrated with products that break in a week?",
                "Done with overpaying for basic items?",
            ],
            "solution": [
                "This {product} is game-changing!",
                "Finally found the perfect solution - this {product}!",
                "This {product} solves everything!",
                "Say goodbye to problems with this {product}!",
                "Upgrade your life with this {product}!",
            ],
            "cta": [
                "Link in bio! Only {price} but selling out fast!",
                "Grab yours before they're gone! Link in bio!",
                "Don't miss out - link in bio! Limited stock! ⏰",
                "Get it now for {price}! Link in bio! 🛒",
                "Last chance! Link in bio! Only {price}!",
            ]
        }
        
    def generate_script(self, product_name: str, features: List[str], 
                       price: float = None) -> VideoScript:
        """生成本地脚本"""
        logger.info(f"Generating script for: {product_name}")
        
        price_text = f"${price:.2f}" if price else "under $30"
        
        # 随机选择模板
        hook = random.choice(self.script_templates["hook"]).format(
            product=product_name, price=price_text
        )
        problem = random.choice(self.script_templates["problem"])
        solution = random.choice(self.script_templates["solution"]).format(
            product=product_name
        )
        cta = random.choice(self.script_templates["cta"]).format(
            product=product_name, price=price_text
        )
        
        voiceover = f"{hook} {problem} {solution} {cta}"
        
        return VideoScript(
            hook=hook,
            problem=problem,
            solution=solution,
            cta=cta,
            duration=40,
            voiceover_text=voiceover
        )
    
    def generate_demo_video(self, product_name: str, script: VideoScript) -> str:
        """生成演示视频（使用MoviePy创建简单视频）"""
        logger.info("Generating demo video with MoviePy...")
        
        try:
            from moviepy import ColorClip, TextClip, CompositeVideoClip
            
            # 创建纯色背景视频
            duration = script.duration
            
            # 视频尺寸 (TikTok 9:16)
            width, height = 1080, 1920
            
            # 创建背景
            bg = ColorClip(size=(width, height), color=(20, 20, 40)).with_duration(duration)
            
            # 创建文字片段
            texts = [
                (script.hook, 0, 5, 80),
                (script.problem, 5, 10, 60),
                (script.solution, 15, 10, 70),
                (script.cta, 30, 10, 90),
            ]
            
            clips = [bg]
            
            for text, start, dur, fontsize in texts:
                try:
                    txt_clip = TextClip(
                        text=text,
                        font_size=fontsize,
                        color='white',
                        font='Arial',
                        size=(width-100, None),
                        method='caption'
                    ).with_duration(dur).with_start(start)
                    
                    # 居中
                    txt_clip = txt_clip.with_position('center')
                    clips.append(txt_clip)
                except Exception as e:
                    logger.warning(f"Failed to create text clip: {e}")
            
            # 合成视频
            if len(clips) > 1:
                video = CompositeVideoClip(clips)
            else:
                video = clips[0]
            
            # 添加背景音乐（如果有）
            # 这里可以添加免版权音乐
            
            # 导出
            output_path = self.videos_dir / f"demo_{int(time.time())}.mp4"
            video.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio=False,
                threads=4
            )
            
            video.close()
            
            logger.info(f"Demo video saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
            # 创建占位文件
            output_path = self.videos_dir / f"demo_{int(time.time())}.mp4"
            output_path.touch()
            return str(output_path)
    
    def generate_thumbnail(self, product_name: str, script: VideoScript) -> str:
        """生成缩略图"""
        logger.info("Generating thumbnail...")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建图片 (TikTok缩略图尺寸)
            width, height = 1080, 1920
            img = Image.new('RGB', (width, height), color=(255, 100, 50))
            draw = ImageDraw.Draw(img)
            
            # 添加文字
            title = script.hook[:50] + "..." if len(script.hook) > 50 else script.hook
            
            # 使用默认字体
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
            except:
                font = ImageFont.load_default()
            
            # 计算文字位置（居中）
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height // 3
            
            # 绘制文字（带阴影）
            draw.text((x+4, y+4), title, font=font, fill=(0, 0, 0))
            draw.text((x, y), title, font=font, fill=(255, 255, 255))
            
            # 保存
            thumb_path = self.videos_dir / f"thumb_{int(time.time())}.jpg"
            img.save(thumb_path, quality=90)
            
            logger.info(f"Thumbnail saved: {thumb_path}")
            return str(thumb_path)
            
        except Exception as e:
            logger.error(f"Failed to generate thumbnail: {e}")
            thumb_path = self.videos_dir / f"thumb_{int(time.time())}.jpg"
            thumb_path.touch()
            return str(thumb_path)
    
    def _generate_hashtags(self, product_name: str) -> List[str]:
        """生成标签"""
        base_tags = ["#tiktokmademebuyit", "#amazonfinds", "#musthave", "#viral"]
        
        # 根据产品名添加相关标签
        product_words = product_name.lower().split()
        for word in product_words[:3]:
            if len(word) > 3:
                base_tags.append(f"#{word}")
        
        return base_tags[:8]
    
    def run(self, product_name: str, product_images: List[str] = None,
            product_price: float = None, product_features: List[str] = None) -> GeneratedVideo:
        """完整流程"""
        logger.info("=" * 50)
        logger.info("Starting Demo Video Generation")
        logger.info("=" * 50)
        
        if product_features is None:
            product_features = ["high quality", "affordable"]
        
        # 生成脚本
        script = self.generate_script(product_name, product_features, product_price)
        logger.info(f"Script: {script.hook}")
        
        # 生成视频
        video_path = self.generate_demo_video(product_name, script)
        
        # 生成缩略图
        thumbnail_path = self.generate_thumbnail(product_name, script)
        
        # 生成标题和描述
        title = f"{script.hook} 🔥 #shorts"
        description = f"{script.problem}\n\n{script.solution}\n\n{script.cta}\n\n#tiktokmademebuyit #amazonfinds #musthave"
        hashtags = self._generate_hashtags(product_name)
        
        logger.info("Demo video generation completed!")
        
        return GeneratedVideo(
            video_path=video_path,
            thumbnail_path=thumbnail_path,
            title=title,
            description=description,
            hashtags=hashtags,
            script=script,
            product_name=product_name,
            duration=script.duration
        )


if __name__ == "__main__":
    config = {"output_dir": "./output"}
    generator = DemoVideoGenerator(config)
    
    video = generator.run(
        product_name="Wireless Bluetooth Earbuds",
        product_price=24.99,
        product_features=["Bluetooth 5.3", "30h battery", "IPX7 waterproof"]
    )
    
    print(f"\n✅ 视频生成完成!")
    print(f"视频文件: {video.video_path}")
    print(f"缩略图: {video.thumbnail_path}")
    print(f"标题: {video.title}")
