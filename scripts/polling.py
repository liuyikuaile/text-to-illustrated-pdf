#!/usr/bin/env python3
"""
任务轮询器 - 从Tasks目录获取未处理的任务

功能：
1. 扫描Tasks目录中的所有.txt文件
2. 检查Results目录中是否有同名的.pdf文件
3. 返回未处理的任务队列（文件名和内容）
"""

import os
import sys
import json
from pathlib import Path

# 目录配置
# 默认使用相对于脚本位置的路径，可通过环境变量覆盖
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.environ.get("TEXT_TO_PDF_DIR", SCRIPT_DIR)

TASKS_DIR = os.path.join(BASE_DIR, "Tasks")
RESULTS_DIR = os.path.join(BASE_DIR, "Results")

def ensure_directories():
    """确保必要目录存在"""
    os.makedirs(TASKS_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

def get_pending_tasks():
    """
    获取所有待处理的任务

    Returns:
        list: 待处理任务列表，每个元素是 {"filename": str, "content": str}
    """
    ensure_directories()

    # 获取已完成的任务（Results中的pdf文件名，去掉扩展名）
    completed_files = set()
    if os.path.exists(RESULTS_DIR):
        for file in os.listdir(RESULTS_DIR):
            if file.endswith('.pdf'):
                completed_files.add(file[:-4])  # 去掉.pdf

    # 扫描Tasks目录
    pending_tasks = []
    if os.path.exists(TASKS_DIR):
        for file in sorted(os.listdir(TASKS_DIR)):
            if file.endswith('.txt'):
                filename_no_ext = file[:-4]  # 去掉.txt
                if filename_no_ext not in completed_files:
                    # 读取文件内容
                    file_path = os.path.join(TASKS_DIR, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        pending_tasks.append({
                            "filename": filename_no_ext,
                            "content": content
                        })
                    except Exception as e:
                        print(f"[ERROR] 读取文件 {file} 失败: {str(e)}", file=sys.stderr)
                        # 记录到错误日志
                        log_error(filename_no_ext, f"读取文件失败: {str(e)}")

    return pending_tasks

def log_error(task_name, error_msg):
    """记录错误日志"""
    log_file = os.path.join(BASE_DIR, "error_log.txt")

    with open(log_file, 'a', encoding='utf-8') as f:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] 任务 {task_name}: {error_msg}\n")

def main():
    """主函数"""
    try:
        pending_tasks = get_pending_tasks()

        if not pending_tasks:
            # 没有待处理任务
            result = {
                "status": "done",
                "message": "所有任务已完成处理",
                "tasks": []
            }
        else:
            # 返回待处理任务队列
            result = {
                "status": "pending",
                "count": len(pending_tasks),
                "tasks": pending_tasks
            }

        # 输出JSON格式
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    except Exception as e:
        error_msg = f"轮询任务失败: {str(e)}"
        print(f"[ERROR] {error_msg}", file=sys.stderr)
        log_error("polling", error_msg)
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
