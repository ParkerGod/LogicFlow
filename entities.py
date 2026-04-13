import pygame
import math
from config import GRID_SIZE, COLORS, BUILDING_TYPES, RESOURCE_COLORS

class Building(pygame.sprite.Sprite):
    def __init__(self, building_type, grid_x, grid_y):
        super().__init__()
        self.building_type = building_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.config = BUILDING_TYPES[building_type]
        
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topleft = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)
        
        self._draw_building()
    
    def _draw_building(self):
        self.image.fill(self.config['color'])
        
        if 'conveyor' in self.building_type:
            self._draw_conveyor_arrow()
        elif 'producer' in self.building_type:
            self._draw_producer_symbol()
        elif 'consumer' in self.building_type:
            self._draw_consumer_symbol()
        elif 'filter' in self.building_type:
            self._draw_filter_symbol()
    
    def _draw_conveyor_arrow(self):
        direction = self.config['direction']
        center = GRID_SIZE // 2
        arrow_size = 10
        
        if direction == (1, 0):
            points = [(center - 8, center - 6), (center + 8, center), (center - 8, center + 6)]
        elif direction == (-1, 0):
            points = [(center + 8, center - 6), (center - 8, center), (center + 8, center + 6)]
        elif direction == (0, -1):
            points = [(center - 6, center + 8), (center, center - 8), (center + 6, center + 8)]
        else:
            points = [(center - 6, center - 8), (center, center + 8), (center + 6, center - 8)]
        
        pygame.draw.polygon(self.image, COLORS['conveyor_arrow'], points)
    
    def _draw_producer_symbol(self):
        resource_type = self.config['produces']
        color = RESOURCE_COLORS[resource_type]
        pygame.draw.circle(self.image, color, (GRID_SIZE // 2, GRID_SIZE // 2), 12)
        pygame.draw.circle(self.image, (255, 255, 255), (GRID_SIZE // 2, GRID_SIZE // 2), 12, 2)
    
    def _draw_consumer_symbol(self):
        accepts = self.config['accepts']
        color = RESOURCE_COLORS[accepts]
        pygame.draw.rect(self.image, color, (8, 8, GRID_SIZE - 16, GRID_SIZE - 16))
        pygame.draw.rect(self.image, (255, 255, 255), (8, 8, GRID_SIZE - 16, GRID_SIZE - 16), 2)
    
    def _draw_filter_symbol(self):
        filter_type = self.config['filter_type']
        color = RESOURCE_COLORS[filter_type]
        pygame.draw.polygon(self.image, color, [
            (GRID_SIZE // 2, 6),
            (GRID_SIZE - 6, GRID_SIZE - 6),
            (6, GRID_SIZE - 6)
        ])
        pygame.draw.polygon(self.image, (255, 255, 255), [
            (GRID_SIZE // 2, 6),
            (GRID_SIZE - 6, GRID_SIZE - 6),
            (6, GRID_SIZE - 6)
        ], 2)


class ResourceBall(pygame.sprite.Sprite):
    def __init__(self, resource_type, grid_x, grid_y):
        super().__init__()
        self.resource_type = resource_type
        self.color = RESOURCE_COLORS[resource_type]
        
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        self._draw_ball()
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (grid_x * GRID_SIZE, grid_y * GRID_SIZE)
        
        self.position = pygame.math.Vector2(grid_x * GRID_SIZE, grid_y * GRID_SIZE)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 1.5
        
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.target_grid_x = grid_x
        self.target_grid_y = grid_y
        self.moving = False
    
    def _draw_ball(self):
        center = GRID_SIZE // 2
        pygame.draw.circle(self.image, self.color, (center, center), 14)
        pygame.draw.circle(self.image, (255, 255, 255), (center - 4, center - 4), 4)
        pygame.draw.circle(self.image, (0, 0, 0), (center, center), 14, 2)
    
    def update_grid_position(self):
        self.grid_x = int(self.position.x // GRID_SIZE)
        self.grid_y = int(self.position.y // GRID_SIZE)
    
    def set_velocity(self, direction):
        if direction == (1, 0):
            self.velocity = pygame.math.Vector2(self.speed, 0)
        elif direction == (-1, 0):
            self.velocity = pygame.math.Vector2(-self.speed, 0)
        elif direction == (0, -1):
            self.velocity = pygame.math.Vector2(0, -self.speed)
        elif direction == (0, 1):
            self.velocity = pygame.math.Vector2(0, self.speed)
        else:
            self.velocity = pygame.math.Vector2(0, 0)
    
    def is_at_grid_center(self):
        center_offset_x = self.position.x % GRID_SIZE
        center_offset_y = self.position.y % GRID_SIZE
        tolerance = self.speed + 1
        
        return (abs(center_offset_x - GRID_SIZE // 2) < tolerance and 
                abs(center_offset_y - GRID_SIZE // 2) < tolerance)
    
    def get_current_grid(self):
        return (int(self.position.x // GRID_SIZE), int(self.position.y // GRID_SIZE))
    
    def move(self):
        if self.velocity.length() > 0:
            self.position += self.velocity
            self.rect.topleft = (int(self.position.x), int(self.position.y))
            self.update_grid_position()
            self.moving = True
        else:
            self.moving = False
