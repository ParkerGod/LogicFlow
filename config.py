import pygame

GRID_SIZE = 40
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GAME_AREA_WIDTH = 1000
TOOLBAR_WIDTH = 200

FPS = 60

COLORS = {
    'background': (30, 30, 35),
    'grid_line': (50, 50, 55),
    'toolbar_bg': (45, 45, 50),
    'toolbar_border': (70, 70, 80),
    'button_normal': (60, 60, 70),
    'button_hover': (80, 80, 90),
    'button_selected': (100, 150, 200),
    'text_white': (220, 220, 220),
    'text_highlight': (255, 200, 100),
    'conveyor': (80, 80, 90),
    'conveyor_arrow': (150, 150, 160),
    'producer': (100, 180, 100),
    'consumer': (180, 100, 100),
    'filter': (180, 150, 80),
    'resource_red': (220, 80, 80),
    'resource_blue': (80, 120, 220),
    'resource_green': (80, 200, 80),
    'resource_yellow': (220, 200, 80),
    'blocked': (200, 50, 50),
    'preview': (100, 150, 200, 128),
}

BUILDING_TYPES = {
    'conveyor_right': {'name': '传送带→', 'color': COLORS['conveyor'], 'direction': (1, 0)},
    'conveyor_left': {'name': '传送带←', 'color': COLORS['conveyor'], 'direction': (-1, 0)},
    'conveyor_up': {'name': '传送带↑', 'color': COLORS['conveyor'], 'direction': (0, -1)},
    'conveyor_down': {'name': '传送带↓', 'color': COLORS['conveyor'], 'direction': (0, 1)},
    'producer_red': {'name': '红色产出器', 'color': COLORS['producer'], 'produces': 'red'},
    'producer_blue': {'name': '蓝色产出器', 'color': COLORS['producer'], 'produces': 'blue'},
    'producer_green': {'name': '绿色产出器', 'color': COLORS['producer'], 'produces': 'green'},
    'consumer_red': {'name': '红色回收站', 'color': COLORS['consumer'], 'accepts': 'red'},
    'consumer_blue': {'name': '蓝色回收站', 'color': COLORS['consumer'], 'accepts': 'blue'},
    'consumer_green': {'name': '绿色回收站', 'color': COLORS['consumer'], 'accepts': 'green'},
    'filter_red': {'name': '红色过滤器', 'color': COLORS['filter'], 'filter_type': 'red'},
    'filter_blue': {'name': '蓝色过滤器', 'color': COLORS['filter'], 'filter_type': 'blue'},
    'filter_green': {'name': '绿色过滤器', 'color': COLORS['filter'], 'filter_type': 'green'},
}

RESOURCE_COLORS = {
    'red': COLORS['resource_red'],
    'blue': COLORS['resource_blue'],
    'green': COLORS['resource_green'],
    'yellow': COLORS['resource_yellow'],
}

MAX_RESOURCES_PER_CELL = 3
BLOCKED_DAMAGE = 1
INITIAL_LIVES = 5

GAME_SPEEDS = [0, 1, 2]
GAME_SPEED_NAMES = ['暂停', '1x', '2x']
