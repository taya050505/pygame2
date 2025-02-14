import pygame
import sys


class Button:
    def __init__(self, text, x, y, width, height, inactive_color, active_color, action=None):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.action = action

    def draw(self, surface, font):
        mouse_pos = pygame.mouse.get_pos()
        if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
            pygame.draw.rect(surface, self.active_color, (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(surface, self.inactive_color, (self.x, self.y, self.width, self.height))

        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        text_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.x < mouse_pos[0] < self.x + self.width and self.y < mouse_pos[1] < self.y + self.height:
                if self.action:
                    self.action()
                return True  # Возвращаем True, если кнопка была нажата
        return False


def draw_text(surface, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_surface, text_rect)


def show_start_screen(window):
    SCREEN_WIDTH, SCREEN_HEIGHT = window.get_size()
    clock = pygame.time.Clock()

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (147, 112, 216)
    PURPLE = (75, 0, 130)

    button_font = pygame.font.Font(None, 74)
    title_font = pygame.font.Font(None, 96)

    play_button = Button("Играть", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50, 400, 100, PURPLE, GRAY)
    quit_button = Button("Выйти", SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 100, 400, 100, PURPLE, GRAY,
                         lambda: pygame.quit())

    in_menu = True
    while in_menu:
        window.fill(BLACK)

        draw_text(window, "Лабиринт вечной ночи", title_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)

        play_button.draw(window, button_font)
        quit_button.draw(window, button_font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if quit_button.is_clicked(event):
                    pygame.quit()
                    sys.exit()
                if play_button.is_clicked(event):
                    return True  # Игрок выбрал "Играть"

        pygame.display.flip()
        clock.tick(30)
