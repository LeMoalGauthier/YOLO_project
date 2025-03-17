import gym
import pygame as pg
import numpy as np
import sys
from gym import spaces

BLOC_WIDTH = 61
BLOC_HEIGHT = 20 

class BreakOut(gym.Env):
    def __init__(self, WIDTH: int = 1280, HEIGHT: int = 720, rows = 3, ball_speed = 7):
        super(BreakOut, self).__init__()
        pg.init()
        self.clock = pg.time.Clock()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

        self.ball_radius = 6
        self.paddle_width = 112
        self.paddle_height = 18
        self.paddle_speed = 10

        self.paddle_player_x = WIDTH // 2
        self.paddle_player_y = HEIGHT - self.paddle_height

        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2 - 50
        self.ball_speed = ball_speed

        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))

        self.score_player = 0
        self.life = 3
        self.nb_rows = rows
        # 80 Correspond to the bloc width
        self.nb_columns = self.WIDTH // BLOC_WIDTH -1

        self.dirty_rects = []
        self.background = None
        self.need_redraw = True

        # Définition des actions : 0 = rien, 1 = haut et 2 = bas
        self.action_space = spaces.Discrete(18)
        self.low = np.zeros((self.WIDTH, self.HEIGHT, 3))
        self.high = np.zeros((self.WIDTH, self.HEIGHT, 3))
        self.high.fill(255)
        self.observation_space = spaces.Box(
            low = self.low,
            high = self.high)
        
        self.load_assets()
        self.reset()

    def load_assets(self):
        """Pré-calculer toutes les transformations d'images"""
        self.background_asset = pg.image.load("breakout/BasicBreakoutAssetPack/background.png").convert()
        self.background = pg.transform.scale(self.background_asset, (self.WIDTH, self.HEIGHT))
        
        self.ball_img = pg.image.load("breakout/BasicBreakoutAssetPack/ball.png").convert_alpha()
        self.ball_img = pg.transform.scale(self.ball_img, (self.ball_radius*2, self.ball_radius*2))
        
        self.paddle = pg.image.load("breakout/BasicBreakoutAssetPack/paddle.png").convert_alpha()
        self.paddle = pg.transform.scale(self.paddle, (self.paddle_width, self.paddle_height))
        
        # Charger le spritesheet une seule fois
        self.block_spritesheet = pg.image.load("breakout/BasicBreakOutAssetPack/blocks.png").convert_alpha()

    def control(self):
        """Détecte les touches pressées pour bouger la raquette."""
        keys = pg.key.get_pressed()
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            if self.paddle_player_x < self.WIDTH - self.paddle_width:
                self.paddle_player_x += self.paddle_speed
        if keys[pg.K_s] or keys[pg.K_LEFT]:
            if self.paddle_player_x > 0:
                self.paddle_player_x -= self.paddle_speed

    def check_event(self):
        """Vérifie les événements Pygame."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close()

    def update_score(self):
        if self.life < 1:
            self.reset()
            self.life = 3

    def check_life(self):       
        if self.ball_y + self.ball_radius > self.HEIGHT:
            self.life -= 1
            self.reset_ball()
            #print(self.life)
        
    def reset_ball(self):
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2 - 10
        self.ball_dx = np.random.choice([-self.ball_speed, self.ball_speed])
        self.ball_dy = np.random.choice([-self.ball_speed, self.ball_speed])

    def create_blocs(self):
        pos_x = 5
        pos_y = 5
        self.bloc_list = []
        for i in range(0, self.nb_columns*self.nb_rows, 1):
            reste = i // self.nb_columns
            pos_y = 5 + (reste * 21)
            if i % self.nb_columns == 0:
                pos_x = 15
            #print(f"pos_x: {pos_x}/tpos_y: {pos_y}")
            self.bloc_list.append(Bloc(pos_x=pos_x, pos_y=pos_y, life=2))
            pos_x += 64

    def draw_blocs(self):
        for bloc in self.bloc_list:
            bloc.draw_bloc(self.screen)
        
    def update_ball(self):

        if self.ball_y - self.ball_radius <= 0:
            self.ball_dy = -self.ball_dy

        """if self.ball_y - self.ball_radius <= -10: or self.ball_y + self.ball_radius >= self.HEIGHT:
            self.ball_dy = -self.ball_dy"""

        if self.ball_x - self.ball_radius <  0 or self.ball_x + self.ball_radius >= self.WIDTH:
            self.ball_dx = -self.ball_dx

        if (
            self.paddle_player_x <= self.ball_x - self.ball_radius <= self.paddle_player_x + self.paddle_width
            and self.paddle_player_y <= self.ball_y <= self.paddle_player_y + self.paddle_height
        ) :
            self.ball_dy = -self.ball_dy  # Inverser la direction

        self.check_collision_with_blocks()

        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

    def reset(self):
        self.reset_ball()

        self.paddle_player_x = self.WIDTH // 2 
        self.paddle_player_y = self.HEIGHT - 30
        self.create_blocs()
    
    def check_collision_with_blocks(self):
        for bloc in self.bloc_list:
            if (
                self.ball_x + self.ball_radius >= bloc.pos_x and
                self.ball_x - self.ball_radius <= bloc.pos_x + bloc.width and
                self.ball_y + self.ball_radius >= bloc.pos_y and
                self.ball_y - self.ball_radius <= bloc.pos_y + bloc.height
            ):
                bloc.life -= 1
                #print(bloc)
                if bloc.life <= 0:
                    self.bloc_list.remove(bloc)  # Supprime le bloc s'il n'a plus de vie
                
                # Inverser la direction de la balle
                self.ball_dy = -self.ball_dy
                break  # Pour éviter de traiter plusieurs collisions en une frame

    def step(self, action):
        """Exécute une action"""
        reward = 0
        done = False

        if action == 1 and self.paddle_player_x > 0:
                self.paddle_player_x -= self.paddle_speed
        
        elif action == 2 and self.paddle_player_x < self.WIDTH - self.paddle_width:
                self.paddle_player_x += self.paddle_speed

        self.update_ball()

        if self.ball_y >= self.HEIGHT:
            reward -= 2 
            done = True

    def render(self):
        # Efface complètement l'écran avant de dessiner
        self.screen.blit(self.background, (0, 0))

        # Dessiner les éléments dynamiques
        self.screen.blit(self.paddle, (self.paddle_player_x, self.paddle_player_y))
        self.screen.blit(self.ball_img, (self.ball_x - 7, self.ball_y - 7))

        # Dessiner les blocs
        for bloc in self.bloc_list:
            bloc.draw_bloc(self.screen)

        pg.display.flip()  # Met à jour tout l'écran pour éviter les artefacts
        self.clock.tick(60)


    def run(self):
        while True:
            start_time = pg.time.get_ticks()
            self.check_event()
            self.control()
            self.update_ball()
            self.check_life()
            self.update_score()
            self.render()
            print(f"Frame time: {pg.time.get_ticks() - start_time}ms")
    
    def close(self):
        """Ferme la fenêtre."""
        pg.quit()
        sys.exit()

class Bloc:
    def __init__(self, pos_x, pos_y, life=4, spritesheet=None):
        self.width = BLOC_WIDTH
        self.height = BLOC_HEIGHT
        self.life = life
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.spritesheet = spritesheet
        self.load_assets()
    
    def load_assets(self):
        """Charger une seule fois le spritesheet pour toutes les instances"""
        if self.spritesheet is None:
            self.spritesheet = pg.image.load("breakout/BasicBreakOutAssetPack/blocks.png").convert_alpha()
        
        self.bloc_asset_list = {}
        sprite_width = self.spritesheet.get_width() // 8
        sprite_height = self.spritesheet.get_height()
        
        # Découper le spritesheet en sous-surfaces
        for i in range(8):
            rect = pg.Rect(i * sprite_width, 0, sprite_width, sprite_height)
            self.bloc_asset_list[i] = self.spritesheet.subsurface(rect)

    def draw_bloc(self, screen):
        sprite = self.bloc_asset_list.get(self.life, self.bloc_asset_list[0])
        scaled_sprite = pg.transform.scale(sprite, (self.width, self.height))
        rect = scaled_sprite.get_rect(topleft=(self.pos_x, self.pos_y))
        screen.blit(scaled_sprite, rect)
        return rect

    def __repr__(self):
        return f"x: {self.pos_x}\ty: {self.pos_y}\tlife: {self.life}"

if __name__ == '__main__':
    env = BreakOut()
    env.run()