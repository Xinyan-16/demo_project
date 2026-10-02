#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用法说明：
  python todo.py list          列出所有任务（未完成显示 [ ]，已完成显示 [x]）
  python todo.py add "内容"    添加一个新任务
任务保存在同目录下的 todos.json 文件中。
"""

import json  # 用于读写 JSON 文件
import os    # 用于拼接文件路径
import sys   # 用于解析命令行参数

# todos.json 与本脚本放在同一目录
TODO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")


def load_todos():
    """从 todos.json 读取任务列表；文件不存在或损坏时返回空列表"""
    if not os.path.exists(TODO_FILE):
        return []
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def save_todos(todos):
    """把任务列表写回 todos.json"""
    with open(TODO_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def cmd_list():
    """按序号列出所有任务；没有任务时显示（暂无任务）"""
    todos = load_todos()
    print("=== TODO 清单 ===")
    if not todos:
        print("（暂无任务）")
        return
    for i, todo in enumerate(todos, start=1):
        # 完成状态：[x] 已完成，[ ] 未完成
        mark = "[x]" if todo.get("done") else "[ ]"
        print(f"{i}. {mark} {todo.get('title', '')}")


def cmd_add(title):
    """添加一个新任务，默认未完成"""
    todos = load_todos()
    todos.append({"title": title, "done": False})
    save_todos(todos)
    print(f"已添加任务：{title}")


def main():
    # 用 sys.argv 解析参数：第一个是脚本名，后面是子命令和参数
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return

    command = args[0]
    if command == "list":
        cmd_list()
    elif command == "add":
        if len(args) < 2:
            print('用法：python todo.py add "内容"')
            return
        cmd_add(args[1])
    else:
        print(f"未知命令：{command}")
        print(__doc__)


if __name__ == "__main__":
    main()
