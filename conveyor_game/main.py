"""
传送带物流游戏主程序
"""
import pygame
import sys
from pygame.math import Vector2

from settings import *
from sprites import Building, Resource, GridOverlay, PreviewOverlay
from ui import UI


class Game:
    """游戏主类"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Conveyor Belt Logistics Game")
        self.clock = pygame.time.Clock()
        
        # 游戏状态
        self.build_mode = True  # True=建造模式, False=运行模式
        self.game_speed = SPEED_1X
        self.running = True
        
        # 关卡状态
        self.current_level = 0
        self.hp = 100
        self.collected = 0
        self.target = 0
        
        # 建筑字典 {(x,y): Building}
        self.buildings = {}
        
        # 资源球组
        self.resources = pygame.sprite.Group()
        
        # 图层管理
        # Layer 0: 网格
        # Layer 1: 建筑
        # Layer 2: 资源球
        # Layer 3: 预览
        # Layer 4: UI（单独绘制）
        self.all_sprites = pygame.sprite.LayeredUpdates()
        
        # 创建网格覆盖层
        self.grid_overlay = GridOverlay()
        self.all_sprites.add(self.grid_overlay, layer=0)
        
        # 创建预览覆盖层
        self.preview = PreviewOverlay()
        self.all_sprites.add(self.preview, layer=3)
        
        # UI系统
        self.ui = UI(self)
        
        # 源生成计时器
        self.source_timers = {}
        
        # 加载关卡
        self.load_level(0)
    
    def load_level(self, level_index):
        """加载关卡"""
        if level_index >= len(LEVELS):
            print("Congratulations! All levels completed!")
            self.running = False
            return
        
        level_data = LEVELS[level_index]
        self.current_level = level_index
        self.hp = level_data["hp"]
        self.target = level_data["target"]
        self.collected = 0
        
        # 清理旧数据
        self.clear_dynamic_objects()
        self.buildings.clear()
        
        # 移除旧建筑精灵
        for sprite in list(self.all_sprites):
            if isinstance(sprite, Building):
                sprite.kill()
        
        # 加载地图
        for y, row in enumerate(level_data["map"]):
            for x, cell in enumerate(row):
                if cell != BUILDING_NONE:
                    building = Building(x, y, cell, DIR_RIGHT)
                    self.buildings[(x, y)] = building
                    self.all_sprites.add(building, layer=1)
        
        # 加载源
        for source_pos in level_data["sources"]:
            building = Building(source_pos[0], source_pos[1], BUILDING_SOURCE, DIR_RIGHT)
            self.buildings[source_pos] = building
            self.all_sprites.add(building, layer=1)
            self.source_timers[source_pos] = 0
        
        # 加载汇
        for sink_pos in level_data["sinks"]:
            building = Building(sink_pos[0], sink_pos[1], BUILDING_SINK, DIR_RIGHT)
            self.buildings[sink_pos] = building
            self.all_sprites.add(building, layer=1)
        
        print(f"Loaded {level_data['name']}")
    
    def clear_dynamic_objects(self):
        """清理动态物体（资源球等）"""
        # 清理所有资源球
        for resource in self.resources:
            resource.kill()
        self.resources.empty()
        self.source_timers.clear()
    
    def reset_level(self):
        """重置当前关卡"""
        # 清理资源球但保留计时器
        for resource in self.resources:
            resource.kill()
        self.resources.empty()
        
        self.collected = 0
        self.hp = LEVELS[self.current_level]["hp"]
        
        # 重新初始化源计时器（只针对仍然存在的源）
        self.source_timers.clear()
        level_data = LEVELS[self.current_level]
        for source_pos in level_data["sources"]:
            if source_pos in self.buildings and self.buildings[source_pos].building_type == BUILDING_SOURCE:
                self.source_timers[source_pos] = 0
    
    def next_level(self):
        """进入下一关"""
        self.load_level(self.current_level + 1)
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # 切换建造/运行模式
                    self.toggle_mode()
                elif event.key == pygame.K_1:
                    self.game_speed = SPEED_1X
                elif event.key == pygame.K_2:
                    self.game_speed = SPEED_2X
                elif event.key == pygame.K_p:
                    if self.game_speed == SPEED_PAUSE:
                        self.game_speed = SPEED_1X
                    else:
                        self.game_speed = SPEED_PAUSE
                elif event.key == pygame.K_r:
                    # 旋转建筑方向
                    self.ui.building_direction = (self.ui.building_direction + 1) % 4
                elif event.key == pygame.K_ESCAPE:
                    self.ui.selected_building = BUILDING_NONE
                    self.preview.set_building_type(BUILDING_NONE)
                elif event.key == pygame.K_F5:
                    # 重置关卡
                    self.reset_level()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # 检查是否点击UI
                    if mouse_pos[0] >= GAME_AREA_WIDTH:
                        if self.ui.handle_click(mouse_pos):
                            self.preview.set_building_type(self.ui.selected_building)
                    else:
                        # 在游戏区域点击
                        if self.build_mode:
                            self.handle_build_click(mouse_pos)
            
            elif event.type == pygame.MOUSEMOTION:
                # 更新预览位置
                self.preview.update(event.pos)
    
    def toggle_mode(self):
        """切换建造/运行模式"""
        self.build_mode = not self.build_mode
        if self.build_mode:
            # 进入建造模式：清理资源球和源计时器
            self.clear_dynamic_objects()
            # 重置游戏速度为1x
            self.game_speed = SPEED_1X
            print("Entering BUILD MODE")
        else:
            # 进入运行模式：重置关卡状态（清理旧资源球，重新初始化）
            self.reset_level()
            print("Entering RUN MODE")
    
    def handle_build_click(self, mouse_pos):
        """处理建造点击"""
        grid_x = mouse_pos[0] // GRID_SIZE
        grid_y = mouse_pos[1] // GRID_SIZE
        
        if grid_x >= GRID_WIDTH or grid_y >= GRID_HEIGHT:
            return
        
        pos = (grid_x, grid_y)
        
        if self.ui.selected_building == BUILDING_NONE:
            # 删除建筑
            if pos in self.buildings:
                building = self.buildings[pos]
                building.kill()
                del self.buildings[pos]
        else:
            # 放置建筑
            # 检查是否已有建筑
            if pos in self.buildings:
                # 更新方向
                building = self.buildings[pos]
                if building.building_type == self.ui.selected_building:
                    building.direction = self.ui.building_direction
                    building._render()
                else:
                    # 替换建筑
                    building.kill()
                    new_building = Building(grid_x, grid_y, self.ui.selected_building, self.ui.building_direction)
                    self.buildings[pos] = new_building
                    self.all_sprites.add(new_building, layer=1)
            else:
                # 创建新建筑
                new_building = Building(grid_x, grid_y, self.ui.selected_building, self.ui.building_direction)
                self.buildings[pos] = new_building
                self.all_sprites.add(new_building, layer=1)
    
    def spawn_resource(self, source_pos):
        """在源位置生成资源球"""
        # 确保源位置存在且是有效的源建筑
        if source_pos in self.buildings:
            source = self.buildings[source_pos]
            # 只有 SOURCE 类型的建筑才能生成资源球
            if source.building_type == BUILDING_SOURCE:
                center = source.get_center()
                resource = Resource(center.x, center.y)
                resource.set_velocity_from_direction(source.direction)
                self.resources.add(resource)
                self.all_sprites.add(resource, layer=2)
    
    def check_collisions(self):
        """检测碰撞和堆积"""
        # 统计每个网格的资源球数量
        grid_counts = {}
        for resource in self.resources:
            grid = resource.current_grid
            if grid not in grid_counts:
                grid_counts[grid] = []
            grid_counts[grid].append(resource)
        
        # 检查堆积上限
        for grid, resources in grid_counts.items():
            if len(resources) > STACK_LIMIT:
                # 堵塞！扣除生命值
                self.hp -= 1
                print(f"Grid {grid} is jammed! HP: {self.hp}")
                # 移除多余的资源球
                for resource in resources[STACK_LIMIT:]:
                    resource.kill()
        
        # 检查资源球是否被收集（通过 _on_enter_building 标记）
        for resource in list(self.resources):
            if resource.collected:
                self.collected += 1
                print(f"Resource collected! {self.collected}/{self.target}")
                # 从资源组中移除（但已经在 _on_enter_building 中 kill 了）
                self.resources.remove(resource)
    
    def update(self):
        """更新游戏逻辑"""
        if self.game_speed == SPEED_PAUSE:
            return
        
        dt = self.game_speed
        
        if not self.build_mode:
            # 运行模式：更新资源球
            
            # 生成资源
            level_data = LEVELS[self.current_level]
            source_rate = level_data["source_rate"]
            
            for source_pos in self.source_timers:
                self.source_timers[source_pos] += dt
                if self.source_timers[source_pos] >= source_rate:
                    self.source_timers[source_pos] = 0
                    self.spawn_resource(source_pos)
            
            # 更新资源球
            for resource in self.resources:
                resource.update(dt, self.buildings)
            
            # 检测碰撞
            self.check_collisions()
            
            # 检查关卡完成
            if self.collected >= self.target:
                print(f"Level {self.current_level + 1} completed!")
                self.next_level()
            
            # 检查游戏结束
            if self.hp <= 0:
                print("Game Over!")
                self.reset_level()
    
    def draw(self):
        """绘制游戏画面"""
        # 清空屏幕
        self.screen.fill(COLOR_BACKGROUND)
        
        # 绘制所有精灵
        self.all_sprites.draw(self.screen)
        
        # 绘制UI
        self.ui.draw()
        
        # 更新显示
        pygame.display.flip()
    
    def run(self):
        """主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


def main():
    """入口函数"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
