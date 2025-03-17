import gym
import numpy as np
import pygame
from gym import spaces

class PongEnv(gym.Env):
    """Environnement de Pong pour RL compatible avec OpenAI Gym"""
    
    def __init__(self):
        super(PongEnv, self).__init__()
        self.clock = pygame.time.Clock()

        # Dimensions du jeu
        self.WIDTH = 640
        self.HEIGHT = 480
        self.BALL_RADIUS = 10
        self.PADDLE_WIDTH = 10
        self.PADDLE_HEIGHT = 60
        

        # Définition des actions : 0 = rien, 1 = haut, 2 = bas
        self.action_space = spaces.Discrete(3)

        # Observation (états) : position et vitesse de la balle + position des paddles
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -5, -5, 0, 0]),
            high=np.array([self.WIDTH, self.HEIGHT, 5, 5, self.HEIGHT, self.HEIGHT]),
            dtype=np.float32
        )

        self.reset()

    def reset(self):
        """Réinitialisation de l'environnement"""
        self.ball_x = self.WIDTH // 2
        self.ball_y = self.HEIGHT // 2
        self.ball_dx = np.random.choice([-4, 4])
        self.ball_dy = np.random.choice([-3, 3])

        self.paddle_left_y = self.HEIGHT // 2 - self.PADDLE_HEIGHT // 2
        self.paddle_right_y = self.HEIGHT // 2 - self.PADDLE_HEIGHT // 2

        return self._get_obs()

    def step(self, action):
        """Exécute une action et met à jour l'environnement"""
        reward = 0
        done = False

        # Mouvement du paddle du RL agent (gauche)
        if action == 1 and self.paddle_left_y > 0:
            self.paddle_left_y -= 5
        elif action == 2 and self.paddle_left_y < self.HEIGHT - self.PADDLE_HEIGHT:
            self.paddle_left_y += 5

        # Mouvement du paddle de l’adversaire (simple AI)
        if self.ball_y > self.paddle_right_y + self.PADDLE_HEIGHT // 2:
            self.paddle_right_y += 4
        elif self.ball_y < self.paddle_right_y + self.PADDLE_HEIGHT // 2:
            self.paddle_right_y -= 4

        # Déplacement de la balle
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy

        # Collision avec le mur
        if self.ball_y <= 0 or self.ball_y >= self.HEIGHT:
            self.ball_dy = -self.ball_dy

        # Collision avec le paddle gauche
        if (
            self.ball_x <= self.PADDLE_WIDTH and
            self.paddle_left_y <= self.ball_y <= self.paddle_left_y + self.PADDLE_HEIGHT
        ):
            self.ball_dx = -self.ball_dx
            reward += 1  # Récompense pour avoir renvoyé la balle

        # Collision avec le paddle droit (adversaire)
        if (
            self.ball_x >= self.WIDTH - self.PADDLE_WIDTH and
            self.paddle_right_y <= self.ball_y <= self.paddle_right_y + self.PADDLE_HEIGHT
        ):
            self.ball_dx = -self.ball_dx

        # Si la balle sort du côté gauche (perte)
        if self.ball_x <= 0:
            reward -= 10
            done = True

        # Si la balle sort du côté droit (victoire)
        if self.ball_x >= self.WIDTH:
            reward += 10
            done = True

        return self._get_obs(), reward, done, {}

    def _get_obs(self):
        """Retourne l'état actuel sous forme de vecteur"""
        return np.array([self.ball_x, self.ball_y, self.ball_dx, self.ball_dy, self.paddle_left_y, self.paddle_right_y], dtype=np.float32)

    def render(self, mode="human"):
        """Affichage avec Pygame (avec limitation à 100 FPS)"""
        if not hasattr(self, "screen"):
            pygame.init()
            self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))

        self.screen.fill((0, 0, 0))

        # Dessin des paddles et de la balle
        pygame.draw.rect(self.screen, (255, 255, 255), (0, self.paddle_left_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT))
        pygame.draw.rect(self.screen, (255, 255, 255), (self.WIDTH - self.PADDLE_WIDTH, self.paddle_right_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT))
        pygame.draw.circle(self.screen, (255, 255, 255), (self.ball_x, self.ball_y), self.BALL_RADIUS)

        pygame.display.flip()
        self.clock.tick(100)


    def close(self):
        """Ferme la fenêtre"""
        pygame.quit()
