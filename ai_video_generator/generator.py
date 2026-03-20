# AI视频生成器 - 完整实现
# 生成带货脚本、配音、合成视频

import os
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from loguru import logger

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not installed, using mock mode")

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

class AIVideoGenerator:
    """AI视频生成器 - 使用OpenAI API"""
    
    def __init__(self, config: dict):
        self.config = config
        self.api_key = config.get("openai_api_key")
        self.mock_mode = not OPENAI_AVAILABLE or not self.api_key
        
        if not self.mock_mode:
            openai.api_key = self.api_key
        else:
            logger.warning("Running in MOCK mode - no actual AI generation")
        
        self.output_dir = Path(config.get("output_dir", "./output"))
        self.videos_dir = self.output_dir / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_script(self, product_name: str, features: List[str], 
                       price: float = None) -> VideoScript:
        """生成带货脚本"""
        logger.info(f"Generating script for: {product_name}")
        
        if self.mock_mode:
            # 模拟脚本生成
            return self._generate_mock_script(product_name, features, price)
        
        # 使用GPT-4生成脚本
        features_text = ", ".join(features) if features else "high quality, affordable price"
        price_text = f"priced at ${price}" if price else "affordable"
        
        prompt = f"""Create a viral TikTok dropshipping video script for this product:

Product: {product_name}
Features: {features_text}
Price: {price_text}

Requirements:
- Hook: Attention-grabbing first 3 seconds
- Problem: Relatable pain point
- Solution: How this product solves it
- CTA: Strong call-to-action with urgency
- Duration: 30-45 seconds
- Tone: Excited, authentic, FOMO-inducing

Output format (JSON):
{{
    "hook": "...",
    "problem": "...",
    "solution": "...",
    "cta": "...",
    "duration": 40,
    "voiceover_text": "full script for voiceover"
}}"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert TikTok dropshipping content creator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            # 解析JSON
            script_data = json.loads(content)
            
            return VideoScript(
                hook=script_data["hook"],
                problem=script_data["problem"],
                solution=script_data["solution"],
                cta=script_data["cta"],
                duration=script_data.get("duration", 40),
                voiceover_text=script_data["voiceover_text"]
            )
            
        except Exception as e:
            logger.error(f"Failed to generate script with AI: {e}")
            return self._generate_mock_script(product_name, features, price)
    
    def _generate_mock_script(self, product_name: str, features: List[str], 
                             price: float = None) -> VideoScript:
        """生成模拟脚本"""
        price_text = f"${price:.2f}" if price else "under $30"
        
        hooks = [
            f"Stop scrolling! You need to see this {product_name}!",
            f"I can't believe this {product_name} is only {price_text}!",
            f"This {product_name} just changed my life!",
            f"POV: You finally found the perfect {product_name}",
        ]
        
        problems = [
            "Tired of overpriced products that don't work?",
            "Sick of wasting money on cheap knockoffs?",
            "Struggling to find a good quality option?",
        ]
        
        solutions = [
            f"This {product_name} is game-changing!",
            f"Finally found the perfect solution - this {product_name}!",
        ]
        
        ctas = [
            f"Link in bio! Only {price_text} but selling out fast!",
            "Grab yours before they're gone! Link in bio!",
            "Don't miss out - link in bio! Limited stock!",
        ]
        
        hook = random.choice(hooks)
        problem = random.choice(problems)
        solution = random.choice(solutions)
        cta = random.choice(ctas)
        
        voiceover = f"{hook} {problem} {solution} {cta}"
        
        return VideoScript(
            hook=hook,
            problem=problem,
            solution=solution,
            cta=cta,
            duration=40,
            voiceover_text=voiceover
        )
    
    def generate_voiceover(self, script: VideoScript, output_name: str = None) -> str:
        """生成配音"""
        logger.info("Generating voiceover...")
        
        if output_name is None:
            output_name = f"voiceover_{int(time.time())}.mp3"
        
        output_path = self.videos_dir / output_name
        
        if self.mock_mode:
            # 模拟生成配音文件
            output_path.touch()
            logger.info(f"Mock voiceover saved: {output_path}")
            return str(output_path)
        
        # 使用OpenAI TTS
        try:
            response = openai.audio.speech.create(
                model="tts-1",
                voice="alloy",  # alloy, echo, fable, onyx, nova, shimmer
                input=script.voiceover_text
            )
            
            response.stream_to_file(output_path)
            logger.info(f"Voiceover saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate voiceover: {e}")
            output_path.touch()
            return str(output_path)
    
    def generate_captions(self, script: VideoScript) -> List[Dict]:
        """生成字幕时间轴"""
        logger.info("Generating captions...")
        
        # 简单的时间轴分配
        parts = [
            {"text": script.hook, "start": 0, "end": 5},
            {"text": script.problem, "start": 5, "end": 15},
            {"text": script.solution, "start": 15, "end": 30},
            {"text": script.cta, "start": 30, "end": script.duration},
        ]
        
        return parts
    
    def generate_video(self, product_images: List[str],
                       voiceover_path: str,
                       script: VideoScript,
                       product_name: str,
                       output_name: str = None) -> GeneratedVideo:
        """生成完整视频"""
        logger.info(f"Generating video for: {product_name}")
        
        if output_name is None:
            output_name = f"video_{int(time.time())}.mp4"
        
        video_path = self.videos_dir / output_name
        thumbnail_path = self.videos_dir / f"thumb_{int(time.time())}.jpg"
        
        if self.mock_mode:
            # 模拟生成视频文件
            video_path.touch()
            thumbnail_path.touch()
            logger.info(f"Mock video saved: {video_path}")
        else:
            # 实际视频合成（使用MoviePy或其他工具）
            try:
                self._compose_video(product_images, voiceover_path, script, video_path)
            except Exception as e:
                logger.error(f"Failed to compose video: {e}")
                video_path.touch()
        
        # 生成标题和描述
        title = self._generate_title(product_name, script)
        description = self._generate_description(script)
        hashtags = self._generate_hashtags(product_name)
        
        return GeneratedVideo(
            video_path=str(video_path),
            thumbnail_path=str(thumbnail_path),
            title=title,
            description=description,
            hashtags=hashtags,
            script=script,
            product_name=product_name,
            duration=script.duration
        )
    
    def _compose_video(self, images: List[str], audio_path: str, 
                      script: VideoScript, output_path: Path):
        """合成视频（需要MoviePy）"""
        try:
            from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
            
            # 创建图片片段
            clips = []
            duration_per_image = script.duration / max(len(images), 1)
            
            for img_path in images:
                if os.path.exists(img_path):
                    clip = ImageClip(img_path, duration=duration_per_image)
                    clips.append(clip)
            
            if clips:
                video = concatenate_videoclips(clips, method="compose")
                
                # 添加音频
                if os.path.exists(audio_path):
                    audio = AudioFileClip(audio_path)
                    video = video.set_audio(audio)
                
                # 导出
                video.write_videofile(str(output_path), fps=24, codec='libx264')
                video.close()
            
        except ImportError:
            logger.warning("MoviePy not installed, skipping video composition")
            output_path.touch()
    
    def _generate_title(self, product_name: str, script: VideoScript) -> str:
        """生成视频标题"""
        return f"{script.hook} 🔥 #shorts"
    
    def _generate_description(self, script: VideoScript) -> str:
        """生成视频描述"""
        return f"{script.problem}\n\n{script.solution}\n\n{script.cta}\n\n#tiktokmademebuyit #amazonfinds #musthave"
    
    def _generate_hashtags(self, product_name: str) -> List[str]:
        """生成标签"""
        base_tags = ["#tiktokmademebuyit", "#amazonfinds", "#musthave", "#viral"]
        
        # 根据产品名添加相关标签
        product_words = product_name.lower().split()
        for word in product_words[:3]:
            if len(word) > 3:
                base_tags.append(f"#{word}")
        
        return base_tags[:8]  # 最多8个标签
    
    def run(self, product_name: str, product_images: List[str], 
            product_price: float = None, product_features: List[str] = None) -> GeneratedVideo:
        """完整流程"""
        logger.info("=" * 50)
        logger.info("Starting AI Video Generation")
        logger.info("=" * 50)
        
        if product_features is None:
            product_features = ["high quality", "affordable"]
        
        # 生成脚本
        script = self.generate_script(product_name, product_features, product_price)
        logger.info(f"Script generated: {script.hook}")
        
        # 生成配音
        voiceover_path = self.generate_voiceover(script)
        
        # 生成视频
        video = self.generate_video(
            product_images=product_images,
            voiceover_path=voiceover_path,
            script=script,
            product_name=product_name
        )
        
        logger.info("Video generation completed!")
        logger.info(f"  Title: {video.title}")
        logger.info(f"  Duration: {video.duration}s")
        logger.info(f"  Hashtags: {', '.join(video.hashtags[:3])}...")
        
        return video


if __name__ == "__main__":
    import random
    
    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "output_dir": "./output"
    }
    
    generator = AIVideoGenerator(config)
    
    # 测试生成
    video = generator.run(
        product_name="Wireless Bluetooth Earbuds",
        product_images=["image1.jpg", "image2.jpg"],
        product_price=24.99,
        product_features=["Bluetooth 5.3", "30h battery", "IPX7 waterproof"]
    )
    
    print(f"\nGenerated video:")
    print(f"  Title: {video.title}")
    print(f"  Path: {video.video_path}")
    print(f"  Script: {video.script.voiceover_text}")
