# 小说转视频系统 - 《桃运无双》

将网络小说《桃运无双》(洛雷) 自动转换为视频内容。

## 📖 项目说明

本项目可以将小说文本自动转换为视频，实现：
- 自动解析小说章节
- 智能提取场景
- 生成视频提示词
- 调用 VEOAIFree 免费生成视频
- 自动合成最终视频

## 🔧 系统要求

- Python 3.8+
- ffmpeg
- playwright
- 网络连接

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 初始化

```bash
python scripts/main.py --mode init
```

### 3. 运行演示

```bash
python scripts/main.py --mode demo
```

### 4. 转换视频

```bash
python scripts/main.py --mode convert
```

## 📂 目录结构

```
novel-to-video/
├── novels/              # 小说文件
├── scripts/             # 脚本
├── scenes/              # 场景
├── output/              # 输出
└── logs/                # 日志
```

## 🎬 工作流程

```
小说.txt → 章节解析 → 场景提取 → 提示词生成 → VEOAIFree → 视频片段
```

## 📝 支持的小说格式

```
第1章 章节标题

章节内容...

第2章 章节标题

章节内容...
```

## ⚠️ 注意事项

1. VEOAIFree (veoaifree.com) 免费但可能有请求限制
2. 需要稳定的网络连接
3. 视频生成需要等待
4. 建议在本地运行（非沙盒环境）

## 📤 视频共享

运行后视频保存在 `output/videos/` 目录

共享方式：
1. 直接复制文件
2. 上传到网盘
3. 通过服务器共享
