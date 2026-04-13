import pygame
import sys
import os
from config import (GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, GAME_AREA_WIDTH, TOOLBAR_WIDTH,
                    FPS, COLORS, BUILDING_TYPES, MAX_RESOURCES_PER_CELL, BLOCKED_DAMAGE,
                    INITIAL_LIVES, GAME_SPEEDS)
from entities import Building, ResourceBall
from collision import CollisionManager
from ui import UISystem, get_chinese_font
from levels import LEVELS

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("传送带物流游戏")
        self.clock = pygame.time.Clock()
        
        self.game_area_width = GAME_AREA_WIDTH
        self.toolbar_width = TOOLBAR_WIDTH
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        
        self.build_mode = True
        self.running = True
        self.game_over = False
        self.level_complete = False
        
        self.speed_index = 1
        self.game_speed = GAME_SPEEDS[self.speed_index]
        
        self.current_level_index = 0
        self.current_level = None
        self.lives = INITIAL_LIVES
        
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.buildings = pygame.sprite.Group()
        self.resources = pygame.sprite.Group()
        self.buildings_dict = {}
        
        self.collision_manager = CollisionManager(self)
        self.ui = UISystem(self)
        
        self.producers = {}
        self.producer_timers = {}
        
        self.collected_resources = {}
        self.blocked_timer = {}
        
        self.grid_width = 20
        self.grid_height = 15
        
        self.load_level(0)
    
    def load_level(self, level_index):
        if level_index >= len(LEVELS):
            self.game_complete = True
            return
        
        self.current_level_index = level_index
        self.current_level = LEVELS[level_index]
        
        self.grid_width = self.current_level['grid_width']
        self.grid_height = self.current_level['grid_height']
        
        self.reset_level()
        
        self.ui._create_toolbar()
    
    def reset_level(self):
        self.all_sprites.empty()
        self.buildings.empty()
        self.resources.empty()
        self.buildings_dict.clear()
        self.producers.clear()
        self.producer_timers.clear()
        self.collected_resources = {k: 0 for k in self.current_level.get('consumer_goals', {}).keys()}
        self.blocked_timer.clear()
        
        self.lives = INITIAL_LIVES
        self.game_over = False
        self.level_complete = False
        self.build_mode = True
        
        producer_idx = 0
        for building_data in self.current_level.get('initial_buildings', []):
            building = Building(building_data['type'], building_data['grid_x'], building_data['grid_y'])
            self.buildings.add(building)
            self.all_sprites.add(building, layer=0)
            self.buildings_dict[(building_data['grid_x'], building_data['grid_y'])] = building
            
            if 'producer' in building_data['type']:
                key = f"{building_data['type']}_{producer_idx}"
                self.producers[key] = building
                self.producer_timers[key] = 0
                producer_idx += 1
        
        if 'producer_config' in self.current_level:
            for key, config in self.current_level['producer_config'].items():
                if key in self.producers:
                    self.producers[key].interval = config.get('interval', 120)
                    self.producers[key].resource_type = config.get('resource_type', 'red')
    
    def set_game_speed(self, speed_index):
        self.speed_index = speed_index
        self.game_speed = GAME_SPEEDS[speed_index]
    
    def toggle_mode(self):
        self.build_mode = not self.build_mode
    
    def place_building(self, grid_x, grid_y):
        if self.ui.selected_building is None:
            return
        
        if (grid_x, grid_y) in self.buildings_dict:
            return
        
        building = Building(self.ui.selected_building, grid_x, grid_y)
        self.buildings.add(building)
        self.all_sprites.add(building, layer=0)
        self.buildings_dict[(grid_x, grid_y)] = building
        
        if 'producer' in self.ui.selected_building:
            key = f"{self.ui.selected_building}_{len(self.producers)}"
            self.producers[key] = building
            self.producer_timers[key] = 0
            building.interval = 120
            building.resource_type = self.ui.selected_building.split('_')[1]
    
    def remove_building(self, grid_x, grid_y):
        if (grid_x, grid_y) not in self.buildings_dict:
            return
        
        building = self.buildings_dict[(grid_x, grid_y)]
        
        for key, prod in list(self.producers.items()):
            if prod == building:
                del self.producers[key]
                if key in self.producer_timers:
                    del self.producer_timers[key]
                break
        
        building.kill()
        del self.buildings_dict[(grid_x, grid_y)]
    
    def spawn_resource(self, producer):
        grid_x = producer.grid_x
        grid_y = producer.grid_y
        
        resource = ResourceBall(producer.resource_type, grid_x, grid_y)
        self.resources.add(resource)
        self.all_sprites.add(resource, layer=1)
    
    def update_resources(self):
        if self.game_speed == 0:
            return
        
        speed_multiplier = self.game_speed
        
        for _ in range(speed_multiplier):
            resources_to_remove = []
            
            for resource in self.resources:
                building = self.collision_manager.check_resource_at_building_center(resource)
                
                if building:
                    if self.collision_manager.check_resource_reached_consumer(resource, building):
                        res_type = resource.resource_type
                        self.collected_resources[res_type] = self.collected_resources.get(res_type, 0) + 1
                        resources_to_remove.append(resource)
                        continue
                    
                    self.collision_manager.process_resource_collision(resource, building)
                
                if self.collision_manager.check_resource_out_of_bounds(resource, self.grid_width, self.grid_height):
                    resources_to_remove.append(resource)
                    continue
                
                resource.move()
            
            for resource in resources_to_remove:
                resource.kill()
        
        blocked_grids = self.collision_manager.check_blocked_grids(self.resources)
        for grid in blocked_grids:
            if grid not in self.blocked_timer:
                self.blocked_timer[grid] = 0
            self.blocked_timer[grid] += 1
            
            if self.blocked_timer[grid] >= 60:
                self.lives -= BLOCKED_DAMAGE
                self.blocked_timer[grid] = 0
                
                if self.lives <= 0:
                    self.game_over = True
        
        for grid in list(self.blocked_timer.keys()):
            if grid not in blocked_grids:
                del self.blocked_timer[grid]
        
        self.check_level_complete()
    
    def update_producers(self):
        if self.game_speed == 0 or self.build_mode:
            return
        
        speed_multiplier = self.game_speed
        
        for key, producer in self.producers.items():
            if not hasattr(producer, 'interval'):
                continue
            
            self.producer_timers[key] = self.producer_timers.get(key, 0) + speed_multiplier
            
            if self.producer_timers[key] >= producer.interval:
                self.spawn_resource(producer)
                self.producer_timers[key] = 0
    
    def check_level_complete(self):
        if not self.current_level or 'consumer_goals' not in self.current_level:
            return
        
        for res_type, goal in self.current_level['consumer_goals'].items():
            if self.collected_resources.get(res_type, 0) < goal:
                return
        
        self.level_complete = True
    
    def next_level(self):
        self.load_level(self.current_level_index + 1)
    
    def draw_grid(self):
        for x in range(self.grid_width + 1):
            pygame.draw.line(self.screen, COLORS['grid_line'],
                           (x * GRID_SIZE, 0),
                           (x * GRID_SIZE, self.grid_height * GRID_SIZE))
        
        for y in range(self.grid_height + 1):
            pygame.draw.line(self.screen, COLORS['grid_line'],
                           (0, y * GRID_SIZE),
                           (self.grid_width * GRID_SIZE, y * GRID_SIZE))
    
    def draw_game_over(self):
        overlay = pygame.Surface((self.game_area_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        font = get_chinese_font(48)
        text = font.render("游戏结束", True, (255, 100, 100))
        text_rect = text.get_rect(center=(self.game_area_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(text, text_rect)
        
        hint_font = get_chinese_font(24)
        hint = hint_font.render("按 R 重新开始", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.game_area_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(hint, hint_rect)
    
    def draw_level_complete(self):
        overlay = pygame.Surface((self.game_area_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        font = get_chinese_font(48)
        text = font.render("关卡完成!", True, (100, 255, 100))
        text_rect = text.get_rect(center=(self.game_area_width // 2, self.screen_height // 2 - 50))
        self.screen.blit(text, text_rect)
        
        hint_font = get_chinese_font(24)
        hint = hint_font.render("按 N 进入下一关", True, (200, 200, 200))
        hint_rect = hint.get_rect(center=(self.game_area_width // 2, self.screen_height // 2 + 20))
        self.screen.blit(hint, hint_rect)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.toggle_mode()
                elif event.key == pygame.K_1:
                    self.set_game_speed(1)
                elif event.key == pygame.K_2:
                    self.set_game_speed(2)
                elif event.key == pygame.K_0:
                    self.set_game_speed(0)
                elif event.key == pygame.K_r:
                    self.reset_level()
                elif event.key == pygame.K_n and self.level_complete:
                    self.next_level()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if mouse_pos[0] >= self.game_area_width:
                    self.ui.handle_click(mouse_pos)
                else:
                    grid_x = mouse_pos[0] // GRID_SIZE
                    grid_y = mouse_pos[1] // GRID_SIZE
                    
                    if self.build_mode:
                        if event.button == 1:
                            self.place_building(grid_x, grid_y)
                        elif event.button == 3:
                            self.remove_building(grid_x, grid_y)
    
    def update(self):
        if self.game_over or self.level_complete:
            return
        
        self.update_producers()
        self.update_resources()
    
    def draw(self):
        self.screen.fill(COLORS['background'])
        
        self.draw_grid()
        
        blocked_grids = self.collision_manager.check_blocked_grids(self.resources)
        self.ui.draw_blocked_warning(self.screen, blocked_grids)
        
        self.all_sprites.draw(self.screen)
        
        self.ui.draw_toolbar(self.screen)
        
        if self.build_mode:
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[0] < self.game_area_width:
                grid_x = mouse_pos[0] // GRID_SIZE
                grid_y = mouse_pos[1] // GRID_SIZE
                self.ui.draw_preview(self.screen, mouse_pos, grid_x, grid_y)
        
        if self.game_over:
            self.draw_game_over()
        elif self.level_complete:
            self.draw_level_complete()
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
