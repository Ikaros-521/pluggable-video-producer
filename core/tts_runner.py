"""
Edge-TTS 本地真实语音合成执行器
"""

import asyncio
import subprocess
from pathlib import Path
import edge_tts


async def generate_speech_async(text: str, voice: str, rate: str, output_path: str):
    """异步调用 edge-tts 生成音频"""
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def generate_audio(text: str, voice: str, rate: str, output_path: str) -> float:
    """
    同步封装：生成真实 MP3 音频，并通过 ffprobe 精确获取音频时长（秒）
    """
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    # 运行异步 TTS
    asyncio.run(generate_speech_async(text, voice, rate, str(out_p)))

    # 使用 ffprobe 精准获取音频时长
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(out_p)
    ]
    res = subprocess.run(
        cmd,
        capture_output=True,
        encoding="utf-8",
        errors="ignore",
        check=True
    )
    duration = float(res.stdout.strip())
    return duration
