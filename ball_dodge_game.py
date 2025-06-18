import pygame
import sys
import random
import time
import math

# Game initialization
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ball Dodge Game")

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Player settings
player_radius = 15
player_pos = [WIDTH // 2, HEIGHT // 2]

# Ball class
class Ball:
    def __init__(self, x, difficulty, is_homing=False, player_pos=None):
        self.x = x
        self.y = 0
        self.is_homing = is_homing
        self.player_pos = player_pos
        
        # Adjust ball size probabilities based on difficulty
        size_chances = [0.7 - difficulty * 0.3, 0.2, 0.1 + difficulty * 0.3]  # [small, medium, large]
        size_choice = random.choices([0, 1, 2], weights=size_chances)[0]
        
        if size_choice == 0:  # Small ball
            self.radius = random.randint(10, 20)
            self.speed = random.randint(3, 5)
            self.color = BLUE  # Small balls are blue
        elif size_choice == 1:  # Medium ball
            self.radius = random.randint(21, 35)
            self.speed = random.randint(2, 4)
            self.color = GREEN  # Medium balls are green
        else:  # Large ball
            self.radius = random.randint(36, 50)
            self.speed = random.randint(1, 3)
            self.color = RED  # Large balls are red
        
        # Homing balls are purple
        if self.is_homing:
            self.color = PURPLE
            self.speed = 1  # Homing balls are slower

    def update(self):
        if self.is_homing and self.player_pos:
            # Calculate direction towards player
            dx = self.player_pos[0] - self.x
            dy = self.player_pos[1] - self.y
            distance = max(1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero
            
            # Normalize and apply speed
            self.x += (dx / distance) * self.speed
            self.y += self.speed
        else:
            # Normal vertical movement
            self.y += self.speed
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Start screen
def start_screen():
    font_large = pygame.font.SysFont(None, 64)
    font_medium = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 36)
    
    title_text = font_large.render("BALL DODGE", True, WHITE)
    normal_text = font_medium.render("1: Normal Mode", True, GREEN)
    hard_text = font_medium.render("2: Hard Mode", True, RED)
    instruction_text = font_small.render("Move mouse to avoid balls", True, WHITE)
    
    difficulty = None
    
    while difficulty is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = "normal"
                elif event.key == pygame.K_2:
                    difficulty = "hard"
        
        screen.fill(BLACK)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
        screen.blit(normal_text, (WIDTH // 2 - normal_text.get_width() // 2, HEIGHT // 2))
        screen.blit(hard_text, (WIDTH // 2 - hard_text.get_width() // 2, HEIGHT // 2 + 60))
        screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT * 3 // 4))
        
        pygame.display.update()
    
    return difficulty

# Game loop
def game(difficulty_level):
    # Game variables
    balls = []
    score = 0
    start_time = time.time()
    last_score_update = start_time
    ball_spawn_timer = 0
    homing_ball_timer = 0
    game_over = False
    clock = pygame.time.Clock()
    
    # Set difficulty parameters
    if difficulty_level == "normal":
        difficulty_multiplier = 1.0
        homing_ball_threshold = 0.5  # When to start spawning homing balls
        max_difficulty = 0.9
        difficulty_time = 60  # Seconds to reach max difficulty
    else:  # Hard mode
        difficulty_multiplier = 1.5
        homing_ball_threshold = 0.3  # Earlier homing balls
        max_difficulty = 1.0
        difficulty_time = 45  # Reach max difficulty faster
    
    # Font settings
    font = pygame.font.SysFont(None, 36)
    
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        difficulty = min(max_difficulty, elapsed_time / difficulty_time) * difficulty_multiplier
        
        # Score update (10 points per second)
        if current_time - last_score_update >= 1 and not game_over:
            score += 10
            last_score_update = current_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    return  # Return to start screen
        
        # Get mouse position
        if not game_over:
            player_pos[0], player_pos[1] = pygame.mouse.get_pos()
        
        # New ball generation (adjust frequency based on difficulty)
        ball_spawn_timer += 1
        spawn_rate = max(30 - int(difficulty * 20), 10)  # Higher difficulty = faster spawn rate
        
        if ball_spawn_timer >= spawn_rate and not game_over:
            ball_spawn_timer = 0
            new_ball = Ball(random.randint(0, WIDTH), difficulty)
            balls.append(new_ball)
        
        # Homing ball generation
        if difficulty >= homing_ball_threshold and not game_over:
            homing_ball_timer += 1
            homing_spawn_rate = max(180 - int(difficulty * 60), 90)  # Spawn homing balls less frequently
            
            if homing_ball_timer >= homing_spawn_rate:
                homing_ball_timer = 0
                new_homing_ball = Ball(random.randint(0, WIDTH), difficulty, is_homing=True, player_pos=player_pos)
                balls.append(new_homing_ball)
        
        # Clear screen
        screen.fill(BLACK)
        
        # Update and draw balls
        for ball in balls[:]:
            # Update homing balls with current player position
            if ball.is_homing:
                ball.player_pos = player_pos
            
            ball.update()
            ball.draw(screen)
            
            # Remove balls that are off-screen
            if ball.y > HEIGHT + ball.radius or ball.y < -ball.radius or ball.x < -ball.radius or ball.x > WIDTH + ball.radius:
                balls.remove(ball)
            
            # Collision detection
            if not game_over:
                distance = ((player_pos[0] - ball.x) ** 2 + (player_pos[1] - ball.y) ** 2) ** 0.5
                if distance < player_radius + ball.radius:
                    game_over = True
        
        # Draw player
        if not game_over:
            pygame.draw.circle(screen, BLUE, player_pos, player_radius)
        
        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Display time
        time_text = font.render(f"Time: {int(elapsed_time)}s", True, WHITE)
        screen.blit(time_text, (10, 50))
        
        # Display difficulty level
        diff_text = font.render(f"Mode: {'Normal' if difficulty_level == 'normal' else 'Hard'}", True, 
                               GREEN if difficulty_level == "normal" else RED)
        screen.blit(diff_text, (WIDTH - 150, 10))
        
        # Game over display
        if game_over:
            game_over_text = font.render("GAME OVER!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 2))
            
            restart_text = font.render("Press R to return to menu", True, GREEN)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
        
        pygame.display.update()
        clock.tick(60)

# Main loop
def main():
    while True:
        difficulty = start_screen()
        game(difficulty)

if __name__ == "__main__":
    main()
