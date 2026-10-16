"""
Video Producer Runner: 供 AI Agent 在后台自主调用的多媒体物理执行工具
支持通过 CLI 传参灵活执行，亦支持默认参数自测。
"""

import os
import sys
import argparse
import asyncio
import subprocess
from pathlib import Path
import edge_tts

# 控制台编码安全适配
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass


FILTER_PRESETS = {
    "analog_horror": "eq=contrast=1.2:brightness=-0.05:saturation=0.7,curves=preset=vintage",
    "cyber_scp": "eq=contrast=1.3:brightness=0.03:saturation=1.2,unsharp=5:5:0.8:5:5:0.0",
    "default": "null"
}


def parse_plugin_info(plugin_path: str):
    p = Path(plugin_path)
    text = p.read_text(encoding="utf-8")
    meta = {}
    content = text

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1]
            content = parts[2].strip()
            for line in raw_meta.splitlines():
                if ":" in line and not line.strip().startswith("#"):
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")

    return {
        "id": meta.get("id", p.stem),
        "name": meta.get("name", p.stem),
        "voice_id": meta.get("voice_id", "zh-CN-YunxiNeural"),
        "rate": meta.get("rate", "+0%"),
        "clip_start": float(meta.get("clip_start", "0.0")),
        "filter_preset": meta.get("filter_preset", "default"),
        "script": content.replace("## 旁白剧本", "").strip()
    }


async def generate_speech(text: str, voice: str, rate: str, output_path: str):
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(output_path)


def synthesize_audio(text: str, voice: str, rate: str, output_path: str) -> float:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(generate_speech(text, voice, rate, output_path))

    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        output_path
    ]
    res = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", check=True)
    return float(res.stdout.strip())


def render_video_cut(source_video: str, start_time: float, duration: float, audio_file: str, filter_preset: str, output_video: str):
    Path(output_video).parent.mkdir(parents=True, exist_ok=True)
    vf = FILTER_PRESETS.get(filter_preset, FILTER_PRESETS["default"])

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", source_video,
        "-i", audio_file,
        "-vf", vf,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_video
    ]
    subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", check=True)


def main():
    parser = argparse.ArgumentParser(description="Pluggable Video Producer Backend Runner")
    parser.add_argument("--source", type=str, default=r"F:\【视频】\《后室》预告片，深度解读.mp4", help="源视频文件路径")
    parser.add_argument("--plugin", type=str, required=True, help="挂载的风格插件路径")
    parser.add_argument("--custom_text", type=str, default=None, help="Agent自主生成的自定义台词(可选)")
    parser.add_argument("--output", type=str, default="output/final_video.mp4", help="输出视频路径")
    args = parser.parse_args()

    if not os.path.exists(args.source):
        print(f"Error: 找不到源视频素材 {args.source}")
        sys.exit(1)

    plugin_info = parse_plugin_info(args.plugin)
    text_to_speak = args.custom_text if args.custom_text else plugin_info["script"]

    print(f"[Agent工具调用] 正在装配插件: {plugin_info['name']}")
    print(f"  * 设定发音人: {plugin_info['voice_id']} (调速: {plugin_info['rate']})")
    print(f"  * 设定滤镜调色: {plugin_info['filter_preset']}")

    temp_audio = f"temp_audio_{plugin_info['id']}.mp3"
    try:
        duration = synthesize_audio(text_to_speak, plugin_info["voice_id"], plugin_info["rate"], temp_audio)
        print(f"  * 语音合成成功，精确时长: {duration:.2f} 秒")

        render_video_cut(
            source_video=args.source,
            start_time=plugin_info["clip_start"],
            duration=duration,
            audio_file=temp_audio,
            filter_preset=plugin_info["filter_preset"],
            output_video=args.output
        )
        print(f"  * 视频切片调色渲染完成: {args.output} ({os.path.getsize(args.output) / (1024*1024):.2f} MB)")
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)


if __name__ == "__main__":
    main()
