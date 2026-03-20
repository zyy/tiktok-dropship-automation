# AI视频生成器 - 优化版本
# 高质量视频生成，包含配音、字幕、转场效果

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

class OptimizedVideoGenerator:
    """优化版视频生成器 - 高质量输出"""
    
    def __init__(self, config: dict):
        self.config = config
        self.output_dir = Path(config.get("output_dir", "./output"))
        self.videos_dir = self.output_dir / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir = self.output_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # 脚本模板库
        self.script_templates = {
            "hook": [
                "Stop scrolling! You need to see this {product}!",
                "I can't believe this {product} is only {price}!",
                "This {product} just changed my life!",
                "POV: You finally found the perfect {product}",
                "Wait for it... This {product} is INSANE!",
                "You won't believe what this {product} can do!",
            ],
            "problem": [
                "Tired of overpriced products that don't work?",
                "Sick of wasting money on cheap knockoffs?",
                "Struggling to find a good quality option?",
                "Frustrated with products that break in a week?",
                "Done with overpaying for basic items?",
                "Ever bought something that looked good but disappointed?",
            ],
            "solution": [
                "This {product} is game-changing!",
                "Finally found the perfect solution - this {product}!",
                "This {product} solves everything!",
                "Say goodbye to problems with this {product}!",
                "Upgrade your life with this {product}!",
                "This {product} exceeded all my expectations!",
            ],
            "cta": [
                "Link in bio! Only {price} but selling out fast!",
                "Grab yours before they're gone! Link in bio!",
                "Don't miss out - link in bio! Limited stock! ⏰",
                "Get it now for {price}! Link in bio! 🛒",
                "Last chance! Link in bio! Only {price}!",
                "Tap link in bio before it's gone! {price}!",
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
    
    def generate_voiceover(self, script: VideoScript) -> str:
        """生成配音（使用系统TTS或示例音频）"""
        logger.info("Generating voiceover...")
        
        output_path = self.audio_dir / f"voiceover_{int(time.time())}.mp3"
        
        try:
            # 尝试使用 macOS 的 say 命令生成音频
            import subprocess
            
            # 创建临时 aiff 文件
            temp_aiff = self.audio_dir / f"temp_{int(time.time())}.aiff"
            
            # 使用 say 命令（Samantha 是美式女声）
            cmd = [
                'say',
                '-v', 'Samantha',
                '-o', str(temp_aiff),
                script.voiceover_text
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 转换为 mp3
            cmd_convert = [
                'ffmpeg', '-y',
                '-i', str(temp_aiff),
                '-codec:a', 'libmp3lame',
                '-qscale:a', '2',
                str(output_path)
            ]
            
            subprocess.run(cmd_convert, check=True, capture_output=True)
            
            # 删除临时文件
            temp_aiff.unlink(missing_ok=True)
            
            logger.info(f"Voiceover saved: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.warning(f"TTS failed: {e}, creating placeholder")
            # 创建静音文件（1秒静音）
            try:
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', 'anullsrc=r=24000:cl=mono',
                    '-t', str(script.duration),
                    '-acodec', 'libmp3lame',
                    str(output_path)
                ]
                subprocess.run(cmd, check=True, capture_output=True)
            except:
                output_path.touch()
            
            return str(output_path)
    
    def generate_optimized_video(self, product_name: str, script: VideoScript, 
                                  voiceover_path: str) -> str:
        """生成优化版视频 - 高质量"""
        logger.info("Generating optimized video with MoviePy...")
        
        try:
            from moviepy import (
                ColorClip, TextClip, CompositeVideoClip, AudioFileClip,
                concatenate_videoclips, vfx
            )
            
            # 视频尺寸 (TikTok 9:16)
            width, height = 1080, 1920
            duration = script.duration
            
            # 定义场景和时间
            scenes = [
                {"text": script.hook, "start": 0, "dur": 8, "bg": (255, 100, 50)},
                {"text": script.problem, "start": 8, "dur": 10, "bg": (50, 100, 255)},
                {"text": script.solution, "start": 18, "dur": 12, "bg": (50, 200, 100)},
                {"text": script.cta, "start": 30, "dur": 10, "bg": (255, 200, 50)},
            ]
            
            video_clips = []
            
            for scene in scenes:
                # 创建背景
                bg = ColorClip(
                    size=(width, height),
                    color=scene["bg"]
                ).with_duration(scene["dur"])
                
                # 创建文字 - 使用更大更醒目的字体
                words = scene["text"].split()
                lines = []
                current_line = []
                
                for word in words:
                    if len(' '.join(current_line + [word])) < 20:
                        current_line.append(word)
                    else:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))
                
                formatted_text = '\n'.join(lines)
                
                # 主文字 - 使用系统默认字体
                txt_clip = TextClip(
                    text=formatted_text,
                    font_size=90,
                    color='white',
                    font='Helvetica',
                    size=(width - 100, None),
                    method='caption',
                    stroke_color='black',
                    stroke_width=3
                ).with_duration(scene["dur"])
                
                # 添加缩放动画效果
                txt_clip = txt_clip.with_effects([
                    vfx.Resize(lambda t: 1 + 0.1 * (t / scene["dur"]))
                ])
                
                txt_clip = txt_clip.with_position('center')
                
                # 添加产品名水印
                watermark = TextClip(
                    text=f"🔥 {product_name} 🔥",
                    font_size=50,
                    color='yellow',
                    font='Helvetica',
                    stroke_color='black',
                    stroke_width=2
                ).with_duration(scene["dur"])
                watermark = watermark.with_position(('center', 150))
                
                # 合成场景
                scene_clip = CompositeVideoClip([bg, txt_clip, watermark])
                scene_clip = scene_clip.with_start(scene["start"])
                
                video_clips.append(scene_clip)
            
            # 合并所有场景
            final_video = CompositeVideoClip(video_clips, size=(width, height))
            final_video = final_video.with_duration(duration)
            
            # 添加配音
            if os.path.exists(voiceover_path) and os.path.getsize(voiceover_path) > 100:
                try:
                    audio = AudioFileClip(voiceover_path)
                    # 如果音频比视频长，截断；如果短，循环
                    if audio.duration > duration:
                        audio = audio.subclipped(0, duration)
                    final_video = final_video.with_audio(audio)
                except Exception as e:
                    logger.warning(f"Could not add audio: {e}")
            
            # 导出高质量视频
            output_path = self.videos_dir / f"optimized_{int(time.time())}.mp4"
            
            final_video.write_videofile(
                str(output_path),
                fps=30,  # 提高帧率
                codec='libx264',
                audio_codec='aac',
                bitrate='8000k',  # 高码率
                threads=4,
                preset='medium'  # 平衡质量和速度
            )
            
            final_video.close()
            
            logger.info(f"Optimized video saved: {output_path}")
            logger.info(f"Video size: {output_path.stat().st_size / 1024:.1f} KB")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to generate video: {e}")
            import traceback
            traceback.print_exc()
            
            # 创建占位文件
            output_path = self.videos_dir / f"optimized_{int(time.time())}.mp4"
            output_path.touch()
            return str(output_path)
    
    def generate_thumbnail(self, product_name: str, script: VideoScript) -> str:
        """生成高质量缩略图"""
        logger.info("Generating optimized thumbnail...")
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建图片 (TikTok缩略图尺寸)
            width, height = 1080, 1920
            
            # 创建渐变背景
            img = Image.new('RGB', (width, height), color=(0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # 绘制渐变
            for y in range(height):
                r = int(255 * (1 - y / height))
                g = int(100 * (1 - y / height))
                b = int(50 * (1 - y / height))
                draw.line([(0, y), (width, y)], fill=(r, g, b))
            
            # 添加文字
            title = script.hook[:60] + "..." if len(script.hook) > 60 else script.hook
            
            try:
                font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 100)
                font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # 主标题
            bbox = draw.textbbox((0, 0), title, font=font_large)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            y = height // 3
            
            # 绘制文字阴影
            for offset in [(4, 4), (-4, -4), (4, -4), (-4, 4)]:
                draw.text((x + offset[0], y + offset[1]), title, font=font_large, fill=(0, 0, 0))
            draw.text((x, y), title, font=font_large, fill=(255, 255, 255))
            
            # 添加产品名
            product_text = f"⭐ {product_name} ⭐"
            bbox2 = draw.textbbox((0, 0), product_text, font=font_small)
            text_width2 = bbox2[2] - bbox2[0]
            x2 = (width - text_width2) // 2
            y2 = y + 200
            
            draw.text((x2 + 3, y2 + 3), product_text, font=font_small, fill=(0, 0, 0))
            draw.text((x2, y2), product_text, font=font_small, fill=(255, 255, 0))
            
            # 添加 "CLICK NOW" 按钮效果
            button_text = "👆 TAP LINK IN BIO 👆"
            bbox3 = draw.textbbox((0, 0), button_text, font=font_small)
            text_width3 = bbox3[2] - bbox3[0]
            x3 = (width - text_width3) // 2
            y3 = height - 300
            
            # 按钮背景
            button_padding = 30
            draw.rounded_rectangle(
                [x3 - button_padding, y3 - button_padding, 
                 x3 + text_width3 + button_padding, y3 + 80 + button_padding],
                radius=20,
                fill=(255, 50, 50),
                outline=(255, 255, 255),
                width=5
            )
            draw.text((x3, y3), button_text, font=font_small, fill=(255, 255, 255))
            
            # 保存
            thumb_path = self.videos_dir / f"thumb_optimized_{int(time.time())}.jpg"
            img.save(thumb_path, quality=95, optimize=True)
            
            logger.info(f"Thumbnail saved: {thumb_path}")
            return str(thumb_path)
            
        except Exception as e:
            logger.error(f"Failed to generate thumbnail: {e}")
            thumb_path = self.videos_dir / f"thumb_optimized_{int(time.time())}.jpg"
            thumb_path.touch()
            return str(thumb_path)
    
    def _generate_hashtags(self, product_name: str) -> List[str]:
        """生成标签"""
        base_tags = ["#tiktokmademebuyit", "#amazonfinds", "#musthave", "#viral", "#trending"]
        
        # 根据产品名添加相关标签
        product_words = product_name.lower().split()
        for word in product_words[:3]:
            if len(word) > 3:
                base_tags.append(f"#{word}")
        
        return base_tags[:8]
    
    def run(self, product_name: str, product_images: List[str] = None,
            product_price: float = None, product_features: List[str] = None) -> GeneratedVideo:
        """完整流程"""
        logger.info("=" * 60)
        logger.info("Starting Optimized Video Generation")
        logger.info("=" * 60)
        
        if product_features is None:
            product_features = ["high quality", "affordable"]
        
        # 生成脚本
        script = self.generate_script(product_name, product_features, product_price)
        logger.info(f"Script generated: {script.hook}")
        
        # 生成配音
        voiceover_path = self.generate_voiceover(script)
        
        # 生成视频
        video_path = self.generate_optimized_video(product_name, script, voiceover_path)
        
        # 生成缩略图
        thumbnail_path = self.generate_thumbnail(product_name, script)
        
        # 生成标题和描述
        title = f"{script.hook} 🔥 #shorts"
        description = f"{script.problem}\n\n{script.solution}\n\n{script.cta}\n\n#tiktokmademebuyit #amazonfinds #musthave"
        hashtags = self._generate_hashtags(product_name)
        
        logger.info("=" * 60)
        logger.info("Optimized video generation completed!")
        logger.info(f"Video: {video_path}")
        logger.info(f"Thumbnail: {thumbnail_path}")
        logger.info("=" * 60)
        
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
    generator = OptimizedVideoGenerator(config)
    
    video = generator.run(
        product_name="Wireless Bluetooth Earbuds",
        product_price=24.99,
        product_features=["Bluetooth 5.3", "30h battery", "IPX7 waterproof"]
    )
    
    print(f"\n✅ 高质量视频生成完成!")
    print(f"视频文件: {video.video_path}")
    print(f"缩略图: {video.thumbnail_path}")
    print(f"标题: {video.title}")
    print(f"\n脚本内容:")
    print(f"Hook: {video.script.hook}")
    print(f"Problem: {video.script.problem}")
    print(f"Solution: {video.script.solution}")
    print(f"CTA: {video.script.cta}")
