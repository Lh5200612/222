# -*- coding: utf-8 -*-
"""
Spyder 编辑器

这是一个临时脚本文件。
"""

import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 游戏配置
WIDTH, HEIGHT = 400, 450  # 窗口尺寸（底部留空间显示状态栏）
CELL_SIZE = 20            # 每个格子的大小
GRID_WIDTH = WIDTH // CELL_SIZE   # 网格宽度（列数）
GRID_HEIGHT = (HEIGHT - 50) // CELL_SIZE  # 网格高度（行数，底部50px为状态栏）
MINE_COUNT = 20           # 地雷数量

# 颜色定义
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# 数字颜色映射（不同数字对应不同颜色）
NUM_COLORS = {
    1: (0, 0, 255),
    2: (0, 128, 0),
    3: (255, 0, 0),
    4: (0, 0, 128),
    5: (128, 0, 0),
    6: (0, 128, 128),
    7: (0, 0, 0),
    8: (128, 128, 128)
}

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("扫雷游戏")
font = pygame.font.SysFont(None, 30)

# 游戏状态类
class Minesweeper:
    def __init__(self):
        # 初始化网格：0=空，-1=地雷，1-8=周围地雷数
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        # 显示状态：False=未点开，True=已点开，'flag'=标记旗帜
        self.display = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.game_over = False
        self.win = False
        self.flags_placed = 0
        self.place_mines()  # 放置地雷
        self.calculate_numbers()  # 计算周围地雷数

    # 随机放置地雷
    def place_mines(self):
        mines_placed = 0
        while mines_placed < MINE_COUNT:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if self.grid[y][x] != -1:
                self.grid[y][x] = -1
                mines_placed += 1

    # 计算每个格子周围的地雷数
    def calculate_numbers(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] == -1:
                    continue  # 跳过地雷
                count = 0
                # 遍历8个相邻格子
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < GRID_HEIGHT and 0 <= nx < GRID_WIDTH:
                            if self.grid[ny][nx] == -1:
                                count += 1
                self.grid[y][x] = count

    # 递归展开空白格子
    def reveal(self, x, y):
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        if self.display[y][x] is True or self.display[y][x] == 'flag':
            return
        if self.grid[y][x] == -1:
            self.game_over = True  # 点到地雷，游戏结束
            return
        
        self.display[y][x] = True
        # 如果是空白格子（0），递归展开周围
        if self.grid[y][x] == 0:
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    self.reveal(x + dx, y + dy)

    # 标记/取消标记旗帜
    def toggle_flag(self, x, y):
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT) or self.display[y][x] is True:
            return
        if self.display[y][x] == 'flag':
            self.display[y][x] = False
            self.flags_placed -= 1
        else:
            self.display[y][x] = 'flag'
            self.flags_placed += 1

    # 检查是否获胜（所有非地雷格子都被点开）
    def check_win(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x] != -1 and not self.display[y][x]:
                    return False
        self.win = True
        self.game_over = True
        return True

# 绘制游戏界面
def draw_game(game):
    # 填充背景
    screen.fill(WHITE)
    
    # 绘制网格
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
            # 未点开的格子
            if game.display[y][x] is False:
                pygame.draw.rect(screen, GRAY, rect)
            # 已标记旗帜
            elif game.display[y][x] == 'flag':
                pygame.draw.rect(screen, YELLOW, rect)
                flag_text = font.render("🚩", True, RED)
                screen.blit(flag_text, (x * CELL_SIZE + 3, y * CELL_SIZE + 3))
            # 已点开的格子
            else:
                pygame.draw.rect(screen, WHITE, rect)
                # 显示地雷（游戏结束时）
                if game.grid[y][x] == -1:
                    mine_text = font.render("💣", True, BLACK)
                    screen.blit(mine_text, (x * CELL_SIZE + 3, y * CELL_SIZE + 3))
                # 显示数字
                elif game.grid[y][x] > 0:
                    num_text = font.render(str(game.grid[y][x]), True, NUM_COLORS[game.grid[y][x]])
                    screen.blit(num_text, (x * CELL_SIZE + 5, y * CELL_SIZE + 2))
            # 绘制格子边框
            pygame.draw.rect(screen, BLACK, rect, 1)
    
    # 绘制状态栏（底部）
    status_rect = pygame.Rect(0, HEIGHT - 50, WIDTH, 50)
    pygame.draw.rect(screen, GRAY, status_rect)
    # 显示剩余地雷数
    mines_left = MINE_COUNT - game.flags_placed
    mines_text = font.render(f"地雷剩余: {max(0, mines_left)}", True, BLACK)
    screen.blit(mines_text, (10, HEIGHT - 40))
    # 显示游戏状态
    if game.game_over:
        if game.win:
            win_text = font.render("恭喜获胜！", True, GREEN)
            screen.blit(win_text, (WIDTH - 120, HEIGHT - 40))
        else:
            lose_text = font.render("游戏结束！", True, RED)
            screen.blit(lose_text, (WIDTH - 120, HEIGHT - 40))
    else:
        play_text = font.render("左键点开 | 右键标记", True, BLACK)
        screen.blit(play_text, (WIDTH - 180, HEIGHT - 40))
    
    pygame.display.update()

# 主游戏循环
def main():
    game = Minesweeper()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 鼠标点击事件（游戏未结束时）
            if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                x, y = pygame.mouse.get_pos()
                # 转换为网格坐标
                grid_x = x // CELL_SIZE
                grid_y = y // CELL_SIZE
                # 只处理网格区域的点击
                if grid_y < GRID_HEIGHT:
                    # 左键：点开格子
                    if event.button == 1:
                        game.reveal(grid_x, grid_y)
                        if not game.game_over:
                            game.check_win()
                    # 右键：标记/取消标记旗帜
                    elif event.button == 3:
                        game.toggle_flag(grid_x, grid_y)
            
            # 按R键重新开始游戏
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game = Minesweeper()
        
        draw_game(game)
        clock.tick(60)

if __name__ == "__main__":
    main()