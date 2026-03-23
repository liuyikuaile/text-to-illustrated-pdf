#!/usr/bin/env python3
"""
结果保存器 - 将 Markdown 转换为 PDF 并保存

职责：
1. 接收 Markdown 内容和文件名
2. 保存中间 Markdown 到 temp/
3. 将 Markdown 转换为 HTML
4. 使用 WeasyPrint 生成 PDF
5. 保存到 Results/ 目录

注意：
- 本文件只负责 PDF 相关工作
- 不再负责任何图片下载、复制、批量保存、单张保存
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from weasyprint import HTML


# 目录配置
# 默认使用相对于脚本位置的路径，可通过环境变量覆盖
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.environ.get("TEXT_TO_PDF_DIR", SCRIPT_DIR)

RESULTS_DIR = os.path.join(BASE_DIR, "Results")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ERROR_LOG_PATH = os.path.join(BASE_DIR, "error_log.txt")
WORKSPACE_DIR = BASE_DIR  # 保持兼容性


def ensure_directories():
    """确保必要目录存在"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)


def log_error(task_name, error_msg):
    """记录错误日志"""
    os.makedirs(BASE_DIR, exist_ok=True)

    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] 任务 {task_name}: {error_msg}\n")


def save_markdown_temp(filename, markdown_content):
    """
    保存中间 Markdown 文件到 temp 目录

    Args:
        filename (str): 文件名（不含扩展名）
        markdown_content (str): Markdown 内容

    Returns:
        str: 保存后的 Markdown 路径
    """
    md_path = os.path.join(TEMP_DIR, f"{filename}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    return md_path


def markdown_to_html(markdown_text, title="文档"):
    """
    将 Markdown 转换为 HTML（优先使用 pandoc，失败则降级）

    Args:
        markdown_text (str): Markdown 文本
        title (str): 文档标题

    Returns:
        str: HTML 内容
    """
    try:
        result = subprocess.run(
            ["pandoc", "-f", "markdown", "-t", "html", "--standalone"],
            input=markdown_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=60,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "pandoc 转换失败")

        html = result.stdout

    except Exception:
        escaped = (
            markdown_text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>
<body>
<pre>{escaped}</pre>
</body>
</html>"""

    custom_style = """
    <style>
    @page {
        size: A4;
        margin: 20mm 16mm 20mm 16mm;
    }

    body {
        font-family: "Microsoft YaHei", "SimHei", Arial, sans-serif;
        line-height: 1.7;
        color: #222;
        font-size: 14px;
        max-width: 800px;
        margin: 0 auto;
        padding: 0;
        background: white;
        word-break: break-word;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #222;
        margin-top: 1.4em;
        margin-bottom: 0.6em;
        line-height: 1.35;
    }

    h1 {
        font-size: 24px;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 8px;
    }

    h2 {
        font-size: 20px;
    }

    h3 {
        font-size: 17px;
    }

    p {
        margin: 0.8em 0;
        text-align: justify;
    }

    ul, ol {
        margin: 0.8em 0 0.8em 1.5em;
        padding: 0;
    }

    li {
        margin: 0.35em 0;
    }

    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 18px auto;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    }

    code {
        background: #f5f5f5;
        padding: 2px 5px;
        border-radius: 3px;
        font-family: "Consolas", "Monaco", monospace;
        font-size: 0.95em;
    }

    pre {
        background: #f5f5f5;
        padding: 14px;
        border-radius: 6px;
        overflow-wrap: anywhere;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    blockquote {
        margin: 1em 0;
        padding: 0.8em 1em;
        border-left: 4px solid #d1d5db;
        background: #fafafa;
        color: #444;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
        font-size: 13px;
    }

    th, td {
        border: 1px solid #dcdcdc;
        padding: 8px 10px;
        vertical-align: top;
        text-align: left;
    }

    th {
        background: #f3f4f6;
        font-weight: bold;
    }

    hr {
        border: none;
        border-top: 1px solid #e5e7eb;
        margin: 1.5em 0;
    }
    </style>
    """

    if "</head>" in html:
        html = html.replace("</head>", f"{custom_style}\n</head>")
    else:
        html = f"<html><head>{custom_style}</head><body>{html}</body></html>"

    return html


def save_pdf(filename, markdown_content):
    """
    保存 PDF

    Args:
        filename (str): 文件名（不含扩展名）
        markdown_content (str): Markdown 内容

    Returns:
        dict: 结果信息
    """
    ensure_directories()

    md_path = None
    pdf_path = None

    try:
        md_path = save_markdown_temp(filename, markdown_content)

        html_content = markdown_to_html(markdown_content, title=filename)
        pdf_path = os.path.join(RESULTS_DIR, f"{filename}.pdf")

        # base_url 设为工作区，便于 HTML 中引用本地绝对/相对资源
        HTML(string=html_content, base_url=WORKSPACE_DIR).write_pdf(pdf_path)

        return {
            "success": True,
            "message": f"PDF已成功保存到 {pdf_path}",
            "pdf_path": pdf_path,
            "markdown_path": md_path,
        }

    except Exception as e:
        error_msg = f"PDF转换失败: {str(e)}"
        log_error(filename, error_msg)

        return {
            "success": False,
            "message": error_msg,
            "pdf_path": pdf_path,
            "markdown_path": md_path,
        }


def main():
    parser = argparse.ArgumentParser(description="Markdown 转 PDF 保存器")
    parser.add_argument("--filename", required=True, help="文件名（不含扩展名）")
    args = parser.parse_args()

    markdown_content = sys.stdin.read()

    if not markdown_content.strip():
        result = {
            "success": False,
            "message": "未从 stdin 读取到 Markdown 内容",
            "pdf_path": None,
            "markdown_path": None,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    result = save_pdf(args.filename, markdown_content)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())