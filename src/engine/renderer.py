import pygame
import pygame.display as display
import pygame.font as font
import numpy as np

from OpenGL.GL import *
import glm

from dataclasses import dataclass

from engine import shader

class Renderer:
    def __init__(self):
        modes = display.list_modes()
        self.viewport = glm.vec2(modes[0])
        self.screen = display.set_mode(modes[0], pygame.OPENGL | pygame.DOUBLEBUF | pygame.FULLSCREEN)

        self.font = font.SysFont('iosevka', size=30)
        self.clock = pygame.time.Clock()
        self.dt = 0.0
        
        self.camera = Camera(self.viewport, 70.0, glm.vec2(-1, 0), 100.0, glm.vec2(11.5, 8))

        # triangle
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.triangle_bootstrap()

    def render_text(self, text, position):
        glUseProgram(0)
        surface = self.font.render(text, True, (0, 255, 0, 255)).convert_alpha()
        data = pygame.image.tobytes(surface, "RGBA", True)
        glWindowPos2f(position.x, position.y)
        glDrawPixels(surface.get_width(), surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, data)
    
    def triangle_bootstrap(self):
        glViewport(0, 0, int(self.viewport.x), int(self.viewport.y))
        
        self.shader = shader.Shader(None, "shaders/fragment.glsl")

        self.vertices = np.array([
            1, 1, 0,
            1, -1, 0,
            -1, -1, 0,
            -1, 1, 0,
        ], dtype=np.float32) 

        self.indices = np.array([0, 1, 3, 1, 2, 3], dtype=np.uint32)

        self.vbo = glGenBuffers(1)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.size * 4, self.vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * 4, None)
        glEnableVertexAttribArray(0)

        glBindBuffer(GL_ARRAY_BUFFER, 0) 
        glBindVertexArray(0) 
        
        self.shader.use()
        self.shader.set_vec2("iResolution", self.viewport)

    def render_triangle(self):
        self.shader.use()
        self.shader.set_vec2("iViewDirection", self.camera.view_direction)
        self.shader.set_vec2("iPosition", self.camera.position)
        # self.shader.set_float("iTime", pygame.time.get_ticks() / 1000.0)
        glBindVertexArray(self.vao) 
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, self.indices)

    def render(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.render_triangle()
        self.render_text(f'Frame time: {self.dt}ms', glm.vec2(10, 10))
        self.render_text(f'FPS: {self.clock.get_fps()}', glm.vec2(10, 45))
        display.flip()
        self.dt = self.clock.tick()

@dataclass(init = False, repr = True, eq = True)
class Plane:
    length: float
    direction: glm.vec2
    
    def __init__(self, fov: float, view_direction: glm.vec2):
        self.length = glm.tan(glm.radians(fov / 2.0)) 
        self.direction = glm.vec2(view_direction.y, -view_direction.x) * self.length

class Camera:
    def __init__(self, viewport: glm.vec2, fov: float, view_direction: glm.vec2, view_distance: float, position: glm.vec2):
        self.viewport = viewport
        self.fov = fov
        self.view_direction = view_direction
        self.view_distance = view_distance
        self.position = position
        self.plane = Plane(fov, view_direction)
        
        self.tex_height = 64
        self.tex_width = 64
        self.textures = []
        self.load_textures()

    def load_textures(self):
        self.textures.append(pygame.image.load('pics/eagle.png'))
        self.textures.append(pygame.image.load('pics/redbrick.png'))
        self.textures.append(pygame.image.load('pics/purplestone.png'))
        self.textures.append(pygame.image.load('pics/greystone.png'))
        self.textures.append(pygame.image.load('pics/bluestone.png'))
        self.textures.append(pygame.image.load('pics/mossy.png'))
        self.textures.append(pygame.image.load('pics/wood.png'))
        self.textures.append(pygame.image.load('pics/colorstone.png'))

        for i in range(len(self.textures)):
            self.textures[i] = pygame.image.tobytes(self.textures[i], 'RGB')

    def move(self, direction: glm.vec2, speed: float, dt: float):
        basis = glm.mat2x2(self.view_direction.y, self.view_direction.x, -self.view_direction.x, self.view_direction.y)
        final_direction = direction * basis
        final_position = self.position + final_direction * speed * dt
        if MAP[int(final_position.y), int(final_position.x)] == 0:
            self.position = final_position

    def rotate(self, dt: float):
        rotation = -pygame.mouse.get_rel()[0] / 960.0
        self.view_direction = glm.rotateZ(glm.vec3(self.view_direction.x, self.view_direction.y, 0), rotation * dt * 400.0).xy
        self.plane = Plane(self.fov, self.view_direction)

    def render_view(self, screen: pygame.Surface):
        for x in range(int(self.viewport.x)):
            uv_x = 2.0 * x / self.viewport.x - 1.0
            ray_direction = self.view_direction + self.plane.direction * uv_x
           
            map_cell_x = int(self.position.x)
            map_cell_y = int(self.position.y)
            
            delta_distance = glm.vec2(1e30, 1e30)
            side_distance = glm.vec2()
            
            if ray_direction.x != 0.0:
                delta_distance.x = glm.abs(1.0 / ray_direction.x)
            if ray_direction.y != 0.0:
                delta_distance.y = glm.abs(1.0 / ray_direction.y)

            if ray_direction.x < 0:
                step_x = -1
                side_distance.x = (self.position.x - map_cell_x) * delta_distance.x
            else:
                step_x = 1
                side_distance.x = (map_cell_x - self.position.x + 1.0) * delta_distance.x

            if ray_direction.y < 0:
                step_y = -1
                side_distance.y = (self.position.y - map_cell_y) * delta_distance.y
            else:
                step_y = 1
                side_distance.y = (map_cell_y - self.position.y + 1.0) * delta_distance.y

            hit = False
            side = False
            while not hit:
                if side_distance.x < side_distance.y:
                    side_distance.x += delta_distance.x
                    map_cell_x += step_x
                    side = False
                else:
                    side_distance.y += delta_distance.y
                    map_cell_y += step_y
                    side = True
                
                hit = MAP[map_cell_x, map_cell_y] >= 1

            texture_index = MAP[map_cell_x, map_cell_y] - 1

            if side:
                wall_distance = side_distance.y - delta_distance.y
                wall_x = self.position.x + wall_distance * ray_direction.x
            else:
                wall_distance = side_distance.x - delta_distance.x
                wall_x = self.position.y + wall_distance * ray_direction.y
            
            wall_x -= glm.floor(wall_x) 
            tex_x = int(wall_x * self.tex_width)

            if not side and ray_direction.x > 0: 
                tex_x = self.tex_width - tex_x - 1
            if side and ray_direction.y < 0: 
                tex_x = self.tex_width - tex_x - 1
            
            line_height = int(self.viewport.y / wall_distance)
            step = 1.0 * self.tex_height / line_height

            draw_start = int(max(-line_height // 2 + self.viewport.y // 2, 0))
            draw_end = int(min(line_height // 2 + self.viewport.y // 2, self.viewport.y - 1))
            tex_pos = (draw_start - self.viewport.y // 2 + line_height // 2) * step
      
            for y in range(draw_start, draw_end):
                tex_y = int(tex_pos) & int(self.tex_height - 1)
                tex_pos += step
                offset = 3 * self.tex_width * tex_y + 3 * tex_x
                texture = self.textures[texture_index];
                color = (texture[offset] << 16) + (texture[offset + 1] << 8) + texture[offset + 2] 
                if side: 
                    color = (color >> 1) & 8355711;
                screen.set_at((x, y), color)

MAP = np.array([
[4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,7,7,7,7,7,7,7,7],
[4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
[4,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
[4,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7],
[4,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,7,0,0,0,0,0,0,7],
[4,0,4,0,0,0,0,5,5,5,5,5,5,5,5,5,7,7,0,7,7,7,7,7],
[4,0,5,0,0,0,0,5,0,5,0,5,0,5,0,5,7,0,0,0,7,7,7,1],
[4,0,6,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,8],
[4,0,7,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,7,7,7,1],
[4,0,8,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,0,0,0,8],
[4,0,0,0,0,0,0,5,0,0,0,0,0,0,0,5,7,0,0,0,7,7,7,1],
[4,0,0,0,0,0,0,5,5,5,5,0,5,5,5,5,7,7,7,7,7,7,7,1],
[6,6,6,6,6,6,6,6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6],
[8,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4],
[6,6,6,6,6,6,0,6,6,6,6,0,6,6,6,6,6,6,6,6,6,6,6,6],
[4,4,4,4,4,4,0,4,4,4,6,0,6,2,2,2,2,2,2,2,3,3,3,3],
[4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2],
[4,0,0,0,0,0,0,0,0,0,0,0,6,2,0,0,5,0,0,2,0,0,0,2],
[4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2],
[4,0,6,0,6,0,0,0,0,4,6,0,0,0,0,0,5,0,0,0,0,0,0,2],
[4,0,0,5,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,2,0,2,2],
[4,0,6,0,6,0,0,0,0,4,6,0,6,2,0,0,5,0,0,2,0,0,0,2],
[4,0,0,0,0,0,0,0,0,4,6,0,6,2,0,0,0,0,0,2,0,0,0,2],
[4,4,4,4,4,4,4,4,4,4,1,1,1,2,2,2,2,2,2,3,3,3,3,3]], dtype=int)

