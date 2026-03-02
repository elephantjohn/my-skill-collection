#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
分段审核 + 针对性修改工具

优化策略：
1. 先审核整篇文章
2. 如果不合规，分段审核定位问题段落
3. 只修改有问题的段落，节省 token
4. 循环直至整篇文章合规
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests


class SegmentedCensorManager:
    """分段审核管理器"""
    
    def __init__(
        self,
        censor_api_key: str,
        censor_secret_key: str,
        ernie_api_key: Optional[str] = None,
        logs_dir: Optional[Path] = None,
    ):
        """初始化
        
        Args:
            censor_api_key: 百度文本审核 API Key
            censor_secret_key: 百度文本审核 Secret Key
            ernie_api_key: 千帆 API Key（用于修正）
            logs_dir: 日志目录
        """
        self.censor_api_key = censor_api_key
        self.censor_secret_key = censor_secret_key
        self.ernie_api_key = ernie_api_key
        self.logs_dir = logs_dir or Path("logs/censor")
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # 百度 API 端点（官方文档：https://cloud.baidu.com/doc/ANTIPORN/s/Rk3h6xb3i）
        self.token_url = "https://aip.baidubce.com/oauth/2.0/token"
        self.censor_url = "https://aip.baidubce.com/rest/2.0/solution/v1/content_censor/v2/user_defined"
        self.chat_url = "https://qianfan.baidubce.com/v2/chat/completions"
        
        self._access_token = None
        self._ernie_token = None
    
    def _get_censor_token(self) -> str:
        """获取审核 API token"""
        if self._access_token and time.time() < (self._token_expiry - 60):
            return self._access_token
        
        resp = requests.post(
            self.token_url,
            params={
                "grant_type": "client_credentials",
                "client_id": self.censor_api_key,
                "client_secret": self.censor_secret_key,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._access_token = data["access_token"]
        self._token_expiry = time.time() + data.get("expires_in", 2592000)
        return self._access_token
    
    def _get_ernie_token(self) -> str:
        """获取 ERNIE API token"""
        if not self.ernie_api_key:
            return ""
        
        if self._ernie_token and time.time() < (self._ernie_token_expiry - 60):
            return self._ernie_token
        
        resp = requests.post(
            self.token_url,
            params={
                "grant_type": "client_credentials",
                "client_id": self.ernie_api_key,
                "client_secret": "",  # 直传模式
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        self._ernie_token = data["access_token"]
        self._ernie_token_expiry = time.time() + data.get("expires_in", 2592000)
        return self._ernie_token
    
    def censor_text(self, text: str) -> Tuple[bool, List[Dict]]:
        """审核文本
        
        Returns:
            (is_compliant, violations)
            violations: [{"type": ..., "msg": ..., "hits": [...]}]
        """
        token = self._get_censor_token()
        resp = requests.post(
            self.censor_url,
            params={"access_token": token},
            data={"text": text},
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        
        # 解析结果
        conclusion_type = result.get("conclusionType", 1)
        is_compliant = conclusion_type == 1
        
        violations = []
        if not is_compliant:
            for item in result.get("data", []):
                if item.get("type") and item.get("msg"):
                    hits = []
                    for hit in item.get("hits", []):
                        hits.extend(hit.get("words", []))
                    violations.append({
                        "type": item["type"],
                        "msg": item["msg"],
                        "hits": hits
                    })
        
        return is_compliant, violations
    
    def censor_and_fix_segmented(
        self,
        content: Dict,
        max_retries: int = 3,
    ) -> Tuple[bool, Dict]:
        """分段审核 + 针对性修改
        
        Args:
            content: 文章内容 JSON 对象
            max_retries: 最大重试次数
            
        Returns:
            (is_compliant, modified_content)
        """
        print(f"[分段审核] 开始审核...", flush=True)
        
        # 提取所有段落
        paragraphs = self._extract_paragraphs(content)
        
        if not paragraphs:
            print("[分段审核] 未找到段落内容", flush=True)
            return True, content
        
        # 先审核整篇文章
        full_text = "\n".join(paragraphs)
        is_ok, violations = self.censor_text(full_text)
        
        if is_ok:
            print("[分段审核] ✅ 整篇文章合规", flush=True)
            return True, content
        
        print(f"[分段审核] ❌ 发现 {len(violations)} 项问题，开始分段定位...", flush=True)
        
        # 分段审核定位问题
        for retry in range(max_retries):
            print(f"\n[分段审核] 第 {retry + 1}/{max_retries} 轮审核", flush=True)
            
            # 审核每个段落
            problem_segments = []
            for i, (key, text) in enumerate(paragraphs.items()):
                is_ok, seg_violations = self.censor_text(text)
                if not is_ok:
                    problem_segments.append({
                        "key": key,
                        "text": text,
                        "violations": seg_violations
                    })
                    print(f"  段落 {key}: ❌ {len(seg_violations)} 项问题", flush=True)
            
            if not problem_segments:
                print("[分段审核] ✅ 所有段落合规", flush=True)
                return True, content
            
            # 只修改有问题的段落
            print(f"[分段审核] 修改 {len(problem_segments)} 个问题段落...", flush=True)
            for seg in problem_segments:
                modified_text = self._fix_segment(seg["text"], seg["violations"])
                paragraphs[seg["key"]] = modified_text
                print(f"  段落 {seg['key']}: ✅ 已修改", flush=True)
            
            # 更新 content
            content = self._update_content(content, paragraphs)
            
            # 重新审核整篇
            full_text = "\n".join(paragraphs)
            is_ok, violations = self.censor_text(full_text)
            
            if is_ok:
                print("[分段审核] ✅ 审核通过！", flush=True)
                return True, content
        
        print(f"[分段审核] ❌ 超过最大重试次数 {max_retries}", flush=True)
        return False, content
    
    def _extract_paragraphs(self, content: Dict) -> Dict[str, str]:
        """提取所有段落内容为字典"""
        paragraphs = {}
        
        # 标题和副标题
        if content.get("title"):
            paragraphs["title"] = content["title"]
        if content.get("subtitle"):
            paragraphs["subtitle"] = content["subtitle"]
        
        # 引言
        if content.get("introduction"):
            paragraphs["introduction"] = content["introduction"]
        
        # 主体段落
        if content.get("paragraphs"):
            for i, para in enumerate(content["paragraphs"]):
                paragraphs[f"paragraph_{i}"] = para
        
        # 故事章节
        if content.get("story_parts"):
            for i, part in enumerate(content["story_parts"]):
                if isinstance(part, dict):
                    paragraphs[f"story_part_{i}"] = part.get("content", "")
                else:
                    paragraphs[f"story_part_{i}"] = str(part)
        
        # 结尾
        if content.get("conclusion"):
            paragraphs["conclusion"] = content["conclusion"]
        if content.get("moral"):
            paragraphs["moral"] = content["moral"]
        
        return paragraphs
    
    def _update_content(self, content: Dict, paragraphs: Dict[str, str]) -> Dict:
        """更新 content 对象"""
        # 更新标题
        if "title" in paragraphs:
            content["title"] = paragraphs["title"]
        if "subtitle" in paragraphs:
            content["subtitle"] = paragraphs["subtitle"]
        
        # 更新引言
        if "introduction" in paragraphs:
            content["introduction"] = paragraphs["introduction"]
        
        # 更新主体段落
        para_list = []
        i = 0
        while f"paragraph_{i}" in paragraphs:
            para_list.append(paragraphs[f"paragraph_{i}"])
            i += 1
        if para_list:
            content["paragraphs"] = para_list
        
        # 更新故事章节
        story_list = []
        i = 0
        while f"story_part_{i}" in paragraphs:
            # 保持原有结构
            if i < len(content.get("story_parts", [])):
                original = content["story_parts"][i]
                if isinstance(original, dict):
                    original["content"] = paragraphs[f"story_part_{i}"]
                    story_list.append(original)
                else:
                    story_list.append(paragraphs[f"story_part_{i}"])
            else:
                story_list.append(paragraphs[f"story_part_{i}"])
            i += 1
        if story_list:
            content["story_parts"] = story_list
        
        # 更新结尾
        if "conclusion" in paragraphs:
            content["conclusion"] = paragraphs["conclusion"]
        if "moral" in paragraphs:
            content["moral"] = paragraphs["moral"]
        
        return content
    
    def _fix_segment(self, text: str, violations: List[Dict]) -> str:
        """修改问题段落"""
        if not self.ernie_api_key:
            print("  [修正] 未配置 ERNIE API，跳过修正", flush=True)
            return text
        
        # 构建违规描述
        violation_desc = "\n".join([
            f"- {v['type']}: {v['msg']}" + (f" (涉及词：{', '.join(v['hits'])})" if v["hits"] else "")
            for v in violations
        ])
        
        prompt = f"""请对以下文本进行最小化修改，使其符合内容规范。

【违规原因】
{violation_desc}

【原文本】
{text}

【要求】
1. 只修改违规部分，保持原文风格和结构
2. 最小化改动，不要重写整段
3. 替换或删除违规词汇
4. 保持语义连贯

请直接返回修改后的文本："""
        
        try:
            token = self._get_ernie_token()
            resp = requests.post(
                self.chat_url,
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "model": "ernie-4.5-turbo-128k",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()
            
            if "result" in data:
                modified = data["result"]
            elif "choices" in data:
                modified = data["choices"][0]["message"]["content"]
            else:
                modified = text
            
            return modified.strip()
            
        except Exception as e:
            print(f"  [修正] 失败：{e}", flush=True)
            return text
    
    def _save_log(self, filename: str, data: Dict):
        """保存日志"""
        log_file = self.logs_dir / f"{filename}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def censor_article_content(content: Dict, max_retries: int = 3) -> Tuple[bool, Dict]:
    """审核文章内容的便捷函数
    
    Args:
        content: 文章内容 JSON
        max_retries: 最大重试次数
        
    Returns:
        (is_compliant, modified_content)
    """
    censor_api_key = os.getenv('TEXT_API_KEY')
    censor_secret_key = os.getenv('TEXT_SECRET_KEY')
    ernie_api_key = os.getenv('BAIDU_API_KEY')
    
    if not censor_api_key or not censor_secret_key:
        print("[审核] 未配置审核 API，跳过审核", flush=True)
        return True, content
    
    mgr = SegmentedCensorManager(
        censor_api_key=censor_api_key,
        censor_secret_key=censor_secret_key,
        ernie_api_key=ernie_api_key,
        logs_dir=Path("logs/censor"),
    )
    
    return mgr.censor_and_fix_segmented(content, max_retries)


if __name__ == "__main__":
    # 测试
    test_content = {
        "title": "测试文章",
        "paragraphs": ["这是第一段测试内容", "这是第二段测试内容"]
    }
    
    is_ok, modified = censor_article_content(test_content)
    print(f"\n审核结果：{'✅ 通过' if is_ok else '❌ 未通过'}")
    print(f"修改后内容：{json.dumps(modified, ensure_ascii=False, indent=2)}")
