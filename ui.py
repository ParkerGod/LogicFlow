import pygame
import os
from config import GRID_SIZE, COLORS, BUILDING_TYPES, GAME_SPEED_NAMES

def get_chinese_font(size):
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return pygame.font.Font(path, size)
            except:
                continue
    return pygame.font.Font(None, size)

class UISystem:
    def __init__(self, game):
        self.game = game
        self.font = get_chinese_font(20)
        self.title_font = get_chinese_font(26)
        self.selected_building = None
        self.toolbar_buttons = []
        self.speed_buttons = []
        self._create_toolbar()
    
    def _create_toolbar(self):
        self.toolbar_buttons = []
        y_offset = 60
        button_height = 45
        button_spacing = 5
        
        if self.game.current_level:
            available = self.game.current_level.get('available_buildings', [])
            for i, building_type in enumerate(available):
                button_rect = pygame.Rect(
                    self.game.game_area_width + 10,
                    y_offset + i * (button_height + button_spacing),
                    self.game.toolbar_width - 20,
                    button_height
                )
                self.toolbar_buttons.append({
                    'rect': button_rect,
                    'type': building_type,
                    'name': BUILDING_TYPES[building_type]['name']
                })
        
        speed_y = self.game.screen_height - 80
        for i, speed_name in enumerate(GAME_SPEED_NAMES):
            button_rect = pygame.Rect(
                self.game.game_area_width + 10 + i * 60,
                speed_y,
                55,
                35
            )
            self.speed_buttons.append({
                'rect': button_rect,
                'speed_index': i,
                'name': speed_name
            })
    
    def handle_click(self, pos):
        for button in self.toolbar_buttons:
            if button['rect'].collidepoint(pos):
                self.selected_building = button['type']
                return True
        
        for button in self.speed_buttons:
            if button['rect'].collidepoint(pos):
                self.game.set_game_speed(button['speed_index'])
                return True
        
        return False
    
    def draw_toolbar(self, screen):
        toolbar_rect = pygame.Rect(
            self.game.game_area_width, 0,
            self.game.toolbar_width, self.game.screen_height
        )
        pygame.draw.rect(screen, COLORS['toolbar_bg'], toolbar_rect)
        pygame.draw.line(screen, COLORS['toolbar_border'], 
                        (self.game.game_area_width, 0),
                        (self.game.game_area_width, self.game.screen_height), 2)
        
        title = self.title_font.render("建筑工具", True, COLORS['text_highlight'])
        screen.blit(title, (self.game.game_area_width + 50, 20))
        
        for button in self.toolbar_buttons:
            color = COLORS['button_selected'] if self.selected_building == button['type'] else COLORS['button_normal']
            pygame.draw.rect(screen, color, button['rect'], border_radius=5)
            pygame.draw.rect(screen, COLORS['toolbar_border'], button['rect'], 2, border_radius=5)
            
            text = self.font.render(button['name'], True, COLORS['text_white'])
            text_rect = text.get_rect(center=button['rect'].center)
            screen.blit(text, text_rect)
        
        self._draw_game_info(screen)
        self._draw_speed_buttons(screen)
    
    def _draw_game_info(self, screen):
        info_y = self.game.screen_height - 180
        
        mode_text = "建造模式" if self.game.build_mode else "运行模式"
        mode_color = COLORS['text_highlight'] if self.game.build_mode else COLORS['text_white']
        text = self.font.render(f"模式: {mode_text}", True, mode_color)
        screen.blit(text, (self.game.game_area_width + 10, info_y))
        
        lives_text = self.font.render(f"生命: {self.game.lives}", True, COLORS['text_white'])
        screen.blit(lives_text, (self.game.game_area_width + 10, info_y + 25))
        
        level_text = self.font.render(f"关卡: {self.game.current_level_index + 1}", True, COLORS['text_white'])
        screen.blit(level_text, (self.game.game_area_width + 10, info_y + 50))
        
        if self.game.current_level and 'consumer_goals' in self.game.current_level:
            goals_y = info_y + 80
            goals_text = self.font.render("目标:", True, COLORS['text_highlight'])
            screen.blit(goals_text, (self.game.game_area_width + 10, goals_y))
            
            for i, (res_type, goal) in enumerate(self.game.current_level['consumer_goals'].items()):
                collected = self.game.collected_resources.get(res_type, 0)
                color = COLORS['text_white']
                if collected >= goal:
                    color = (100, 200, 100)
                goal_text = self.font.render(f"  {res_type}: {collected}/{goal}", True, color)
                screen.blit(goal_text, (self.game.game_area_width + 10, goals_y + 20 + i * 20))
    
    def _draw_speed_buttons(self, screen):
        for button in self.speed_buttons:
            color = COLORS['button_selected'] if self.game.speed_index == button['speed_index'] else COLORS['button_normal']
            pygame.draw.rect(screen, color, button['rect'], border_radius=5)
            pygame.draw.rect(screen, COLORS['toolbar_border'], button['rect'], 2, border_radius=5)
            
            text = self.font.render(button['name'], True, COLORS['text_white'])
            text_rect = text.get_rect(center=button['rect'].center)
            screen.blit(text, text_rect)
    
    def draw_preview(self, screen, mouse_pos, grid_x, grid_y):
        if self.selected_building and self.game.build_mode:
            if 0 <= grid_x < self.game.grid_width and 0 <= grid_y < self.game.grid_height:
                preview_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                color = BUILDING_TYPES[self.selected_building]['color']
                preview_surface.fill((*color[:3], 128))
                
                screen.blit(preview_surface, (grid_x * GRID_SIZE, grid_y * GRID_SIZE))
                
                pygame.draw.rect(screen, (*COLORS['preview'][:3], 200),
                               (grid_x * GRID_SIZE, grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)
    
    def draw_blocked_warning(self, screen, blocked_grids):
        for grid_x, grid_y in blocked_grids:
            warning_surface = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
            warning_surface.fill((*COLORS['blocked'], 100))
            screen.blit(warning_surface, (grid_x * GRID_SIZE, grid_y * GRID_SIZE))
            
            pygame.draw.rect(screen, COLORS['blocked'],
                           (grid_x * GRID_SIZE, grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 3)
