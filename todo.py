#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用法说明：
  python todo.py list          列出所有任务（未完成显示 [ ]，已完成显示 [√]）
  python todo.py add "内容"    添加一个新任务
  python todo.py done <序号>   将第 N 个任务标记为已完成
  python todo.py rm <序号>     删除第 N 个任务
  python todo.py stats         统计任务数量
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
        mark = "[√]" if todo.get("done") else "[ ]"
        print(f"{i}. {mark} {todo.get('title', '')}")


def cmd_add(title):
    """添加一个新任务，默认未完成"""
    todos = load_todos()
    todos.append({"title": title, "done": False})
    save_todos(todos)
    print(f"已添加任务：{title}")


def cmd_done(index_str):
    """将第 N 个任务标记为已完成"""
    todos = load_todos()
    try:
        index = int(index_str)
    except ValueError:
        print(f"无效序号：{index_str}（请输入数字）")
        return
    # 序号从 1 开始，换算成列表下标需要减 1
    if index < 1 or index > len(todos):
        print(f"序号 {index} 不存在，当前共有 {len(todos)} 个任务")
        return
    todos[index - 1]["done"] = True
    save_todos(todos)
    print(f"已完成：{todos[index - 1]['title']}")


def cmd_rm(index_str):
    """删除第 N 个任务"""
    todos = load_todos()
    try:
        index = int(index_str)
    except ValueError:
        print(f"无效序号：{index_str}（请输入数字）")
        return
    if index < 1 or index > len(todos):
        print(f"序号 {index} 不存在，当前共有 {len(todos)} 个任务")
        return
    removed = todos.pop(index - 1)
    save_todos(todos)
    print(f"已删除：{removed['title']}")


def cmd_stats():
    """统计任务总数、已完成数和未完成数"""
    todos = load_todos()
    total = len(todos)
    done = sum(1 for t in todos if t.get("done"))
    print(f"共 {total} 项，已完成 {done} 项，未完成 {total - done} 项")


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
    elif command == "done":
        if len(args) < 2:
            print("用法：python todo.py done <序号>")
            return
        cmd_done(args[1])
    elif command == "rm":
        if len(args) < 2:
            print("用法：python todo.py rm <序号>")
            return
        cmd_rm(args[1])
    elif command == "stats":
        cmd_stats()
    else:
        print(f"未知命令：{command}")
        print(__doc__)


if __name__ == "__main__":
    main()
