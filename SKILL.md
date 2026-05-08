# 小说转视频系统 - SKILL.md

## 🎯 技能目标
将网络小说自动转换为视频内容，支持批量处理和自动生成。

## 📖 支持的小说
- **桃运无双** - 洛雷 (1231章，已测试)

## 🔧 技术架构

```
小说 → 章节解析 → 场景提取 → 提示词生成 → VEOAIFree → 视频片段 → 合成
```

## 📂 目录结构

```
novel-to-video/
├── novels/              # 小说文件
│   └── taoyun_wushuang.txt
├── scripts/
│   ├── main.py          # 主入口
│   ├── fetch_novel.py   # 小说获取
│   ├── novel_to_video.py # 转换器
│   └── veoaifree_generator.py # 视频生成
├── scenes/              # 场景文件
├── output/
│   ├── videos/          # 输出视频
│   └── processing_report.json
└── logs/                # 日志
```

## 🚀 使用方法

```bash
# 1. 初始化项目
python scripts/main.py --mode init

# 2. 运行演示
python scripts/main.py --mode demo

# 3. 转换小说
python scripts/main.py --mode convert

# 4. 共享视频
python scripts/main.py --mode share
```

## 🎬 视频生成流程

1. **读取小说**: 加载 TXT 文件
2. **解析章节**: 自动识别章节标题
3. **提取场景**: 按关键词分割场景
4. **生成提示词**: AI 生成视频提示词
5. **VEOAIFree**: 免费生成视频片段
6. **合成视频**: 合并为完整视频

## 📝 提示词模板

```
A mysterious Chinese martial arts scene, beautiful woman
Ancient Chinese city at dawn, traditional architecture
Modern urban scenery with traditional elements
A grand mansion in traditional Chinese style
Mountain landscape with ancient temple
Night scene of a bustling city, neon lights
```

## 🎥 视频参数

- VEO 版本: 3.0 (最新)
- 视频比例: 16:9 (横向)
- 时长: 根据场景自动调整
- 水印: 无

## 📊 性能指标

- 单场景处理: ~30秒
- 单章节处理: ~2分钟
- 30分钟视频: ~15-20个场景

## 🔄 增量扩展

- 优先处理热门章节
- 支持断点续传
- 自动跳过已处理内容

## ⚠️ 注意事项

1. VEOAIFree 免费但可能有请求限制
2. 视频生成需要网络连接
3. 建议使用代理避免IP限制
4. 视频存储需要足够磁盘空间

## 📤 共享方案

1. **本地复制**: 通过搭建的服务器
2. **网盘分享**: 百度网盘/夸克网盘
3. **GitHub**: 小文件 (<100MB)
4. **云存储**: Google Drive/Dropbox
