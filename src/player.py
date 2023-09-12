import math
import pygame as pg
from map import Map
import numpy as np

from pygame.math import Vector2

class Player:
    def __init__(self, position: Vector2, speed: float, rotation_speed: float, direction = Vector2(-1, 0), fov = 70.0): 
        self.position = position
        self.direction = direction
        self.plane_length = math.tan(math.radians(fov / 2)) 
        self.camera_plane = Vector2(direction.y, -direction.x) * self.plane_length
        
        self.speed = speed
        self.rotation_speed = rotation_speed 

    def move(self, dir: Vector2, delta: float, map: Map):
        basis = np.matrix([[self.direction.y, -self.direction.x], [self.direction.x, self.direction.y]]) 
        final_direction = np.array([dir.x, dir.y]) @ basis
        final_position = self.position + Vector2(final_direction[0, 0], final_direction[0, 1]) * self.speed * delta
        if not map.is_wall(int(final_position.x), int(final_position.y)):
            self.position = final_position

    def rotate(self, delta: float):
        rotation = -pg.mouse.get_rel()[0] / 960.0
        self.direction.rotate_rad_ip(rotation * self.rotation_speed * delta * 10.0)
        self.camera_plane = Vector2(self.direction.y, -self.direction.x) * self.plane_length

    def render_view(self, screen: pg.Surface, map: Map):
        screen_width = screen.get_width()
        screen_height = screen.get_height()

        for x in range(screen_width):
            camera_x = 2 * x / float(screen_width) - 1
            ray_direction = self.direction + self.camera_plane * camera_x
           
            map_cell_x = int(self.position.x)
            map_cell_y = int(self.position.y)    
            
            if ray_direction.x == 0:
                delta_distance_x = math.inf
            else:
                delta_distance_x = abs(1.0 / ray_direction.x)
            
            if ray_direction.y == 0:
                delta_distance_y = math.inf
            else:
                delta_distance_y = abs(1.0 / ray_direction.y)

            if ray_direction.x < 0:
                step_x = -1
                side_distance_x = (self.position.x - map_cell_x) * delta_distance_x
            else:
                step_x = 1
                side_distance_x = (map_cell_x - self.position.x + 1.0) * delta_distance_x

            if ray_direction.y < 0:
                step_y = -1
                side_distance_y = (self.position.y - map_cell_y) * delta_distance_y
            else:
                step_y = 1
                side_distance_y = (map_cell_y - self.position.y + 1.0) * delta_distance_y

            hit = False
            side = False
            while not hit:
                if side_distance_x < side_distance_y:
                    side_distance_x += delta_distance_x
                    map_cell_x += step_x
                    side = False
                else:
                    side_distance_y += delta_distance_y
                    map_cell_y += step_y
                    side = True
                
                # print(f"X: {x}, cell: {map_cell_x}, {map_cell_y}") 
                hit = map.is_wall(map_cell_x, map_cell_y)

            if side:
                wall_distance = side_distance_y - delta_distance_y
            else:
                wall_distance = side_distance_x - delta_distance_x

            # draw
            line_height = int(screen_height / wall_distance)
            draw_start = max(-line_height // 2 + screen_height // 2, 0)
            draw_end = min(line_height // 2 + screen_height // 2, screen_height - 1)

            if side:
                color = pg.Color(128, 128, 128)
            else:
                color = pg.Color(255, 255, 255)

            pg.draw.line(screen, color, (x, draw_start), (x, draw_end))

