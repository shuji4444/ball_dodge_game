import pygame
import sys
import random
import time
import math
from pygame import Surface, gfxdraw

# Game initialization
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("COSMIC DODGE")

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
PINK = (255, 105, 180)
NEON_GREEN = (57, 255, 20)
NEON_BLUE = (0, 191, 255)
DARK_BLUE = (0, 0, 100)
DARK_PURPLE = (48, 25, 52)

# Background colors for space effect
BG_COLOR = (5, 5, 15)
STAR_COLORS = [
    (150, 150, 150),  # Dim white
    (200, 200, 255),  # Light blue
    (255, 255, 255),  # Bright white
    (255, 240, 200),  # Yellowish
]

# Load sound effects
try:
    pygame.mixer.init()
    explosion_sound = pygame.mixer.Sound("explosion.wav")
    powerup_sound = pygame.mixer.Sound("powerup.wav")
    game_over_sound = pygame.mixer.Sound("gameover.wav")
    # Set default volume
    explosion_sound.set_volume(0.3)
    powerup_sound.set_volume(0.5)
    game_over_sound.set_volume(0.7)
    sound_enabled = True
except:
    sound_enabled = False
    print("Sound initialization failed. Game will run without sound.")

# Particle effects
class Particle:
    def __init__(self, x, y, color, velocity=None, size=2, life=30, gravity=False):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.gravity = gravity
        
        if velocity:
            self.vx, self.vy = velocity
        else:
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(0.5, 2.0)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        if self.gravity:
            self.vy += 0.1  # Gravity effect
            
        self.life -= 1
        
        # Fade out based on remaining life
        fade_factor = self.life / self.max_life
        r = min(255, int(self.color[0] * fade_factor))
        g = min(255, int(self.color[1] * fade_factor))
        b = min(255, int(self.color[2] * fade_factor))
        self.color = (r, g, b)
    
    def draw(self, surface: Surface):
        alpha = int(255 * (self.life / self.max_life))
        if self.size <= 1:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)
        else:
            # Use anti-aliased circle for smoother particles
            gfxdraw.aacircle(surface, int(self.x), int(self.y), int(self.size), self.color)
            gfxdraw.filled_circle(surface, int(self.x), int(self.y), int(self.size), self.color)

# Star class for background
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.choice([1, 1, 1, 2, 2, 3])  # Mostly small stars
        self.color = random.choice(STAR_COLORS)
        self.speed = self.size * 0.2  # Larger stars move faster (parallax effect)
        self.twinkle_speed = random.uniform(0.01, 0.05)
        self.brightness = random.uniform(0.5, 1.0)
        self.max_brightness = random.uniform(0.8, 1.0)
        self.min_brightness = random.uniform(0.3, 0.6)
        self.brightening = True
    
    def update(self):
        # Move star down to create scrolling effect
        self.y += self.speed
        
        # Reset position if off screen
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
        
        # Twinkle effect
        if self.brightening:
            self.brightness += self.twinkle_speed
            if self.brightness >= self.max_brightness:
                self.brightening = False
        else:
            self.brightness -= self.twinkle_speed
            if self.brightness <= self.min_brightness:
                self.brightening = True
    
    def draw(self, surface):
        # Apply brightness to color
        r = min(255, int(self.color[0] * self.brightness))
        g = min(255, int(self.color[1] * self.brightness))
        b = min(255, int(self.color[2] * self.brightness))
        color = (r, g, b)
        
        if self.size == 1:
            surface.set_at((int(self.x), int(self.y)), color)
        else:
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.color = WHITE
        self.trail = []
        self.max_trail = 10
        self.angle = 0  # For ship rotation
        self.thruster_particles = []
        self.shield_angle = 0
        self.engine_flicker = 0
    
    def update(self, target_x, target_y, speed_boost=False):
        # Calculate direction to mouse
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Smooth movement with optional speed boost
        move_speed = 0.3 if speed_boost else 0.2
        self.x += dx * move_speed
        self.y += dy * move_speed
        
        # Calculate angle for ship rotation (pointing towards movement direction)
        if abs(dx) > 0.1 or abs(dy) > 0.1:  # Only update angle if moving
            self.angle = math.atan2(dy, dx)
        
        # Add current position to trail
        self.trail.append((self.x, self.y))
        
        # Limit trail length
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
        
        # Create thruster particles
        if random.random() < (0.5 if speed_boost else 0.3):  # More particles when boosting
            # Calculate thruster position (back of the ship)
            thruster_x = self.x - math.cos(self.angle) * self.radius
            thruster_y = self.y - math.sin(self.angle) * self.radius
            
            # Add some randomness to thruster position
            thruster_x += random.uniform(-3, 3)
            thruster_y += random.uniform(-3, 3)
            
            # Create particle with velocity opposite to ship direction
            vel_x = -math.cos(self.angle) * random.uniform(1, 3)
            vel_y = -math.sin(self.angle) * random.uniform(1, 3)
            
            # Random thruster color
            thruster_color = random.choice([ORANGE, YELLOW, RED])
            
            # Larger particles when boosting
            size_range = (1.5, 4) if speed_boost else (1, 3)
            
            self.thruster_particles.append(
                Particle(thruster_x, thruster_y, thruster_color, 
                        velocity=(vel_x, vel_y), 
                        size=random.uniform(size_range[0], size_range[1]), 
                        life=random.randint(10, 20))
            )
        
        # Update thruster particles
        for particle in self.thruster_particles[:]:
            particle.update()
            if particle.life <= 0:
                self.thruster_particles.remove(particle)
        
        # Rotate shield
        self.shield_angle += 0.05
        
        # Engine flicker effect
        self.engine_flicker = (self.engine_flicker + 1) % 10
    
    def draw(self, surface, active_powerups):
        # Draw thruster particles behind ship
        for particle in self.thruster_particles:
            particle.draw(surface)
        
        # Draw trail
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                # Calculate trail opacity based on position
                alpha = int(255 * (i / len(self.trail)))
                color = (min(255, self.color[0]), 
                         min(255, self.color[1]), 
                         min(255, self.color[2]))
                
                # Draw trail segment
                pygame.draw.line(surface, color, 
                                self.trail[i], self.trail[i+1], 
                                max(1, int((i / len(self.trail)) * 3)))
        
        # Draw ship
        ship_points = [
            # Nose of the ship
            (self.x + math.cos(self.angle) * self.radius,
             self.y + math.sin(self.angle) * self.radius),
            # Right wing
            (self.x + math.cos(self.angle + 2.5) * self.radius * 0.8,
             self.y + math.sin(self.angle + 2.5) * self.radius * 0.8),
            # Back of the ship
            (self.x + math.cos(self.angle + math.pi) * self.radius * 0.5,
             self.y + math.sin(self.angle + math.pi) * self.radius * 0.5),
            # Left wing
            (self.x + math.cos(self.angle - 2.5) * self.radius * 0.8,
             self.y + math.sin(self.angle - 2.5) * self.radius * 0.8),
        ]
        
        # Draw engine glow (flickering)
        if self.engine_flicker < 5:
            engine_x = self.x - math.cos(self.angle) * (self.radius * 0.7)
            engine_y = self.y - math.sin(self.angle) * (self.radius * 0.7)
            engine_size = random.uniform(3, 6)
            engine_color = random.choice([ORANGE, YELLOW])
            pygame.draw.circle(surface, engine_color, (int(engine_x), int(engine_y)), int(engine_size))
        
        # Draw ship body
        pygame.draw.polygon(surface, self.color, ship_points)
        
        # Draw ship outline
        pygame.draw.polygon(surface, NEON_BLUE, ship_points, 2)
        
        # Draw cockpit
        cockpit_x = self.x + math.cos(self.angle) * (self.radius * 0.3)
        cockpit_y = self.y + math.sin(self.angle) * (self.radius * 0.3)
        pygame.draw.circle(surface, NEON_BLUE, (int(cockpit_x), int(cockpit_y)), int(self.radius * 0.3))
        
        # Visual effects for active power-ups
        if active_powerups["invincible"]["active"]:
            # Gold aura for invincibility
            pygame.draw.circle(surface, GOLD, (int(self.x), int(self.y)), self.radius + 8, 2)
            
            # Rotating shield effect
            for i in range(8):
                angle = self.shield_angle + i * (math.pi / 4)
                shield_x = self.x + math.cos(angle) * (self.radius + 12)
                shield_y = self.y + math.sin(angle) * (self.radius + 12)
                pygame.draw.circle(surface, GOLD, (int(shield_x), int(shield_y)), 3)
        
        if active_powerups["reflect"]["active"]:
            # Orange shield for reflect
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), self.radius + 10, 2)
            
            # Pulsing shield effect
            pulse = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
            shield_radius = self.radius + 10 + int(pulse * 5)
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), shield_radius, 1)
        
        if active_powerups["speed"]["active"]:
            # Extra trail for speed
            if len(self.trail) > 1:
                for i in range(len(self.trail) - 1):
                    alpha = int(255 * (i / len(self.trail)))
                    pygame.draw.line(surface, YELLOW, 
                                    self.trail[i], self.trail[i+1], 
                                    max(1, int((i / len(self.trail)) * 5)))
        
        if active_powerups["slow"]["active"]:
            # Cyan ripple for slow time
            ripple_size = (math.sin(pygame.time.get_ticks() * 0.01) + 1) * 0.5
            pygame.draw.circle(surface, CYAN, (int(self.x), int(self.y)), 
                              int(self.radius + 10 + ripple_size * 10), 1)
            pygame.draw.circle(surface, CYAN, (int(self.x), int(self.y)), 
                              int(self.radius + 15 + ripple_size * 10), 1)

# Ball class with enhanced visuals
class Ball:
    def __init__(self, x, difficulty, is_homing=False, player_pos=None):
        self.x = x
        self.y = 0
        self.is_homing = is_homing
        self.player_pos = player_pos
        self.particles = []
        self.pulse_phase = random.uniform(0, math.pi * 2)  # Random starting phase
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.1, 0.1)
        
        # Adjust ball size probabilities based on difficulty
        size_chances = [0.7 - difficulty * 0.3, 0.2, 0.1 + difficulty * 0.3]  # [small, medium, large]
        size_choice = random.choices([0, 1, 2], weights=size_chances)[0]
        
        if size_choice == 0:  # Small ball
            self.radius = random.randint(10, 20)
            self.speed = random.randint(3, 5)
            self.color = NEON_BLUE  # Small balls are neon blue
            self.inner_color = BLUE
            self.type = "small"
        elif size_choice == 1:  # Medium ball
            self.radius = random.randint(21, 35)
            self.speed = random.randint(2, 4)
            self.color = NEON_GREEN  # Medium balls are neon green
            self.inner_color = GREEN
            self.type = "medium"
        else:  # Large ball
            self.radius = random.randint(36, 50)
            self.speed = random.randint(1, 3)
            self.color = RED  # Large balls are red
            self.inner_color = (150, 0, 0)
            self.type = "large"
        
        # Homing balls are purple
        if self.is_homing:
            self.color = PURPLE
            self.inner_color = DARK_PURPLE
            self.speed = 1  # Homing balls are slower
            self.type = "homing"
            
        # Create points for the asteroid shape
        self.points = []
        num_points = random.randint(6, 10)
        for i in range(num_points):
            angle = i * (2 * math.pi / num_points)
            # Vary the radius to create jagged edges
            radius_var = self.radius * random.uniform(0.8, 1.2)
            x_offset = math.cos(angle) * radius_var
            y_offset = math.sin(angle) * radius_var
            self.points.append((x_offset, y_offset))

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
        
        # Update rotation
        self.rotation += self.rotation_speed * time_factor
        
        # Create trail particles occasionally
        if random.random() < 0.2:
            if self.type == "small":
                particle_color = BLUE
            elif self.type == "medium":
                particle_color = GREEN
            elif self.type == "large":
                particle_color = RED
            else:  # homing
                particle_color = PURPLE
            
            self.particles.append(
                Particle(self.x, self.y, particle_color, 
                        size=random.uniform(1, 3), 
                        life=random.randint(10, 30))
            )
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        # Draw particles first (behind the ball)
        for particle in self.particles:
            particle.draw(surface)
        
        # Calculate pulse effect
        pulse = math.sin(self.pulse_phase + pygame.time.get_ticks() * 0.005) * 0.2 + 0.8
        
        if self.type == "homing":
            # Special drawing for homing balls - pulsing evil eye
            # Outer circle
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
            
            # Inner circle
            inner_radius = int(self.radius * 0.7)
            pygame.draw.circle(surface, self.inner_color, (int(self.x), int(self.y)), inner_radius)
            
            # Pupil
            pupil_radius = int(self.radius * 0.3)
            pupil_offset = (self.player_pos[0] - self.x) * 0.2, (self.player_pos[1] - self.y) * 0.2
            pupil_offset = (
                max(-inner_radius + pupil_radius, min(inner_radius - pupil_radius, pupil_offset[0])),
                max(-inner_radius + pupil_radius, min(inner_radius - pupil_radius, pupil_offset[1]))
            )
            pygame.draw.circle(surface, BLACK, 
                              (int(self.x + pupil_offset[0]), int(self.y + pupil_offset[1])), 
                              pupil_radius)
            
            # Glowing effect
            glow_radius = int(self.radius * (1.1 + pulse * 0.2))
            pygame.draw.circle(surface, (PURPLE[0]//2, PURPLE[1]//2, PURPLE[2]//2), 
                              (int(self.x), int(self.y)), glow_radius, 2)
        else:
            # Draw asteroid-like shape for regular balls
            points = []
            for point in self.points:
                rotated_x = point[0] * math.cos(self.rotation) - point[1] * math.sin(self.rotation)
                rotated_y = point[0] * math.sin(self.rotation) + point[1] * math.cos(self.rotation)
                points.append((self.x + rotated_x, self.y + rotated_y))
            
            # Draw filled asteroid
            pygame.draw.polygon(surface, self.inner_color, points)
            
            # Draw outline
            pygame.draw.polygon(surface, self.color, points, 2)
            
            # Add some craters for detail
            for _ in range(3):
                crater_angle = random.uniform(0, math.pi * 2)
                crater_dist = random.uniform(0, self.radius * 0.7)
                crater_x = self.x + math.cos(crater_angle + self.rotation) * crater_dist
                crater_y = self.y + math.sin(crater_angle + self.rotation) * crater_dist
                crater_size = random.randint(2, max(3, int(self.radius * 0.2)))
                pygame.draw.circle(surface, (30, 30, 30), (int(crater_x), int(crater_y)), crater_size)

# PowerUp class with enhanced visuals
class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.type = random.choice(["invincible", "slow", "reflect", "speed"])
        self.active = True
        self.speed = 2
        self.particles = []
        self.angle = 0
        self.pulse_phase = random.uniform(0, math.pi * 2)
        
        # Set color based on power-up type
        if self.type == "invincible":
            self.color = GOLD
            self.inner_color = YELLOW
        elif self.type == "slow":
            self.color = CYAN
            self.inner_color = (0, 150, 150)
        elif self.type == "reflect":
            self.color = ORANGE
            self.inner_color = (200, 100, 0)
        elif self.type == "speed":
            self.color = YELLOW
            self.inner_color = (200, 200, 0)
    
    def update(self):
        self.y += self.speed
        self.angle += 0.05  # Rotate the power-up
        
        # Create particles occasionally
        if random.random() < 0.2:
            self.particles.append(
                Particle(self.x, self.y, self.color, 
                        size=random.uniform(1, 2), 
                        life=random.randint(10, 20))
            )
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface):
        if not self.active:
            return
        
        # Draw particles first (behind the power-up)
        for particle in self.particles:
            particle.draw(surface)
        
        # Calculate pulse effect
        pulse = math.sin(self.pulse_phase + pygame.time.get_ticks() * 0.01) * 0.2 + 0.8
        outer_radius = int(self.radius * (1 + pulse * 0.3))
            
        # Draw power-up circle with pulsing outer glow
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), outer_radius, 2)
        pygame.draw.circle(surface, self.inner_color, (int(self.x), int(self.y)), self.radius)
        
        # Draw icon inside based on type
        if self.type == "invincible":
            # Draw a star shape
            for i in range(5):
                angle = self.angle + i * (2 * math.pi / 5)
                outer_point = (
                    self.x + math.cos(angle) * self.radius * 0.8,
                    self.y + math.sin(angle) * self.radius * 0.8
                )
                inner_angle = angle + math.pi / 5
                inner_point = (
                    self.x + math.cos(inner_angle) * self.radius * 0.4,
                    self.y + math.sin(inner_angle) * self.radius * 0.4
                )
                
                next_angle = angle + 2 * math.pi / 5
                next_outer_point = (
                    self.x + math.cos(next_angle) * self.radius * 0.8,
                    self.y + math.sin(next_angle) * self.radius * 0.8
                )
                
                pygame.draw.polygon(surface, WHITE, [outer_point, inner_point, next_outer_point])
                
        elif self.type == "slow":
            # Draw a clock shape
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(self.radius * 0.6), 1)
            # Clock hands
            hand_length = self.radius * 0.5
            # Hour hand
            hour_angle = self.angle
            pygame.draw.line(surface, WHITE, 
                            (self.x, self.y),
                            (self.x + math.cos(hour_angle) * hand_length * 0.6,
                             self.y + math.sin(hour_angle) * hand_length * 0.6), 2)
            # Minute hand
            minute_angle = self.angle * 2
            pygame.draw.line(surface, WHITE, 
                            (self.x, self.y),
                            (self.x + math.cos(minute_angle) * hand_length,
                             self.y + math.sin(minute_angle) * hand_length), 1)
            
        elif self.type == "reflect":
            # Draw a shield shape
            shield_points = []
            num_points = 12
            for i in range(num_points):
                angle = self.angle + i * (2 * math.pi / num_points)
                # Make the shield slightly oval
                x_radius = self.radius * 0.7
                y_radius = self.radius * 0.8
                point = (
                    self.x + math.cos(angle) * x_radius,
                    self.y + math.sin(angle) * y_radius
                )
                shield_points.append(point)
            
            pygame.draw.polygon(surface, WHITE, shield_points, 1)
            # Draw cross on shield
            pygame.draw.line(surface, WHITE, 
                            (self.x - self.radius * 0.4, self.y),
                            (self.x + self.radius * 0.4, self.y), 1)
            pygame.draw.line(surface, WHITE, 
                            (self.x, self.y - self.radius * 0.4),
                            (self.x, self.y + self.radius * 0.4), 1)
            
        elif self.type == "speed":
            # Draw a lightning bolt
            bolt_points = [
                (self.x, self.y - self.radius * 0.7),  # Top
                (self.x - self.radius * 0.3, self.y),  # Middle left
                (self.x, self.y),                      # Middle
                (self.x + self.radius * 0.3, self.y),  # Middle right
                (self.x, self.y + self.radius * 0.7),  # Bottom
            ]
            pygame.draw.lines(surface, WHITE, False, bolt_points, 2)

# Explosion effect
def create_explosion(x, y, color, count=20, size_range=(2, 5), speed_range=(1, 3)):
    particles = []
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(speed_range[0], speed_range[1])
        vel_x = math.cos(angle) * speed
        vel_y = math.sin(angle) * speed
        size = random.uniform(size_range[0], size_range[1])
        life = random.randint(20, 40)
        
        particles.append(Particle(x, y, color, velocity=(vel_x, vel_y), size=size, life=life))
    
    return particles

# Start screen with enhanced visuals
def start_screen():
    # Create stars for background
    stars = [Star() for _ in range(100)]
    
    # Title animation variables
    title_scale = 0
    title_target_scale = 1.0
    
    # Button animation
    button_pulse = 0
    
    # Fonts
    title_font = pygame.font.SysFont(None, 100)
    font_medium = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 36)
    
    # Particles
    particles = []
    
    # Title text
    title_text = title_font.render("COSMIC DODGE", True, NEON_BLUE)
    normal_text = font_medium.render("1: Normal Mode", True, GREEN)
    hard_text = font_medium.render("2: Hard Mode", True, RED)
    instruction_text = font_small.render("Move mouse to avoid asteroids", True, WHITE)
    
    difficulty = None
    start_time = time.time()
    
    while difficulty is None:
        current_time = time.time()
        elapsed = current_time - start_time
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = "normal"
                    # Add explosion effect when selecting
                    particles.extend(create_explosion(WIDTH // 2, HEIGHT // 2, GREEN, 50, (2, 6), (2, 5)))
                elif event.key == pygame.K_2:
                    difficulty = "hard"
                    # Add explosion effect when selecting
                    particles.extend(create_explosion(WIDTH // 2, HEIGHT // 2, RED, 50, (2, 6), (2, 5)))
        
        # Update stars
        for star in stars:
            star.update()
        
        # Update title animation
        title_scale = min(title_target_scale, title_scale + 0.02)
        
        # Update button pulse
        button_pulse = (button_pulse + 0.05) % (2 * math.pi)
        
        # Add random particles occasionally
        if random.random() < 0.1:
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            color = random.choice([NEON_BLUE, NEON_GREEN, CYAN, PURPLE])
            particles.append(Particle(x, y, color, size=random.uniform(1, 3), life=random.randint(20, 40)))
        
        # Update particles
        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)
        
        # Clear screen with space background
        screen.fill(BG_COLOR)
        
        # Draw stars
        for star in stars:
            star.draw(screen)
        
        # Draw particles
        for particle in particles:
            particle.draw(screen)
        
        # Draw title with scaling effect
        scaled_title = pygame.transform.scale(
            title_text, 
            (int(title_text.get_width() * title_scale), 
             int(title_text.get_height() * title_scale))
        )
        screen.blit(scaled_title, 
                   (WIDTH // 2 - scaled_title.get_width() // 2, 
                    HEIGHT // 4 - scaled_title.get_height() // 2))
        
        # Draw pulsing outline around title
        if title_scale >= 0.9:
            pulse = math.sin(elapsed * 5) * 0.5 + 0.5
            outline_color = (
                int(NEON_BLUE[0] * pulse),
                int(NEON_BLUE[1] * pulse),
                int(NEON_BLUE[2] * pulse)
            )
            pygame.draw.rect(screen, outline_color, 
                            (WIDTH // 2 - scaled_title.get_width() // 2 - 10,
                             HEIGHT // 4 - scaled_title.get_height() // 2 - 10,
                             scaled_title.get_width() + 20,
                             scaled_title.get_height() + 20), 2)
        
        # Draw buttons with pulse effect
        normal_pulse = math.sin(button_pulse) * 0.1 + 1.0
        hard_pulse = math.sin(button_pulse + math.pi) * 0.1 + 1.0
        
        normal_scaled = pygame.transform.scale(
            normal_text,
            (int(normal_text.get_width() * normal_pulse),
             int(normal_text.get_height() * normal_pulse))
        )
        hard_scaled = pygame.transform.scale(
            hard_text,
            (int(hard_text.get_width() * hard_pulse),
             int(hard_text.get_height() * hard_pulse))
        )
        
        # Draw button backgrounds
        normal_rect = pygame.Rect(
            WIDTH // 2 - normal_scaled.get_width() // 2 - 20,
            HEIGHT // 2 - normal_scaled.get_height() // 2 - 10,
            normal_scaled.get_width() + 40,
            normal_scaled.get_height() + 20
        )
        pygame.draw.rect(screen, (0, 50, 0), normal_rect, 0, 10)
        pygame.draw.rect(screen, GREEN, normal_rect, 2, 10)
        
        hard_rect = pygame.Rect(
            WIDTH // 2 - hard_scaled.get_width() // 2 - 20,
            HEIGHT // 2 + 60 - hard_scaled.get_height() // 2 - 10,
            hard_scaled.get_width() + 40,
            hard_scaled.get_height() + 20
        )
        pygame.draw.rect(screen, (50, 0, 0), hard_rect, 0, 10)
        pygame.draw.rect(screen, RED, hard_rect, 2, 10)
        
        # Draw button text
        screen.blit(normal_scaled, 
                   (WIDTH // 2 - normal_scaled.get_width() // 2, 
                    HEIGHT // 2 - normal_scaled.get_height() // 2))
        screen.blit(hard_scaled, 
                   (WIDTH // 2 - hard_scaled.get_width() // 2, 
                    HEIGHT // 2 + 60 - hard_scaled.get_height() // 2))
        
        # Draw instruction with fade-in effect
        if elapsed > 1.0:  # Start showing instructions after 1 second
            alpha = min(255, int((elapsed - 1.0) * 255))
            instruction_surface = font_small.render("Move mouse to avoid asteroids", True, (255, 255, 255))
            screen.blit(instruction_surface, 
                       (WIDTH // 2 - instruction_surface.get_width() // 2, 
                        HEIGHT * 3 // 4))
        
        pygame.display.update()
        pygame.time.Clock().tick(60)
    
    # Wait a moment before returning to show explosion effect
    if difficulty:
        start_time = time.time()
        while time.time() - start_time < 0.5:  # Wait for 0.5 seconds
            # Update and draw particles
            screen.fill(BG_COLOR)
            
            # Draw stars
            for star in stars:
                star.update()
                star.draw(screen)
            
            # Draw particles
            for particle in particles[:]:
                particle.update()
                if particle.life <= 0:
                    particles.remove(particle)
                particle.draw(screen)
            
            pygame.display.update()
            pygame.time.Clock().tick(60)
    
    return difficulty

# Game loop with enhanced visuals
def game(difficulty_level):
    # Game variables
    balls = []
    powerups = []
    explosion_particles = []
    score = 0
    start_time = time.time()
    last_score_update = start_time
    ball_spawn_timer = 0
    homing_ball_timer = 0
    powerup_timer = 0
    game_over = False
    clock = pygame.time.Clock()
    
    # Create stars for background
    stars = [Star() for _ in range(100)]
    
    # Create player
    player = Player(WIDTH // 2, HEIGHT // 2)
    
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
    large_font = pygame.font.SysFont(None, 72)
    
    # UI animation variables
    score_pulse = 0
    score_flash = 0
    
    # Game over animation
    game_over_alpha = 0
    game_over_scale = 0
    
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
            score_flash = 1.0  # Flash score when updated
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    return  # Return to start screen
        
        # Get mouse position
        if not game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Update player
        if not game_over:
            player.update(mouse_x, mouse_y, active_powerups["speed"]["active"])
        
        # Check for near misses (balls passing close to player)
        if current_time - last_near_miss_check >= 0.5:  # Check every half second
            last_near_miss_check = current_time
            for ball in balls:
                distance = ((player.x - ball.x) ** 2 + (player.y - ball.y) ** 2) ** 0.5
                if player.radius + ball.radius < distance < player.radius + ball.radius + 30:
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
                new_homing_ball = Ball(random.randint(0, WIDTH), difficulty, is_homing=True, player_pos=[player.x, player.y])
                balls.append(new_homing_ball)
        
        # Power-up generation
        powerup_timer += 1
        powerup_spawn_rate = 300  # Spawn power-up every ~5 seconds
        
        if powerup_timer >= powerup_spawn_rate and not game_over:
            powerup_timer = 0
            if random.random() < 0.7:  # 70% chance to spawn a power-up
                new_powerup = PowerUp(random.randint(50, WIDTH - 50), 0)
                powerups.append(new_powerup)
        
        # Update stars
        for star in stars:
            star.update()
        
        # Calculate time factor for ball speed (for slow power-up)
        time_factor = 0.5 if active_powerups["slow"]["active"] else 1.0
        
        # Update balls
        for ball in balls[:]:
            # Update homing balls with current player position
            if ball.is_homing:
                ball.player_pos = [player.x, player.y]
            
            ball.update(time_factor)
            
            # Remove balls that are off-screen
            if ball.y > HEIGHT + ball.radius or ball.y < -ball.radius or ball.x < -ball.radius or ball.x > WIDTH + ball.radius:
                balls.remove(ball)
                continue
            
            # Collision detection
            if not game_over:
                distance = ((player.x - ball.x) ** 2 + (player.y - ball.y) ** 2) ** 0.5
                if distance < player.radius + ball.radius:
                    if active_powerups["invincible"]["active"]:
                        # Invincible - remove the ball with explosion effect
                        explosion_particles.extend(create_explosion(
                            ball.x, ball.y, ball.color, 30, (2, 5), (1, 3)
                        ))
                        balls.remove(ball)
                        
                        # Play sound if enabled
                        if sound_enabled:
                            explosion_sound.play()
                            
                        # Add bonus points
                        score += 25
                        score_flash = 1.0
                    elif active_powerups["reflect"]["active"]:
                        # Reflect - bounce the ball away with effect
                        dx = ball.x - player.x
                        dy = ball.y - player.y
                        angle = math.atan2(dy, dx)
                        ball.x = player.x + math.cos(angle) * (player.radius + ball.radius + 5)
                        ball.y = player.y + math.sin(angle) * (player.radius + ball.radius + 5)
                        
                        # Add some random velocity
                        ball.speed = random.randint(5, 8)
                        
                        # Add reflection particles
                        explosion_particles.extend(create_explosion(
                            player.x + math.cos(angle) * player.radius,
                            player.y + math.sin(angle) * player.radius,
                            ORANGE, 10, (1, 3), (1, 2)
                        ))
                    else:
                        # Game over with explosion
                        game_over = True
                        explosion_particles.extend(create_explosion(
                            player.x, player.y, WHITE, 50, (2, 6), (2, 5)
                        ))
                        
                        # Play game over sound if enabled
                        if sound_enabled:
                            game_over_sound.play()
        
        # Update power-ups
        for powerup in powerups[:]:
            powerup.update()
            
            # Remove power-ups that are off-screen
            if powerup.y > HEIGHT + powerup.radius:
                powerups.remove(powerup)
                continue
            
            # Collision detection with player
            if not game_over and powerup.active:
                distance = ((player.x - powerup.x) ** 2 + (player.y - powerup.y) ** 2) ** 0.5
                if distance < player.radius + powerup.radius:
                    # Activate power-up
                    powerup_type = powerup.type
                    active_powerups[powerup_type]["active"] = True
                    active_powerups[powerup_type]["end_time"] = current_time + 5  # 5 seconds duration
                    
                    # Add bonus points for collecting power-up
                    score += 50
                    score_flash = 1.0
                    
                    # Add power-up collection effect
                    explosion_particles.extend(create_explosion(
                        powerup.x, powerup.y, powerup.color, 20, (1, 3), (1, 2)
                    ))
                    
                    # Play power-up sound if enabled
                    if sound_enabled:
                        powerup_sound.play()
                    
                    # Remove collected power-up
                    powerup.active = False
                    powerups.remove(powerup)
        
        # Check and deactivate expired power-ups
        for powerup_type, status in active_powerups.items():
            if status["active"] and current_time > status["end_time"]:
                status["active"] = False
        
        # Update explosion particles
        for particle in explosion_particles[:]:
            particle.update()
            if particle.life <= 0:
                explosion_particles.remove(particle)
        
        # Update UI animations
        score_pulse = (score_pulse + 0.05) % (2 * math.pi)
        if score_flash > 0:
            score_flash = max(0, score_flash - 0.05)
        
        # Update game over animation
        if game_over:
            game_over_alpha = min(255, game_over_alpha + 5)
            game_over_scale = min(1.0, game_over_scale + 0.05)
        
        # Clear screen with space background
        screen.fill(BG_COLOR)
        
        # Draw stars
        for star in stars:
            star.draw(screen)
        
        # Draw balls
        for ball in balls:
            ball.draw(screen)
        
        # Draw power-ups
        for powerup in powerups:
            powerup.draw(screen)
        
        # Draw player
        if not game_over:
            player.draw(screen, active_powerups)
        
        # Draw explosion particles
        for particle in explosion_particles:
            particle.draw(screen)
        
        # Draw UI with animations
        
        # Score display with pulse and flash effects
        score_color = WHITE
        if score_flash > 0:
            flash_intensity = int(255 * score_flash)
            score_color = (255, 255, flash_intensity)
        
        score_scale = 1.0 + math.sin(score_pulse) * 0.05
        score_text = font.render(f"Score: {score}", True, score_color)
        score_text = pygame.transform.scale(
            score_text,
            (int(score_text.get_width() * score_scale),
             int(score_text.get_height() * score_scale))
        )
        screen.blit(score_text, (10, 10))
        
        # Time display
        time_text = font.render(f"Time: {int(elapsed_time)}s", True, WHITE)
        screen.blit(time_text, (10, 50))
        
        # Difficulty display with color gradient
        diff_color = GREEN
        if difficulty > 0.5:
            diff_color = YELLOW
        if difficulty > 0.8:
            diff_color = RED
            
        diff_text = font.render(f"Mode: {'Normal' if difficulty_level == 'normal' else 'Hard'}", True, 
                               GREEN if difficulty_level == "normal" else RED)
        screen.blit(diff_text, (WIDTH - 150, 10))
        
        # Difficulty meter
        diff_meter_text = small_font.render(f"Difficulty: {difficulty:.2f}", True, diff_color)
        screen.blit(diff_meter_text, (WIDTH - 150, 50))
        
        # Draw difficulty bar
        bar_width = 100
        bar_height = 10
        bar_x = WIDTH - 150
        bar_y = 75
        
        # Background bar
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Fill bar based on difficulty
        fill_width = int(bar_width * (difficulty / max_difficulty))
        
        # Gradient color for bar
        if difficulty <= 0.5:
            # Green to yellow gradient
            r = int(255 * (difficulty / 0.5))
            g = 255
            b = 0
        else:
            # Yellow to red gradient
            r = 255
            g = int(255 * (1 - (difficulty - 0.5) / 0.5))
            b = 0
        
        pygame.draw.rect(screen, (r, g, b), (bar_x, bar_y, fill_width, bar_height))
        
        # Display active power-ups with countdown
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
                
                # Pulse effect for countdown
                pulse = math.sin(current_time * 10) * 0.2 + 0.8
                if time_left <= 1:  # Flash when about to expire
                    pulse = math.sin(current_time * 20) * 0.5 + 0.5
                
                # Draw power-up icon
                pygame.draw.circle(screen, color, (WIDTH - 140, powerup_y + 10), 8)
                
                # Draw power-up text with pulse effect
                powerup_text = small_font.render(f"{name}: {time_left}s", True, color)
                screen.blit(powerup_text, (WIDTH - 120, powerup_y))
                
                # Draw countdown bar
                bar_width = 100
                bar_height = 4
                bar_x = WIDTH - 120
                bar_y = powerup_y + 20
                
                # Background bar
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                
                # Fill bar based on time left
                fill_width = int(bar_width * (time_left / 5))  # 5 seconds is full duration
                pygame.draw.rect(screen, color, (bar_x, bar_y, fill_width, bar_height))
                
                powerup_y += 30
        
        # Game over display with animation
        if game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, min(150, game_over_alpha)))
            screen.blit(overlay, (0, 0))
            
            # Game over text with scale animation
            game_over_text = large_font.render("GAME OVER!", True, RED)
            scaled_text = pygame.transform.scale(
                game_over_text,
                (int(game_over_text.get_width() * game_over_scale),
                 int(game_over_text.get_height() * game_over_scale))
            )
            screen.blit(scaled_text, 
                       (WIDTH // 2 - scaled_text.get_width() // 2, 
                        HEIGHT // 2 - 50 - scaled_text.get_height() // 2))
            
            # Final score with fade-in
            if game_over_alpha > 100:
                alpha = min(255, game_over_alpha - 100)
                final_score_text = font.render(f"Final Score: {score}", True, WHITE)
                screen.blit(final_score_text, 
                           (WIDTH // 2 - final_score_text.get_width() // 2, 
                            HEIGHT // 2))
            
            # Restart instruction with pulse
            if game_over_alpha > 150:
                pulse = (math.sin(current_time * 5) + 1) * 0.5
                restart_color = (
                    int(GREEN[0] * pulse + 100),
                    int(GREEN[1] * pulse + 100),
                    int(GREEN[2] * pulse + 100)
                )
                restart_text = font.render("Press R to return to menu", True, restart_color)
                screen.blit(restart_text, 
                           (WIDTH // 2 - restart_text.get_width() // 2, 
                            HEIGHT // 2 + 50))
        
        pygame.display.update()
        clock.tick(60)

# Main loop
def main():
    while True:
        difficulty = start_screen()
        game(difficulty)

if __name__ == "__main__":
    main()
