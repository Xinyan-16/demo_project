#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用法说明：
  python todo.py list          列出每日日程与所有任务（未完成显示 [ ]，已完成显示 [√]）
  python todo.py add "内容"    添加一个新任务
  python todo.py done <序号>   将第 N 个任务标记为已完成
  python todo.py rm <序号>     删除第 N 个任务
  python todo.py stats         统计任务数量
  python todo.py prio <序号>   将第 N 个任务标记为高优先级
  python todo.py daily add "内容"    添加新的每日日程
  python todo.py daily done <序号>   把今天的第 N 个日程标记为完成
  python todo.py daily rm <序号>     删除今天的第 N 个日程
任务保存在同目录下的 todos.json 文件中；每日日程保存在 daily.json 文件中。
"""

import json        # 用于读写 JSON 文件
import os         # 用于拼接文件路径
import sys        # 用于解析命令行参数
import datetime   # 用于日期判断与每日重置
# ANSI 颜色代码
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"      # 重置回默认色

# todos.json 与本脚本放在同一目录
TODO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")
# daily.json 用于保存每日日程，每条记录包含：title, done, date
DAILY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daily.json")


def today_str():
    """返回今天日期字符串，如 '2026-10-20'"""
    return datetime.date.today().isoformat()


def yesterday_str():
    """返回昨天日期字符串"""
    return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()


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


# ---------------- 每日日程相关 ----------------

def load_daily():
    """从 daily.json 读取每日日程列表；文件不存在或损坏时返回空列表"""
    if not os.path.exists(DAILY_FILE):
        return []
    try:
        with open(DAILY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def save_daily(daily):
    """把每日日程列表写回 daily.json"""
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump(daily, f, ensure_ascii=False, indent=2)


def reset_daily_if_new_day(daily):
    """
    如果跨天了，把所有日程的完成状态重置为 False，
    并把昨天的 done 保存到 yesterday_done 字段，供 list 显示。
    日程名字（模板）永久保留，每天只重置完成状态。
    """
    today = today_str()
    changed = False
    for d in daily:
        if d.get("date") != today:
            d["yesterday_done"] = d.get("done", False)
            d["done"] = False
            d["date"] = today
            changed = True
    if changed:
        save_daily(daily)
    return daily


def get_daily():
    """加载每日日程，并在必要时自动做跨天重置"""
    return reset_daily_if_new_day(load_daily())


def _next_id(daily):
    """生成下一个日程 id"""
    existing = [d.get("id", 0) for d in daily if isinstance(d.get("id"), int)]
    return max(existing, default=0) + 1


def cmd_daily_add(title):
    """添加一个固定的每日日程模板（永久保存，每天只重置完成状态）"""
    daily = get_daily()
    daily.append({
        "id": _next_id(daily),
        "title": title,
        "done": False,
        "date": today_str(),
        "yesterday_done": None,  # None 表示尚无昨日数据；跨天重置后才会变成布尔值
    })
    save_daily(daily)
    print(f"已添加每日日程：{title}")


def cmd_daily_done(index_str):
    """把今天的第 N 个日程标记为完成"""
    daily = get_daily()
    try:
        index = int(index_str)
    except ValueError:
        print(f"无效序号：{index_str}（请输入数字）")
        return
    if index < 1 or index > len(daily):
        print(f"序号 {index} 不存在，今日共有 {len(daily)} 个日程")
        return
    d = daily[index - 1]
    d["done"] = True
    save_daily(daily)
    print(f"已完成每日日程：{d['title']}")


def cmd_daily_rm(index_str):
    """删除今天的第 N 个日程（即删除该日程模板）"""
    daily = get_daily()
    try:
        index = int(index_str)
    except ValueError:
        print(f"无效序号：{index_str}（请输入数字）")
        return
    if index < 1 or index > len(daily):
        print(f"序号 {index} 不存在，今日共有 {len(daily)} 个日程")
        return
    removed = daily.pop(index - 1)
    save_daily(daily)
    print(f"已删除每日日程：{removed['title']}")


def print_daily_section():
    """打印每日日程部分：前一天状态 + 今日日程"""
    daily = get_daily()

    # 前一天完成情况：根据保存的 yesterday_done 判断
    if not daily:
        print("前一天无日程")
        return

    yesterday_flags = [d.get("yesterday_done") for d in daily]
    if all(f is None for f in yesterday_flags):
        # 尚未发生过跨天重置，说明是第一天使用，没有昨日数据
        print("前一天无日程")
    else:
        # 只有真正有昨日数据的条目才参与判断
        real_flags = [f for f in yesterday_flags if f is not None]
        all_done = all(real_flags)
        if all_done:
            print(f"{GREEN}前一天日程全部完成！{RESET}")
        else:
            print(f"{RED}前一天日程未完成，再接再厉{RESET}")

    # 今日日程（固定模板，已在 get_daily 中重置完成状态）
    print("今日日程：")
    if not daily:
        print("（今日无日程）")
    else:
        for i, d in enumerate(daily, start=1):
            mark = "[√]" if d.get("done") else "[ ]"
            title = d.get("title", "")
            if d.get("done"):
                print(f"{i}. {mark} {GREEN}{title}{RESET}")
            else:
                print(f"{i}. {mark} {title}")


def cmd_list():
    """列出每日日程与普通任务；没有任务时显示（暂无任务）"""
    print_daily_section()
    print("——————————————————————")
    print("任务：")

    todos = load_todos()
    if not todos:
        print("（暂无任务）")
        return
    for i, todo in enumerate(todos, start=1):
        mark = "[√]" if todo.get("done") else "[ ]"
        title = todo.get("title", "")

        if todo.get("prio"):
            # 高优先级：红色
            line = f"{i}. {mark} {RED}{title}{RESET}"
        elif todo.get("done"):
            # 已完成：绿色
            line = f"{i}. {mark} {GREEN}{title}{RESET}"
        else:
            # 普通：默认色
            line = f"{i}. {mark} {title}"

        print(line)


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

    # 在唤起游戏前，先在终端打印当前任务清单（输出与 list 命令完全一致）
    cmd_list()

    # 完成任务奖励：启动贪吃蛇小游戏（失败不影响主程序）
    try:
        from snake_game import run_snake_game
        run_snake_game()
    except Exception as e:  # pygame 未安装等情况，只提示，不中断
        print(f"(奖励游戏未能启动：{e})")


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


def cmd_prio(index_str):
    """将第 N 个任务标记为高优先级"""
    todos = load_todos()
    try:
        index = int(index_str)
    except ValueError:
        print(f"无效序号：{index_str}（请输入数字）")
        return
    if index < 1 or index > len(todos):
        print(f"序号 {index} 不存在，当前共有 {len(todos)} 个任务")
        return
    todos[index - 1]["prio"] = True
    save_todos(todos)
    print(f"已标记高优先级：{todos[index - 1]['title']}")


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
    elif command == "prio":
        if len(args) < 2:
            print("用法：python todo.py prio <序号>")
            return
        cmd_prio(args[1])
    elif command == "stats":
        cmd_stats()
    elif command == "daily":
        if len(args) < 2:
            print('用法：python todo.py daily <add|done|rm> ...')
            print('  daily add "内容"')
            print("  daily done <序号>")
            print("  daily rm <序号>")
            return
        sub = args[1]
        if sub == "add":
            if len(args) < 3:
                print('用法：python todo.py daily add "内容"')
                return
            cmd_daily_add(args[2])
        elif sub == "done":
            if len(args) < 3:
                print("用法：python todo.py daily done <序号>")
                return
            cmd_daily_done(args[2])
        elif sub == "rm":
            if len(args) < 3:
                print("用法：python todo.py daily rm <序号>")
                return
            cmd_daily_rm(args[2])
        else:
            print(f"未知每日日程命令：{sub}")
    else:
        print(f"未知命令：{command}")
        print(__doc__)


if __name__ == "__main__":
    main()