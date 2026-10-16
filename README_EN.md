# Pluggable Video Producer

> 🎬 **Official End-to-End Production Reference Implementation for Pluggable Skills**: Automated generation of radically distinct short video styles using real multimedia pipelines (Edge-TTS + FFmpeg).

[English](README_EN.md) | [中文](README.md)

🔗 **Core Specification Repo**: [Ikaros-521/pluggable-skills](https://github.com/Ikaros-521/pluggable-skills)

---

## 💡 Why This Repository?

The primary specification repo [pluggable-skills](https://github.com/Ikaros-521/pluggable-skills) defines the **Spec v1.0 standard and the lightweight orchestration microkernel**.

This repository serves as its **official production-grade reference implementation**, answering the fundamental question:
> *"Can pluggable skills actually drive real-world, complex video production pipelines without output homogenization?"*

The answer is **Yes**. In under 15 seconds, this pipeline renders two physically distinct, non-homogenized `.mp4` video files from the same source clip.

---

## 🧪 Case Study: Two Opposing Styles from "The Backrooms"

Using the same source video (*The Backrooms* trailer), we mount two single-file Markdown plugins:

| Dimension | Option A: Analog Horror (`plugin_analog_horror.md`) | Option B: SCP Archive Speedrun (`plugin_scp_archive.md`) |
| :--- | :--- | :--- |
| **Plugin File** | Plain Markdown (Zero code) | Plain Markdown (Zero code) |
| **Voice Character** | `zh-CN-YunjianNeural` (Somber, deep whisper) | `zh-CN-YunxiNeural` (High-octane tech narrator) |
| **Speech Rate** | `-8%` (Oppressive, slow pacing) | `+18%` (Rapid-fire informational speedrun) |
| **Clip Cut** | 15.0s (Eerie, quiet yellow corridors) | 50.0s (Dynamic, sudden anomaly action) |
| **Color Grading** | Vintage VHS tape, muted greenish-yellow tint | Cyberpunk cold contrast + unsharp edge boost |
| **Output File** | `output/output_analog_horror.mp4` | `output/output_scp_archive.mp4` |

---

## 🚀 Quickstart

### 1. Requirements
Ensure `ffmpeg` and `edge-tts` are available:
```bash
pip install edge-tts
```

### 2. Run the Production Pipeline
```bash
python run_producer.py
```

The script will synthesize real human voices and assemble physical `.mp4` videos into `output/` in ~15 seconds.

---

## 📂 Repository Structure

```text
pluggable-video-producer/
├── README.md                  # Chinese documentation
├── README_EN.md               # English documentation (this file)
├── LICENSE                    # MIT License
├── run_producer.py            # Main automated pipeline script
├── core/
│   ├── engine.py              # Plugin parser and slot orchestrator
│   ├── tts_runner.py          # Edge-TTS voice synthesis runner
│   └── ffmpeg_runner.py       # FFmpeg video cut & color grading runner
├── plugins/                   # Single-file Markdown style plugins
│   ├── plugin_analog_horror.md# Analog Horror psychological plugin
│   └── plugin_scp_archive.md  # SCP Archive speedrun plugin
└── output/                    # Real generated physical MP4 videos
    ├── output_analog_horror.mp4
    └── output_scp_archive.mp4
```

---

## 📄 License

Licensed under the [MIT License](./LICENSE).
