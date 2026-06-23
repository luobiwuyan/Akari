#!/usr/bin/env python3
"""
Akari 点灯游戏 - 完整版
✅ 矩形棋盘 | ✅ Undo/Redo | ✅ 胜利特效 | ✅ 计时器
"""

import pygame
import sys
import time
import random
from board import Board
from puzzle_loader import ALL_PUZZLES
from puzzle_data import EASY_5x5

pygame.init()

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (70, 130, 180)
RED = (220, 20, 60)
GREEN = (50, 205, 50)
YELLOW = (255, 255, 0)
LIGHT_YELLOW = (255, 255, 200)
PURPLE = (138, 43, 226)
CROSS_COLOR = (200, 0, 0)
GOLD = (255, 215, 0)


class AkariGame:
    def __init__(self, initial_puzzle_index=0):
        self.puzzle_list = [(name, data) for name, data, meta in ALL_PUZZLES]

        if not self.puzzle_list:
            self.puzzle_list = [("默认谜题", EASY_5x5)]

        self.current_puzzle_index = initial_puzzle_index % len(self.puzzle_list)
        self.current_puzzle_name, self.current_puzzle_data = self.puzzle_list[self.current_puzzle_index]

        self.board_rows = len(self.current_puzzle_data)
        self.board_cols = len(self.current_puzzle_data[0])
        self.board = Board(initial_grid=self.current_puzzle_data)

        # 窗口
        self.screen_width = 1200
        self.screen_height = 800
        self.min_cell_size = 30
        self.max_cell_size = 120
        self.margin = 80
        self.side_panel_width = 320

        self.calculate_adaptive_sizes()

        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)
        pygame.display.set_caption(f"Akari 美术馆 - {self.current_puzzle_name}")

        self.load_fonts()
        self.clock = pygame.time.Clock()

        # 状态
        self.running = True
        self.message = f"当前谜题: {self.current_puzzle_name}\n左键: 放置/移除灯泡 | 右键: 标记/取消叉号"
        self.message_color = BLUE

        # ✅ 计时器
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.timer_running = True

        # ✅ 胜利特效
        self.victory = False
        self.victory_start = 0
        self.victory_duration = 2500
        self.flash_interval = 200

    def calculate_adaptive_sizes(self):
        max_grid_width = self.screen_width - 2 * self.margin - self.side_panel_width
        max_grid_height = self.screen_height - 2 * self.margin

        cell_size_by_width = max_grid_width // self.board_cols
        cell_size_by_height = max_grid_height // self.board_rows

        cell_size = min(cell_size_by_width, cell_size_by_height)
        cell_size = max(self.min_cell_size, min(cell_size, self.max_cell_size))

        if cell_size < 40 and (self.board_rows > 10 or self.board_cols > 10):
            cell_size = 40

        self.cell_size = cell_size
        actual_grid_width = cell_size * self.board_cols
        actual_grid_height = cell_size * self.board_rows

        self.window_width = actual_grid_width + 2 * self.margin + self.side_panel_width
        self.window_height = actual_grid_height + 2 * self.margin

        self.grid_x = (self.window_width - self.side_panel_width - actual_grid_width) // 2
        self.grid_y = (self.window_height - actual_grid_height) // 2
        self.side_panel_x = self.grid_x + actual_grid_width + 20

    def load_fonts(self):
        base_font_size = max(16, min(self.cell_size // 3, 40))
        title_font_size = base_font_size + 8
        small_font_size = max(12, base_font_size - 4)
        self.number_font_size = max(20, min(self.cell_size // 2, 60))
        self.rules_font_size = 18
        self.button_font_size = 20
        self.message_font_size = 18
        self.timer_font_size = 28

        font_names = ["pingfangsc", "stheiti", "heiti", "microsoftyahei", "arial"]
        selected_font = None
        available_fonts = pygame.font.get_fonts()

        for name in font_names:
            if name.lower().replace(" ", "") in available_fonts:
                selected_font = name
                break

        try:
            if selected_font:
                self.font = pygame.font.SysFont(selected_font, base_font_size)
                self.title_font = pygame.font.SysFont(selected_font, title_font_size)
                self.small_font = pygame.font.SysFont(selected_font, small_font_size)
                self.number_font = pygame.font.SysFont(selected_font, self.number_font_size)
                self.rules_font = pygame.font.SysFont(selected_font, self.rules_font_size)
                self.button_font = pygame.font.SysFont(selected_font, self.button_font_size)
                self.message_font = pygame.font.SysFont(selected_font, self.message_font_size)
                self.timer_font = pygame.font.SysFont(selected_font, self.timer_font_size)
            else:
                raise ValueError
        except Exception:
            self.font = pygame.font.SysFont(None, base_font_size)
            self.title_font = pygame.font.SysFont(None, title_font_size)
            self.small_font = pygame.font.SysFont(None, small_font_size)
            self.number_font = pygame.font.SysFont(None, self.number_font_size)
            self.rules_font = pygame.font.SysFont(None, self.rules_font_size)
            self.button_font = pygame.font.SysFont(None, self.button_font_size)
            self.message_font = pygame.font.SysFont(None, self.message_font_size)
            self.timer_font = pygame.font.SysFont(None, self.timer_font_size)

    def handle_resize(self, w, h):
        self.screen_width, self.screen_height = w, h
        self.calculate_adaptive_sizes()
        self.load_fonts()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)

    def get_cell_rect(self, row, col):
        return pygame.Rect(
            self.grid_x + col * self.cell_size,
            self.grid_y + row * self.cell_size,
            self.cell_size,
            self.cell_size
        )

    def draw_grid(self):
        grid_rect = pygame.Rect(self.grid_x, self.grid_y, self.board_cols * self.cell_size,
                                self.board_rows * self.cell_size)
        pygame.draw.rect(self.screen, WHITE, grid_rect)

        for i in range(self.board_cols + 1):
            pygame.draw.line(self.screen, DARK_GRAY, (self.grid_x + i * self.cell_size, self.grid_y),
                             (self.grid_x + i * self.cell_size, self.grid_y + self.board_rows * self.cell_size), 2)
        for i in range(self.board_rows + 1):
            pygame.draw.line(self.screen, DARK_GRAY, (self.grid_x, self.grid_y + i * self.cell_size),
                             (self.grid_x + self.board_cols * self.cell_size, self.grid_y + i * self.cell_size), 2)

        for row in range(self.board_rows):
            for col in range(self.board_cols):
                value = self.board.get_cell(row, col)
                if value in [-1, 0, 1, 2, 3, 4]:
                    pygame.draw.rect(self.screen, BLACK, self.get_cell_rect(row, col))

        for row in range(self.board_rows):
            for col in range(self.board_cols):
                if self.board.is_cell_lit(row, col) and self.board.get_cell(row, col) == 5:
                    cell_rect = self.get_cell_rect(row, col)
                    pygame.draw.rect(self.screen, LIGHT_YELLOW, cell_rect.inflate(-2, -2))

        for row in range(self.board_rows):
            for col in range(self.board_cols):
                value = self.board.get_cell(row, col)
                cell_rect = self.get_cell_rect(row, col)
                if value in [0, 1, 2, 3, 4]:
                    text = self.number_font.render(str(value), True, WHITE)
                    self.screen.blit(text, text.get_rect(center=cell_rect.center))
                elif value == 9:
                    center = cell_rect.center
                    radius = max(10, self.cell_size // 3)
                    pygame.draw.circle(self.screen, YELLOW, center, radius)
                    if radius >= 12:
                        pygame.draw.circle(self.screen, WHITE,
                                           (center[0] - radius // 3, center[1] - radius // 3),
                                           max(3, radius // 3))
                elif value == 5 and self.board.is_crossed(row, col):
                    m = self.cell_size // 5
                    pygame.draw.line(self.screen, CROSS_COLOR,
                                     (cell_rect.left + m, cell_rect.top + m),
                                     (cell_rect.right - m, cell_rect.bottom - m), 3)
                    pygame.draw.line(self.screen, CROSS_COLOR,
                                     (cell_rect.left + m, cell_rect.bottom - m),
                                     (cell_rect.right - m, cell_rect.top + m), 3)

        for row in range(self.board_rows):
            for col in range(self.board_cols):
                pygame.draw.rect(self.screen, BLACK, self.get_cell_rect(row, col), 2)

    def draw_timer(self):
        """绘制计时器"""
        if self.timer_running and not self.victory:
            self.elapsed_time = pygame.time.get_ticks() - self.start_time

        seconds = self.elapsed_time // 1000
        minutes = seconds // 60
        seconds %= 60

        timer_text = f"{minutes:02d}:{seconds:02d}"
        text = self.timer_font.render(timer_text, True, DARK_GRAY)
        self.screen.blit(text, (self.grid_x, 20))

    def draw_victory_effect(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.victory_start

        if elapsed > self.victory_duration:
            self.victory = False
            return

        # 金色遮罩
        alpha = int(100 * (1 - elapsed / self.victory_duration))
        overlay = pygame.Surface((self.window_width, self.window_height), pygame.SRCALPHA)
        overlay.fill((255, 215, 0, alpha))
        self.screen.blit(overlay, (0, 0))

        # 闪烁文字
        if (elapsed // self.flash_interval) % 2 == 0:
            text = self.title_font.render("恭喜通关！", True, GOLD)
            rect = text.get_rect(center=(self.window_width // 2, self.grid_y - 40))
            self.screen.blit(text, rect)

    def draw_side_panel(self):
        panel_rect = pygame.Rect(self.side_panel_x, self.grid_y, self.side_panel_width,
                                 self.board_rows * self.cell_size)
        pygame.draw.rect(self.screen, (240, 240, 245), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, BLUE, panel_rect, 3, border_radius=10)

        title = self.title_font.render("Akari 美术馆", True, BLUE)
        self.screen.blit(title, title.get_rect(center=(panel_rect.centerx, self.grid_y + 30)))

        y = self.grid_y + 70
        self.screen.blit(self.small_font.render(f"谜题: {self.current_puzzle_name}", True, DARK_GRAY),
                         (panel_rect.x + 15, y))
        y += 40

        rules = ["游戏规则:", "1. 左键放置/移除灯泡", "2. 右键标记/取消叉号",
                 "3. 灯泡照亮整行整列", "4. 灯泡不能互照", "5. 数字=相邻灯泡数", "6. 点亮所有白格"]
        for rule in rules:
            self.screen.blit(self.rules_font.render(rule, True, BLACK), (panel_rect.x + 15, y))
            y += 22

        y += 20

        buttons = [
            ("重新开始", self.restart_game),
            ("检查答案", self.check_solution),
            ("随机谜题", self.random_puzzle),
            ("下一谜题", self.next_puzzle)
        ]

        for text, action in buttons:
            rect = pygame.Rect(panel_rect.x + 20, y, self.side_panel_width - 40, 35)

            if text == "重新开始":
                self.restart_btn_rect = rect
            elif text == "检查答案":
                self.check_btn_rect = rect
            elif text == "随机谜题":
                self.random_btn_rect = rect
            elif text == "下一谜题":
                self.next_btn_rect = rect

            pygame.draw.rect(self.screen, BLUE, rect, border_radius=5)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 2, border_radius=5)
            self.screen.blit(self.button_font.render(text, True, WHITE),
                             self.button_font.render(text, True, WHITE).get_rect(center=rect.center))
            y += 45

        msg_lines = self.message.split('\n')
        msg_rect = pygame.Rect(panel_rect.x + 10, y + 10, self.side_panel_width - 20, len(msg_lines) * 22 + 10)
        pygame.draw.rect(self.screen, (255, 255, 240), msg_rect, border_radius=5)
        pygame.draw.rect(self.screen, DARK_GRAY, msg_rect, 1, border_radius=5)
        for i, line in enumerate(msg_lines):
            if line:
                self.screen.blit(self.message_font.render(line, True, self.message_color),
                                 (msg_rect.x + 5, msg_rect.y + 5 + i * 22))

    def handle_click(self, pos, button):
        x, y = pos

        if button == 1:
            if hasattr(self, 'restart_btn_rect') and self.restart_btn_rect.collidepoint(pos):
                self.restart_game()
                return
            elif hasattr(self, 'check_btn_rect') and self.check_btn_rect.collidepoint(pos):
                self.check_solution()
                return
            elif hasattr(self, 'random_btn_rect') and self.random_btn_rect.collidepoint(pos):
                self.random_puzzle()
                return
            elif hasattr(self, 'next_btn_rect') and self.next_btn_rect.collidepoint(pos):
                self.next_puzzle()
                return

        if self.grid_x <= x < self.grid_x + self.board_cols * self.cell_size and \
                self.grid_y <= y < self.grid_y + self.board_rows * self.cell_size:

            col = (x - self.grid_x) // self.cell_size
            row = (y - self.grid_y) // self.cell_size

            if 0 <= row < self.board_rows and 0 <= col < self.board_cols:
                if button == 1:
                    cell = self.board.get_cell(row, col)
                    if cell == 5 and self.board.is_valid_move(row, col):
                        self.board.place_bulb(row, col)
                        self.message = f"在 ({row},{col}) 放置灯泡"
                        self.message_color = GREEN
                    elif cell == 9:
                        self.board.remove_bulb(row, col)
                        self.message = f"移除 ({row},{col}) 的灯泡"
                        self.message_color = BLUE
                    elif cell != 5:
                        self.message = "黑色格子不能放置灯泡"
                        self.message_color = RED
                elif button == 3:
                    if self.board.get_cell(row, col) == 5:
                        self.board.toggle_cross(row, col)
                        state = "标记" if self.board.is_crossed(row, col) else "移除"
                        self.message = f"{state} ({row},{col}) 的叉号"
                        self.message_color = PURPLE
                    else:
                        self.message = "黑色格子不能标记叉号"
                        self.message_color = RED

    def restart_game(self):
        self.board.reset_to_initial()
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.timer_running = True
        self.victory = False
        self.message = "已重置当前谜题"
        self.message_color = GREEN

    def check_solution(self):
        solved, (lit_info, bulb_info, num_info) = self.board.is_solved()
        if solved:
            self.victory = True
            self.victory_start = pygame.time.get_ticks()
            self.timer_running = False
            self.message = "恭喜通关！"
            self.message_color = GREEN
        else:
            self.victory = False
            msg = "解法有误：\n"
            if lit_info: msg += f"({lit_info[0]},{lit_info[1]}) 未照亮\n"
            if bulb_info: msg += bulb_info + "\n"
            if num_info: msg += num_info
            self.message = msg
            self.message_color = RED

    def random_puzzle(self):
        if len(self.puzzle_list) > 1:
            available = [i for i in range(len(self.puzzle_list)) if i != self.current_puzzle_index]
            if available:
                self.load_puzzle(random.choice(available))
            else:
                self.message = "只有一个谜题可用"
                self.message_color = RED
        else:
            self.message = "没有更多谜题"
            self.message_color = RED

    def next_puzzle(self):
        self.load_puzzle((self.current_puzzle_index + 1) % len(self.puzzle_list))

    def load_puzzle(self, index):
        self.current_puzzle_index = index
        self.current_puzzle_name, self.current_puzzle_data = self.puzzle_list[index]
        self.board_rows = len(self.current_puzzle_data)
        self.board_cols = len(self.current_puzzle_data[0])
        self.board = Board(initial_grid=self.current_puzzle_data)
        self.calculate_adaptive_sizes()
        self.load_fonts()
        self.screen = pygame.display.set_mode((self.window_width, self.window_height), pygame.RESIZABLE)

        # 重置计时
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.timer_running = True
        self.victory = False

        self.message = f"已加载谜题: {self.current_puzzle_name}"
        self.message_color = BLUE

    def draw(self):
        self.screen.fill((230, 230, 240))
        pygame.display.set_caption(f"Akari 点灯游戏 - {self.current_puzzle_name}")

        size_text = self.font.render(f"棋盘大小: {self.board_rows}×{self.board_cols}", True, DARK_GRAY)
        self.screen.blit(size_text, size_text.get_rect(center=(self.window_width // 2, 20)))

        self.draw_timer()
        self.draw_grid()
        self.draw_side_panel()

        if self.victory:
            self.draw_victory_effect()

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button in [1, 3]:
                        self.handle_click(event.pos, event.button)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.restart_game()
                    elif event.key == pygame.K_n:
                        self.next_puzzle()
                    elif event.key == pygame.K_SPACE:
                        self.random_puzzle()
                    elif event.key == pygame.K_c:
                        self.check_solution()
                    elif event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        if self.board.undo():
                            self.message = " 已撤销"
                            self.message_color = BLUE
                    elif event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        if self.board.redo():
                            self.message = " 已重做"
                            self.message_color = BLUE
                    elif event.key == pygame.K_z:
                        self.board.undo()
                    elif event.key == pygame.K_y:
                        self.board.redo()
                elif event.type == pygame.VIDEORESIZE:
                    self.handle_resize(event.w, event.h)
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()


def main():
    print("启动Akari图形界面...")
    print(f"可用谜题数量: {len(ALL_PUZZLES)}")
    for i, (name, data, meta) in enumerate(ALL_PUZZLES):
        print(f"  {i + 1}. {name} (难度: {meta.get('difficulty', '未知')}, 大小: {meta.get('size', '未知')})")
    game = AkariGame()
    game.run()


if __name__ == "__main__":
    main()
