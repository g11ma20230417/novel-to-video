# 小说转视频完整工作流程

## 🎯 目标
将小说《桃运无双》转换为高质量视频，上传到YouTube赚钱

---

## 📋 工作流程总览

```
┌─────────────────────────────────────────────────────────────────┐
│  1. veoaifree.com 网页生成视频 (用户操作)                          │
│     ↓                                                           │
│  2. 下载视频到本地                                               │
│     ↓                                                           │
│  3. 上传到分享系统 (Agent操作)                                   │
│     ↓                                                           │
│  4. 视频质量审查 (Agent操作)                                     │
│     ↓                                                           │
│  5. 最终分享下载链接 (Agent操作)                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📝 详细步骤

### 第一步：生成视频 (用户操作)

1. **访问网站**: https://veoaifree.com/veo-video-generator/

2. **输入提示词** (示例):
```
A mysterious young man in ancient Chinese robes walking through a misty forest at dawn, 
cinematic lighting, dramatic camera movement, ethereal atmosphere, magical particles floating
```

3. **点击生成**: 等待10-30秒

4. **下载最佳视频**: 保存到本地

### 第二步：分享给Agent审查 (用户操作)

将下载的视频文件发送给Agent

### 第三步：Agent处理 (Agent自动)

1. **上传到分享系统**
2. **自动质量审查**
3. **生成下载链接**

---

## 🔧 Agent可执行的操作

### 1. 视频质量审查
```bash
python3 scripts/video_quality_reviewer.py video.mp4
```

审查内容:
- 分辨率 (1920x1080)
- 音频轨道
- 视频时长
- 文件大小
- 视觉质量

### 2. 视频上传分享
```bash
python3 scripts/video_share.py video1.mp4 video2.mp4 --tag v1.0
```

### 3. 批量处理
```bash
python3 scripts/video_share.py *.mp4 --tag v1.0
```

---

## 📊 质量标准

| 项目 | 标准 | 评分 |
|------|------|------|
| 分辨率 | 1920x1080 | 30分 |
| 视频流 | H264 | 25分 |
| 音频 | AAC 44100Hz | 25分 |
| 时长 | 30秒-10分钟 | 15分 |
| 文件大小 | >1MB | 5分 |
| **总分** | **≥70分通过** | 100分 |

---

## 💡 提示词模板

### 都市言情
```
A beautiful Chinese woman in elegant dress standing in a luxury apartment, 
large windows with city skyline at night, romantic atmosphere, 
soft warm lighting, cinematic composition
```

### 玄幻修仙
```
A mysterious jade pendant glowing with golden light, ancient runes floating around, 
dark chamber with magical particles, epic fantasy atmosphere, dramatic close-up
```

### 都市爽文
```
A handsome young man in stylish suit walking confidently through modern office, 
glass walls, professional atmosphere, confident expression, cinematic lighting
```

### 动作场景
```
A martial artist performing high kick in traditional training hall, 
dust particles in air, dramatic lighting, fast action, cinematic slow motion
```

---

## 📱 分享链接说明

### GitHub Releases
- 下载速度：一般
- 文件大小限制：无
- 有效期：永久

### 其他方案
- 奶牛快传：临时分享，7天有效
- 123云盘：需要注册

---

## 🚀 快速开始

1. 打开 https://veoaifree.com/veo-video-generator/
2. 输入提示词生成视频
3. 下载视频
4. 发送给Agent审查
5. 获取分享链接

---

## ⚠️ 常见问题

Q: veoaifree.com 需要注册吗？
A: 不需要，完全免费使用

Q: 视频有水印吗？
A: 没有，完全无水印

Q: 每次可以生成多少个视频？
A: 无限制，可无限生成

Q: 视频最长多久？
A: 4-8秒

Q: 如何生成更长的视频？
A: 可以生成多个短视频然后拼接
