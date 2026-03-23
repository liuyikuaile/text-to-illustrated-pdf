#!/usr/bin/env python3
"""Creaa AI image generation helper for text-to-illustrated-pdf.

风格尽量对齐 tavily_search.py：
- 暴露简单、直接的主函数给 Agent 调用
- CLI 参数尽量少且直白
- 返回 JSON-friendly dict/list 结构
- 失败时统一返回 success=False，而不是抛复杂异常给上层
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional

API_BASE = "https://creaa.ai/api/open/v1"
GENERATE_URL = f"{API_BASE}/images/generate"
TASK_URL = f"{API_BASE}/tasks/{{task_id}}"
DEFAULT_MODEL = "seedream-5.0"
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_POLL_INTERVAL = 8
DEFAULT_TIMEOUT = 300
DEFAULT_SOURCE = "openclaw"


def _request_json(url: str, *, method: str = "GET", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    api_key = os.getenv("CREAA_API_KEY")
    if not api_key:
        return {
            "success": False,
            "error": "CREAA_API_KEY not set",
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-Source": DEFAULT_SOURCE,
        "User-Agent": "openclaw",  # 关键：添加 User-Agent 避免被 API 拒绝
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", errors="ignore")
        except Exception:
            pass
        return {
            "success": False,
            "error": f"HTTP {e.code}",
            "http_status": e.code,
            "error_body": body,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def creaa_submit(prompt: str, model: str = DEFAULT_MODEL, aspect_ratio: str = DEFAULT_ASPECT_RATIO, n: int = 1) -> Dict[str, Any]:
    """提交一张生图任务。"""
    return _request_json(
        GENERATE_URL,
        method="POST",
        payload={
            "prompt": prompt,
            "model": model,
            "aspect_ratio": aspect_ratio,
            "n": n,
        },
    )


def creaa_poll(task_id: str) -> Dict[str, Any]:
    """查询单个任务状态。"""
    return _request_json(TASK_URL.format(task_id=task_id), method="GET")


def creaa_wait(task_id: str, poll_interval: int = DEFAULT_POLL_INTERVAL, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """轮询任务直到 completed / failed / timeout。"""
    deadline = time.time() + timeout
    last: Dict[str, Any] = {}

    while time.time() < deadline:
        last = creaa_poll(task_id)
        status = str(last.get("status", "")).lower()
        if status in {"completed", "failed"}:
            return last
        time.sleep(poll_interval)

    return {
        "success": False,
        "task_id": task_id,
        "status": "timeout",
        "last_response": last,
    }


def creaa_result_url(task_response: Dict[str, Any]) -> Optional[str]:
    """从任务结果中提取第一张图片 URL。"""
    return task_response.get("result_url") or ((task_response.get("result_urls") or [None])[0])


def creaa_download(url: str, output_path: str) -> Dict[str, Any]:
    """下载图片到本地。"""
    try:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "openclaw/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            path.write_bytes(resp.read())
        return {
            "success": True,
            "path": str(path),
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "path": output_path,
        }


def creaa_generate(
    prompt: str,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    n: int = 1,
    wait: bool = True,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    timeout: int = DEFAULT_TIMEOUT,
    download: Optional[str] = None,
) -> Dict[str, Any]:
    """高层封装：提交 → 等待 → 可选下载。"""
    submit = creaa_submit(prompt, model=model, aspect_ratio=aspect_ratio, n=n)
    result: Dict[str, Any] = {
        "success": bool(submit.get("success")),
        "model": model,
        "prompt": prompt,
        "submit": submit,
        "task_id": submit.get("task_id"),
    }

    if not submit.get("success") or not submit.get("task_id") or not wait:
        return result

    task = creaa_wait(submit["task_id"], poll_interval=poll_interval, timeout=timeout)
    result["task"] = task
    result["status"] = task.get("status")

    url = creaa_result_url(task)
    if url:
        result["result_url"] = url

    if download and url:
        download_result = creaa_download(url, download)
        result["download"] = download_result

    if task.get("status") == "completed" and url:
        result["success"] = True
    elif task.get("status") in {"failed", "timeout"}:
        result["success"] = False

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate one image with Creaa AI")
    parser.add_argument("prompt", help="Prompt text")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model name, default: {DEFAULT_MODEL}")
    parser.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO, help=f"Aspect ratio, default: {DEFAULT_ASPECT_RATIO}")
    parser.add_argument("--n", type=int, default=1, help="Number of images to request, default: 1")
    parser.add_argument("--no-wait", action="store_true", help="Only submit task, do not poll")
    parser.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL, help=f"Polling interval seconds, default: {DEFAULT_POLL_INTERVAL}")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help=f"Timeout seconds, default: {DEFAULT_TIMEOUT}")
    parser.add_argument("--download", help="Optional output path for downloaded image")
    args = parser.parse_args()

    result = creaa_generate(
        args.prompt,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        n=args.n,
        wait=not args.no_wait,
        poll_interval=args.poll_interval,
        timeout=args.timeout,
        download=args.download,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
