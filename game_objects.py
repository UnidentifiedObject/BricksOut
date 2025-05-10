import pygame
import random

pygame.mixer.init()


# Load sound effects
paddle_hit_sound = pygame.mixer.Sound("sounds/shot_01.ogg")
brick_hit_sound = pygame.mixer.Sound("sounds/shot_02.ogg")
power_up_sound = pygame.mixer.Sound("sounds/power_up_01.ogg")


# Function to set the volume of all sounds
def set_volume(muted):
    if muted:
        paddle_hit_sound.set_volume(0)  # Mute the paddle hit sound
        brick_hit_sound.set_volume(0)  # Mute the brick hit sound
        power_up_sound.set_volume(0)  # Mute the power-up sound
    else:
        paddle_hit_sound.set_volume(1)  # Restore the paddle hit sound
        brick_hit_sound.set_volume(1)  # Restore the brick hit sound
        power_up_sound.set_volume(1)  # Restore the power-up sound


# -------------------------
# PowerUp Class
# -------------------------
class PowerUp:
    def __init__(self, x, y, power_up_type):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.power_up_type = power_up_type
        self.color = (0, 255, 0)  # Green for power-ups

        # Set color based on the power-up type
        if self.power_up_type == "ball_multiplier":
            self.color = (255, 0, 0)  # Red for ball multiplier
        elif self.power_up_type == "paddle_size":
            self.color = (0, 0, 255)  # Blue for paddle size
        elif self.power_up_type == "faster_paddle":
            self.color = (0, 255, 0)  # Green for faster paddle
        else:
            self.color = (255, 255, 255)  # Default color (white)

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def update(self):
        self.y += 5  # Power-up falls down



# -------------------------
# Game Functions for Ball and Paddle
# -------------------------
def create_bricks(screen_width):
    bricks = []
    brick_width = 60  # Width of each brick
    brick_height = 20  # Height of each brick
    vertical_gap = 5  # Vertical gap between rows
    horizontal_gap = 5  # Horizontal gap between columns
    margin_left = 50  # Margin from the left side of the screen
    margin_right = 20  # Margin from the right side of the screen

    # Calculate how many bricks can fit within the available width, taking margin into account
    available_width = screen_width - margin_left - margin_right
    bricks_per_row = available_width // (brick_width + horizontal_gap)

    # Number of rows of bricks (fixed to 5 in this case)
    rows = 5

    for row in range(rows):
        for col in range(bricks_per_row):
            brick_x = margin_left + col * (brick_width + horizontal_gap)
            brick_y = row * (brick_height + vertical_gap) + 50  # 50 for top margin
            brick = pygame.Rect(brick_x, brick_y, brick_width, brick_height)
            bricks.append(brick)

    return bricks


def move_paddle(paddle_x, paddle_speed, screen_width, paddle_width):
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and paddle_x > 0:
        paddle_x -= paddle_speed
    if keys[pygame.K_RIGHT] and paddle_x < screen_width - paddle_width:
        paddle_x += paddle_speed
    return paddle_x


def move_ball(balls, screen_width, ball_radius):
    for ball in balls[:]:
        # Update ball's position
        ball["x"] += ball["dx"]
        ball["y"] += ball["dy"]

        # Ball collision with walls
        if ball["x"] <= ball_radius or ball["x"] >= screen_width - ball_radius:
            ball["dx"] *= -1  # Reverse the horizontal direction
            paddle_hit_sound.play()
        if ball["y"] <= ball_radius:
            ball["dy"] *= -1  # Reverse the vertical direction
            paddle_hit_sound.play()

    return balls

def check_collisions_with_bricks(balls, bricks, ball_radius, screen_width, score, power_ups):
    for brick in bricks[:]:
        for ball in balls:
            if brick.collidepoint(ball["x"], ball["y"]):
                bricks.remove(brick)  # Remove the brick when it's hit
                ball["dy"] *= -1  # Reverse ball's Y direction
                score += 10  # Increase score for destroying the brick

                brick_hit_sound.play()

                # Randomly decide whether to drop a power-up
                if random.random() < 0.1:
                    power_up_type = random.choice(["ball_multiplier", "paddle_size", "faster_paddle"])  # Add faster_paddle
                    #   print(f"Power-up spawned: {power_up_type}") This line shows power ups
                    power_ups.append(PowerUp(brick.x, brick.y, power_up_type))
                    power_up_sound.play()
                    # Append to the passed power_ups list
                break
    return bricks, score