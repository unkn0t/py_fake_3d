# import pygame.ftfont
import pygame as pg
# import pygame.freetype
from player import Player
from map import Map
from pygame.math import Vector2

MAP = "\
111111111111111111111111\
100000000000000000000001\
100000000000000000000001\
100000000000000000000001\
100000222220000303030001\
100000200020000000000001\
100000200020000300030001\
100000200020000000000001\
100000220220000303030001\
100000000000000000000001\
100000000000000000000001\
100000000000000000000001\
100000000000000000000001\
100000000000000000000001\
100000000000000000000001\
100000000000000000000001\
144444444000000000000001\
140400004000000000000001\
140000504000000000000001\
140400004000000000000001\
140444444000000000000001\
140000000000000000000001\
144444444000000000000001\
111111111111111111111111"

def create_screen() -> pg.Surface:
    modes = pg.display.list_modes()
    flags = pg.FULLSCREEN
    screen = pg.display.set_mode(modes[0], flags=flags, vsync=1)
    return screen

class Application:
    def __init__(self):
        pg.init()

        self.running = False
        self.screen = create_screen()
        self.clock = pg.time.Clock()
        # self.font = pygame.freetype.SysFont('iosevka', 20, bold=True)
        self.axis = Vector2(0, 0)
        pg.mouse.set_visible(False)
        pg.event.set_grab(True)

    def __del__(self):
        pg.quit()
    
    def run(self):
        self.__main_loop()

    def __main_loop(self): 
        self.running = True
        
        self.map = Map(MAP, 24, 24)
        self.player = Player(Vector2(22, 12), 2.5, 8.0)
        
        dt = 0.01

        while self.running:     
            self.__handle_events()
            self.player.rotate(dt)
            self.player.move(self.axis, dt)
            self.__render(dt)
            dt = self.clock.tick() / 1000.0
    
    def __render(self, delta: float):
        self.screen.fill(0x000000)
        self.player.render_view(self.screen, self.map)
        self.__render_fps_counter(delta)
        pg.display.flip()

    def __render_fps_counter(self, delta: float):
        fps = 1.0 / delta
        # self.font.render_to(self.screen, (10, 10), f"FPS: {fps}", pg.Color(0, 255, 0))
        # self.screen.blit(text, (10, 10)) 

    def __handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_w:
                    self.axis.y = 1
                if event.key == pg.K_s:
                    self.axis.y = -1
                if event.key == pg.K_a:
                    self.axis.x = -1
                if event.key == pg.K_d:
                    self.axis.x = 1

            elif event.type == pg.KEYUP:
                if event.key == pg.K_w:
                    self.axis.y = 0
                if event.key == pg.K_s:
                    self.axis.y = 0
                if event.key == pg.K_a:
                    self.axis.x = 0
                if event.key == pg.K_d:
                    self.axis.x = 0
        
        if self.axis != Vector2(0, 0):
            self.axis.normalize_ip()
