#!/usr/bin/env python3
"""
文件共享服务器
通过 HTTP 提供文件下载服务
"""

import os
import sys
import json
import logging
import http.server
import socketserver
import webbrowser
from pathlib import Path
from urllib.parse import urlparse, unquote
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

PORT = 8080
SHARE_DIR = Path("./output")


class ShareHandler(http.server.SimpleHTTPRequestHandler):
    """自定义 HTTP 处理器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SHARE_DIR.absolute()), **kwargs)

    def do_GET(self):
        """处理 GET 请求"""
        parsed_path = urlparse(self.path)
        path = unquote(parsed_path.path)

        if path == '/' or path == '/index.html':
            self.send_index()
        else:
            super().do_GET()

    def send_index(self):
        """发送文件列表页面"""
        files = []
        video_dir = SHARE_DIR / "videos"

        if video_dir.exists():
            for f in video_dir.glob("*.mp4"):
                size = f.stat().st_size
                size_str = self.format_size(size)
                files.append({
                    "name": f.name,
                    "path": f"/videos/{f.name}",
                    "size": size_str,
                    "size_bytes": size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                })

        for f in SHARE_DIR.glob("*.mp4"):
            size = f.stat().st_size
            size_str = self.format_size(size)
            files.append({
                "name": f.name,
                "path": f"/{f.name}",
                "size": size_str,
                "size_bytes": size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })

        html = self.generate_html(files)

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(html))
        self.end_headers()
        self.wfile.write(html.encode())

    def generate_html(self, files):
        """生成 HTML 页面"""
        total_size = sum(f["size_bytes"] for f in files)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>文件共享服务器</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #1a1a2e; color: #fff; }}
        h1 {{ color: #e94560; }}
        .info {{ background: #16213e; padding: 20px; border-radius: 10px; margin: 20px 0; }}
        .file-list {{ list-style: none; padding: 0; }}
        .file-item {{ background: #16213e; margin: 10px 0; padding: 15px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }}
        .file-item:hover {{ background: #1f4068; }}
        .file-name {{ font-weight: bold; color: #e94560; }}
        .file-info {{ color: #aaa; font-size: 14px; }}
        .download-btn {{ background: #e94560; color: white; padding: 8px 20px; text-decoration: none; border-radius: 5px; }}
        .download-btn:hover {{ background: #ff6b6b; }}
        .total {{ color: #4ecca3; }}
    </style>
</head>
<body>
    <h1>📁 文件共享服务器</h1>
    <div class="info">
        <p>📂 共享目录: {SHARE_DIR.absolute()}</p>
        <p>📹 文件数量: {len(files)}</p>
        <p class="total">💾 总大小: {self.format_size(total_size)}</p>
        <p>⏰ 服务器时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <h2>📹 视频文件</h2>
"""

        if files:
            html += '<ul class="file-list">'
            for f in sorted(files, key=lambda x: x["size_bytes"], reverse=True):
                html += f"""
    <li class="file-item">
        <div>
            <div class="file-name">{f['name']}</div>
            <div class="file-info">大小: {f['size']} | 修改: {f['modified']}</div>
        </div>
        <a href="{f['path']}" class="download-btn" download>⬇️ 下载</a>
    </li>"""
            html += '</ul>'
        else:
            html += '<p>暂无视频文件</p>'

        html += """
    <hr>
    <p style="color: #666;">由 Novel-to-Video System 生成</p>
</body>
</html>"""

        return html

    def format_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def log_message(self, format, *args):
        """自定义日志格式"""
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    SHARE_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("📁 文件共享服务器")
    print("="*60)
    print(f"\n📂 共享目录: {SHARE_DIR.absolute()}")
    print(f"🌐 访问地址: http://localhost:{PORT}")
    print(f"\n按 Ctrl+C 停止服务器")
    print("="*60 + "\n")

    with socketserver.TCPServer(("", PORT), ShareHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 服务器已停止")


if __name__ == "__main__":
    main()
