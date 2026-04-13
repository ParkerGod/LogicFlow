import pygame
from config import GRID_SIZE, BUILDING_TYPES

class CollisionManager:
    def __init__(self, game):
        self.game = game
    
    def check_resource_at_building_center(self, resource):
        grid_x, grid_y = resource.get_current_grid()
        
        if (grid_x, grid_y) not in self.game.buildings_dict:
            return None
        
        building = self.game.buildings_dict[(grid_x, grid_y)]
        
        if resource.is_at_grid_center():
            return building
        
        return None
    
    def process_resource_collision(self, resource, building):
        building_type = building.building_type
        
        if 'conveyor' in building_type:
            direction = building.config['direction']
            resource.set_velocity(direction)
        
        elif 'filter' in building_type:
            filter_type = building.config['filter_type']
            if resource.resource_type == filter_type:
                direction = building.config.get('direction', (1, 0))
                resource.set_velocity(direction)
    
    def get_resources_in_grid(self, resources, grid_x, grid_y):
        count = 0
        for resource in resources:
            rx, ry = resource.get_current_grid()
            if rx == grid_x and ry == grid_y:
                count += 1
        return count
    
    def check_blocked_grids(self, resources):
        blocked_grids = set()
        grid_counts = {}
        
        for resource in resources:
            grid = resource.get_current_grid()
            grid_counts[grid] = grid_counts.get(grid, 0) + 1
        
        for grid, count in grid_counts.items():
            if count > 3:
                blocked_grids.add(grid)
        
        return blocked_grids
    
    def check_resource_reached_consumer(self, resource, building):
        if 'consumer' in building.building_type:
            accepts = building.config['accepts']
            if resource.resource_type == accepts:
                return True
        return False
    
    def check_resource_out_of_bounds(self, resource, grid_width, grid_height):
        grid_x, grid_y = resource.get_current_grid()
        return grid_x < 0 or grid_x >= grid_width or grid_y < 0 or grid_y >= grid_height
