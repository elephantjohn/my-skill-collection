"""
百度文本审核 + 自动修正工具

用法（命令行）:
    python censor.py <text_file>              # 审核文件内容
    python censor.py --text "待审核文本"       # 审核字符串
    python censor.py <text_file> --fix        # 不合规时自动修正（最多3次）
    python censor.py <text_file> --fix --max-retries 5

环境变量（必须）:
    TEXT_API_KEY    百度文本审核 API Key
    TEXT_SECRET_KEY 百度文本审核 Secret Key

环境变量（--fix 模式必须）:
    BAIDU_API_KEY   百度千帆 API Key / Bearer Token（用于 ernie-4.5-turbo-128k 修正）

编程接口:
    from censor import CensorManager, BaiduTextCensor, BaiduErnieClient
    mgr = CensorManager(
        censor_api_key=..., censor_secret_key=...,
        ernie_api_key=...,  # 可选，不传则无法自动修正
    )
    is_ok, final_text = mgr.censor_and_fix_loop(text, item_id=1, max_retries=3)
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


# ---------------------------------------------------------------------------
# 百度文本审核客户端
# ---------------------------------------------------------------------------

class BaiduTextCensor:
    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    # 百度内容审核平台 API 端点（官方文档：https://cloud.baidu.com/doc/ANTIPORN/s/Rk3h6xb3i）
    CENSOR_URL = "https://aip.baidubce.com/rest/2.0/solution/v1/content_censor/v2/user_defined"

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0.0

    def _get_access_token(self) -> str:
        if self._access_token and time.time() < (self._token_expiry - 60):
            return self._access_token
        resp = requests.post(
            self.TOKEN_URL,
            params={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if "access_token" not in data:
            raise RuntimeError(f"获取token失败: {data}")
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 2592000)
        return self._access_token

    def censor_text(self, text: str) -> Dict:
        """调用百度文本审核 API，返回原始响应 dict。"""
        token = self._get_access_token()
        resp = requests.post(
            self.CENSOR_URL,
            params={"access_token": token},
            data={"text": text},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def parse_result(result: Dict) -> Tuple[bool, List[Dict]]:
        """
        解析审核结果。

        Returns:
            (is_compliant, violations)
            violations: [{"type": ..., "msg": ..., "hits": [...]}]

        conclusionType: 1-合规 2-不合规 3-疑似 4-审核失败
        """
        if "error_code" in result:
            return False, [{"type": "API_ERROR", "msg": result.get("error_msg", ""), "hits": []}]

        conclusion_type = result.get("conclusionType", 1)
        is_compliant = conclusion_type == 1

        violations = []
        if not is_compliant:
            for item in result.get("data", []):
                if item.get("type") and item.get("msg"):
                    hits = []
                    for hit in item.get("hits", []):
                        hits.extend(hit.get("words", []))
                    violations.append({"type": item["type"], "msg": item["msg"], "hits": hits})

        return is_compliant, violations


# ---------------------------------------------------------------------------
# 百度千帆 ERNIE 客户端（用于内容修正）
# ---------------------------------------------------------------------------

class BaiduErnieClient:
    TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"
    CHAT_URL = "https://qianfan.baidubce.com/v2/chat/completions"

    def __init__(self, api_key: str, secret_key: str = ""):
        self.api_key = api_key
        self.secret_key = secret_key
        self._direct_mode = not bool(secret_key)
        self._access_token: Optional[str] = None
        self._token_expiry: float = 0.0

    def _get_access_token(self) -> str:
        if self._direct_mode:
            return self.api_key  # Bearer token 直传模式
        if self._access_token and time.time() < (self._token_expiry - 60):
            return self._access_token
        resp = requests.post(
            self.TOKEN_URL,
            params={
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.secret_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 2592000)
        return self._access_token

    def chat(
        self,
        messages: List[Dict],
        model: str = "ernie-4.5-turbo-128k",
        temperature: float = 0.3,
        max_tokens: int = 5000,
    ) -> str:
        """调用 chat completions，返回助手回复文本。"""
        token = self._get_access_token()
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        for url, headers in [
            (self.CHAT_URL, {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}),
            (f"{self.CHAT_URL}?access_token={token}", {"Content-Type": "application/json"}),
        ]:
            resp = requests.post(url, json=payload, headers=headers, timeout=300)
            if resp.status_code in (401, 403):
                continue
            resp.raise_for_status()
            data = resp.json()
            # 兼容 result / choices 两种响应格式
            if "result" in data:
                return data["result"]
            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                return msg.get("content", "")
            return str(data)
        raise RuntimeError("ERNIE 鉴权全部失败")


# ---------------------------------------------------------------------------
# 审核 + 修正循环
# ---------------------------------------------------------------------------

class CensorManager:
    """
    主类：审核 + 自动修正循环。

    Args:
        censor_api_key: 百度文本审核 API Key（TEXT_API_KEY）
        censor_secret_key: 百度文本审核 Secret Key（TEXT_SECRET_KEY）
        ernie_api_key: 千帆 API Key（BAIDU_API_KEY），不传则禁用自动修正
        ernie_secret_key: 千帆 Secret Key（可选，不传则使用直传模式）
        logs_dir: 审核/修正日志保存目录（可选）
    """

    def __init__(
        self,
        censor_api_key: str,
        censor_secret_key: str,
        ernie_api_key: Optional[str] = None,
        ernie_secret_key: str = "",
        logs_dir: Optional[Path] = None,
    ):
        self._censor = BaiduTextCensor(censor_api_key, censor_secret_key)
        self._ernie = BaiduErnieClient(ernie_api_key, ernie_secret_key) if ernie_api_key else None
        self.logs_dir = logs_dir
        if logs_dir:
            logs_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 公开 API
    # ------------------------------------------------------------------

    def censor_once(self, text: str, item_id: int = 0) -> Tuple[bool, List[Dict]]:
        """
        审核一次，返回 (is_compliant, violations)。

        violations: [{"type": ..., "msg": ..., "hits": [...]}]
        """
        print(f"[审核] #{item_id}: 调用百度文本审核...", flush=True)
        raw = self._censor.censor_text(text)
        is_ok, violations = BaiduTextCensor.parse_result(raw)
        self._save_log(f"censor_{item_id:04d}", {"compliant": is_ok, "violations": violations, "raw": raw})

        if is_ok:
            print(f"[审核] #{item_id}: 合规", flush=True)
        else:
            print(f"[审核] #{item_id}: 不合规 — {len(violations)} 项问题", flush=True)
            for v in violations:
                hits_str = ", ".join(v["hits"]) if v["hits"] else "无"
                print(f"         {v['type']}: {v['msg']} | 命中词: {hits_str}", flush=True)

        return is_ok, violations

    def fix_violations(self, text: str, violations: List[Dict], item_id: int = 0) -> str:
        """
        用 ernie-4.5-turbo-128k 对违规内容做最小化修改，返回修正后文本。
        若未配置 ernie_api_key，直接返回原文。
        """
        if not self._ernie:
            print(f"[修正] #{item_id}: 未配置 ERNIE 客户端，跳过修正", flush=True)
            return text

        print(f"[修正] #{item_id}: 使用 ernie-4.5-turbo-128k 修正...", flush=True)
        violation_desc = "\n".join(
            f"- {v['type']}: {v['msg']}" + (f" (涉及词: {', '.join(v['hits'])})" if v["hits"] else "")
            for v in violations
        )
        prompt = (
            f"请根据以下审核反馈，对文本进行最小化修改使其合规。\n\n"
            f"问题：\n{violation_desc}\n\n"
            f"要求：\n"
            f"1. 只针对上述问题修改，保持原文风格和情节\n"
            f"2. 用委婉、隐喻的表达替代直接描述\n"
            f"3. 不改变核心情节和人物关系\n"
            f"4. 只输出修改后的正文，不要任何说明\n\n"
            f"原文：\n{text}"
        )
        messages = [
            {"role": "system", "content": "你是专业文本编辑，擅长在保持原意的前提下将内容改得更合规。"},
            {"role": "user", "content": prompt},
        ]
        fixed = self._ernie.chat(messages)
        self._save_log(f"fix_{item_id:04d}", {"original_len": len(text), "fixed_len": len(fixed)})
        print(f"[修正] #{item_id}: 修正完成（{len(text)} → {len(fixed)} 字）", flush=True)
        return fixed

    def censor_and_fix_loop(
        self,
        text: str,
        item_id: int = 0,
        max_retries: int = 3,
    ) -> Tuple[bool, str]:
        """
        审核 + 自动修正循环，最多修正 max_retries 次。

        Returns:
            (is_compliant, final_text)
            is_compliant=False 表示达到最大重试仍未通过
        """
        current = text
        for attempt in range(max_retries + 1):
            is_ok, violations = self.censor_once(current, item_id)
            if is_ok:
                return True, current
            if attempt >= max_retries:
                print(f"[审核] #{item_id}: 已达最大重试次数 {max_retries}，审核未通过", flush=True)
                return False, current
            if not violations:
                print(f"[审核] #{item_id}: 无具体违规信息，无法修正", flush=True)
                return False, current
            print(f"[审核] #{item_id}: 第 {attempt + 1} 次修正...", flush=True)
            current = self.fix_violations(current, violations, item_id)
            time.sleep(2)  # 避免限流
        return False, current

    # ------------------------------------------------------------------
    # 内部工具
    # ------------------------------------------------------------------

    def _save_log(self, name: str, data: Dict) -> None:
        if not self.logs_dir:
            return
        log_path = self.logs_dir / f"{name}_{int(time.time())}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 命令行入口
# ---------------------------------------------------------------------------

def _build_manager(fix: bool) -> CensorManager:
    censor_api_key = os.getenv("TEXT_API_KEY", "")
    censor_secret_key = os.getenv("TEXT_SECRET_KEY", "")
    if not censor_api_key or not censor_secret_key:
        sys.exit("错误: 需要设置 TEXT_API_KEY 和 TEXT_SECRET_KEY 环境变量")

    ernie_api_key = os.getenv("BAIDU_API_KEY", "") if fix else None
    if fix and not ernie_api_key:
        sys.exit("错误: --fix 模式需要设置 BAIDU_API_KEY 环境变量")

    return CensorManager(
        censor_api_key=censor_api_key,
        censor_secret_key=censor_secret_key,
        ernie_api_key=ernie_api_key or None,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="百度文本审核 + 自动修正")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("file", nargs="?", help="待审核的文本文件路径")
    group.add_argument("--text", help="直接传入待审核文本字符串")
    parser.add_argument("--fix", action="store_true", help="不合规时自动调用 ERNIE 修正")
    parser.add_argument("--max-retries", type=int, default=3, help="最大修正次数（默认3）")
    parser.add_argument("--output", help="修正后文本保存路径（仅 --fix 模式有效）")
    args = parser.parse_args()

    if args.text:
        text = args.text
    else:
        text = Path(args.file).read_text(encoding="utf-8")

    mgr = _build_manager(args.fix)

    if args.fix:
        is_ok, final = mgr.censor_and_fix_loop(text, max_retries=args.max_retries)
        if args.output:
            Path(args.output).write_text(final, encoding="utf-8")
            print(f"结果已保存: {args.output}")
        print(f"\n{'合规' if is_ok else '未通过'}: 最终文本长度 {len(final)} 字")
        sys.exit(0 if is_ok else 1)
    else:
        is_ok, violations = mgr.censor_once(text)
        sys.exit(0 if is_ok else 1)


if __name__ == "__main__":
    main()
