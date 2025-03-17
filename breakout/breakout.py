import gym
import pygame as pg
import numpy as np
import sys
from gym import spaces

class BreakOut(gym.Env):
    def __init__(self, WIDTH: int = 210, HEIGHT: int = 160):
        super(BreakOut, self).__init__()
        pg.init()
        self.clock = pg.time.Clock()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

        self.ball_radius = 2
        self.paddle_width = 30
        self.paddle_height = 5
        self.paddle_speed = 3

        self.paddle_player_x = WIDTH // 2
        self.paddle_player_y = HEIGHT - 10

        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2 - 10
         
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.score_player = 0

        self.life = 3

        # Définition des actions : 0 = rien, 1 = haut et 2 = bas
        self.action_space = spaces.Discrete(18)
        self.low = np.zeros((self.WIDTH, self.HEIGHT, 3))
        self.high = np.zeros((self.WIDTH, self.HEIGHT, 3))
        self.high.fill(255)
        self.observation_space = spaces.Box(
            low = self.low,
            high = self.high)
        
        self.reset()

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
        self.ball_dx = np.random.choice([-1.5, 1.5])
        self.ball_dy = np.random.choice([-1.5, 1.5])

    def create_blocs(self):
        pos_x = 6
        pos_y = 5
        self.bloc_list = []
        for i in range(0, 54, 1):
            reste = i // 18
            pos_y = 5 + (reste * 7)
            if i % 18 == 0:
                pos_x = 6
            print(f"pos_x: {pos_x}\tpos_y: {pos_y}")
            self.bloc_list.append(Bloc(pos_x=pos_x, pos_y=pos_y, life=2))
            pos_x += 11

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
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2 - 10
        self.ball_dx = np.random.choice([-2, 2])
        self.ball_dy = np.random.choice([-2, 2])

        self.paddle_player_x = self.WIDTH // 2 - 5
        self.paddle_player_y = self.HEIGHT - 10
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
                print(bloc)
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

        self.screen.fill((0, 0, 0))
        #self.screen.blit(self.background, (0, 0))

        pg.draw.circle(self.screen, (255, 255, 255), (self.ball_x, self.ball_y), self.ball_radius)
        pg.draw.rect(self.screen, (255, 255, 255), (self.paddle_player_x, self.paddle_player_y, self.paddle_width, self.paddle_height))
        self.draw_blocs()

        pg.display.flip()
        self.clock.tick(60)

    def run(self):
        while True:
            self.check_event()
            self.control()
            self.update_ball()
            self.check_life()
            self.update_score()
            self.render()
    
    def close(self):
        """Ferme la fenêtre."""
        pg.quit()
        sys.exit()

class Bloc:
    def __init__(self, pos_x, pos_y, life = 4):
        self.width = 10
        self.height = 5
        self.life = life

        self.pos_x = pos_x
        self.pos_y = pos_y
    
    def draw_bloc(self, screen):
        if self.life == 4:
            pg.draw.rect(screen, (255, 0, 0), (self.pos_x, self.pos_y, self.width, self.height))
        elif self.life == 3:
            pg.draw.rect(screen, (0, 0, 255), (self.pos_x, self.pos_y, self.width, self.height))
        elif self.life ==2:
            pg.draw.rect(screen, (0, 255, 255), (self.pos_x, self.pos_y, self.width, self.height))
        elif self.life ==1:
            pg.draw.rect(screen, (255, 255, 255), (self.pos_x, self.pos_y, self.width, self.height))

    def __repr__(self):
        return f"x: {self.pos_x}\ty: {self.pos_y}\tlife: {self.life}"

if __name__ == '__main__':
    env = BreakOut()
    env.run()