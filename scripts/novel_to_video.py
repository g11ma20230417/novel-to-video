#!/usr/bin/env python3
"""
小说转视频主控脚本
《桃运无双》- 洛雷

工作流程：
1. 读取小说章节
2. 分场景处理
3. 生成视频片段 (VEOAIFree)
4. 文本转语音 (TTS)
5. 合成最终视频
"""

import os
import sys
import json
import time
import random
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class NovelToVideoConverter:
    """小说转视频转换器"""

    def __init__(self, novel_path: str = None):
        self.novel_path = novel_path
        self.novel_content = ""
        self.chapters = []
        self.scenes = []
        self.output_dir = Path("./output")
        self.novel_dir = Path("./novels")
        self.scenes_dir = Path("./scenes")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.novel_dir.mkdir(parents=True, exist_ok=True)
        self.scenes_dir.mkdir(parents=True, exist_ok=True)

        self.stats = {
            "total_chapters": 0,
            "processed_chapters": 0,
            "total_scenes": 0,
            "generated_videos": 0,
            "total_duration": 0
        }

    def load_novel(self, filename: str = "taoyun_wushuang.txt") -> bool:
        """加载小说内容"""
        novel_file = self.novel_dir / filename

        if not novel_file.exists():
            logger.error(f"小说文件不存在: {novel_file}")
            return False

        logger.info(f"加载小说: {novel_file}")
        with open(novel_file, 'r', encoding='utf-8') as f:
            self.novel_content = f.read()

        logger.info(f"✓ 小说加载完成，字数: {len(self.novel_content)}")
        return True

    def parse_chapters(self) -> List[Dict]:
        """解析章节"""
        logger.info("解析章节...")

        lines = self.novel_content.split('\n')
        current_chapter = None
        current_content = []
        chapters = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('第') and '章' in line and len(line) < 50:
                if current_chapter:
                    chapters.append({
                        "title": current_chapter,
                        "content": '\n'.join(current_content),
                        "word_count": len('\n'.join(current_content))
                    })

                current_chapter = line
                current_content = []
            else:
                current_content.append(line)

        if current_chapter:
            chapters.append({
                "title": current_chapter,
                "content": '\n'.join(current_content),
                "word_count": len('\n'.join(current_content))
            })

        self.chapters = chapters
        self.stats["total_chapters"] = len(chapters)
        logger.info(f"✓ 解析完成，共 {len(chapters)} 章")
        return chapters

    def extract_scenes(self, chapter: Dict) -> List[Dict]:
        """提取场景"""
        scenes = []
        content = chapter["content"]

        paragraphs = content.split('\n')
        current_scene = []
        scene_descriptions = []

        keywords = ['清晨', '夜晚', '忽然', '只见', '这时', '突然', '正在', '只见']

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if any(kw in para for kw in keywords):
                if current_scene:
                    scene_text = '\n'.join(current_scene)
                    scenes.append({
                        "text": scene_text,
                        "word_count": len(scene_text),
                        "duration": len(scene_text) * 0.5
                    })
                    current_scene = []

            current_scene.append(para)

        if current_scene:
            scene_text = '\n'.join(current_scene)
            scenes.append({
                "text": scene_text,
                "word_count": len(scene_text),
                "duration": len(scene_text) * 0.5
            })

        return scenes

    def generate_scene_prompt(self, scene_text: str) -> str:
        """从场景文本生成视频提示词"""
        prompt_templates = [
            "A mysterious Chinese martial arts scene, {}",
            "Ancient Chinese city at dawn, {}",
            "Modern urban scenery with traditional elements, {}",
            "A grand mansion in traditional Chinese style, {}",
            "Mountain landscape with ancient temple, {}",
            "Night scene of a bustling city, {}",
            "A beautiful woman in traditional Chinese dress, {}",
            "Action scene in a modern setting, {}",
        ]

        keywords = []
        if any(w in scene_text for w in ['美女', '女人', '小姐', '女神']):
            keywords.append("beautiful woman")
        if any(w in scene_text for w in ['打', '战斗', '武']):
            keywords.append("martial arts")
        if any(w in scene_text for w in ['夜', '月', '星']):
            keywords.append("night scene")
        if any(w in scene_text for w in ['清晨', '日出', '阳光']):
            keywords.append("sunrise")
        if any(w in scene_text for w in ['城市', '都市', '高楼']):
            keywords.append("modern city")

        keyword_str = ", ".join(keywords) if keywords else "cinematic atmosphere"
        template = random.choice(prompt_templates)
        return template.format(keyword_str)

    def estimate_video_duration(self, text: str) -> float:
        """估算视频时长（秒）"""
        word_count = len(text)
        duration = word_count * 0.3
        return min(duration, 30)

    def create_video_with_veoaifree(self, prompt: str, output_name: str) -> Optional[str]:
        """使用 VEOAIFree 创建视频"""
        try:
            logger.info(f"🎬 生成视频: {output_name}")
            logger.info(f"📝 提示词: {prompt[:80]}...")

            output_path = self.scenes_dir / f"{output_name}.mp4"

            from veoaifree_generator import VEOAIFreeGenerator
            generator = VEOAIFreeGenerator()
            video_path = generator.run(prompt, veo_version="3.0", aspect_ratio="16:9")

            if video_path and os.path.exists(video_path):
                import shutil
                final_path = self.output_dir / f"{output_name}.mp4"
                shutil.copy(video_path, final_path)
                self.stats["generated_videos"] += 1
                return str(final_path)

            logger.warning(f"⚠️ 视频生成可能未完成")
            return None

        except Exception as e:
            logger.error(f"❌ 视频生成失败: {e}")
            return None

    def create_text_video(self, text: str, output_name: str) -> str:
        """创建文字视频（备选方案）"""
        try:
            import subprocess

            output_path = self.output_dir / f"{output_name}.mp4"

            duration = min(len(text) * 0.1, 30)

            cmd = [
                'ffmpeg', '-f', 'lavfi', '-i',
                f'color=c=black:s=1280x720:d={duration}',
                '-f', 'lavfi', '-i',
                f'anullsrc=r=44100:cl=stereo:d={duration}',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-shortest',
                '-y', str(output_path)
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"✓ 文字视频创建: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"❌ 文字视频创建失败: {e}")
            return None

    def add_subtitle(self, video_path: str, subtitle_text: str, output_name: str) -> Optional[str]:
        """为视频添加字幕"""
        try:
            import subprocess

            output_path = self.output_dir / f"{output_name}_subtitled.mp4"
            subtitle_file = self.scenes_dir / f"{output_name}.srt"

            srt_content = f"""1
00:00:00,000 --> 00:00:30,000
{subtitle_text}
"""
            with open(subtitle_file, 'w', encoding='utf-8') as f:
                f.write(srt_content)

            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', f'subtitles={subtitle_file}',
                '-c:a', 'copy', '-y',
                str(output_path)
            ]

            subprocess.run(cmd, check=True, capture_output=True)
            return str(output_path)

        except Exception as e:
            logger.warning(f"字幕添加失败: {e}")
            return video_path

    def process_chapter(self, chapter: Dict, chapter_num: int) -> Dict:
        """处理单个章节"""
        logger.info(f"\n{'='*60}")
        logger.info(f"📖 处理章节 {chapter_num}: {chapter['title']}")
        logger.info(f"{'='*60}")

        scenes = self.extract_scenes(chapter)
        self.stats["total_scenes"] += len(scenes)

        chapter_output = {
            "chapter": chapter["title"],
            "chapter_num": chapter_num,
            "scenes": [],
            "video_clips": []
        }

        for i, scene in enumerate(scenes[:3]):
            scene_name = f"ch{chapter_num:03d}_scene{i+1:02d}"

            prompt = self.generate_scene_prompt(scene["text"])

            video_path = self.create_video_with_veoaifree(prompt, scene_name)

            if not video_path:
                video_path = self.create_text_video(scene["text"][:200], scene_name)

            chapter_output["scenes"].append({
                "name": scene_name,
                "text": scene["text"][:100] + "...",
                "prompt": prompt,
                "video": video_path
            })
            chapter_output["video_clips"].append(video_path)

            time.sleep(2)

        self.stats["processed_chapters"] += 1
        return chapter_output

    def run(self, start_chapter: int = 1, end_chapter: int = 5):
        """运行转换流程"""
        logger.info("="*60)
        logger.info("🚀 小说转视频系统启动")
        logger.info(f"   小说: 桃运无双 - 洛雷")
        logger.info(f"   处理范围: 第{start_chapter}-{end_chapter}章")
        logger.info("="*60)

        if not self.load_novel():
            logger.error("小说加载失败")
            return None

        chapters = self.parse_chapters()

        results = []
        for i, chapter in enumerate(chapters[start_chapter-1:end_chapter], start_chapter):
            result = self.process_chapter(chapter, i)
            results.append(result)

            if i < end_chapter:
                logger.info(f"⏸️  第{i}章处理完成，暂停...")
                time.sleep(5)

        self.save_report(results)

        logger.info("\n" + "="*60)
        logger.info("📊 处理完成!")
        logger.info(f"   处理章节: {self.stats['processed_chapters']}")
        logger.info(f"   生成视频: {self.stats['generated_videos']}")
        logger.info(f"   输出目录: {self.output_dir}")
        logger.info("="*60)

        return results

    def save_report(self, results: List[Dict]):
        """保存处理报告"""
        report = {
            "novel": "桃运无双",
            "author": "洛雷",
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats,
            "results": results
        }

        report_file = self.output_dir / "processing_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ 报告已保存: {report_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="小说转视频系统")
    parser.add_argument("--start", type=int, default=1, help="起始章节")
    parser.add_argument("--end", type=int, default=3, help="结束章节")
    parser.add_argument("--novel", default="taoyun_wushuang.txt", help="小说文件名")

    args = parser.parse_args()

    converter = NovelToVideoConverter()
    converter.run(args.start, args.end)


if __name__ == "__main__":
    main()
