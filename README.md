# Pluggable Video Producer (可插拔视频生产落地实战)

> 🎬 **Pluggable Skills 官方端到端物理落地参考实现**：基于可插拔技能规范，使用真实音视频管线（Edge-TTS + FFmpeg），实现多风格短视频的真正自动化合成。

[中文](README.md) | [English](README_EN.md)

🔗 **主规范仓库**：[Ikaros-521/pluggable-skills](https://github.com/Ikaros-521/pluggable-skills)

---

## 💡 为什么需要这个独立实战仓库？

主仓库 [pluggable-skills](https://github.com/Ikaros-521/pluggable-skills) 聚焦于**标准协议（Spec v1.0）与轻量编排微内核**。

本仓库则是它的**官方全功能物理落地工程（Reference Implementation）**，旨在回答一个核心痛点：
> *“可插拔 Skills 到底能不能在复杂的真实视频生产中落地？生成的成品真的不会同质化吗？”*

答案是：**不仅能落地，而且仅需几秒钟即可现场渲染出两部视听风格完全不撞车的真实 MP4 视频！**

---

## 🧪 实战案例：同一部《后室》素材的双生反差

我们以同一部原始视频素材（《后室》预告片）作为输入源，分别挂载两套单文件 Markdown 插件：

| 维度 | 方案 A：伪纪录片心理恐惧风 (`plugin_analog_horror.md`) | 方案 B：SCP 异常档案快解说风 (`plugin_scp_archive.md`) |
| :--- | :--- | :--- |
| **插件文件** | 纯文本 Markdown（零代码） | 纯文本 Markdown（零代码） |
| **人声音色** | `zh-CN-YunjianNeural`（沉稳阴郁男声） | `zh-CN-YunxiNeural`（极速激情科技男声） |
| **配音调速** | `-8%`（慢速压迫低语） | `+18%`（高信息密度快节奏轰炸） |
| **分镜切片** | 第 15 秒（静谧黄色走廊） | 第 50 秒（动态异常高能突变） |
| **色彩预设** | 复古 VHS 录像带冷黄绿偏色 + 暗角 | 极客冷光高对比度 + 锐化滤镜 |
| **输出视频** | `output/output_analog_horror.mp4` | `output/output_scp_archive.mp4` |

---

## 🚀 极速运行与复现

### 1. 环境准备
确保本机安装了 `ffmpeg` 和 `edge-tts`：
```bash
pip install edge-tts
```

### 2. 一键运行生产
```bash
python run_producer.py
```

终端将在 10~15 秒内自动调用 `edge-tts` 与 `ffmpeg`，并在 `output/` 目录下生成两部真实的 `.mp4` 文件！

---

## 📂 仓库结构

```text
pluggable-video-producer/
├── README.md                  # 中文使用文档
├── README_EN.md               # 英文说明文档
├── LICENSE                    # MIT 协议
├── run_producer.py            # 主运行流水线 (一键执行)
├── core/
│   ├── engine.py              # 插件解析与槽位调度
│   ├── tts_runner.py          # Edge-TTS 真实人声合成器
│   └── ffmpeg_runner.py       # FFmpeg 切片与滤镜合成器
├── plugins/                   # 纯单文件风格插件
│   ├── plugin_analog_horror.md# 伪纪录片心理恐怖风插件
│   └── plugin_scp_archive.md  # SCP异常档案快解说插件
└── output/                    # 真实渲染生成的 MP4 文件
    ├── output_analog_horror.mp4
    └── output_scp_archive.mp4
```

---

## 🤝 关联与扩展

本工程完全基于 [pluggable-skills Spec v1.0 协议](https://github.com/Ikaros-521/pluggable-skills/blob/main/specification/spec_v1.md) 构建。您可以自由编写新的 Markdown 插件加入 `plugins/` 目录，体验一键切换文风、音色与画风的乐趣！
