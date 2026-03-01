#!/usr/bin/env python3
"""Gemini Veo 视频生成模块

使用 Google Gemini Veo 3.1 模型从文本或图片生成视频。
支持自定义宽高比、分辨率、时长等参数。

依赖: pip install google-genai

环境变量:
    GEMINI3PRO_API_KEY: Google AI API Key（也支持 GEMINI_API_KEY）
"""

import argparse
import os
import sys
import time
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("错误: 请先安装 google-genai 包")
    print("  pip install google-genai")
    sys.exit(1)


def _load_dotenv() -> None:
    """从 ~/.env 加载环境变量（不覆盖已有值）"""
    env_path = Path.home() / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()


# ──────────────────────────────────────────────
# 常量 & 默认值
# ──────────────────────────────────────────────

DEFAULT_MODEL = "veo-3.1-generate-preview"
DEFAULT_ASPECT_RATIO = "9:16"
DEFAULT_RESOLUTION = "720p"
DEFAULT_DURATION = 8
POLL_INTERVAL = 10  # 秒

VALID_ASPECT_RATIOS = ("9:16", "16:9")
VALID_RESOLUTIONS = ("720p", "1080p", "4k")
VALID_DURATIONS = (4, 6, 8)


# ──────────────────────────────────────────────
# 核心类
# ──────────────────────────────────────────────

class GeminiVideoGenerator:
    """Gemini Veo 视频生成器

    用法:
        gen = GeminiVideoGenerator(api_key="...")
        path = gen.generate_from_text("一只猫在弹钢琴")
        path = gen.generate_from_image("让这张图动起来", "photo.jpg")
    """

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        """初始化生成器

        Args:
            api_key: Google AI API Key，不传则从 GEMINI_API_KEY 环境变量读取
            model: 模型名称，默认 veo-3.1-generate-preview
        """
        self.api_key = (
            api_key
            or os.getenv("GEMINI3PRO_API_KEY")
            or os.getenv("GEMINI_API_KEY")
        )
        if not self.api_key:
            raise ValueError(
                "需要提供 API Key: 传入 api_key 参数或设置 GEMINI3PRO_API_KEY 环境变量"
            )
        self.model = model
        self.client = genai.Client(api_key=self.api_key)

    def generate_from_text(
        self,
        prompt: str,
        *,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        resolution: str = DEFAULT_RESOLUTION,
        duration: int = DEFAULT_DURATION,
        negative_prompt: str | None = None,
        output_path: str | None = None,
    ) -> Path:
        """文本生成视频

        Args:
            prompt: 视频描述文本
            aspect_ratio: 宽高比，"9:16"(竖屏) 或 "16:9"(横屏)
            resolution: 分辨率，"720p" / "1080p" / "4k"
            duration: 时长(秒)，4 / 6 / 8
            negative_prompt: 不希望出现的内容描述
            output_path: 输出文件路径，不传则自动生成

        Returns:
            保存的视频文件路径
        """
        self._validate_params(aspect_ratio, resolution, duration)

        config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            duration_seconds=duration,
            negative_prompt=negative_prompt,
        )

        print(f"正在生成视频...")
        print(f"  提示词: {prompt}")
        print(f"  宽高比: {aspect_ratio} | 分辨率: {resolution} | 时长: {duration}s")
        if negative_prompt:
            print(f"  负面提示: {negative_prompt}")

        operation = self.client.models.generate_videos(
            model=self.model,
            prompt=prompt,
            config=config,
        )

        return self._wait_and_save(operation, output_path)

    def generate_from_image(
        self,
        prompt: str,
        image_path: str,
        *,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        resolution: str = DEFAULT_RESOLUTION,
        duration: int = DEFAULT_DURATION,
        negative_prompt: str | None = None,
        output_path: str | None = None,
    ) -> Path:
        """图片 + 文本生成视频（图生视频）

        Args:
            prompt: 动画描述文本
            image_path: 输入图片路径
            aspect_ratio: 宽高比
            resolution: 分辨率
            duration: 时长(秒)
            negative_prompt: 不希望出现的内容描述
            output_path: 输出文件路径

        Returns:
            保存的视频文件路径
        """
        self._validate_params(aspect_ratio, resolution, duration)

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {image_path}")

        # 上传图片到 Gemini
        print(f"正在上传图片: {image_path}")
        uploaded_image = self.client.files.upload(file=image_path)

        config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            duration_seconds=duration,
            negative_prompt=negative_prompt,
        )

        print(f"正在生成视频...")
        print(f"  提示词: {prompt}")
        print(f"  参考图: {image_path}")
        print(f"  宽高比: {aspect_ratio} | 分辨率: {resolution} | 时长: {duration}s")

        operation = self.client.models.generate_videos(
            model=self.model,
            prompt=prompt,
            image=uploaded_image,
            config=config,
        )

        return self._wait_and_save(operation, output_path)

    def _validate_params(
        self, aspect_ratio: str, resolution: str, duration: int
    ) -> None:
        """校验参数合法性"""
        if aspect_ratio not in VALID_ASPECT_RATIOS:
            raise ValueError(
                f"不支持的宽高比 '{aspect_ratio}'，可选: {VALID_ASPECT_RATIOS}"
            )
        if resolution not in VALID_RESOLUTIONS:
            raise ValueError(
                f"不支持的分辨率 '{resolution}'，可选: {VALID_RESOLUTIONS}"
            )
        if duration not in VALID_DURATIONS:
            raise ValueError(
                f"不支持的时长 {duration}s，可选: {VALID_DURATIONS}"
            )
        # 1080p 和 4k 仅支持 8 秒
        if resolution in ("1080p", "4k") and duration != 8:
            raise ValueError(
                f"{resolution} 分辨率仅支持 8 秒时长，当前设置: {duration}s"
            )

    def _wait_and_save(
        self, operation, output_path: str | None
    ) -> Path:
        """轮询等待生成完成并保存视频"""
        elapsed = 0
        while not operation.done:
            print(f"  等待生成中... (已等待 {elapsed}s)")
            time.sleep(POLL_INTERVAL)
            elapsed += POLL_INTERVAL
            operation = self.client.operations.get(operation)

        # 检查是否成功
        if not operation.response or not operation.response.generated_videos:
            raise RuntimeError("视频生成失败: 未返回生成结果")

        video = operation.response.generated_videos[0]

        # 确定输出路径
        if output_path is None:
            timestamp = int(time.time())
            output_path = f"video_{timestamp}.mp4"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 下载并保存
        print(f"正在下载视频...")
        self.client.files.download(file=video.video)
        video.video.save(str(output_path))

        print(f"视频已保存: {output_path}")
        print(f"总耗时: {elapsed}s")
        return output_path


# ──────────────────────────────────────────────
# CLI 入口
# ──────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Gemini Veo 视频生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 文本生成视频（默认 9:16 竖屏 720p 8s）
  python generate_video.py "一只橘猫在钢琴上弹月光奏鸣曲"

  # 指定横屏 1080p
  python generate_video.py "日落时分的海滩" --ratio 16:9 --resolution 1080p

  # 图片生成视频
  python generate_video.py "让画面中的人物跳舞" --image photo.jpg

  # 指定输出路径和负面提示词
  python generate_video.py "森林中的小鹿" -o deer.mp4 --negative "模糊,低质量"
        """,
    )

    parser.add_argument("prompt", help="视频描述文本")

    parser.add_argument(
        "--image", "-i",
        help="参考图片路径（图生视频模式）",
    )
    parser.add_argument(
        "--ratio", "-r",
        default=DEFAULT_ASPECT_RATIO,
        choices=VALID_ASPECT_RATIOS,
        help=f"宽高比 (默认: {DEFAULT_ASPECT_RATIO})",
    )
    parser.add_argument(
        "--resolution", "-res",
        default=DEFAULT_RESOLUTION,
        choices=VALID_RESOLUTIONS,
        help=f"分辨率 (默认: {DEFAULT_RESOLUTION})",
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=DEFAULT_DURATION,
        choices=VALID_DURATIONS,
        help=f"视频时长秒数 (默认: {DEFAULT_DURATION})",
    )
    parser.add_argument(
        "--negative", "-n",
        help="负面提示词（不希望出现的内容）",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径 (默认: video_<timestamp>.mp4)",
    )
    parser.add_argument(
        "--api-key",
        help="Google AI API Key (默认从 GEMINI_API_KEY 环境变量读取)",
    )

    return parser


def main() -> None:
    """CLI 主入口"""
    parser = build_parser()
    args = parser.parse_args()

    try:
        gen = GeminiVideoGenerator(api_key=args.api_key)

        if args.image:
            path = gen.generate_from_image(
                prompt=args.prompt,
                image_path=args.image,
                aspect_ratio=args.ratio,
                resolution=args.resolution,
                duration=args.duration,
                negative_prompt=args.negative,
                output_path=args.output,
            )
        else:
            path = gen.generate_from_text(
                prompt=args.prompt,
                aspect_ratio=args.ratio,
                resolution=args.resolution,
                duration=args.duration,
                negative_prompt=args.negative,
                output_path=args.output,
            )

        print(f"\n完成! 视频文件: {path}")

    except ValueError as e:
        print(f"参数错误: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"文件错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"生成失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
