"""
Video Producer Runner: 供 AI Agent 在后台自主调用的多媒体物理执行工具
支持：
1. 单视频切片创作
2. 文件夹下多视频素材智能混剪 (Multi-video Montage)
"""

import os
import sys
import math
import argparse
import asyncio
import subprocess
from pathlib import Path
from typing import List
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
        "shot_duration": float(meta.get("shot_duration", "3.0")),
        "filter_preset": meta.get("filter_preset", "default"),
        "script": content.replace("## 旁白剧本", "").strip()
    }


def get_video_duration(video_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        video_path
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", check=True)
        return float(res.stdout.strip())
    except Exception:
        return 60.0  # 默认保守时长


def resolve_video_sources(source_path: str) -> List[str]:
    p = Path(source_path)
    if p.is_file():
        return [str(p)]
    elif p.is_dir():
        exts = {".mp4", ".mov", ".mkv", ".flv", ".avi"}
        vids = [str(f) for f in p.iterdir() if f.suffix.lower() in exts and not f.name.startswith("temp_")]
        if not vids:
            raise FileNotFoundError(f"目录 {source_path} 下没有发现可用视频文件")
        return vids
    else:
        raise FileNotFoundError(f"找不到指定的素材路径: {source_path}")


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


def render_single_video(source_video: str, start_time: float, duration: float, audio_file: str, filter_preset: str, output_video: str):
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


def render_montage_video(
    video_sources: List[str],
    total_duration: float,
    shot_duration: float,
    audio_file: str,
    filter_preset: str,
    output_video: str
):
    """
    多视频混剪引擎：
    1. 计算镜头切片数量与时长
    2. 轮流从视频素材池中提取切片，并统一标准化为 1920x1080 30fps
    3. FFmpeg Concat 无损拼接，挂载插件滤镜，混流 TTS 语音
    """
    Path(output_video).parent.mkdir(parents=True, exist_ok=True)

    num_shots = max(1, math.ceil(total_duration / shot_duration))
    actual_shot_dur = total_duration / num_shots

    print(f"  🎬 [混剪装配器] 总配音时长: {total_duration:.2f}s | 单镜头节奏: {shot_duration:.1f}s")
    print(f"  🎬 [混剪装配器] 计算生成 {num_shots} 个镜头切片，来自 {min(len(video_sources), num_shots)} 个素材文件...")

    # 构建 FFmpeg 多输入与 filter_complex
    inputs = []
    filter_chains = []

    for i in range(num_shots):
        src_file = video_sources[i % len(video_sources)]
        # 预估安全切片起始点（轮换不同位置避免所有视频都从第0秒切）
        src_dur = get_video_duration(src_file)
        start_t = min(max(0.0, src_dur - actual_shot_dur - 5.0), float((i * 15) % max(1, int(src_dur - actual_shot_dur))))

        inputs.extend(["-ss", str(start_t), "-t", str(actual_shot_dur), "-i", src_file])
        
        # 统一标准化为 1920x1080 30fps, 居中自适应补黑边
        norm_filter = (
            f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
            f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v{i}];"
        )
        filter_chains.append(norm_filter)

    # 拼接节点
    concat_inputs = "".join(f"[v{i}]" for i in range(num_shots))
    style_filter = FILTER_PRESETS.get(filter_preset, FILTER_PRESETS["default"])
    if style_filter != "null":
        concat_node = f"{concat_inputs}concat=n={num_shots}:v=1:a=0[vconcat];[vconcat]{style_filter}[vfinal]"
    else:
        concat_node = f"{concat_inputs}concat=n={num_shots}:v=1:a=0[vfinal]"

    filter_chains.append(concat_node)
    full_filter_str = "".join(filter_chains)

    # 加上音频输入 (最后一个输入端口)
    audio_idx = num_shots
    inputs.extend(["-i", audio_file])

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", full_filter_str,
        "-map", "[vfinal]",
        "-map", f"{audio_idx}:a:0",
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
    parser.add_argument("--source", type=str, default=r"F:\【视频】\《后室》预告片，深度解读.mp4", help="源视频文件或素材文件夹路径")
    parser.add_argument("--plugin", type=str, required=True, help="挂载的风格插件路径")
    parser.add_argument("--custom_text", type=str, default=None, help="Agent自主生成的自定义台词(可选)")
    parser.add_argument("--output", type=str, default="output/final_video.mp4", help="输出视频路径")
    args = parser.parse_args()

    sources = resolve_video_sources(args.source)
    plugin_info = parse_plugin_info(args.plugin)
    text_to_speak = args.custom_text if args.custom_text else plugin_info["script"]

    print(f"[Agent工具调用] 正在装配插件: {plugin_info['name']}")
    print(f"  * 设定发音人: {plugin_info['voice_id']} (调速: {plugin_info['rate']})")
    print(f"  * 设定滤镜调色: {plugin_info['filter_preset']}")
    print(f"  * 设定镜头节奏: {plugin_info['shot_duration']}s/镜头")

    temp_audio = f"temp_audio_{plugin_info['id']}.mp3"
    try:
        duration = synthesize_audio(text_to_speak, plugin_info["voice_id"], plugin_info["rate"], temp_audio)
        print(f"  * 语音合成成功，精确时长: {duration:.2f} 秒")

        if len(sources) == 1:
            print(f"  * 识别为【单素材精剪模式】: {Path(sources[0]).name}")
            render_single_video(
                source_video=sources[0],
                start_time=plugin_info["clip_start"],
                duration=duration,
                audio_file=temp_audio,
                filter_preset=plugin_info["filter_preset"],
                output_video=args.output
            )
        else:
            print(f"  * 识别为【多素材智能混剪模式】: 素材池中包含 {len(sources)} 个视频")
            render_montage_video(
                video_sources=sources,
                total_duration=duration,
                shot_duration=plugin_info["shot_duration"],
                audio_file=temp_audio,
                filter_preset=plugin_info["filter_preset"],
                output_video=args.output
            )

        file_size_mb = os.path.getsize(args.output) / (1024 * 1024)
        print(f"  🎉 最终物理视频生成成功 -> 【{args.output}】 ({file_size_mb:.2f} MB)")
    finally:
        if os.path.exists(temp_audio):
            os.remove(temp_audio)


if __name__ == "__main__":
    main()
