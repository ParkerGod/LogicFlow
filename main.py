import pygame
import sys
from pygame.math import Vector2
from pygame.sprite import LayeredUpdates, Sprite

GRID_SIZE = 40
GRID_WIDTH = 20
GRID_HEIGHT = 15
SCREEN_WIDTH = GRID_WIDTH * GRID_SIZE + 200
SCREEN_HEIGHT = GRID_HEIGHT * GRID_SIZE
FPS = 60

COLORS = {
    'background': (40, 44, 52),
    'grid': (60, 65, 75),
    'conveyor': (100, 100, 100),
    'generator': (0, 150, 0),
    'recycler': (150, 0, 0),
    'filter': (0, 100, 200),
    'resource_red': (255, 50, 50),
    'resource_blue': (50, 50, 255),
    'ui_panel': (50, 55, 65),
    'ui_button': (70, 75, 85),
    'ui_button_hover': (90, 95, 105),
    'text': (255, 255, 255),
    'blocked': (255, 100, 100, 100)
}

BUILDING_TYPES = {
    'empty': 0,
    'conveyor_right': 1,
    'conveyor_down': 2,
    'conveyor_left': 3,
    'conveyor_up': 4,
    'generator_red': 5,
    'generator_blue': 6,
    'recycler': 7,
    'filter_red_right': 8,
    'filter_blue_down': 9
}

LEVELS = [
    {
        'map': [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,5,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,1,1,1,1,1,7,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,6,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ],
        'target_collect': 10,
        'spawn_rates': {'red': 120, 'blue': 150}
    },
    {
        'map': [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,5,1,1,1,8,1,1,1,1,7,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,6,1,1,1,9,1,1,1,1,7,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ],
        'target_collect': 20,
        'spawn_rates': {'red': 90, 'blue': 100}
    }
]

LAYER_ORDER = {
    'track': 1,
    'resource': 2,
    'ui': 3
}

class Building(Sprite):
    def __init__(self, grid_x, grid_y, building_type):
        super().__init__()
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.building_type = building_type
        self._layer = LAYER_ORDER['track']
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = grid_x * GRID_SIZE
        self.rect.y = grid_y * GRID_SIZE
        self.spawn_timer = 0
        self.draw()

    def draw(self):
        self.image.fill((0, 0, 0, 0))
        center = (GRID_SIZE // 2, GRID_SIZE // 2)
        
        if self.building_type == BUILDING_TYPES['conveyor_right']:
            pygame.draw.rect(self.image, COLORS['conveyor'], (5, 15, 30, 10))
            pygame.draw.polygon(self.image, (200, 200, 200), [(30, 20), (35, 15), (35, 25)])
        elif self.building_type == BUILDING_TYPES['conveyor_down']:
            pygame.draw.rect(self.image, COLORS['conveyor'], (15, 5, 10, 30))
            pygame.draw.polygon(self.image, (200, 200, 200), [(20, 30), (15, 35), (25, 35)])
        elif self.building_type == BUILDING_TYPES['conveyor_left']:
            pygame.draw.rect(self.image, COLORS['conveyor'], (5, 15, 30, 10))
            pygame.draw.polygon(self.image, (200, 200, 200), [(10, 20), (5, 15), (5, 25)])
        elif self.building_type == BUILDING_TYPES['conveyor_up']:
            pygame.draw.rect(self.image, COLORS['conveyor'], (15, 5, 10, 30))
            pygame.draw.polygon(self.image, (200, 200, 200), [(20, 10), (15, 5), (25, 5)])
        elif self.building_type == BUILDING_TYPES['generator_red']:
            pygame.draw.rect(self.image, COLORS['generator'], (5, 5, 30, 30))
            pygame.draw.circle(self.image, COLORS['resource_red'], center, 10)
            pygame.draw.polygon(self.image, (200, 200, 200), [(30, 20), (35, 15), (35, 25)])
        elif self.building_type == BUILDING_TYPES['generator_blue']:
            pygame.draw.rect(self.image, COLORS['generator'], (5, 5, 30, 30))
            pygame.draw.circle(self.image, COLORS['resource_blue'], center, 10)
            pygame.draw.polygon(self.image, (200, 200, 200), [(30, 20), (35, 15), (35, 25)])
        elif self.building_type == BUILDING_TYPES['recycler']:
            pygame.draw.rect(self.image, COLORS['recycler'], (5, 5, 30, 30))
            pygame.draw.rect(self.image, (0, 0, 0), (10, 15, 20, 10))
        elif self.building_type == BUILDING_TYPES['filter_red_right']:
            pygame.draw.rect(self.image, COLORS['filter'], (5, 5, 30, 30))
            pygame.draw.circle(self.image, COLORS['resource_red'], (15, 20), 6)
            pygame.draw.polygon(self.image, (200, 200, 200), [(30, 20), (35, 15), (35, 25)])
        elif self.building_type == BUILDING_TYPES['filter_blue_down']:
            pygame.draw.rect(self.image, COLORS['filter'], (5, 5, 30, 30))
            pygame.draw.circle(self.image, COLORS['resource_blue'], (20, 15), 6)
            pygame.draw.polygon(self.image, (200, 200, 200), [(20, 30), (15, 35), (25, 35)])

    def get_direction(self):
        dir_map = {
            BUILDING_TYPES['conveyor_right']: Vector2(1, 0),
            BUILDING_TYPES['conveyor_down']: Vector2(0, 1),
            BUILDING_TYPES['conveyor_left']: Vector2(-1, 0),
            BUILDING_TYPES['conveyor_up']: Vector2(0, -1),
            BUILDING_TYPES['generator_red']: Vector2(1, 0),
            BUILDING_TYPES['generator_blue']: Vector2(1, 0),
            BUILDING_TYPES['filter_red_right']: Vector2(1, 0),
            BUILDING_TYPES['filter_blue_down']: Vector2(0, 1),
        }
        return dir_map.get(self.building_type, Vector2(0, 0))

    def is_generator(self):
        return self.building_type in [BUILDING_TYPES['generator_red'], BUILDING_TYPES['generator_blue']]

    def get_resource_type(self):
        if self.building_type == BUILDING_TYPES['generator_red']:
            return 'red'
        elif self.building_type == BUILDING_TYPES['generator_blue']:
            return 'blue'
        return None

    def is_recycler(self):
        return self.building_type == BUILDING_TYPES['recycler']

    def is_filter(self):
        return self.building_type in [BUILDING_TYPES['filter_red_right'], BUILDING_TYPES['filter_blue_down']]

    def get_filter_type(self):
        if self.building_type == BUILDING_TYPES['filter_red_right']:
            return 'red'
        elif self.building_type == BUILDING_TYPES['filter_blue_down']:
            return 'blue'
        return None


class ResourceBall(Sprite):
    def __init__(self, x, y, resource_type):
        super().__init__()
        self._layer = LAYER_ORDER['resource']
        self.resource_type = resource_type
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.speed = 1.5
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        color = COLORS[f'resource_{resource_type}']
        pygame.draw.circle(self.image, color, (10, 10), 10)
        pygame.draw.circle(self.image, (255, 255, 255), (7, 7), 3)
        self.update_rect()

    def update_rect(self):
        self.rect.center = (int(self.position.x), int(self.position.y))

    def get_grid_pos(self):
        return (int(self.position.x // GRID_SIZE), int(self.position.y // GRID_SIZE))

    def get_center_distance_to_grid(self, grid_x, grid_y):
        grid_center = Vector2(grid_x * GRID_SIZE + GRID_SIZE // 2, 
                              grid_y * GRID_SIZE + GRID_SIZE // 2)
        return self.position.distance_to(grid_center)

    def update(self):
        self.position += self.velocity * self.speed
        self.update_rect()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("传送带物流游戏")
        self.clock = pygame.time.Clock()
        try:
            self.font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 24)
            self.large_font = pygame.font.Font("C:/Windows/Fonts/msyh.ttc", 36)
        except:
            try:
                self.font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 24)
                self.large_font = pygame.font.Font("C:/Windows/Fonts/simhei.ttf", 36)
            except:
                self.font = pygame.font.SysFont(["microsoftyahei", "simhei", "simsun", "arial"], 24)
                self.large_font = pygame.font.SysFont(["microsoftyahei", "simhei", "simsun", "arial"], 36)
        
        self.game_speed = 1
        self.paused = False
        self.build_mode = True
        self.current_level = 0
        self.lives = 10
        self.collected = 0
        self.target_collect = 0
        
        self.all_sprites = LayeredUpdates()
        self.buildings = []
        self.resource_balls = []
        self.grid_map = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        self.selected_building = BUILDING_TYPES['conveyor_right']
        self.mouse_pos = (0, 0)
        
        self.toolbar_buttons = self.create_toolbar_buttons()
        self.load_level(self.current_level)

    def create_toolbar_buttons(self):
        buttons = []
        button_size = 50
        start_x = GRID_WIDTH * GRID_SIZE + 25
        start_y = 80
        building_list = [
            ('conveyor_right', '→'),
            ('conveyor_down', '↓'),
            ('conveyor_left', '←'),
            ('conveyor_up', '↑'),
            ('generator_red', 'R'),
            ('generator_blue', 'B'),
            ('recycler', 'Rec'),
            ('filter_red_right', 'FR'),
            ('filter_blue_down', 'FB')
        ]
        
        for i, (b_type, label) in enumerate(building_list):
            row = i % 4
            col = i // 4
            x = start_x + col * (button_size + 10)
            y = start_y + row * (button_size + 10)
            buttons.append({
                'rect': pygame.Rect(x, y, button_size, button_size),
                'type': BUILDING_TYPES[b_type],
                'label': label,
                'name': b_type
            })
        return buttons

    def load_level(self, level_index):
        if level_index >= len(LEVELS):
            print("恭喜！所有关卡完成！")
            pygame.quit()
            sys.exit()
        
        level = LEVELS[level_index]
        self.target_collect = level['target_collect']
        self.collected = 0
        
        for building in self.buildings:
            building.kill()
        self.buildings.clear()
        
        for ball in self.resource_balls:
            ball.kill()
        self.resource_balls.clear()
        
        self.grid_map = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for y, row in enumerate(level['map']):
            for x, building_type in enumerate(row):
                if building_type != 0:
                    self.place_building(x, y, building_type)

    def place_building(self, grid_x, grid_y, building_type):
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            if self.grid_map[grid_y][grid_x] != 0:
                for building in self.buildings:
                    if building.grid_x == grid_x and building.grid_y == grid_y:
                        building.kill()
                        self.buildings.remove(building)
                        break
            
            if building_type != 0:
                building = Building(grid_x, grid_y, building_type)
                self.all_sprites.add(building)
                self.buildings.append(building)
                self.grid_map[grid_y][grid_x] = building_type
            else:
                self.grid_map[grid_y][grid_x] = 0

    def spawn_resource(self, generator):
        if generator.is_generator():
            resource_type = generator.get_resource_type()
            x = generator.grid_x * GRID_SIZE + GRID_SIZE // 2
            y = generator.grid_y * GRID_SIZE + GRID_SIZE // 2
            ball = ResourceBall(x, y, resource_type)
            ball.velocity = generator.get_direction()
            self.all_sprites.add(ball)
            self.resource_balls.append(ball)

    def check_collisions(self):
        for ball in self.resource_balls:
            grid_x, grid_y = ball.get_grid_pos()
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                building_type = self.grid_map[grid_y][grid_x]
                
                if building_type != 0:
                    distance = ball.get_center_distance_to_grid(grid_x, grid_y)
                    
                    if distance < 8:
                        for building in self.buildings:
                            if building.grid_x == grid_x and building.grid_y == grid_y:
                                if building.is_recycler():
                                    self.collected += 1
                                    ball.kill()
                                    self.resource_balls.remove(ball)
                                    break
                                elif building.is_filter():
                                    filter_type = building.get_filter_type()
                                    if ball.resource_type == filter_type:
                                        ball.velocity = building.get_direction()
                                    center_x = grid_x * GRID_SIZE + GRID_SIZE // 2
                                    center_y = grid_y * GRID_SIZE + GRID_SIZE // 2
                                    ball.position = Vector2(center_x, center_y)
                                else:
                                    ball.velocity = building.get_direction()
                                    center_x = grid_x * GRID_SIZE + GRID_SIZE // 2
                                    center_y = grid_y * GRID_SIZE + GRID_SIZE // 2
                                    ball.position = Vector2(center_x, center_y)
                                break
        
        for ball in self.resource_balls[:]:
            grid_x, grid_y = ball.get_grid_pos()
            if grid_x < 0 or grid_x >= GRID_WIDTH or grid_y < 0 or grid_y >= GRID_HEIGHT:
                ball.kill()
                self.resource_balls.remove(ball)

    def check_blockages(self):
        grid_counts = {}
        for ball in self.resource_balls:
            grid_pos = ball.get_grid_pos()
            grid_counts[grid_pos] = grid_counts.get(grid_pos, 0) + 1
        
        for grid_pos, count in grid_counts.items():
            if count > 3:
                self.lives -= 1
                balls_to_remove = [b for b in self.resource_balls if b.get_grid_pos() == grid_pos]
                for ball in balls_to_remove:
                    ball.kill()
                    self.resource_balls.remove(ball)
                if self.lives <= 0:
                    print("游戏结束！")
                    pygame.quit()
                    sys.exit()

    def update(self):
        if not self.paused:
            for _ in range(self.game_speed):
                level = LEVELS[self.current_level]
                
                for building in self.buildings:
                    if building.is_generator():
                        building.spawn_timer += 1
                        resource_type = building.get_resource_type()
                        spawn_rate = level['spawn_rates'].get(resource_type, 120)
                        if building.spawn_timer >= spawn_rate:
                            self.spawn_resource(building)
                            building.spawn_timer = 0
                
                if not self.build_mode:
                    for ball in self.resource_balls:
                        ball.update()
                    
                    self.check_collisions()
                    self.check_blockages()
                
                if self.collected >= self.target_collect:
                    self.current_level += 1
                    self.load_level(self.current_level)

    def draw_grid(self):
        for x in range(GRID_WIDTH + 1):
            pygame.draw.line(self.screen, COLORS['grid'], 
                            (x * GRID_SIZE, 0), 
                            (x * GRID_SIZE, GRID_HEIGHT * GRID_SIZE))
        for y in range(GRID_HEIGHT + 1):
            pygame.draw.line(self.screen, COLORS['grid'], 
                            (0, y * GRID_SIZE), 
                            (GRID_WIDTH * GRID_SIZE, y * GRID_SIZE))

    def draw_toolbar(self):
        toolbar_rect = pygame.Rect(GRID_WIDTH * GRID_SIZE, 0, 200, SCREEN_HEIGHT)
        pygame.draw.rect(self.screen, COLORS['ui_panel'], toolbar_rect)
        
        title = self.font.render("工具栏", True, COLORS['text'])
        self.screen.blit(title, (GRID_WIDTH * GRID_SIZE + 60, 20))
        
        for button in self.toolbar_buttons:
            color = COLORS['ui_button_hover'] if button['type'] == self.selected_building else COLORS['ui_button']
            pygame.draw.rect(self.screen, color, button['rect'])
            pygame.draw.rect(self.screen, COLORS['grid'], button['rect'], 2)
            
            label = self.font.render(button['label'], True, COLORS['text'])
            label_rect = label.get_rect(center=button['rect'].center)
            self.screen.blit(label, label_rect)
        
        mode_text = "建造模式" if self.build_mode else "运行模式"
        mode_color = (0, 200, 0) if self.build_mode else (200, 100, 0)
        mode_surf = self.font.render(mode_text, True, mode_color)
        self.screen.blit(mode_surf, (GRID_WIDTH * GRID_SIZE + 45, 300))
        
        speed_text = f"速度: {self.game_speed}x" if not self.paused else "暂停"
        speed_surf = self.font.render(speed_text, True, COLORS['text'])
        self.screen.blit(speed_surf, (GRID_WIDTH * GRID_SIZE + 50, 330))
        
        lives_surf = self.font.render(f"生命: {self.lives}", True, (255, 100, 100))
        self.screen.blit(lives_surf, (GRID_WIDTH * GRID_SIZE + 50, 360))
        
        progress_surf = self.font.render(f"{self.collected}/{self.target_collect}", True, COLORS['text'])
        self.screen.blit(progress_surf, (GRID_WIDTH * GRID_SIZE + 50, 390))
        
        level_surf = self.font.render(f"关卡: {self.current_level + 1}", True, COLORS['text'])
        self.screen.blit(level_surf, (GRID_WIDTH * GRID_SIZE + 50, 420))

        help_text1 = self.font.render("SPACE-切换模式", True, COLORS['text'])
        help_text2 = self.font.render("1/2/3-速度", True, COLORS['text'])
        self.screen.blit(help_text1, (GRID_WIDTH * GRID_SIZE + 10, 460))
        self.screen.blit(help_text2, (GRID_WIDTH * GRID_SIZE + 10, 485))

    def draw_building_preview(self):
        grid_x = self.mouse_pos[0] // GRID_SIZE
        grid_y = self.mouse_pos[1] // GRID_SIZE
        
        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
            preview = Building(grid_x, grid_y, self.selected_building)
            preview.image.set_alpha(128)
            self.screen.blit(preview.image, preview.rect)

    def draw(self):
        self.screen.fill(COLORS['background'])
        self.draw_grid()
        self.all_sprites.draw(self.screen)
        self.draw_toolbar()
        
        if self.build_mode and self.mouse_pos[0] < GRID_WIDTH * GRID_SIZE:
            self.draw_building_preview()
        
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in self.toolbar_buttons:
                        if button['rect'].collidepoint(event.pos):
                            self.selected_building = button['type']
                            break
                    else:
                        if self.build_mode:
                            grid_x = event.pos[0] // GRID_SIZE
                            grid_y = event.pos[1] // GRID_SIZE
                            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                                self.place_building(grid_x, grid_y, self.selected_building)
                
                elif event.button == 3:
                    if self.build_mode:
                        grid_x = event.pos[0] // GRID_SIZE
                        grid_y = event.pos[1] // GRID_SIZE
                        if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                            self.place_building(grid_x, grid_y, 0)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.build_mode = not self.build_mode
                elif event.key == pygame.K_1:
                    self.game_speed = 1
                    self.paused = False
                elif event.key == pygame.K_2:
                    self.game_speed = 2
                    self.paused = False
                elif event.key == pygame.K_3:
                    self.paused = not self.paused

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
