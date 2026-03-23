#!/usr/bin/env python3
"""
Tavily 图片搜索工具

功能：使用 Tavily API 搜索图片
用法：
    python3 tavily_search.py "搜索关键词"
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse


def search_images_tavily(query, max_results=3):
    """
    使用 Tavily API 搜索图片

    Args:
        query (str): 搜索关键词
        max_results (int): 最大结果数

    Returns:
        dict: 搜索结果
    """
    api_key = os.environ.get("TAVILY_API_KEY")

    if not api_key:
        return {
            "success": False,
            "message": "未设置 TAVILY_API_KEY 环境变量",
            "url": None,
            "title": None,
            "source": None
        }

    # Tavily Search API
    url = "https://api.tavily.com/search"

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_images": True,
        "include_image_descriptions": True
    }

    try:
        # 创建请求
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        # 发送请求
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))

        # 提取图片信息
        if "images" in result and len(result["images"]) > 0:
            # 返回第一张图片
            image = result["images"][0]
            return {
                "success": True,
                "message": "搜索成功",
                "url": image.get("url"),
                "title": image.get("description", query),
                "source": "tavily"
            }
        else:
            return {
                "success": False,
                "message": "未找到相关图片",
                "url": None,
                "title": None,
                "source": None
            }

    except urllib.error.URLError as e:
        return {
            "success": False,
            "message": f"网络错误: {str(e)}",
            "url": None,
            "title": None,
            "source": None
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "message": f"解析错误: {str(e)}",
            "url": None,
            "title": None,
            "source": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"未知错误: {str(e)}",
            "url": None,
            "title": None,
            "source": None
        }


def main():
    if len(sys.argv) < 2:
        print(json.dumps("错误：请提供搜索关键词", ensure_ascii=False))
        return 1

    query = " ".join(sys.argv[1:])
    result = search_images_tavily(query)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
