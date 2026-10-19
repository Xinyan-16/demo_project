#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贪吃蛇小游戏（Pygame），供 todo.py 的“完成任务奖励”调用。

单独运行演示：
    python snake_game.py

在其他脚本中调用：
    from snake_game import run_snake_game
    run_snake_game()
"""

import random

import pygame

# --- 窗口与网格 ---
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
GRID_SIZE = 20
GRID_COLS = WINDOW_WIDTH // GRID_SIZE      # 30 列
GRID_ROWS = WINDOW_HEIGHT // GRID_SIZE     # 20 行

FPS = 10

# 颜色 (R, G, B)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GRAY = (160, 160, 160)

# 按键 -> 移动方向 (dx, dy)
KEY_DIR = {
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
}


def _font(size):
    """尽量使用能显示中文的系统字体，找不到则回退默认字体。"""
    return pygame.font.SysFont("simhei,microsoft yahei,arial", size)


def draw_text(screen, font, text, color, center):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)


def wait_screen(screen, font):
    """
    等待界面：“任务已完成！是否开始贪吃蛇游戏？(按 Y 开始 / 按 N 退出)”
    返回 True 表示开始游戏，False 表示退出回到终端。
    """
    clock = pygame.time.Clock()
    while True:
        screen.fill(BLACK)
        draw_text(screen, font, "任务已完成！", WHITE,
                  (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        draw_text(screen, font, "是否开始贪吃蛇游戏？", WHITE,
                  (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        draw_text(screen, font, "(按 Y 开始 / 按 N 退出)", GRAY,
                  (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return True
                if event.key in (pygame.K_n, pygame.K_ESCAPE):
                    return False
        clock.tick(30)


def random_food(snake_body):
    """在不与蛇身体重叠的网格位置随机生成食物。"""
    while True:
        pos = (random.randrange(GRID_COLS), random.randrange(GRID_ROWS))
        if pos not in snake_body:
            return pos


def run_snake_game():
    """初始化 Pygame -> 等待界面 -> (可选)贪吃蛇游戏 -> 退出 Pygame。不重开。"""
    pygame.init()
    pygame.display.set_caption("贪吃蛇 - 任务完成奖励")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    font = _font(24)
    big_font = _font(48)
    ui_font = pygame.font.Font(None, 20)  # 计分/长度显示用：默认字体，字号 20

    try:
        # -------- 等待界面 --------
        if not wait_screen(screen, font):
            return  # 按 N / ESC / 关闭窗口，直接返回终端

        # -------- 游戏初始状态 --------
        # 初始长度 3，位于屏幕中央，朝向右侧，初始静止
        start_col = GRID_COLS // 2
        start_row = GRID_ROWS // 2
        snake = [
            (start_col, start_row),
            (start_col - 1, start_row),
            (start_col - 2, start_row),
        ]
        direction = (1, 0)        # 当前移动方向（向右）
        next_direction = (1, 0)   # 下一帧即将采用的方向
        moving = False            # 初始静止
        food = random_food(snake)
        score = 0
        clock = pygame.time.Clock()
        game_over = False

        while True:
            screen.fill(BLACK)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if game_over:
                        if event.key == pygame.K_ESCAPE:
                            return
                        continue

                    if event.key == pygame.K_ESCAPE:
                        return

                    if not moving:
                        # 尚未开始：按空格或任意方向键开始移动
                        if event.key == pygame.K_SPACE:
                            moving = True
                        elif event.key in KEY_DIR:
                            moving = True
                            nd = KEY_DIR[event.key]
                            # 不能直接反向掉头
                            if not (nd[0] == -direction[0] and nd[1] == -direction[1]):
                                direction = nd
                            next_direction = direction
                        continue

                    # 已在移动中：方向键切换方向，禁止反向掉头
                    if event.key in KEY_DIR:
                        nd = KEY_DIR[event.key]
                        if not (nd[0] == -direction[0] and nd[1] == -direction[1]):
                            next_direction = nd

            # -------- 更新 --------
            if not game_over and moving:
                direction = next_direction
                head_x, head_y = snake[0]
                new_head = (head_x + direction[0], head_y + direction[1])

                # 碰墙
                if (new_head[0] < 0 or new_head[0] >= GRID_COLS or
                        new_head[1] < 0 or new_head[1] >= GRID_ROWS):
                    game_over = True
                # 碰身
                elif new_head in snake:
                    game_over = True
                else:
                    snake.insert(0, new_head)
                    if new_head == food:
                        score += 10  # 每吃到一个食物加 10 分
                        food = random_food(snake)  # 吃到食物：增长一节（尾巴不移除）
                    else:
                        snake.pop()

            # -------- 绘制 --------
            # 食物（红色）
            fx, fy = food
            pygame.draw.rect(
                screen, RED,
                (fx * GRID_SIZE, fy * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1),
            )
            # 蛇（绿色）
            for (x, y) in snake:
                pygame.draw.rect(
                    screen, GREEN,
                    (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE - 1, GRID_SIZE - 1),
                )

            # 界面信息：左上角得分、右上角长度（白色，默认字体 20，位于屏幕两端，避开中央游戏内容）
            score_surf = ui_font.render(f"得分: {score}", True, WHITE)
            screen.blit(score_surf, (10, 6))
            len_surf = ui_font.render(f"长度: {len(snake)}", True, WHITE)
            len_rect = len_surf.get_rect(topright=(WINDOW_WIDTH - 10, 6))
            screen.blit(len_surf, len_rect)

            if game_over:
                draw_text(screen, big_font, "Game Over", WHITE,
                          (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
                draw_text(screen, font, "按 ESC 退出", GRAY,
                          (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))

            pygame.display.flip()
            clock.tick(FPS if moving else 30)

    finally:
        pygame.quit()


if __name__ == "__main__":
    run_snake_game()
