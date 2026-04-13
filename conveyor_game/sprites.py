"""
游戏精灵类定义
"""
import pygame
from pygame.math import Vector2
from settings import *


class Building(pygame.sprite.Sprite):
    """建筑基类"""
    
    def __init__(self, grid_x, grid_y, building_type, direction=DIR_RIGHT):
        super().__init__()
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.building_type = building_type
        self.direction = direction
        self.rect = pygame.Rect(
            grid_x * GRID_SIZE,
            grid_y * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE
        )
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        self._render()
    
    def _render(self):
        """渲染建筑外观"""
        self.image.fill((0, 0, 0, 0))
        
        if self.building_type == BUILDING_CONVEYOR:
            pygame.draw.rect(self.image, COLOR_CONVEYOR, (2, 2, GRID_SIZE-4, GRID_SIZE-4))
            # 绘制方向箭头
            center = (GRID_SIZE // 2, GRID_SIZE // 2)
            if self.direction == DIR_RIGHT:
                pygame.draw.polygon(self.image, COLOR_TEXT, [
                    (center[0] - 5, center[1] - 5),
                    (center[0] + 10, center[1]),
                    (center[0] - 5, center[1] + 5)
                ])
            elif self.direction == DIR_LEFT:
                pygame.draw.polygon(self.image, COLOR_TEXT, [
                    (center[0] + 5, center[1] - 5),
                    (center[0] - 10, center[1]),
                    (center[0] + 5, center[1] + 5)
                ])
            elif self.direction == DIR_DOWN:
                pygame.draw.polygon(self.image, COLOR_TEXT, [
                    (center[0] - 5, center[1] - 5),
                    (center[0] + 5, center[1] - 5),
                    (center[0], center[1] + 10)
                ])
            elif self.direction == DIR_UP:
                pygame.draw.polygon(self.image, COLOR_TEXT, [
                    (center[0] - 5, center[1] + 5),
                    (center[0] + 5, center[1] + 5),
                    (center[0], center[1] - 10)
                ])
                
        elif self.building_type == BUILDING_SOURCE:
            pygame.draw.rect(self.image, COLOR_SOURCE, (2, 2, GRID_SIZE-4, GRID_SIZE-4))
            # 绘制S标识
            font = pygame.font.SysFont(None, 24)
            text = font.render("S", True, COLOR_TEXT)
            text_rect = text.get_rect(center=(GRID_SIZE//2, GRID_SIZE//2))
            self.image.blit(text, text_rect)
            
        elif self.building_type == BUILDING_SINK:
            pygame.draw.rect(self.image, COLOR_SINK, (2, 2, GRID_SIZE-4, GRID_SIZE-4))
            # 绘制T标识
            font = pygame.font.SysFont(None, 24)
            text = font.render("T", True, COLOR_TEXT)
            text_rect = text.get_rect(center=(GRID_SIZE//2, GRID_SIZE//2))
            self.image.blit(text, text_rect)
            
        elif self.building_type == BUILDING_FILTER:
            pygame.draw.rect(self.image, COLOR_FILTER, (2, 2, GRID_SIZE-4, GRID_SIZE-4))
            # 绘制F标识
            font = pygame.font.SysFont(None, 24)
            text = font.render("F", True, COLOR_TEXT)
            text_rect = text.get_rect(center=(GRID_SIZE//2, GRID_SIZE//2))
            self.image.blit(text, text_rect)
    
    def get_center(self):
        """获取建筑中心点坐标"""
        return Vector2(self.rect.centerx, self.rect.centery)
    
    def get_output_direction(self):
        """获取输出方向向量"""
        if self.direction == DIR_RIGHT:
            return Vector2(1, 0)
        elif self.direction == DIR_LEFT:
            return Vector2(-1, 0)
        elif self.direction == DIR_DOWN:
            return Vector2(0, 1)
        elif self.direction == DIR_UP:
            return Vector2(0, -1)
        return Vector2(1, 0)


class Resource(pygame.sprite.Sprite):
    """资源球"""
    
    def __init__(self, x, y, resource_type=0):
        super().__init__()
        self.pos = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.resource_type = resource_type
        self.radius = RESOURCE_RADIUS
        
        # 创建图像
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self._render()
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        
        # 当前所在网格
        self.current_grid = None
        self.update_grid()
        
        # 是否已被收集
        self.collected = False
    
    def _render(self):
        """渲染资源球"""
        self.image.fill((0, 0, 0, 0))
        if self.resource_type == 0:
            color = COLOR_RESOURCE
        elif self.resource_type == 1:
            color = COLOR_RESOURCE_BLUE
        else:
            color = COLOR_RESOURCE_GREEN
        pygame.draw.circle(self.image, color, (self.radius, self.radius), self.radius)
        pygame.draw.circle(self.image, COLOR_TEXT, (self.radius, self.radius), self.radius, 2)
    
    def update_grid(self):
        """更新当前所在网格坐标"""
        self.current_grid = (
            int(self.pos.x // GRID_SIZE),
            int(self.pos.y // GRID_SIZE)
        )
    
    def update(self, dt, buildings_dict):
        """更新资源球位置"""
        # 保存旧网格
        old_grid = self.current_grid
        
        # 移动
        self.pos += self.velocity * dt * RESOURCE_SPEED
        
        # 检查边界，超出边界则删除
        if (self.pos.x < 0 or self.pos.x >= GAME_AREA_WIDTH or
            self.pos.y < 0 or self.pos.y >= SCREEN_HEIGHT):
            self.kill()
            return
        
        # 更新网格
        self.update_grid()
        
        # 更新rect位置
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # 检测当前所在网格的建筑（每帧都检测，确保在传送带上正确移动）
        if self.current_grid in buildings_dict:
            building = buildings_dict[self.current_grid]
            building_center = building.get_center()
            distance = (self.pos - building_center).length()
            
            # 如果进入建筑中心点附近，触发碰撞逻辑
            if distance < 10:
                self._on_enter_building(building)
        
        # 检测是否进入新网格
        if self.current_grid != old_grid:
            # 进入新网格时，检查是否需要改变方向
            if self.current_grid in buildings_dict:
                building = buildings_dict[self.current_grid]
                if building.building_type == BUILDING_CONVEYOR:
                    # 立即应用传送带方向
                    direction = building.get_output_direction()
                    self.velocity = direction
    
    def _on_enter_building(self, building):
        """当进入建筑时触发"""
        if building.building_type == BUILDING_FILTER:
            # 过滤器改变资源类型并转向
            self.resource_type = (self.resource_type + 1) % 3
            self._render()
            # 改变速度方向
            direction = building.get_output_direction()
            self.velocity = direction
        elif building.building_type == BUILDING_CONVEYOR:
            # 传送带改变方向
            direction = building.get_output_direction()
            self.velocity = direction
        elif building.building_type == BUILDING_SINK:
            # 回收站收集资源 - 标记为已收集，由主循环计分
            self.collected = True
            self.kill()
    
    def set_velocity_from_direction(self, direction):
        """根据方向设置速度"""
        if direction == DIR_RIGHT:
            self.velocity = Vector2(1, 0)
        elif direction == DIR_LEFT:
            self.velocity = Vector2(-1, 0)
        elif direction == DIR_DOWN:
            self.velocity = Vector2(0, 1)
        elif direction == DIR_UP:
            self.velocity = Vector2(0, -1)


class GridOverlay(pygame.sprite.Sprite):
    """网格覆盖层"""
    
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((GAME_AREA_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(0, 0))
        self._render()
    
    def _render(self):
        """渲染网格线"""
        self.image.fill((0, 0, 0, 0))
        # 绘制垂直线
        for x in range(0, GAME_AREA_WIDTH + 1, GRID_SIZE):
            pygame.draw.line(self.image, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))
        # 绘制水平线
        for y in range(0, SCREEN_HEIGHT + 1, GRID_SIZE):
            pygame.draw.line(self.image, COLOR_GRID, (0, y), (GAME_AREA_WIDTH, y))


class PreviewOverlay(pygame.sprite.Sprite):
    """建筑预览覆盖层"""
    
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.building_type = BUILDING_NONE
        self.visible = False
    
    def set_building_type(self, building_type):
        """设置预览的建筑类型"""
        self.building_type = building_type
        self._render()
    
    def _render(self):
        """渲染预览"""
        self.image.fill((0, 0, 0, 0))
        if self.building_type == BUILDING_NONE:
            return
        
        # 半透明填充
        if self.building_type == BUILDING_CONVEYOR:
            color = (*COLOR_CONVEYOR, 128)
        elif self.building_type == BUILDING_SOURCE:
            color = (*COLOR_SOURCE, 128)
        elif self.building_type == BUILDING_SINK:
            color = (*COLOR_SINK, 128)
        elif self.building_type == BUILDING_FILTER:
            color = (*COLOR_FILTER, 128)
        else:
            color = (255, 255, 255, 128)
        
        pygame.draw.rect(self.image, color, (0, 0, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(self.image, (*COLOR_TEXT, 128), (0, 0, GRID_SIZE, GRID_SIZE), 2)
    
    def update(self, mouse_pos):
        """更新预览位置"""
        if self.building_type == BUILDING_NONE:
            self.visible = False
            return
        
        grid_x = mouse_pos[0] // GRID_SIZE
        grid_y = mouse_pos[1] // GRID_SIZE
        
        # 只在游戏区域内显示
        if grid_x < GRID_WIDTH and mouse_pos[0] < GAME_AREA_WIDTH:
            self.rect.topleft = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)
            self.visible = True
        else:
            self.visible = False
