#!/usr/bin/env python3
"""
小说转视频系统 - 主入口
《桃运无双》- 洛雷

使用方法:
  python main.py --mode init     # 初始化（创建示例小说）
  python main.py --mode convert # 转换小说到视频
  python main.py --mode demo    # 运行演示
"""

import os
import sys
import json
import time
import shutil
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def setup_directories():
    """创建目录结构"""
    dirs = ['novels', 'scenes', 'output', 'logs', 'scripts']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    logger.info("✓ 目录结构已创建")


def init_project():
    """初始化项目"""
    logger.info("="*60)
    logger.info("🚀 初始化小说转视频项目")
    logger.info("="*60)

    setup_directories()

    novel_file = Path("novels/taoyun_wushuang.txt")
    if not novel_file.exists():
        logger.info("创建示例小说...")
        from fetch_novel import NovelFetcher
        fetcher = NovelFetcher()
        fetcher.create_sample_novel()
    else:
        logger.info(f"✓ 小说文件已存在: {novel_file}")

    logger.info("="*60)
    logger.info("✅ 初始化完成!")
    logger.info("="*60)
    logger.info("\n接下来运行:")
    logger.info("  python main.py --mode convert  # 转换视频")


def convert_novel_to_video():
    """转换小说到视频"""
    logger.info("="*60)
    logger.info("🎬 小说转视频")
    logger.info("="*60)

    from novel_to_video import NovelToVideoConverter

    converter = NovelToVideoConverter()

    novel_file = Path("novels/taoyun_wushuang.txt")
    if not novel_file.exists():
        logger.error("小说文件不存在，请先运行: python main.py --mode init")
        return False

    converter.load_novel()
    converter.parse_chapters()

    start = 1
    end = min(3, converter.stats["total_chapters"])

    results = converter.run(start, end)

    logger.info("\n✅ 转换完成!")
    logger.info(f"输出目录: {converter.output_dir}")

    return True


def create_video_with_images():
    """使用图片创建视频（简单方案）"""
    logger.info("="*60)
    logger.info("🎬 使用图片生成视频")
    logger.info("="*60)

    try:
        from veoaifree_generator import VEOAIFreeGenerator
    except ImportError:
        logger.error("请先安装 veoaifree_generator 依赖")
        return False

    prompts = [
        "A mysterious Chinese martial arts scene, beautiful woman, cinematic atmosphere",
        "Ancient Chinese city at dawn, traditional architecture, misty mountains",
        "Modern urban scenery with traditional elements, beautiful woman, sunrise",
        "A grand mansion in traditional Chinese style, luxury interior",
        "Night scene of a bustling city, neon lights, futuristic",
        "A beautiful woman in traditional Chinese dress, elegant, stunning",
        "Action scene in a modern setting, martial arts, dynamic",
        "Mountain landscape with ancient temple, peaceful, spiritual"
    ]

    generator = VEOAIFreeGenerator()
    output_dir = Path("./output/videos")
    output_dir.mkdir(parents=True, exist_ok=True)

    videos = []

    for i, prompt in enumerate(prompts[:3]):
        logger.info(f"\n生成第 {i+1}/{len(prompts[:3])} 个视频...")
        video_path = generator.run(prompt, veo_version="3.0", aspect_ratio="16:9")

        if video_path and os.path.exists(video_path):
            final_path = output_dir / f"scene_{i+1:02d}.mp4"
            shutil.copy(video_path, final_path)
            videos.append(str(final_path))
            logger.info(f"✅ 视频已保存: {final_path}")

        time.sleep(3)

    logger.info("\n" + "="*60)
    logger.info("📊 生成结果")
    logger.info("="*60)
    logger.info(f"成功生成: {len(videos)} 个视频")
    for v in videos:
        logger.info(f"  📹 {v}")
    logger.info("="*60)

    return len(videos) > 0


def share_videos():
    """共享视频"""
    logger.info("="*60)
    logger.info("📤 视频共享")
    logger.info("="*60)

    output_dir = Path("./output/videos")
    videos = list(output_dir.glob("*.mp4"))

    if not videos:
        logger.warning("没有找到视频文件")
        return False

    logger.info(f"找到 {len(videos)} 个视频文件:")
    for v in videos:
        size = v.stat().st_size / (1024*1024)
        logger.info(f"  📹 {v.name} ({size:.2f} MB)")

    logger.info("\n共享方式:")
    logger.info("1. 上传到 GitHub (大文件不推荐)")
    logger.info("2. 使用网盘分享 (百度网盘/夸克网盘)")
    logger.info("3. 使用云存储 (Google Drive/Dropbox)")
    logger.info("4. 直接复制文件 (通过我们搭建的服务器)")

    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="小说转视频系统 - 《桃运无双》",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --mode init    # 初始化项目
  python main.py --mode demo   # 运行演示
  python main.py --mode convert # 转换小说到视频
  python main.py --mode share   # 共享视频
        """
    )

    parser.add_argument(
        "--mode",
        choices=["init", "demo", "convert", "share"],
        default="demo",
        help="运行模式"
    )

    args = parser.parse_args()

    setup_directories()

    if args.mode == "init":
        init_project()

    elif args.mode == "demo":
        logger.info("="*60)
        logger.info("🎬 小说转视频演示模式")
        logger.info("="*60)

        novel_file = Path("novels/taoyun_wushuang.txt")
        if not novel_file.exists():
            logger.info("创建示例小说...")
            from fetch_novel import NovelFetcher
            fetcher = NovelFetcher()
            fetcher.create_sample_novel()

        logger.info("\n📝 小说内容预览:")
        with open(novel_file, 'r', encoding='utf-8') as f:
            content = f.read()[:500]
            logger.info(content)

        logger.info("\n🎬 生成测试视频...")
        success = create_video_with_images()

        if success:
            logger.info("\n✅ 演示完成!")
            logger.info("查看 output/videos 目录")
        else:
            logger.info("\n⚠️ 演示完成，但视频生成可能失败")

    elif args.mode == "convert":
        convert_novel_to_video()

    elif args.mode == "share":
        share_videos()


if __name__ == "__main__":
    main()
