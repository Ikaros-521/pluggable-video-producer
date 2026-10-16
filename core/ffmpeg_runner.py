"""
FFmpeg 本地多媒体真实切片、调色与音视频装配执行器
"""

import subprocess
from pathlib import Path


FILTER_PRESETS = {
    "analog_horror": (
        # 伪纪录片/后室复古微暗角与冷黄绿偏色滤镜
        "eq=contrast=1.2:brightness=-0.05:saturation=0.7,"
        "curves=preset=vintage"
    ),
    "cyber_scp": (
        # 极客异常档案/高对比锐化冷感滤镜
        "eq=contrast=1.3:brightness=0.03:saturation=1.2,"
        "unsharp=5:5:0.8:5:5:0.0"
    ),
    "default": "null"
}


def render_final_video(
    source_video: str,
    start_time: float,
    duration: float,
    audio_track: str,
    filter_preset: str,
    output_video: str
):
    """
    根据插件指令，切取原始素材，挂载专属滤镜，并混流最新 TTS 真实人声生成 MP4
    """
    out_p = Path(output_video)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    vf_filter = FILTER_PRESETS.get(filter_preset, FILTER_PRESETS["default"])

    # 构造 FFmpeg 装配命令
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", source_video,
        "-i", audio_track,
        "-vf", vf_filter,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(out_p)
    ]

    subprocess.run(
        cmd,
        capture_output=True,
        encoding="utf-8",
        errors="ignore",
        check=True
    )
    return str(out_p)
