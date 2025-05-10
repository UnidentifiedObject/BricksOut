import pygame
import math
import random
import game_objects
from game_objects import set_volume, PowerUp, create_bricks, move_paddle, move_ball, check_collisions_with_bricks

pygame.init()
pygame.mixer.init()

game_over_sound = pygame.mixer.Sound("sounds/retro_die_03.ogg")
win_sound = pygame.mixer.Sound("sounds/Win Jingle.wav")

# Game settings
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Breakout")

clock = pygame.time.Clock()


# Game variables
paddle_width = 100
paddle_height = 20
paddle_x = (screen_width - paddle_width) // 2
paddle_y = screen_height - paddle_height - 10
paddle_speed = 7

ball_radius = 10
ball_x = screen_width // 2
ball_y = paddle_y - ball_radius
ball_dx = 3
ball_dy = -3

key_buffer = ""

score = 0
bricks = create_bricks(screen_width)

# Power-up types
BALL_MULTIPLIER = "ball_multiplier"
PADDLE_SIZE = "paddle_size"
FASTER_PADDLE = "faster_paddle"

power_ups = []

balls = [{"x": ball_x, "y": ball_y, "dx": ball_dx, "dy": ball_dy}]

# Fonts
font = pygame.font.SysFont('Arial', 30)

def read_high_score():
    try:
        with open("high_score.txt", "r") as file:
            content = file.read().strip()  # Read and strip any extra spaces or newlines
            if content:  # Check if the content is not empty
                return int(content)  # Try converting the content to an integer
            else:
                return 0  # If empty, return 0 as the default high score
    except FileNotFoundError:
        return 0  # If file doesn't exist, return 0
    except ValueError:
        return 0  # If the content is not a valid integer, return 0

def write_high_score(score):
    with open("high_score.txt", "w") as file:
        file.write(str(score))

# Mute flag
sounds_muted = False

win_sound_played = False
game_over_sound_played = False


# -------------------------
# Main Game Functions
# -------------------------

# Function to mute/unmute background music in the main file
def toggle_background_music(muted):
    if muted:
        pygame.mixer.music.set_volume(0)  # Mute background music
    else:
        pygame.mixer.music.set_volume(1)  # Restore background music volume

def set_all_sounds_volume(muted):
    if muted:
        game_over_sound.set_volume(0)  # Mute game over sound
        win_sound.set_volume(0)   # Mute game win sound
    else:
        game_over_sound.set_volume(1)  # Restore game over sound
        win_sound.set_volume(1)   # Restore game win sound

def draw_paddle():
    pygame.draw.rect(screen, (255, 255, 255), (paddle_x, paddle_y, paddle_width, paddle_height))

def draw_win_message():
    global win_sound_played, high_score

    # Check if the player has a new high score and update it
    if score > high_score:
        high_score = score  # Update high score with current score
        write_high_score(high_score)  # Save the new high score to file

    win_font = pygame.font.SysFont('Arial', 60)
    win_text = win_font.render("You Won! You are the Best!", True, (0, 255, 0))  # Green text
    screen.blit(win_text, (screen_width // 2 - win_text.get_width() // 2, screen_height // 3))

    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (screen_width // 2 - high_score_text.get_width() // 2, screen_height // 2 + 60))

    if best_time is not None:
        minutes = best_time // 60000
        seconds = (best_time % 60000) // 1000
        best_time_text = font.render(f"Best Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        screen.blit(best_time_text, (screen_width // 2 - best_time_text.get_width() // 2, screen_height // 2 + 100))


    restart_font = pygame.font.SysFont('Arial', 30)
    restart_text = restart_font.render("Press R to play again", True, (255, 255, 255))  # White text
    screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2))
    if not win_sound_played:  # Check if the sound has already been played
        win_sound.play()  # Play sound
        win_sound_played = True  # Set the flag to True to prevent replays

def draw_score():
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))  # White text
    screen.blit(score_text, (10, 10))

# Timer variables
start_time = pygame.time.get_ticks()
timer_running = True

# Best time tracking
def read_best_time():
    try:
        with open("best_time.txt", "r") as file:
            return int(file.read().strip())
    except:
        return None  # No best time yet

def write_best_time(milliseconds):
    with open("best_time.txt", "w") as file:
        file.write(str(milliseconds))

best_time = read_best_time()


def draw_timer():
    if not game_over and not game_won:  # Only show timer during gameplay
        elapsed_time = pygame.time.get_ticks() - start_time
        minutes = elapsed_time // 60000
        seconds = (elapsed_time % 60000) // 1000
        time_text = font.render(f"Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        screen.blit(time_text, (screen_width // 2 - time_text.get_width() // 2, 10))  # Top center




def draw_game_over():
    global game_over_sound_played, best_time_text
    game_over_font = pygame.font.SysFont('Arial', 60)
    game_over_text = game_over_font.render("Game Over", True, (255, 0, 0))  # Red text
    screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 3))

    # Display high score and best time
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (screen_width // 2 - high_score_text.get_width() // 2, screen_height // 2 + 60))

    if best_time is not None:
        minutes = best_time // 60000
        seconds = (best_time % 60000) // 1000
        best_time_text = font.render(f"Best Time: {minutes:02}:{seconds:02}", True, (255, 255, 255))
        screen.blit(best_time_text, (screen_width // 2 - best_time_text.get_width() // 2, screen_height // 2 + 100))


    restart_font = pygame.font.SysFont('Arial', 30)
    restart_text = restart_font.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
    screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2))
    if not game_over_sound_played:  # Check if the sound has already been played
        game_over_sound.play()  # Play sound
        game_over_sound_played = True  # Set the flag to True to prevent replays

def restart_game():
    global paddle_x, ball_x, ball_y, ball_dx, ball_dy, score, bricks, balls, power_ups, paddle_width, game_over, game_won
    global paddle_width, game_over, game_won, paddle_speed_timer
    global start_time, timer_running, final_time
    paddle_x = (screen_width - paddle_width) // 2
    ball_x = screen_width // 2
    ball_y = paddle_y - ball_radius

    # Reset ball speed (to avoid cumulative effects)
    ball_dx = 3  # Ensure this matches the default ball speed
    ball_dy = -3  # Ensure this matches the default ball speed

    score = 0
    bricks = create_bricks(screen_width)  # Recreate the bricks
    balls = [{"x": ball_x, "y": ball_y, "dx": ball_dx, "dy": ball_dy}]  # Reset balls with the initial velocity
    power_ups.clear()  # Clear power-ups
    paddle_width = 100  # Reset paddle size
    game_over = False  # Reset game over flag
    game_won = False  # Reset game won flag
    paddle_speed_timer = 0
    game_over_sound_played = False
    win_sound_played = False
    timer_running = True
    start_time = pygame.time.get_ticks()
    final_time = 0

# Global variable to track the timer for the faster paddle
paddle_speed_timer = 0

def multiply_balls():
    global balls
    new_ball = {"x": ball_x, "y": ball_y, "dx": -ball_dx, "dy": ball_dy}
    balls.append(new_ball)  # Add new ball


def increase_paddle_size():
    global paddle_width
    paddle_width = 150  # Increase the paddle width

def activate_faster_paddle():
    global paddle_speed, paddle_speed_timer
    paddle_speed *= 1.5
    paddle_speed_timer = pygame.time.get_ticks()  # Store the current time in milliseconds

def check_power_up_collisions():
    global balls, paddle_width, paddle_speed, paddle_speed_timer
    for power_up in power_ups[:]:
        # Check if paddle touches power-up
        if (paddle_y < power_up.y + power_up.height < paddle_y + paddle_height) and \
           (paddle_x < power_up.x < paddle_x + paddle_width):
            if power_up.power_up_type == BALL_MULTIPLIER:
                multiply_balls()
            elif power_up.power_up_type == PADDLE_SIZE:
                increase_paddle_size()
            elif power_up.power_up_type == "faster_paddle":
                activate_faster_paddle()

            power_ups.remove(power_up)  # Remove the power-up after it's collected


def spawn_random_balls():
    global balls
    for _ in range(20):
        angle = random.uniform(0, 2 * math.pi)
        speed = 4
        dx = speed * math.cos(angle)
        dy = speed * math.sin(angle)
        new_ball = {
            "x": paddle_x + paddle_width // 2,
            "y": paddle_y - ball_radius,
            "dx": dx,
            "dy": dy
        }
        balls.append(new_ball)




#
#------------------------- Main Game Loop -------------------------
#
running = True
game_over = False
game_won = False
paddle_speed_timer = 0
game_over_sound_played = False
win_sound_played = False
# Load the high score
high_score = read_high_score()



while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                restart_game()
                game_won = False
                game_over = False
                game_over_sound_played = False
                win_sound_played = False
            elif event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_m:
                sounds_muted = not sounds_muted
                game_objects.set_volume(sounds_muted)
                toggle_background_music(sounds_muted)
                set_all_sounds_volume(sounds_muted)

            # --- Cheat Code Handling ---
            if event.unicode.isalpha():
                key_buffer += event.unicode.lower()
                key_buffer = key_buffer[-10:]  # Trim buffer

                if "alot" in key_buffer:
                    spawn_random_balls()
                    key_buffer = ""




    # Check if all bricks are cleared (player wins)
    if not game_over and len(bricks) == 0:
        game_won = True  # Set the game won flag to True

    # If the game is won, stop the game and display the winning message
    if game_won:
        if not sounds_muted and not win_sound_played:  # Prevent the win sound from playing repeatedly
            win_sound.play()
            win_sound_played = True  # Ensure it only plays once
        if timer_running:
            final_time = pygame.time.get_ticks() - start_time
            timer_running = False
            # Save best time if it's faster or if no previous best time
            if best_time is None or final_time < best_time:
                best_time = final_time
                write_best_time(best_time)
        draw_win_message()  # Display "You Won!" message

    # If the game is over, play the game over sound only once
    elif game_over:
        if not sounds_muted and not game_over_sound_played:  # Check that it hasn’t played before
            game_over_sound.play()
            game_over_sound_played = True  #
        if score > high_score:
            high_score = score  # Update the high score
            write_high_score(high_score)  # Save it to the file
        if not game_over_sound_played:
            game_over_sound.play()
            game_over_sound_played = True
        if timer_running:
            final_time = pygame.time.get_ticks() - start_time
            timer_running = False
        draw_game_over()



    else:
        # Regular gameplay code
        paddle_x = move_paddle(paddle_x, paddle_speed, screen_width, paddle_width)  # Move paddle
        balls = move_ball(balls, screen_width, ball_radius)  # Move balls
        bricks, score = check_collisions_with_bricks(balls, bricks, ball_radius, screen_width, score, power_ups)
        check_power_up_collisions()  # Check for power-up collisions

        # Handle paddle speed timer reset after 5 seconds
        if paddle_speed_timer != 0:
            if pygame.time.get_ticks() - paddle_speed_timer > 5000:  # 5000 ms = 5 seconds
                paddle_speed /= 1.5  # Reset paddle speed to normal
                paddle_speed_timer = 0  # Reset the timer

        # Check if all balls are out (game over)
        balls_to_remove = []
        for ball in balls[:]:
            if ball["y"] > screen_height:  # Ball goes beyond the screen
                balls_to_remove.append(ball)  # Mark ball for removal

        # Remove balls that go beyond the screen
        for ball in balls_to_remove:
            balls.remove(ball)

        # If there are no balls left and game is not won, show game over
        if len(balls) == 0 and not game_won:
            game_over = True  # Set game over flag to True

        # Draw everything
        screen.fill((0, 0, 0))  # Fill screen with black
        draw_score()
        draw_timer()

        # Draw bricks
        for brick in bricks:
            pygame.draw.rect(screen, (220, 10, 10), brick)  # Draw bricks in red
        draw_paddle()

        # Ball movement and collision detection
        for ball in balls:
            ball["x"] += ball["dx"]
            ball["y"] += ball["dy"]

            if paddle_y <= ball["y"] + ball_radius <= paddle_y + paddle_height:
                if paddle_x <= ball["x"] <= paddle_x + paddle_width:
                    # Calculate the hit position relative to the paddle center (-1 to 1)
                    offset = (ball["x"] - (paddle_x + paddle_width / 2)) / (paddle_width / 2)

                    # Max bounce angle in radians (60 degrees)
                    max_angle = math.radians(60)
                    angle = offset * max_angle

                    # Set ball speed
                    speed = 5

                    # Use angle to calculate new dx, dy
                    ball["dx"] = speed * math.sin(angle)
                    ball["dy"] = -speed * math.cos(angle)

                    ball["y"] = paddle_y - ball_radius  # Position it on top of the paddle

            # Ball screen boundaries (top and sides)
            if ball["x"] - ball_radius <= 0 or ball["x"] + ball_radius >= screen_width:
                ball["dx"] *= -1  # Reverse ball's X direction (bounce off side walls)

            if ball["y"] - ball_radius <= 0:  # Ball hits the top of the screen
                ball["dy"] *= -1  # Reverse ball's Y direction (bounce off the top)

            # Drawing the ball on the screen
            pygame.draw.circle(screen, (255, 255, 255), (ball["x"], ball["y"]), ball_radius)  # Draw ball in white

        # Draw power-ups
        for power_up in power_ups:
            power_up.update()
            power_up.draw(screen)

    pygame.display.flip()  # Update the screen
    clock.tick(60)  # FPS limit

pygame.quit()