"""
本地回归与自测脚本（可选）：
供开发者在未接入 AI Agent 宿主环境时，直接通过 Python 快速验证底层技能流水线。
"""

import subprocess
import sys
from pathlib import Path

# 控制台编码
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass

RUNNER = "skills/video-producer/scripts/producer_runner.py"
SOURCE_VIDEO = r"F:\【视频】\《后室》预告片，深度解读.mp4"

def run_test(plugin_rel_path, output_rel_path):
    cmd = [
        sys.executable, RUNNER,
        "--source", SOURCE_VIDEO,
        "--plugin", plugin_rel_path,
        "--output", output_rel_path
    ]
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 正在自测 Agent 视频技能后台多媒体管线...")
    print("=" * 60)

    # 1. 悬疑风
    run_test(
        "skills/video-producer/plugins/plugin_analog_horror.md",
        "output/output_analog_horror.mp4"
    )

    # 2. SCP档案风
    run_test(
        "skills/video-producer/plugins/plugin_scp_archive.md",
        "output/output_scp_archive.mp4"
    )

    # 3. 文件夹多素材混剪自测
    print("\n🎬 测试素材文件夹多视频混剪...")
    cmd_montage = [
        sys.executable, RUNNER,
        "--source", r"F:\【视频】",
        "--plugin", "skills/video-producer/plugins/plugin_scp_archive.md",
        "--output", "output/output_montage_scp.mp4"
    ]
    subprocess.run(cmd_montage, check=True)

    print("\n✅ 全流程自测通过！skills/video-producer 支持单文件与文件夹混剪双模。")
