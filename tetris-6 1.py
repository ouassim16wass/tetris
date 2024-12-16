import pygame
import random
from dataclasses import dataclass
from typing import List, Tuple

# Pygame Initialization
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Game Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE + 300
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE

# Chargement des sons
SOUNDS = {
    'clear': pygame.mixer.Sound('sounds/clear.wav'),
    'drop': pygame.mixer.Sound('sounds/drop.wav'),
    'lateral_move': pygame.mixer.Sound('sounds/lateralmove.wav'),
    'level_up': pygame.mixer.Sound('sounds/levelup.wav'),
    'rotate': pygame.mixer.Sound('sounds/rotate.wav'),
    'select': pygame.mixer.Sound('sounds/select.wav'),
    'start': pygame.mixer.Sound('sounds/start.wav'),
    'tetris': pygame.mixer.Sound('sounds/tetris.wav'),
    'game_over': pygame.mixer.Sound('sounds/gameover.wav')
}

# Musique de fond
# pygame.mixer.music.load('sounds/tetrismusic.wav')
pygame.mixer.music.load('sounds/background_music.mp3') 
pygame.mixer.music.set_volume(0.5)  # Réglez le volume (0.0 à 1.0)
pygame.mixer.music.play(-1)  # -1 pour jouer en boucle infinie

# Colors
COLORS = {
    'background': (20, 20, 20),
    'grid_lines': (50, 50, 50),
    'text': (255, 255, 255),
    'button_normal': (70, 70, 70),
    'button_hover': (100, 100, 100),
    'button_difficulty': {
        'easy': (50, 200, 50),
        'medium': (255, 165, 0),
        'hard': (255, 0, 0)
    },
    'pieces': {
        'I': (0, 255, 255),   # Cyan
        'O': (255, 255, 0),   # Yellow
        'T': (128, 0, 128),   # Purple
        'S': (0, 255, 0),     # Green
        'Z': (255, 0, 0),     # Red
        'J': (0, 0, 255),     # Blue
        'L': (255, 165, 0)    # Orange
    }
}

# Piece Shapes
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

# Difficulty Levels
# DIFFICULTIES = {
#     'easy': {'fall_speed': 0.7, 'speed_increase': 0.3},
#     'medium': {'fall_speed': 0.4, 'speed_increase': 0.25},
#     'hard': {'fall_speed': 0.1, 'speed_increase': 0.35}
# }

DIFFICULTIES = {
    'easy': {'fall_speed': 0.7, 'speed_increase': 0.3},
    'medium': {'fall_speed': 0.4, 'speed_increase': 0.35},
    'hard': {'fall_speed': 0.1, 'speed_increase': 0.45}
}

@dataclass
class Piece:
    shape: List[List[int]]
    x: int
    y: int
    type: str

class Button:
    def __init__(self, x, y, width, height, text, color=None, font_size=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.color = color or COLORS['button_normal']

    def draw(self, screen):
        color = (min(255, self.color[0] + 30), 
                 min(255, self.color[1] + 30), 
                 min(255, self.color[2] + 30)) if self.hovered else self.color
        
        pygame.draw.rect(screen, color, self.rect)
        text_surface = self.font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_hovered(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

class DifficultySelect:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris - Select Difficulty')
        
        button_width, button_height = 200, 60
        button_x = (SCREEN_WIDTH - button_width) // 2
        self.buttons = {
            'easy': Button(button_x, 200, button_width, button_height, 
                           'Easy', COLORS['button_difficulty']['easy']),
            'medium': Button(button_x, 300, button_width, button_height, 
                             'Medium', COLORS['button_difficulty']['medium']),
            'hard': Button(button_x, 400, button_width, button_height, 
                           'Hard', COLORS['button_difficulty']['hard'])
        }

    def run(self):
        running = True
        while running:
            self.screen.fill(COLORS['background'])
            
            # Title and Subtitle
            font_title = pygame.font.Font(None, 72)
            font_subtitle = pygame.font.Font(None, 36)
            
            title = font_title.render('Tetris', True, COLORS['text'])
            subtitle = font_subtitle.render('Select Difficulty', True, COLORS['text'])
            
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 150))
            
            self.screen.blit(title, title_rect)
            self.screen.blit(subtitle, subtitle_rect)
            
            # Draw Difficulty Buttons
            for button in self.buttons.values():
                button.draw(self.screen)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return None
                
                if event.type == pygame.MOUSEMOTION:
                    for button in self.buttons.values():
                        button.is_hovered(event.pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for name, button in self.buttons.items():
                        if button.is_hovered(event.pos):
                            return name
        
        return None

class TetrisUI:
    def __init__(self, game):
        self.game = game
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        
        # Game Control Buttons
        button_width = 200
        button_x = GRID_WIDTH * BLOCK_SIZE + 50
        self.buttons = {
            'pause': Button(button_x, 400, button_width, 50, 'Pause'),
            'restart': Button(button_x, 460, button_width, 50, 'Restart'),
            'quit': Button(button_x, 520, button_width, 50, 'Quit')
        }

    def draw(self):
        self.screen.fill(COLORS['background'])
        
        # Draw Game Grid
        self._draw_grid()
        self._draw_current_piece()
        self._draw_next_piece()
        self._draw_stats()
        
        # Draw Control Buttons
        for button in self.buttons.values():
            button.draw(self.screen)
        
        # Draw Game State Messages
        self._draw_game_messages()
        
        pygame.display.flip()

    def _draw_grid(self):
        # Grid background and lines
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                if self.game.grid[i][j]:
                    pygame.draw.rect(self.screen, 
                                     COLORS['pieces'][self.game.grid[i][j]],
                                     (j * BLOCK_SIZE, 
                                      i * BLOCK_SIZE, 
                                      BLOCK_SIZE - 1, 
                                      BLOCK_SIZE - 1))
        
        for x in range(0, GRID_WIDTH * BLOCK_SIZE, BLOCK_SIZE):
            pygame.draw.line(self.screen, COLORS['grid_lines'], 
                             (x, 0), (x, GRID_HEIGHT * BLOCK_SIZE))
        for y in range(0, GRID_HEIGHT * BLOCK_SIZE, BLOCK_SIZE):
            pygame.draw.line(self.screen, COLORS['grid_lines'], 
                             (0, y), (GRID_WIDTH * BLOCK_SIZE, y))

    def _draw_current_piece(self):
        if not self.game.paused and not self.game.game_over:
            for i, row in enumerate(self.game.current_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen,
                                       COLORS['pieces'][self.game.current_piece.type],
                                       ((self.game.current_piece.x + j) * BLOCK_SIZE,
                                        (self.game.current_piece.y + i) * BLOCK_SIZE,
                                        BLOCK_SIZE - 1,
                                        BLOCK_SIZE - 1))

    def _draw_next_piece(self):
        font = pygame.font.Font(None, 36)
        next_text = font.render('Next:', True, COLORS['text'])
        self.screen.blit(next_text, (GRID_WIDTH * BLOCK_SIZE + 50, 50))
        
        if not self.game.paused:
            for i, row in enumerate(self.game.next_piece.shape):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen,
                                       COLORS['pieces'][self.game.next_piece.type],
                                       (GRID_WIDTH * BLOCK_SIZE + 70 + j * BLOCK_SIZE,
                                        100 + i * BLOCK_SIZE,
                                        BLOCK_SIZE - 1,
                                        BLOCK_SIZE - 1))

    def _draw_stats(self):
        font = pygame.font.Font(None, 36)
        
        stats = [
            f'Score: {self.game.score}',
            f'Level: {self.game.level}',
            f'Lines: {self.game.lines}'
        ]
        
        for i, stat in enumerate(stats):
            stat_text = font.render(stat, True, COLORS['text'])
            self.screen.blit(stat_text, (GRID_WIDTH * BLOCK_SIZE + 50, 250 + i * 50))

    def _draw_game_messages(self):
        font = pygame.font.Font(None, 48)
        
        if self.game.paused:
            pause_text = font.render('PAUSE', True, COLORS['text'])
            text_rect = pause_text.get_rect(
                center=(GRID_WIDTH * BLOCK_SIZE // 2, 
                        GRID_HEIGHT * BLOCK_SIZE // 2)
            )
            self.screen.blit(pause_text, text_rect)
        
        if self.game.game_over:
            game_over_text = font.render('GAME OVER', True, COLORS['text'])
            text_rect = game_over_text.get_rect(
                center=(GRID_WIDTH * BLOCK_SIZE // 2, 
                        GRID_HEIGHT * BLOCK_SIZE // 2)
            )
            self.screen.blit(game_over_text, text_rect)

        if not self.game.game_over and not self.game.paused:
            # font = pygame.font.Font(None, 48)
            level_text = font.render(f'Level {self.game.level}', True, COLORS['text'])
            text_rect = level_text.get_rect(center=(GRID_WIDTH * BLOCK_SIZE // 2, 50))
            self.screen.blit(level_text, text_rect)

class Tetris:
    def __init__(self, difficulty='medium'):
        self.clock = pygame.time.Clock()
        self.difficulty = difficulty
        self.reset_game()
        self.ui = TetrisUI(self)

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.paused = False
        
        self.fall_speed = DIFFICULTIES[self.difficulty]['fall_speed']

    def new_piece(self) -> Piece:
        piece_type = random.choice(list(SHAPES.keys()))
        shape = SHAPES[piece_type]
        return Piece(
            shape=shape,
            x=GRID_WIDTH // 2 - len(shape[0]) // 2,
            y=0,
            type=piece_type
        )

    def rotate_piece(self):
        shape = self.current_piece.shape
        rotated = list(zip(*shape[::-1]))
        if self.is_valid_move(rotated, self.current_piece.x, self.current_piece.y):
            self.current_piece.shape = [list(row) for row in rotated]

    def is_valid_move(self, shape, x, y):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if (y + i >= GRID_HEIGHT or 
                        x + j < 0 or 
                        x + j >= GRID_WIDTH or 
                        (y + i >= 0 and self.grid[y + i][x + j])):
                        return False
        return True

    def place_piece(self):
        for i, row in enumerate(self.current_piece.shape):
            for j, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + i][self.current_piece.x + j] = \
                        self.current_piece.type
        
        self.clear_lines()
        self.current_piece = self.next_piece
        self.next_piece = self.new_piece()
        
        if not self.is_valid_move(self.current_piece.shape, 
                                  self.current_piece.x, 
                                  self.current_piece.y):
            self.game_over = True

    # def clear_lines(self):
    #     lines_cleared = 0
    #     for i in range(GRID_HEIGHT):
    #         if all(self.grid[i]):
    #             del self.grid[i]
    #             self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
    #             lines_cleared += 1
        
    #     if lines_cleared:
    #         self.lines += lines_cleared
    #         self.score += lines_cleared * 100 * self.level
            
    #         # Level progression and speed increase
    #         new_level = self.lines // 10 + 1
    #         if new_level > self.level:
    #             self.level = new_level
    #             speed_increase = DIFFICULTIES[self.difficulty]['speed_increase']
    #             self.fall_speed = max(0.1, self.fall_speed - speed_increase)

    def clear_lines(self):
        lines_cleared = 0
        for i in range(GRID_HEIGHT):
            if all(self.grid[i]):
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(GRID_WIDTH)])
                lines_cleared += 1
        
        if lines_cleared:
            self.lines += lines_cleared
            self.score += lines_cleared * 100 * self.level
            
            # Augmenter le niveau et réduire `fall_speed`
            new_level = self.lines // 1 + 1  # Nouveau niveau après chaque 1 lignes
            if new_level > self.level:
                self.level = new_level
                speed_increase = DIFFICULTIES[self.difficulty]['speed_increase']
                self.fall_speed = max(0.1, self.fall_speed - speed_increase)
                SOUNDS['level_up'].play()  # Jouer le son de progression de niveau

    def run(self):
        fall_time = 0
        
        while True:
            self.clock.tick(60)
            if not self.paused:
                fall_time += self.clock.get_rawtime()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.MOUSEMOTION:
                    for button in self.ui.buttons.values():
                        button.is_hovered(event.pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for name, button in self.ui.buttons.items():
                        if button.is_hovered(event.pos):
                            if name == 'pause':
                                self.paused = not self.paused
                            elif name == 'restart':
                                self.reset_game()
                            elif name == 'quit':
                                pygame.quit()
                                return    
                if event.type == pygame.KEYDOWN:
                    # Contrôles du jeu uniquement si pas en pause et pas game over
                    if not self.paused and not self.game_over:
                        if event.key == pygame.K_LEFT:
                            if self.is_valid_move(self.current_piece.shape,
                                               self.current_piece.x - 1,
                                               self.current_piece.y):
                                self.current_piece.x -= 1
                                SOUNDS['lateral_move'].play()
                        elif event.key == pygame.K_RIGHT:
                            if self.is_valid_move(self.current_piece.shape,
                                               self.current_piece.x + 1,
                                               self.current_piece.y):
                                self.current_piece.x += 1
                                SOUNDS['lateral_move'].play()
                        elif event.key == pygame.K_DOWN:
                            if self.is_valid_move(self.current_piece.shape,
                                               self.current_piece.x,
                                               self.current_piece.y + 1):
                                self.current_piece.y += 1
                                SOUNDS['drop'].play()
                        elif event.key == pygame.K_UP:
                            self.rotate_piece()
                            SOUNDS['rotate'].play()
                        elif event.key == pygame.K_SPACE:
                            while self.is_valid_move(self.current_piece.shape,
                                                  self.current_piece.x,
                                                  self.current_piece.y + 1):
                                self.current_piece.y += 1
                            self.place_piece()
                            SOUNDS['drop'].play()
            
            # Chute automatique si pas en pause et pas game over
            if fall_time >= self.fall_speed * 1000 and not self.paused and not self.game_over:
                fall_time = 0
                if self.is_valid_move(self.current_piece.shape,
                                   self.current_piece.x,
                                   self.current_piece.y + 1):
                    self.current_piece.y += 1
                else:
                    self.place_piece()
            
            # Dessiner l'interface
            self.ui.draw()
            
            # Game over
            if self.game_over:
                SOUNDS['game_over'].play()
                break
        
        # Écran de Game Over avec option de redémarrage
        self.game_over_screen()

    def game_over_screen(self):
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Game Over')
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        
        # Boutons
        restart_button = Button(
            (SCREEN_WIDTH - 300) // 2, 400, 300, 60, 
            'Restart', COLORS['button_difficulty']['medium']
        )
        quit_button = Button(
            (SCREEN_WIDTH - 300) // 2, 480, 300, 60, 
            'Quit', COLORS['button_difficulty']['hard']
        )
        
        running = True
        while running:
            screen.fill(COLORS['background'])
            
            # Game Over
            game_over_text = font_large.render('Game Over', True, COLORS['text'])
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
            screen.blit(game_over_text, game_over_rect)
            
            # Score final
            score_text = font_medium.render(f'Score: {self.score}', True, COLORS['text'])
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            screen.blit(score_text, score_rect)
            
            # Dessiner les boutons
            restart_button.draw(screen)
            quit_button.draw(screen)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.MOUSEMOTION:
                    restart_button.is_hovered(event.pos)
                    quit_button.is_hovered(event.pos)
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_button.is_hovered(event.pos):
                        SOUNDS['start'].play()
                        return main()
                    if quit_button.is_hovered(event.pos):
                        pygame.quit()
                        return

def main():
    # Écran de sélection de difficulté
    difficulty_select = DifficultySelect()
    difficulty = difficulty_select.run()
    
    if difficulty:
        SOUNDS['start'].play()
        game = Tetris(difficulty)
        game.run()
    
    pygame.quit()

if __name__ == '__main__':
    main()