"""
Pluggable Skills Video Producer Engine.
遵循 KISS 原则：单文件、零多余抽象、稳定调度真实多媒体管线。
"""

import os
import re
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, List, Optional


@dataclass
class Plugin:
    slot: str
    id: str
    name: str
    version: str
    description: str
    voice_id: str
    rate: str
    clip_start: float
    filter_preset: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def parse_video_plugin(file_path: str) -> Plugin:
    """解析带有音频发音人和滤镜参数的视频专用插件"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"找不到插件文件: {file_path}")

    text = path.read_text(encoding="utf-8")
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.DOTALL)

    meta = {}
    content = text
    if frontmatter_match:
        raw_meta = frontmatter_match.group(1)
        content = frontmatter_match.group(2).strip()

        for line in raw_meta.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")

    return Plugin(
        slot=meta.get("slot", "video_style"),
        id=meta.get("id", path.stem),
        name=meta.get("name", path.stem),
        version=meta.get("version", "1.0.0"),
        description=meta.get("description", ""),
        voice_id=meta.get("voice_id", "zh-CN-YunxiNeural"),
        rate=meta.get("rate", "+0%"),
        clip_start=float(meta.get("clip_start", "0.0")),
        filter_preset=meta.get("filter_preset", "default"),
        content=content,
        metadata=meta
    )
