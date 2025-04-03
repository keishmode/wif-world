import pygame
import random
import sys
import os
import time
import asyncio  # Add asyncio import

# Initialize Pygame
pygame.init()

# Set up the display with specific flags for macOS
os.environ['SDL_VIDEODRIVER'] = 'cocoa'  # For macOS
screen = pygame.display.set_mode((600, 600), pygame.SHOWN)
pygame.display.set_caption('Snake Game')

# Constants
WINDOW_SIZE = 600
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE
GAME_DURATION = 120  # 2 minutes in seconds
SCORE_INCREMENT = 100  # Amount to increase score by

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.color = GREEN
        self.score = 0
        # Load and scale the image with transparency
        try:
            # Load image and ensure it's in RGBA format
            original = pygame.image.load('dog_hat.png').convert_alpha()
            # Scale while preserving alpha
            self.head_image = pygame.transform.smoothscale(original, (GRID_SIZE - 1, GRID_SIZE - 1))
            # Use same size for body
            self.body_image = self.head_image.copy()
        except Exception as e:
            print(f"Could not load dog_hat.png, falling back to green square: {e}")
            self.head_image = None
            self.body_image = None

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_COUNT, (cur[1] + y) % GRID_COUNT)
        if new in self.positions[3:]:
            return False
        self.positions.insert(0, new)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True

    def reset(self):
        self.length = 1
        self.positions = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
        self.score = 0

    def render(self, surface):
        for i, p in enumerate(self.positions):
            if i == 0:  # This is the head
                if self.head_image:
                    angle = 0
                    if self.direction == UP:
                        angle = 90
                    elif self.direction == DOWN:
                        angle = -90
                    elif self.direction == LEFT:
                        angle = 180
                    
                    rotated_head = pygame.transform.rotate(self.head_image, angle)
                    rect = rotated_head.get_rect(center=(p[0] * GRID_SIZE + GRID_SIZE/2,
                                                       p[1] * GRID_SIZE + GRID_SIZE/2))
                    surface.blit(rotated_head, rect)
                else:
                    pygame.draw.rect(surface, self.color,
                                   (p[0] * GRID_SIZE, p[1] * GRID_SIZE,
                                    GRID_SIZE - 1, GRID_SIZE - 1))
            else:  # This is the body
                if self.body_image:
                    rect = self.body_image.get_rect(center=(p[0] * GRID_SIZE + GRID_SIZE/2,
                                                          p[1] * GRID_SIZE + GRID_SIZE/2))
                    surface.blit(self.body_image, rect)
                else:
                    pygame.draw.rect(surface, self.color,
                                   (p[0] * GRID_SIZE, p[1] * GRID_SIZE,
                                    GRID_SIZE - 1, GRID_SIZE - 1))

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
        # Load and scale the image with transparency
        try:
            # Load image and ensure it's in RGBA format
            original = pygame.image.load('pink_hat.png').convert_alpha()
            # Scale while preserving alpha
            self.image = pygame.transform.smoothscale(original, (GRID_SIZE - 1, GRID_SIZE - 1))
        except Exception as e:
            print(f"Could not load pink_hat.png, falling back to red square: {e}")
            self.image = None

    def randomize_position(self):
        self.position = (random.randint(0, GRID_COUNT - 1),
                        random.randint(0, GRID_COUNT - 1))

    def render(self, surface):
        if self.image:
            rect = self.image.get_rect(center=(self.position[0] * GRID_SIZE + GRID_SIZE/2,
                                             self.position[1] * GRID_SIZE + GRID_SIZE/2))
            surface.blit(self.image, rect)
        else:
            pygame.draw.rect(surface, self.color,
                           (self.position[0] * GRID_SIZE,
                            self.position[1] * GRID_SIZE,
                            GRID_SIZE - 1, GRID_SIZE - 1))

# Directional constants
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def format_time(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"

def get_player_name():
    # Initialize font
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(WINDOW_SIZE//4, WINDOW_SIZE//2 - 20, WINDOW_SIZE//2, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = True
    text = ''
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN and text.strip():
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        # Only add character if it's a letter or space
                        if event.unicode.isalpha() or event.unicode.isspace():
                            if len(text) < 20:  # Limit name length
                                text += event.unicode

        # Render the current state
        screen.fill(BLACK)
        
        # Draw prompt text
        prompt_text = font.render('Enter your name:', True, WHITE)
        prompt_rect = prompt_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 - 50))
        screen.blit(prompt_text, prompt_rect)
        
        # Draw the input box
        pygame.draw.rect(screen, color, input_box, 2)
        
        # Render the input text
        txt_surface = font.render(text, True, WHITE)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        
        # Draw instruction text
        instruction_text = font.render('Press ENTER when done', True, YELLOW)
        instruction_rect = instruction_text.get_rect(center=(WINDOW_SIZE//2, WINDOW_SIZE//2 + 50))
        screen.blit(instruction_text, instruction_rect)
        
        pygame.display.flip()
        
    return text.strip() or 'Player'  # Return 'Player' if empty name

async def main():
    # Get player name before starting the game
    player_name = get_player_name()
    
    snake = Snake()
    food = Food()
    font = pygame.font.Font(None, 36)
    start_time = time.time()
    game_over = False

    while True:
        current_time = time.time()
        elapsed_time = int(current_time - start_time)
        remaining_time = max(0, GAME_DURATION - elapsed_time)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != DOWN:
                    snake.direction = UP
                elif event.key == pygame.K_DOWN and snake.direction != UP:
                    snake.direction = DOWN
                elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                    snake.direction = LEFT
                elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                    snake.direction = RIGHT
                elif event.key == pygame.K_r and game_over:  # Restart game
                    snake.reset()
                    food.randomize_position()
                    start_time = time.time()
                    game_over = False

        if not game_over:
            # Update snake
            if not snake.update():
                game_over = True

            # Check if snake ate the food
            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += SCORE_INCREMENT
                food.randomize_position()

            # Check if time is up
            if remaining_time <= 0:
                game_over = True

        # Draw everything
        screen.fill(BLACK)
        snake.render(screen)
        food.render(screen)
        
        # Display score and time
        score_text = font.render(f'Score: ${snake.score}', True, WHITE)
        time_text = font.render(f'Time: {format_time(remaining_time)}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (10, 50))
        
        # Display player name in bottom right
        name_text = font.render(player_name, True, WHITE)
        name_rect = name_text.get_rect()
        screen.blit(name_text, (WINDOW_SIZE - name_rect.width - 10, WINDOW_SIZE - name_rect.height - 10))

        # Display game over message
        if game_over:
            game_over_text = font.render('GAME OVER! Press R to restart', True, YELLOW)
            text_rect = game_over_text.get_rect(center=(WINDOW_SIZE/2, WINDOW_SIZE/2))
            screen.blit(game_over_text, text_rect)

        pygame.display.update()
        clock.tick(10)  # Control game speed
        
        # Required for web deployment
        await asyncio.sleep(0)

if __name__ == '__main__':
    asyncio.run(main()) 