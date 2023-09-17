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
        self.shader.set_textures("iTextures", [0, 1, 2, 3, 4, 5, 6, 7])

    def render_triangle(self):
        self.shader.use()
        self.shader.set_vec2("iViewDirection", self.camera.view_direction)
        self.shader.set_vec2("iPosition", self.camera.position)
        glBindVertexArray(self.vao) 
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, self.indices)

    def render(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.render_triangle()
        self.render_text(f'Frame time: {self.dt}ms', glm.vec2(10, 10))
        self.render_text(f'FPS: {int(self.clock.get_fps())}', glm.vec2(10, 45))
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
        self.texture_ids = np.zeros(8, dtype=np.uint)
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
            glActiveTexture(0x84C0 + i)
            self.textures[i] = pygame.image.tobytes(self.textures[i], 'RGB', True)
            self.texture_ids[i] = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_ids[i])
    
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
            
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, self.tex_width, self.tex_height, 0, GL_RGB, GL_UNSIGNED_BYTE, self.textures[i])
            glGenerateMipmap(GL_TEXTURE_2D);

    def move(self, direction: glm.vec2, speed: float, dt: float):
        basis = glm.mat2x2(self.view_direction.y, self.view_direction.x, -self.view_direction.x, self.view_direction.y)
        final_direction = direction * basis
        final_position = self.position + final_direction * speed * dt
        if MAP[int(final_position.y), int(final_position.x)] == 0:
            self.position = final_position

    def rotate(self, dt: float):
        rotation = -pygame.mouse.get_rel()[0]
        self.view_direction = glm.rotateZ(glm.vec3(self.view_direction.x, self.view_direction.y, 0), rotation * dt).xy
        self.plane = Plane(self.fov, self.view_direction)

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

