import pygame
from pygame.locals import *

import glm

from engine import renderer 

class App:
    def __init__(self):
        print("Initializing...")
        pygame.init()

        self.running = False
        self.renderer = renderer.Renderer()       

        self.axis = glm.vec2(0,0)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)

    def run(self):
        self.running = True
        
        while self.running:
            self.__handle_events()

            self.renderer.camera.rotate(self.renderer.dt / 1000.0)
            self.renderer.camera.move(self.axis, 2.0, self.renderer.dt / 1000.0)
                
            self.renderer.render()

    def __handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                if event.key == K_w:
                    self.axis.y = 1
                if event.key == K_s:
                    self.axis.y = -1
                if event.key == K_a:
                    self.axis.x = -1
                if event.key == K_d:
                    self.axis.x = 1

            elif event.type == KEYUP:
                if event.key == K_w:
                    self.axis.y = 0
                if event.key == K_s:
                    self.axis.y = 0
                if event.key == K_a:
                    self.axis.x = 0
                if event.key == K_d:
                    self.axis.x = 0
        
        if self.axis != glm.vec2(0, 0):
            self.axis = glm.normalize(self.axis)
    
    def __del__(self):
        print("Quiting...")
        pygame.quit()
