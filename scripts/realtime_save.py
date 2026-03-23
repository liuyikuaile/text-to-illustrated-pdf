#!/usr/bin/env python3
"""
实时图片保存器

职责：
1. 在拿到图片 URL 或本地图片路径后，立即保存到 Results/同名文件夹/
2. 支持远程下载和本地复制
3. 返回稳定 JSON，供 LLM 继续组织 Markdown
4. 不再调用 save.py

用法：
    python3 realtime_save.py --filename "任务名" --image-url "https://example.com/a.jpg"
    python3 realtime_save.py --filename "任务名" --image-url "/path/to/local.png" --image-index 3
"""

import os
import sys
import json
import argparse
import hashlib
import shutil
from urllib.parse import urlparse, unquote

import requests


# 目录配置
# 默认使用相对于脚本位置的路径，可通过环境变量覆盖
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.environ.get("TEXT_TO_PDF_DIR", SCRIPT_DIR)

RESULTS_DIR = os.path.join(BASE_DIR, "Results")
ERROR_LOG_PATH = os.path.join(BASE_DIR, "error_log.txt")
WORKSPACE_DIR = BASE_DIR  # 保持兼容性


def ensure_directories():
    """确保必要目录存在"""
    os.makedirs(RESULTS_DIR, exist_ok=True)


def log_error(task_name, error_msg):
    """记录错误日志"""
    os.makedirs(BASE_DIR, exist_ok=True)

    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] 任务 {task_name}: {error_msg}\n")


def is_remote_url(path_or_url):
    """判断是否为远程 URL"""
    return path_or_url.startswith("http://") or path_or_url.startswith("https://")


def sanitize_filename_component(name):
    """清理不安全文件名字符"""
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, "_")
    return name.strip().strip(".")


def detect_extension_from_url(url):
    """从 URL 猜测扩展名"""
    parsed = urlparse(url)
    path = unquote(parsed.path)
    basename = os.path.basename(path)
    _, ext = os.path.splitext(basename)
    ext = ext.lower()

    if ext in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}:
        return ext

    return ""


def detect_extension_from_content_type(content_type):
    """从 content-type 推断扩展名"""
    if not content_type:
        return ".jpg"

    content_type = content_type.lower()

    mapping = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "image/bmp": ".bmp",
    }

    for key, ext in mapping.items():
        if key in content_type:
            return ext

    return ".jpg"


def make_filename(source, index=None, content_type=None):
    """
    生成保存文件名
    优先保留原始文件名特征，不足时回退到哈希
    """
    if is_remote_url(source):
        parsed = urlparse(source)
        base = os.path.basename(unquote(parsed.path))
    else:
        base = os.path.basename(source)

    base = sanitize_filename_component(base)

    stem, ext = os.path.splitext(base)
    if not stem:
        stem = "image"

    if not ext:
        ext = detect_extension_from_url(source)

    if not ext:
        ext = detect_extension_from_content_type(content_type)

    if len(stem) > 80:
        stem = stem[:80]

    source_hash = hashlib.md5(source.encode("utf-8")).hexdigest()[:10]

    if index is None:
        return f"{stem}_{source_hash}{ext}"
    return f"{stem}_{index}{ext}"


def next_available_index(image_dir):
    """返回目录内下一个可用序号"""
    if not os.path.exists(image_dir):
        return 0

    files = [
        f for f in os.listdir(image_dir)
        if os.path.isfile(os.path.join(image_dir, f))
    ]
    return len(files)


def save_remote_image(image_url, image_dir, index=None, timeout=60):
    """下载远程图片到本地"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    with requests.get(
        image_url,
        headers=headers,
        timeout=timeout,
        stream=True,
        allow_redirects=True,
    ) as response:
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        filename = make_filename(image_url, index=index, content_type=content_type)
        save_path = os.path.join(image_dir, filename)

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    return filename, save_path


def save_local_image(local_path, image_dir, index=None):
    """复制本地图片到目标目录"""
    if not os.path.exists(local_path):
        raise FileNotFoundError("本地文件不存在")

    filename = make_filename(local_path, index=index)
    save_path = os.path.join(image_dir, filename)
    shutil.copy2(local_path, save_path)

    return filename, save_path


def save_image_immediately(filename, image_url, index=None, timeout=60):
    """
    立即保存单张图片

    Args:
        filename (str): 任务文件名（不含扩展名）
        image_url (str): 图片 URL 或本地路径
        index (int | None): 图片序号
        timeout (int): 下载超时时间

    Returns:
        dict: 保存结果
    """
    ensure_directories()

    image_dir = os.path.join(RESULTS_DIR, filename)
    os.makedirs(image_dir, exist_ok=True)

    try:
        final_index = index if index is not None else next_available_index(image_dir)

        if is_remote_url(image_url):
            saved_filename, local_path = save_remote_image(
                image_url, image_dir, index=final_index, timeout=timeout
            )
        else:
            saved_filename, local_path = save_local_image(
                image_url, image_dir, index=final_index
            )

        # 生成 Markdown 中使用的相对路径（从 WORKSPACE_DIR 开始）
        markdown_path = os.path.join("Results", filename, saved_filename)

        return {
            "success": True,
            "message": f"图片保存成功: {saved_filename}",
            "url": image_url,
            "filename": saved_filename,
            "local_path": local_path,
            "markdown_path": markdown_path,
            "image_dir": image_dir,
            "index": final_index,
        }

    except Exception as e:
        error_msg = f"单张图片保存失败: {image_url} - {str(e)}"
        log_error(filename, error_msg)

        return {
            "success": False,
            "message": error_msg,
            "url": image_url,
            "filename": None,
            "local_path": None,
            "markdown_path": None,
            "image_dir": image_dir,
            "index": index,
        }


def main():
    parser = argparse.ArgumentParser(description="实时保存单张图片")
    parser.add_argument("--filename", required=True, help="任务文件名（不含扩展名）")
    parser.add_argument("--image-url", required=True, help="图片 URL 或本地路径")
    parser.add_argument("--image-index", type=int, required=False, help="图片序号")
    parser.add_argument("--timeout", type=int, default=60, help="下载超时时间（秒）")

    args = parser.parse_args()

    result = save_image_immediately(
        filename=args.filename,
        image_url=args.image_url,
        index=args.image_index,
        timeout=args.timeout,
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())