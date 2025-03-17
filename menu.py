import pygame
import pygame_gui
from PIL import Image, ImageSequence

class Menu:
    def __init__(self, WIDTH: int = 800, HEIGHT: int = 600):
        pygame.init()

        # Screen setup
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        
        # Load GIF frames
        self.gif_frames = self.load_gif('assets/background.gif')
        
        # Animation variables
        self.current_frame = 0
        self.frame_delay = 100  # Milliseconds between frame changes
        self.last_update = pygame.time.get_ticks()
        
        # UI Manager
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT), theme_path="theme.json")
        self.add_buttons()
    
    def load_gif(self, filename):
        gif = Image.open(filename)
        frames = []
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert('RGBA')
            pygame_image = pygame.image.fromstring(
                frame.tobytes(), frame.size, frame.mode
            ).convert_alpha()
            pygame_image = pygame.transform.scale(pygame_image, (self.WIDTH, self.HEIGHT))
            frames.append(pygame_image)
        return frames

    def add_buttons(self):
        # Buttons
        self.start_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 250), (200, 50)),
            text='Show Games',
            manager=self.manager
        )
        self.settings_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 320), (200, 50)),
            text="Settings",
            manager=self.manager
        )
        self.quit_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((300, 390), (200, 50)),
            text='Quit',
            manager=self.manager
        )
    
    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.gif_frames)
            self.last_update = current_time
    
    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            time_delta = clock.tick(60) / 1000.0
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.start_button:
                        print("Game Started")
                    elif event.ui_element == self.quit_button:
                        running = False
                
                self.manager.process_events(event)
            
            # Update animation
            self.update_animation()
            
            # Update UI
            self.manager.update(time_delta)
            
            # Draw everything
            self.screen.blit(self.gif_frames[self.current_frame], (0, 0))
            self.manager.draw_ui(self.screen)
            
            pygame.display.update()

        pygame.quit()

if __name__ == '__main__':
    menu = Menu()
    menu.run()
