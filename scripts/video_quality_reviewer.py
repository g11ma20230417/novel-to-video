#!/usr/bin/env python3
"""
视频质量自动审查系统 v2
全面检测视频质量，包括：分辨率、音频、视觉质量、AI生成质量评估
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class QualityReport:
    """质量报告"""
    file_path: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # 基本信息
    resolution: str = ""
    width: int = 0
    height: int = 0
    fps: float = 0.0
    duration: float = 0.0
    file_size_mb: float = 0.0
    codec: str = ""
    audio_codec: str = ""
    audio_sample_rate: int = 0

    # 质量评分 (0-100)
    overall_score: int = 0
    resolution_score: int = 0
    video_quality_score: int = 0
    audio_quality_score: int = 0
    subtitle_score: int = 0
    content_score: int = 0

    # 检测结果
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    passed: bool = False

    # AI质量评估
    ai_video_detected: bool = False
    visual_clarity: str = "unknown"
    motion_smoothness: str = "unknown"

    def to_dict(self) -> dict:
        return {
            'file': self.file_path,
            'timestamp': self.timestamp,
            'resolution': self.resolution,
            'dimensions': f"{self.width}x{self.height}",
            'fps': self.fps,
            'duration_sec': round(self.duration, 1),
            'file_size_mb': round(self.file_size_mb, 1),
            'scores': {
                'overall': self.overall_score,
                'resolution': self.resolution_score,
                'video_quality': self.video_quality_score,
                'audio_quality': self.audio_quality_score,
                'subtitle': self.subtitle_score,
                'content': self.content_score
            },
            'ai_detection': {
                'ai_generated': self.ai_video_detected,
                'visual_clarity': self.visual_clarity,
                'motion_smoothness': self.motion_smoothness
            },
            'issues': self.issues,
            'warnings': self.warnings,
            'passed': self.passed
        }


class VideoQualityReviewer:
    """视频质量自动审查"""

    def __init__(self):
        self.ffprobe = 'ffprobe'
        self.ffmpeg = 'ffmpeg'

    def analyze_video(self, video_path: str) -> QualityReport:
        """全面分析视频质量"""
        report = QualityReport(file_path=video_path)

        if not Path(video_path).exists():
            report.issues.append("文件不存在")
            return report

        # 基本信息
        info = self.get_video_info(video_path)
        if not info:
            report.issues.append("无法读取视频信息")
            return report

        self.extract_basic_info(report, info)

        # 质量检测
        self.check_video_quality(report, video_path)
        self.check_audio_quality(report, video_path)
        self.check_resolution_quality(report)
        self.check_duration_quality(report)
        self.check_file_size_quality(report)
        self.check_visual_clarity(report, video_path)

        # 计算总分
        self.calculate_overall_score(report)

        # 判断是否通过
        report.passed = len(report.issues) == 0 and report.overall_score >= 70

        return report

    def get_video_info(self, video_path: str) -> Optional[dict]:
        """获取视频信息"""
        try:
            cmd = [
                self.ffprobe, '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"Error getting video info: {e}")
        return None

    def extract_basic_info(self, report: QualityReport, info: dict):
        """提取基本信息"""
        for stream in info.get('streams', []):
            codec_type = stream.get('codec_type', '')

            if codec_type == 'video':
                report.width = stream.get('width', 0)
                report.height = stream.get('height', 0)
                report.resolution = f"{report.width}x{report.height}"
                report.codec = stream.get('codec_name', '')

                fps_str = stream.get('r_frame_rate', '0/1')
                if '/' in fps_str:
                    num, denom = map(float, fps_str.split('/'))
                    report.fps = num / denom if denom != 0 else 0

            elif codec_type == 'audio':
                report.audio_codec = stream.get('codec_name', '')
                report.audio_sample_rate = int(stream.get('sample_rate', 0))

        format_info = info.get('format', {})
        report.duration = float(format_info.get('duration', 0))
        report.file_size_mb = int(format_info.get('size', 0)) / (1024 * 1024)

    def check_resolution_quality(self, report: QualityReport):
        """检测分辨率质量"""
        # 分辨率评分
        if report.width >= 1920 and report.height >= 1080:
            report.resolution_score = 30
            if report.width >= 3840:  # 4K
                report.resolution_score = 35
        elif report.width >= 1280 and report.height >= 720:
            report.resolution_score = 20
        elif report.width >= 854 and report.height >= 480:
            report.resolution_score = 10
        else:
            report.resolution_score = 5
            report.issues.append(f"分辨率过低: {report.resolution}")

    def check_video_quality(self, report: QualityReport, video_path: str):
        """检测视频质量"""
        # 检查视频流
        try:
            cmd = [
                self.ffprobe, '-v', 'error',
                '-select_streams', 'v:0',
                '-show_entries', 'stream=codec_type',
                '-of', 'csv=p=0', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if 'video' not in result.stdout:
                report.issues.append("未检测到视频流")
                report.video_quality_score = 0
            else:
                report.video_quality_score = 25
        except:
            report.video_quality_score = 10

    def check_audio_quality(self, report: QualityReport, video_path: str):
        """检测音频质量"""
        has_audio = False
        good_audio = False

        try:
            cmd = [
                self.ffprobe, '-v', 'error',
                '-select_streams', 'a',
                '-show_entries', 'stream=codec_type,codec_name,sample_rate',
                '-of', 'csv=p=0', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if 'audio' in result.stdout:
                has_audio = True
                if 'aac' in result.stdout.lower() or 'mp3' in result.stdout.lower():
                    if report.audio_sample_rate >= 44100:
                        good_audio = True
        except:
            pass

        if not has_audio:
            report.issues.append("无音频轨道")
            report.audio_quality_score = 0
        elif good_audio:
            report.audio_quality_score = 25
        else:
            report.audio_quality_score = 15
            report.warnings.append("音频编码可能不是最优")

    def check_duration_quality(self, report: QualityReport):
        """检测时长质量"""
        # YouTube视频最佳时长：8-15分钟
        if 30 <= report.duration <= 900:  # 30秒到15分钟
            if 180 <= report.duration <= 600:  # 3-10分钟最佳
                report.content_score = 25
            else:
                report.content_score = 15
                if report.duration < 60:
                    report.warnings.append("视频较短，建议至少1分钟")
                elif report.duration > 600:
                    report.warnings.append("视频较长，可能影响完播率")
        else:
            report.content_score = 5
            if report.duration < 30:
                report.issues.append(f"视频过短: {report.duration:.0f}秒")
            else:
                report.warnings.append(f"视频较长: {report.duration/60:.1f}分钟")

    def check_file_size_quality(self, report: QualityReport):
        """检测文件大小质量"""
        if report.duration > 0:
            bitrate = (report.file_size_mb * 8) / report.duration  # Mbps

            if bitrate >= 5:  # 高质量
                report.subtitle_score = 10
            elif bitrate >= 2:  # 中等质量
                report.subtitle_score = 7
            else:
                report.subtitle_score = 3
                report.warnings.append(f"码率较低: {bitrate:.1f}Mbps，可能影响画质")

            # 检查文件大小是否合理
            expected_min = report.duration * 0.5  # 至少500kbps
            if report.file_size_mb < expected_min:
                report.issues.append(f"文件过小: {report.file_size_mb:.1f}MB，时长{report.duration:.0f}秒")

    def check_visual_clarity(self, report: QualityReport, video_path: str):
        """检测视觉清晰度 - 通过采样帧分析"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # 提取几个关键帧
            frame_paths = []
            for i in range(3):
                frame_path = temp_dir / f"frame_{i}.png"
                time_pos = report.duration * (i + 1) / 4

                cmd = [
                    self.ffmpeg, '-y', '-ss', str(time_pos),
                    '-i', video_path, '-vframes', '1',
                    '-q:v', '2', str(frame_path)
                ]
                result = subprocess.run(cmd, capture_output=True)

                if frame_path.exists() and frame_path.stat().st_size > 10000:
                    frame_paths.append(frame_path)

            if frame_paths:
                # 检查是否有模糊的帧
                clarity_issues = 0
                for fp in frame_paths:
                    if fp.stat().st_size < 30000:  # 模糊帧通常较小
                        clarity_issues += 1

                if clarity_issues == 0:
                    report.visual_clarity = "清晰"
                elif clarity_issues < len(frame_paths):
                    report.visual_clarity = "大部分清晰"
                else:
                    report.visual_clarity = "可能有模糊"
                    report.warnings.append("部分帧可能模糊")

                # AI视频检测启发式方法
                total_size = sum(fp.stat().st_size for fp in frame_paths)
                avg_size = total_size / len(frame_paths)
                if avg_size > 50000:
                    report.ai_video_detected = True

        except Exception as e:
            report.warnings.append(f"视觉分析失败: {e}")
        finally:
            import shutil
            try:
                shutil.rmtree(temp_dir)
            except:
                pass

    def calculate_overall_score(self, report: QualityReport):
        """计算总分"""
        weights = {
            'resolution': 0.25,
            'video': 0.25,
            'audio': 0.25,
            'content': 0.15,
            'subtitle': 0.10
        }

        score = (
            report.resolution_score * weights['resolution'] +
            report.video_quality_score * weights['video'] +
            report.audio_quality_score * weights['audio'] +
            report.content_score * weights['content'] +
            report.subtitle_score * weights['subtitle']
        )

        report.overall_score = min(100, max(0, int(score)))

    def print_review(self, report: QualityReport):
        """打印审查报告"""
        print("\n" + "="*60)
        print("🎬 视频质量自动审查报告")
        print("="*60)

        print(f"\n📁 文件: {Path(report.file_path).name}")
        print(f"⏱️ 时长: {report.duration:.1f}秒 ({report.duration/60:.1f}分钟)")
        print(f"📐 分辨率: {report.resolution}")
        print(f"🎞️ 帧率: {report.fps:.1f} fps")
        print(f"💾 文件大小: {report.file_size_mb:.2f} MB")

        print(f"\n🎯 总体评分: {report.overall_score}/100")

        print("\n📊 分项评分:")
        print(f"  分辨率: {report.resolution_score}/30")
        print(f"  视频流: {report.video_quality_score}/25")
        print(f"  音频流: {report.audio_quality_score}/25")
        print(f"  内容时长: {report.content_score}/15")
        print(f"  文件质量: {report.subtitle_score}/10")

        print(f"\n🔍 AI检测:")
        print(f"  AI生成视频: {'是' if report.ai_video_detected else '否/不确定'}")
        print(f"  视觉清晰度: {report.visual_clarity}")

        if report.passed:
            print("\n✅ 审查通过 - 视频质量合格")
        else:
            print("\n❌ 审查未通过")

        if report.issues:
            print("\n🚫 严重问题:")
            for issue in report.issues:
                print(f"  ❌ {issue}")

        if report.warnings:
            print("\n⚠️ 警告:")
            for warning in report.warnings:
                print(f"  ⚠️ {warning}")

        if not report.issues and not report.warnings:
            print("\n✨ 无问题 - 视频完美!")

        print("\n" + "="*60)

    def save_report(self, report: QualityReport, output_path: str):
        """保存报告到JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"📄 报告已保存: {output_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='视频质量自动审查')
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('--output', '-o', help='报告输出路径')
    parser.add_argument('--json', '-j', action='store_true', help='JSON格式输出')
    args = parser.parse_args()

    reviewer = VideoQualityReviewer()
    report = reviewer.analyze_video(args.video)

    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        reviewer.print_review(report)

    if args.output:
        reviewer.save_report(report, args.output)

    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main())
