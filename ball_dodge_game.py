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
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)

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

    def update(self, time_factor=1.0):
        if self.is_homing and self.player_pos:
            # Calculate direction towards player
            dx = self.player_pos[0] - self.x
            dy = self.player_pos[1] - self.y
            distance = max(1, math.sqrt(dx*dx + dy*dy))  # Avoid division by zero
            
            # Normalize and apply speed
            self.x += (dx / distance) * self.speed * time_factor
            self.y += self.speed * time_factor
        else:
            # Normal vertical movement
            self.y += self.speed * time_factor
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# PowerUp class
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.type = random.choice(["invincible", "slow", "reflect", "speed"])
        self.active = True
        self.speed = 2
        
        # Set color based on power-up type
        if self.type == "invincible":
            self.color = GOLD
        elif self.type == "slow":
            self.color = CYAN
        elif self.type == "reflect":
            self.color = ORANGE
        elif self.type == "speed":
            self.color = YELLOW
    
    def update(self):
        self.y += self.speed
    
    def draw(self, surface):
        if not self.active:
            return
            
        # Draw power-up circle
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Draw icon inside based on type
        if self.type == "invincible":
            # Draw a star shape
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius // 2)
        elif self.type == "slow":
            # Draw a clock shape
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius // 2, 2)
            # Clock hands
            pygame.draw.line(surface, WHITE, (self.x, self.y), (self.x, self.y - self.radius // 2), 2)
            pygame.draw.line(surface, WHITE, (self.x, self.y), (self.x + self.radius // 3, self.y), 2)
        elif self.type == "reflect":
            # Draw a shield shape
            pygame.draw.polygon(surface, WHITE, [
                (self.x, self.y - self.radius // 2),
                (self.x - self.radius // 2, self.y + self.radius // 3),
                (self.x + self.radius // 2, self.y + self.radius // 3)
            ])
        elif self.type == "speed":
            # Draw a lightning bolt
            pygame.draw.line(surface, WHITE, (self.x - self.radius // 3, self.y - self.radius // 2),
                            (self.x + self.radius // 3, self.y + self.radius // 2), 2)

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
    powerups = []
    score = 0
    start_time = time.time()
    last_score_update = start_time
    ball_spawn_timer = 0
    homing_ball_timer = 0
    powerup_timer = 0
    game_over = False
    clock = pygame.time.Clock()
    
    # Dynamic difficulty variables
    player_skill = 0.5  # Start at medium skill level (0.0 to 1.0)
    near_miss_count = 0
    last_near_miss_check = time.time()
    
    # Power-up status
    active_powerups = {
        "invincible": {"active": False, "end_time": 0},
        "slow": {"active": False, "end_time": 0},
        "reflect": {"active": False, "end_time": 0},
        "speed": {"active": False, "end_time": 0}
    }
    
    # Set difficulty parameters
    if difficulty_level == "normal":
        base_difficulty_multiplier = 1.0
        homing_ball_threshold = 0.5  # When to start spawning homing balls
        max_difficulty = 0.9
        difficulty_time = 60  # Seconds to reach max difficulty
    else:  # Hard mode
        base_difficulty_multiplier = 1.5
        homing_ball_threshold = 0.3  # Earlier homing balls
        max_difficulty = 1.0
        difficulty_time = 45  # Reach max difficulty faster
    
    # Font settings
    font = pygame.font.SysFont(None, 36)
    small_font = pygame.font.SysFont(None, 24)
    
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        # Calculate dynamic difficulty based on time and player skill
        time_difficulty = min(max_difficulty, elapsed_time / difficulty_time)
        difficulty = time_difficulty * base_difficulty_multiplier * (0.8 + player_skill * 0.4)
        
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
        
        # Check for near misses (balls passing close to player)
        if current_time - last_near_miss_check >= 0.5:  # Check every half second
            last_near_miss_check = current_time
            for ball in balls:
                distance = ((player_pos[0] - ball.x) ** 2 + (player_pos[1] - ball.y) ** 2) ** 0.5
                if player_radius + ball.radius < distance < player_radius + ball.radius + 30:
                    near_miss_count += 1
                    # Increase player skill rating based on near misses
                    if near_miss_count % 5 == 0:
                        player_skill = min(1.0, player_skill + 0.05)
        
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
        
        # Power-up generation
        powerup_timer += 1
        powerup_spawn_rate = 300  # Spawn power-up every ~5 seconds
        
        if powerup_timer >= powerup_spawn_rate and not game_over:
            powerup_timer = 0
            if random.random() < 0.7:  # 70% chance to spawn a power-up
                new_powerup = PowerUp(random.randint(50, WIDTH - 50), 0)
                powerups.append(new_powerup)
        
        # Clear screen
        screen.fill(BLACK)
        
        # Calculate time factor for ball speed (for slow power-up)
        time_factor = 0.5 if active_powerups["slow"]["active"] else 1.0
        
        # Update and draw balls
        for ball in balls[:]:
            # Update homing balls with current player position
            if ball.is_homing:
                ball.player_pos = player_pos
            
            ball.update(time_factor)
            ball.draw(screen)
            
            # Remove balls that are off-screen
            if ball.y > HEIGHT + ball.radius or ball.y < -ball.radius or ball.x < -ball.radius or ball.x > WIDTH + ball.radius:
                balls.remove(ball)
            
            # Collision detection
            if not game_over:
                distance = ((player_pos[0] - ball.x) ** 2 + (player_pos[1] - ball.y) ** 2) ** 0.5
                if distance < player_radius + ball.radius:
                    if active_powerups["invincible"]["active"]:
                        # Invincible - remove the ball
                        balls.remove(ball)
                    elif active_powerups["reflect"]["active"]:
                        # Reflect - bounce the ball away
                        dx = ball.x - player_pos[0]
                        dy = ball.y - player_pos[1]
                        angle = math.atan2(dy, dx)
                        ball.x = player_pos[0] + math.cos(angle) * (player_radius + ball.radius + 5)
                        ball.y = player_pos[1] + math.sin(angle) * (player_radius + ball.radius + 5)
                        # Add some random velocity
                        ball.speed = random.randint(5, 8)
                    else:
                        game_over = True
        
        # Update and draw power-ups
        for powerup in powerups[:]:
            powerup.update()
            powerup.draw(screen)
            
            # Remove power-ups that are off-screen
            if powerup.y > HEIGHT + powerup.radius:
                powerups.remove(powerup)
                continue
            
            # Collision detection with player
            if not game_over and powerup.active:
                distance = ((player_pos[0] - powerup.x) ** 2 + (player_pos[1] - powerup.y) ** 2) ** 0.5
                if distance < player_radius + powerup.radius:
                    # Activate power-up
                    powerup_type = powerup.type
                    active_powerups[powerup_type]["active"] = True
                    active_powerups[powerup_type]["end_time"] = current_time + 5  # 5 seconds duration
                    
                    # Add bonus points for collecting power-up
                    score += 50
                    
                    # Remove collected power-up
                    powerup.active = False
                    powerups.remove(powerup)
        
        # Check and deactivate expired power-ups
        for powerup_type, status in active_powerups.items():
            if status["active"] and current_time > status["end_time"]:
                status["active"] = False
        
        # Draw player with visual effects based on active power-ups
        if not game_over:
            # Base player circle
            pygame.draw.circle(screen, WHITE, player_pos, player_radius)
            
            # Visual effects for active power-ups
            if active_powerups["invincible"]["active"]:
                # Gold aura for invincibility
                pygame.draw.circle(screen, GOLD, player_pos, player_radius + 5, 2)
                pygame.draw.circle(screen, GOLD, player_pos, player_radius + 8, 1)
            
            if active_powerups["reflect"]["active"]:
                # Orange shield for reflect
                pygame.draw.circle(screen, ORANGE, player_pos, player_radius + 3, 2)
            
            if active_powerups["speed"]["active"]:
                # Yellow trail for speed
                pygame.draw.circle(screen, YELLOW, player_pos, player_radius - 5)
            
            if active_powerups["slow"]["active"]:
                # Cyan ripple for slow time
                pygame.draw.circle(screen, CYAN, player_pos, player_radius + 10, 1)
        
        # Display score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # Display time
        time_text = font.render(f"Time: {int(elapsed_time)}s", True, WHITE)
        screen.blit(time_text, (10, 50))
        
        # Display difficulty level and dynamic difficulty
        diff_text = font.render(f"Mode: {'Normal' if difficulty_level == 'normal' else 'Hard'}", True, 
                               GREEN if difficulty_level == "normal" else RED)
        screen.blit(diff_text, (WIDTH - 150, 10))
        
        # Display dynamic difficulty meter
        diff_meter_text = small_font.render(f"Difficulty: {difficulty:.2f}", True, 
                                          YELLOW if difficulty > 0.7 else GREEN)
        screen.blit(diff_meter_text, (WIDTH - 150, 50))
        
        # Display active power-ups
        powerup_y = 90
        for powerup_type, status in active_powerups.items():
            if status["active"]:
                time_left = int(status["end_time"] - current_time)
                if powerup_type == "invincible":
                    color = GOLD
                    name = "Invincible"
                elif powerup_type == "slow":
                    color = CYAN
                    name = "Time Slow"
                elif powerup_type == "reflect":
                    color = ORANGE
                    name = "Reflect"
                elif powerup_type == "speed":
                    color = YELLOW
                    name = "Speed Up"
                
                powerup_text = small_font.render(f"{name}: {time_left}s", True, color)
                screen.blit(powerup_text, (WIDTH - 150, powerup_y))
                powerup_y += 25
        
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
