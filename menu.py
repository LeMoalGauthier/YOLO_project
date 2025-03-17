import pygame
import pygame_gui

class Menu:
    def __init__(self, WIDTH:int=800, HEIGHT:int=600):

        pygame.init()

        # Screen setup
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.manager = pygame_gui.UIManager((self.WIDTH, self.HEIGHT))
        
    def add_buttons(self):

        # Buttons
        self.start_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 250), (200, 50)),
                                                    text='Show Games',
                                                    manager=self.manager)
        self.settings_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 320), (200, 50)),
                                                text="Settings",
                                                manager=self.manager)
        self.quit_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 390), (200, 50)),
                                                text='Quit',
                                                manager=self.manager)
        
    
    def back_ground_animation(self):
        pass
        
    
    def run(self):
        self.add_buttons()
        clock = pygame.time.Clock()
        running = True

        while running:
            time_delta = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == self.start_button:
                        print("Game Started")
                    if event.ui_element == self.quit_button:
                        running = False

                self.manager.process_events(event)

            self.screen.fill((0, 0, 0))
            self.manager.update(time_delta)
            self.manager.draw_ui(self.screen)

            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    menu = Menu()
    menu.run()