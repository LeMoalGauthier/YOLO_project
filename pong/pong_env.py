import gym
import pygame as pg
import numpy as np
import sys
from gym import spaces

class PongEnv(gym.Env):
    def __init__(self, WIDTH: int = 1280, HEIGHT: int = 720, grid=True):
        super(PongEnv, self).__init__()
        pg.init()
        self.clock = pg.time.Clock()
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

        self.ball_radius = 10
        self.paddle_width = 10
        self.paddle_height = 100
        self.paddle_speed = 10  # Vitesse de déplacement des raquettes

        self.grid = grid
        self.screen = pg.display.set_mode((self.WIDTH, self.HEIGHT))
        self.score_player_1 = 0
        self.score_player_2 = 0

        # Définition des actions : 0 = rien, 1 = haut et 2 = bas
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(
            low = np.array([0, 0, -7, -7, 0, 0]),
            high = np.array([self.WIDTH, self.HEIGHT, 7, 7, self.WIDTH, self.HEIGHT], dtype=np.float32),
        )
        self.reset()

    def load_asset(self):
        if self.grid:
            self.background = pg.image.load("pong/Neon Pong Assets/Neon Pong/images/Background  Grid.png")
        else:
            self.background = pg.image.load("pong/Neon Pong Assets/Neon Pong/images/Background Empty.png")

        self.paddle_left_img = pg.image.load("pong/Neon Pong Assets/Neon Pong/images/Paddle_1.png")
        self.paddle_right_img = pg.image.load("pong/Neon Pong Assets/Neon Pong/images/Paddle_2.png")
        self.ball_img = pg.image.load("pong/Neon Pong Assets/Neon Pong/images/Ball.png")

        self.police_asset = pg.font.Font("pong/Neon Pong Assets/Micro5-Regular.ttf", 50)

    def reset(self):
        self.load_asset()
        self.update_score()
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2
        self.ball_dx = np.random.choice([-7, 7])
        self.ball_dy = np.random.choice([-7, 7])

        self.paddle_player_y = self.HEIGHT // 2 - self.paddle_height // 2
        self.paddle_bot_y = self.HEIGHT // 2 - self.paddle_height // 2

        self.paddle_player_x = 50
        self.paddle_bot_x = self.WIDTH - self.paddle_width - 50

        return self._get_obs()

    def _get_obs(self):
        
        obs_elements = [
            self.ball_x / self.WIDTH, 
            self.ball_y / self.HEIGHT, 
            self.ball_dx / 7,
            self.ball_dy / 7,
            self.paddle_player_y / self.HEIGHT,
            self.paddle_bot_y / self.HEIGHT,
            
        ]
        
        return np.array(obs_elements, dtype=np.float32)

    def update_score(self):
        """Met à jour les images de score pour affichage"""
        self.text_score_player_1 = self.police_asset.render(str(self.score_player_1), True, (255, 255, 255))
        self.text_score_player_2 = self.police_asset.render(str(self.score_player_2), True, (255, 255, 255))

        self.textRect_1 = self.text_score_player_1.get_rect(center=(self.WIDTH // 2 - 40, 50))
        self.textRect_2 = self.text_score_player_2.get_rect(center=(self.WIDTH // 2 + 40, 50))

    def step(self, action):
        """Exécute une action"""
        reward = 0
        done = False

        #Mouvement du paddle du RL agent (left)
        if action == 1 and self.paddle_player_y > -10:
                self.paddle_player_y -= self.paddle_speed
        
        elif action == 2 and self.paddle_player_y < self.HEIGHT - self.paddle_height -10:
                self.paddle_player_y += self.paddle_speed

        """elif action == 3 and self.paddle_bot_y > -10:               
                self.paddle_bot_y -= self.paddle_speed
                
        elif action == 4 and self.paddle_bot_y < self.HEIGHT - self.paddle_height:
                self.paddle_bot_y += self.paddle_speed"""

        #Mouvement du paddle du RL agent (right)
        if self.ball_y > self.paddle_bot_y + self.paddle_height //2:
            self.paddle_bot_y += self.paddle_speed

        elif self.ball_y < self.paddle_bot_y + self.paddle_height //2:
            self.paddle_bot_y -= self.paddle_speed

        # Déplacement de la balle
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Rebond sur les bords haut et bas
        if self.ball_y - self.ball_radius <= -10 or self.ball_y + self.ball_radius >= self.HEIGHT - 10:
            self.ball_dy = -self.ball_dy

         # Rebond sur raquette agent
        if (self.paddle_player_x <= self.ball_x - self.ball_radius <= self.paddle_player_x + self.paddle_width 
            and self.paddle_player_y <= self.ball_y <= self.paddle_player_y + self.paddle_height):
                self.ball_dx = -self.ball_dx  # Inverser la direction
                reward +=1
        # Rebond sur raquette bot
        if  (self.paddle_bot_x <= self.ball_x + self.ball_radius <= self.paddle_bot_x + self.paddle_width
            and self.paddle_bot_y <= self.ball_y <= self.paddle_bot_y + self.paddle_height):
            self.ball_dx = -self.ball_dx  # Inverser la direction

        if self.ball_x <= 0:
            reward -= 2
            done = True

        if self.ball_x >= self.WIDTH:
            reward += 2
            done = True
            
        #reward -= 0.01
        return self._get_obs(), reward, done, {}
        

    def control(self):
        """Détecte les touches pressées pour bouger la raquette."""
        keys = pg.key.get_pressed()
        if keys[pg.K_s] or keys[pg.K_DOWN]:
            if self.paddle_player_y < self.HEIGHT - self.paddle_height:
                self.paddle_player_y += self.paddle_speed
        if keys[pg.K_z] or keys[pg.K_UP]:
            if self.paddle_player_x > 0:
                self.paddle_player_y -= self.paddle_speed

    def check_event(self):
        """Vérifie les événements Pygame."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.close()

    def bot_movement(self):
        """Déplace l'IA en fonction de la position de la balle."""
        if self.ball_y > self.paddle_bot_y + self.paddle_height // 2:
            if self.paddle_bot_y < self.HEIGHT - self.paddle_height:
                self.paddle_bot_y += self.paddle_speed
        elif self.ball_y < self.paddle_bot_y + self.paddle_height // 2:
            if self.paddle_bot_y > 0:
                self.paddle_bot_y -= self.paddle_speed

    def update_ball(self):
        """Met à jour la position de la balle et gère les rebonds."""
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Rebond sur les bords haut et bas
        if self.ball_y - self.ball_radius <= -10 or self.ball_y + self.ball_radius >= self.HEIGHT - 10:
            self.ball_dy = -self.ball_dy

        # Rebond sur les raquettes
        if (
            self.paddle_player_x <= self.ball_x - self.ball_radius <= self.paddle_player_x + self.paddle_width
            and self.paddle_player_y <= self.ball_y <= self.paddle_player_y + self.paddle_height
        ) or (
            self.paddle_bot_x <= self.ball_x + self.ball_radius <= self.paddle_bot_x + self.paddle_width
            and self.paddle_bot_y <= self.ball_y <= self.paddle_bot_y + self.paddle_height
        ):
            self.ball_dx = -self.ball_dx  # Inverser la direction

        if self.ball_x <= 0:
            self.score_player_2 +=1
            self.update_score()
            self.reset()
            

        if self.ball_x >= self.WIDTH:
            self.score_player_1 += 1
            self.update_score()
            self.reset()

        
    def render(self):
        """Affiche le jeu avec Pygame."""
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.background, (0, 0))

        self.screen.blit(self.paddle_left_img, (self.paddle_player_x -10, self.paddle_player_y - 12, self.paddle_width, self.paddle_height))
        self.screen.blit(self.paddle_right_img, (self.paddle_bot_x - 10, self.paddle_bot_y - 12, self.paddle_width, self.paddle_height))

        self.screen.blit(self.ball_img, (self.ball_x - 15, self.ball_y - 15))
        
        #pg.draw.circle(self.screen, (255, 255, 255), (self.ball_x, self.ball_y), self.ball_radius)
        #pg.draw.rect(self.screen, (255, 255, 255), (self.paddle_player_x, self.paddle_player_y, self.paddle_width, self.paddle_height))
        #pg.draw.rect(self.screen, (255, 255, 255), (self.paddle_bot_x, self.paddle_bot_y, self.paddle_width, self.paddle_height))

        #Score
        self.screen.blit(self.text_score_player_1, self.textRect_1)
        self.screen.blit(self.text_score_player_2, self.textRect_2)

        pg.display.flip()
        self.clock.tick(60)

    def run(self):
        """Boucle principale du jeu."""
        while True:
            self.check_event()
            self.control()
            self.update_ball()
            self.bot_movement()
            self.render()


    def close(self):
        """Ferme la fenêtre."""
        pg.quit()
        sys.exit()

if __name__ == '__main__':
    pong = PongEnv(grid=False)
    pong.run()
