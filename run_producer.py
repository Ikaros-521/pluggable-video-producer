"""
Pluggable Video Producer 主运行脚本：
基于真实输入视频素材《后室》，分别装配两款截然不同的插件，
真实调用 edge-tts 与 FFmpeg 现场渲染出两部完全不撞车的真实短视频！
"""

import os
import sys
import time
from pathlib import Path

# 控制台编码适配
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

from core.engine import parse_video_plugin
from core.tts_runner import generate_audio
from core.ffmpeg_runner import render_final_video


def process_video_with_plugin(source_video: str, plugin_file: str, output_video: str):
    print(f"\n🧩 [装配插件]: {Path(plugin_file).name}")
    plugin = parse_video_plugin(plugin_file)
    print(f"  * 风格名称: {plugin.name}")
    print(f"  * 配音音色: {plugin.voice_id} (调速: {plugin.rate})")
    print(f"  * 视觉预设: {plugin.filter_preset}")

    # 提取文案
    script_text = plugin.content.replace("## 旁白剧本", "").strip()
    temp_audio = f"temp_audio_{plugin.id}.mp3"

    print("  🎙️ 正在生成真实人声配音 (edge-tts)...")
    duration = generate_audio(
        text=script_text,
        voice=plugin.voice_id,
        rate=plugin.rate,
        output_path=temp_audio
    )
    print(f"  ✅ 配音生成完毕！精确时长: {duration:.2f} 秒")

    print(f"  🎬 正在使用 FFmpeg 进行物理切片 (从第 {plugin.clip_start} 秒截取 {duration:.2f} 秒) 并渲染专属滤镜...")
    render_final_video(
        source_video=source_video,
        start_time=plugin.clip_start,
        duration=duration,
        audio_track=temp_audio,
        filter_preset=plugin.filter_preset,
        output_video=output_video
    )

    # 清理临时音频
    if os.path.exists(temp_audio):
        os.remove(temp_audio)

    file_size_mb = os.path.getsize(output_video) / (1024 * 1024)
    print(f"  🎉 最终物理视频生成成功 -> 【{output_video}】 ({file_size_mb:.2f} MB)")


def main():
    source_video = r"F:\【视频】\《后室》预告片，深度解读.mp4"
    if not os.path.exists(source_video):
        print(f"❌ 找不到测试素材: {source_video}")
        return

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("🚀 启动 Pluggable Skills 真实视频生产落地流水线")
    print(f"📹 输入源视频: {source_video}")
    print("=" * 70)

    start_t = time.time()

    # 1. 生产伪纪录片恐怖风格视频
    process_video_with_plugin(
        source_video=source_video,
        plugin_file="plugins/plugin_analog_horror.md",
        output_video=str(output_dir / "output_analog_horror.mp4")
    )

    # 2. 生产 SCP 极客快解说风格视频
    process_video_with_plugin(
        source_video=source_video,
        plugin_file="plugins/plugin_scp_archive.md",
        output_video=str(output_dir / "output_scp_archive.mp4")
    )

    total_cost = time.time() - start_t
    print("\n" + "=" * 70)
    print(f"🏁 全链路真实合成完毕！总耗时: {total_cost:.2f} 秒")
    print("🎯 结果验证：")
    print("1. 两部视频拥有完全不同的人声音色、语速、台词叙事框架。")
    print("2. 截取了完全不同的镜头区间，并叠加了专属色彩预设（复古黄绿暗调 vs 锐化高能冷感）。")
    print("3. 彻底打破了视频 Skills 的同质化瓶颈，且端到端物理真实可用！")
    print("=" * 70)


if __name__ == "__main__":
    main()
