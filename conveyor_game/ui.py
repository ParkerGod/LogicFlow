"""
UI系统
"""
import pygame
from settings import *


class UI:
    """UI管理类"""
    
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # 建筑按钮
        self.buttons = []
        self._create_buttons()
        
        # 当前选中的建筑类型
        self.selected_building = BUILDING_CONVEYOR
        
        # 建筑方向
        self.building_direction = DIR_RIGHT
    
    def _create_buttons(self):
        """创建建筑按钮"""
        button_size = 60
        start_x = GAME_AREA_WIDTH + 30
        start_y = 100
        gap = 20
        
        buildings = [
            (BUILDING_CONVEYOR, "Conveyor", COLOR_CONVEYOR),
            (BUILDING_SOURCE, "Source", COLOR_SOURCE),
            (BUILDING_SINK, "Sink", COLOR_SINK),
            (BUILDING_FILTER, "Filter", COLOR_FILTER),
        ]
        
        for i, (btype, name, color) in enumerate(buildings):
            rect = pygame.Rect(start_x, start_y + i * (button_size + gap), button_size, button_size)
            self.buttons.append({
                "type": btype,
                "name": name,
                "color": color,
                "rect": rect
            })
    
    def handle_click(self, pos):
        """处理鼠标点击"""
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                self.selected_building = button["type"]
                return True
        return False
    
    def draw(self):
        """绘制UI"""
        # 绘制UI背景
        pygame.draw.rect(self.screen, COLOR_UI_BG, (GAME_AREA_WIDTH, 0, UI_AREA_WIDTH, SCREEN_HEIGHT))
        
        # 绘制标题
        title = self.font.render("Conveyor Game", True, COLOR_TEXT)
        self.screen.blit(title, (GAME_AREA_WIDTH + 20, 20))
        
        # 绘制建筑按钮
        for button in self.buttons:
            color = button["color"]
            if button["type"] == self.selected_building:
                # 选中状态加边框
                pygame.draw.rect(self.screen, COLOR_UI_SELECTED, button["rect"].inflate(4, 4))
            pygame.draw.rect(self.screen, color, button["rect"])
            
            # 绘制按钮文字
            text = self.small_font.render(button["name"], True, COLOR_TEXT)
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        
        # 绘制游戏状态信息
        self._draw_status()
        
        # 绘制操作说明
        self._draw_instructions()
    
    def _draw_status(self):
        """绘制游戏状态"""
        x = GAME_AREA_WIDTH + 20
        y = 350
        
        # 模式
        mode_text = "BUILD MODE" if self.game.build_mode else "RUN MODE"
        mode_color = COLOR_UI_SELECTED if self.game.build_mode else (50, 200, 50)
        text = self.font.render(mode_text, True, mode_color)
        self.screen.blit(text, (x, y))
        
        # 速度
        y += 40
        speed_text = f"Speed: {self.game.game_speed}x"
        if self.game.game_speed == SPEED_PAUSE:
            speed_text = "Speed: PAUSED"
        text = self.font.render(speed_text, True, COLOR_TEXT)
        self.screen.blit(text, (x, y))
        
        # 生命值
        y += 40
        hp_text = f"HP: {self.game.hp}"
        text = self.font.render(hp_text, True, COLOR_HP)
        self.screen.blit(text, (x, y))
        
        # 关卡信息
        y += 40
        level_text = f"Level: {self.game.current_level + 1}"
        text = self.font.render(level_text, True, COLOR_TEXT)
        self.screen.blit(text, (x, y))
        
        # 目标进度
        y += 40
        progress_text = f"Progress: {self.game.collected}/{self.game.target}"
        text = self.font.render(progress_text, True, COLOR_TEXT)
        self.screen.blit(text, (x, y))
        
        # 方向
        y += 40
        dir_names = ["RIGHT", "DOWN", "LEFT", "UP"]
        dir_text = f"Dir: {dir_names[self.building_direction]}"
        text = self.small_font.render(dir_text, True, COLOR_TEXT)
        self.screen.blit(text, (x, y))
    
    def _draw_instructions(self):
        """绘制操作说明"""
        x = GAME_AREA_WIDTH + 20
        y = SCREEN_HEIGHT - 200
        
        instructions = [
            "Controls:",
            "SPACE - Toggle Mode",
            "1 - 1x Speed",
            "2 - 2x Speed",
            "P - Pause",
            "R - Rotate",
            "ESC - Clear Selection",
        ]
        
        for instruction in instructions:
            text = self.small_font.render(instruction, True, (150, 150, 150))
            self.screen.blit(text, (x, y))
            y += 25
