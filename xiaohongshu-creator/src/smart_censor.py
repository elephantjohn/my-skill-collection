"""
小红书智能审核器
分段定位 + 局部修改，最小化 token 消耗
"""

import os
import logging
from typing import List, Tuple, Dict, Any
from pathlib import Path

# 导入百度审核模块（假设在同一项目或已安装）
try:
    from baidu_content_censor.scripts.censor import CensorManager
except ImportError:
    # 如果无法导入，使用简化的模拟实现
    CensorManager = None

logger = logging.getLogger(__name__)


class SmartCensor:
    """智能审核器 - 分段定位 + 局部修改"""

    def __init__(
        self,
        text_api_key: str = None,
        text_secret_key: str = None,
        baidu_api_key: str = None,
        max_retries: int = 3,
        segment_size: int = 500,  # 每段字数
    ):
        """
        初始化审核器

        Args:
            text_api_key: 百度文本审核 API Key
            text_secret_key: 百度文本审核 Secret Key
            baidu_api_key: 百度千帆 API Key（用于修正）
            max_retries: 最大重试次数
            segment_size: 分段大小（字数）
        """
        self.text_api_key = text_api_key or os.getenv("TEXT_API_KEY")
        self.text_secret_key = text_secret_key or os.getenv("TEXT_SECRET_KEY")
        self.baidu_api_key = baidu_api_key or os.getenv("BAIDU_API_KEY")
        self.max_retries = max_retries
        self.segment_size = segment_size

        # 初始化百度审核管理器
        if CensorManager:
            self.censor_mgr = CensorManager(
                censor_api_key=self.text_api_key,
                censor_secret_key=self.text_secret_key,
                ernie_api_key=self.baidu_api_key,
            )
        else:
            self.censor_mgr = None
            logger.warning("CensorManager 未找到，使用模拟审核")

    def censor_and_fix(self, text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        智能审核 + 修正

        流程：
        1. 整体审核
        2. 如果不通过，分段定位问题
        3. 只修改问题段落
        4. 重新审核，直到通过或达到最大重试

        Args:
            text: 待审核文本

        Returns:
            (是否通过，最终文本，审核详情)
        """
        logger.info(f"🔍 开始智能审核（{len(text)} 字）")

        # 第 1 步：整体审核
        is_ok, violations = self._censor_once(text)
        detail = {
            "total_segments": 0,
            "problem_segments": 0,
            "retries": 0,
            "violations": violations,
        }

        if is_ok:
            logger.info("✅ 整体审核通过")
            return True, text, detail

        logger.warning(f"⚠️ 整体审核未通过，发现 {len(violations)} 个问题")

        # 第 2 步：分段定位
        segments = self._split_into_segments(text)
        detail["total_segments"] = len(segments)

        problem_indices = []
        for i, segment in enumerate(segments):
            seg_ok, _ = self._censor_once(segment)
            if not seg_ok:
                problem_indices.append(i)

        detail["problem_segments"] = len(problem_indices)
        logger.warning(f"🎯 定位到 {len(problem_indices)} 个问题段落：{problem_indices}")

        # 第 3 步：局部修改 + 重试循环
        retries = 0
        current_text = text

        while retries < self.max_retries:
            retries += 1
            detail["retries"] = retries

            # 只修改问题段落
            modified_segments = segments.copy()
            for idx in problem_indices:
                logger.info(f"📝 修改第 {idx} 段...")
                modified_segments[idx] = self._fix_segment(
                    modified_segments[idx], violations
                )

            current_text = "\n".join(modified_segments)

            # 重新审核
            is_ok, violations = self._censor_once(current_text)
            detail["violations"] = violations

            if is_ok:
                logger.info(f"✅ 审核通过（重试 {retries} 次）")
                return True, current_text, detail

            logger.warning(f"⚠️ 仍未通过，继续修改...")

            # 更新问题段落索引
            segments = modified_segments
            problem_indices = []
            for i, segment in enumerate(segments):
                seg_ok, _ = self._censor_once(segment)
                if not seg_ok:
                    problem_indices.append(i)

            if not problem_indices:
                # 没有明确问题段落，但整体仍未通过
                logger.warning("⚠️ 无法定位具体问题段落，尝试整体修改")
                current_text = self._fix_segment(current_text, violations)
                is_ok, violations = self._censor_once(current_text)
                if is_ok:
                    return True, current_text, detail

        logger.error(f"❌ 达到最大重试次数 ({self.max_retries})，审核失败")
        return False, current_text, detail

    def _censor_once(self, text: str) -> Tuple[bool, List[Dict]]:
        """审核一次"""
        if self.censor_mgr:
            is_ok, violations = self.censor_mgr.censor_once(text)
            return is_ok, violations
        else:
            # 模拟审核（总是通过）
            logger.debug("使用模拟审核（总是通过）")
            return True, []

    def _split_into_segments(self, text: str, size: int = None) -> List[str]:
        """
        将文本分段

        Args:
            text: 原文本
            size: 每段大小（默认使用初始化的 segment_size）

        Returns:
            段落列表
        """
        size = size or self.segment_size
        segments = []

        # 按自然段落分割
        paragraphs = text.split("\n")
        current_segment = ""

        for para in paragraphs:
            if len(current_segment) + len(para) <= size:
                current_segment += para + "\n"
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = para + "\n"

        if current_segment:
            segments.append(current_segment.strip())

        return segments

    def _fix_segment(self, segment: str, violations: List[Dict]) -> str:
        """
        修改问题段落

        Args:
            segment: 问题段落
            violations: 违规信息

        Returns:
            修改后的段落
        """
        if not self.censor_mgr or not self.baidu_api_key:
            logger.warning("无法修正，返回原段落")
            return segment

        # 构建修改提示
        violation_msgs = [v.get("msg", "") for v in violations]
        prompt = f"""
请对以下文本进行最小化修改，使其符合内容规范：

原文本：
{segment}

问题提示：
{", ".join(violation_msgs)}

要求：
1. 只修改有问题的词语或句子
2. 保持原文风格和意思
3. 修改幅度尽可能小
4. 直接返回修改后的文本，不要解释

修改后：
"""

        # 调用百度千帆 API 修改
        try:
            from google import genai
            client = genai.Client()
            response = client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt,
            )
            fixed_text = response.text.strip()
            logger.info(f"✅ 段落修改完成（{len(segment)}字 → {len(fixed_text)}字）")
            return fixed_text
        except Exception as e:
            logger.error(f"❌ 段落修改失败：{e}")
            return segment


# 测试
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    censor = SmartCensor()

    test_text = """
这是一篇测试文章。
内容健康向上，没有任何违规。
适合在小红书平台发布。
"""

    is_ok, final_text, detail = censor.censor_and_fix(test_text)
    print(f"\n审核结果：{'通过' if is_ok else '未通过'}")
    print(f"详情：{detail}")
