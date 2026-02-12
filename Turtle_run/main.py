import pygame
import random
import math
import asyncio
import sys

pygame.init()

WIDTH, HEIGHT = 700, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TURTLE RUN")

clock = pygame.time.Clock()
font = pygame.font.SysFont("courier", 28)
big_font = pygame.font.SysFont("courier", 60)

WHITE = (255,255,255)
BLACK = (0,0,0)
GREEN = (0,255,0)
RED   = (255,0,0)

# Game variables
player_size = 20
food_size = 15

player_x = WIDTH // 2
player_y = HEIGHT // 2
player_angle = 0
speed = 3

score = 0
level = 1

food_x = random.randint(20, WIDTH-20)
food_y = random.randint(20, HEIGHT-20)

# Collision function
def is_collision(x1,y1,x2,y2,dist):
    return math.sqrt((x1-x2)**2 + (y1-y2)**2) < dist


async def main():
    global player_x, player_y, player_angle
    global speed, score, level, food_x, food_y

    running = True
    win = False

    # Food movement direction
    food_dx = 2
    food_dy = 2

    while running:
        clock.tick(60)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if not win:

            # Rotation
            if keys[pygame.K_LEFT]:
                player_angle += 4
            if keys[pygame.K_RIGHT]:
                player_angle -= 4

            # Move ONLY when UP key is pressed
            if keys[pygame.K_UP]:
                player_x += math.cos(math.radians(player_angle)) * speed
                player_y -= math.sin(math.radians(player_angle)) * speed

            # Border collision for player
            if player_x < 60:
                player_x = 60
            if player_x > WIDTH-60:
                player_x = WIDTH-60
            if player_y < 60:
                player_y = 60
            if player_y > HEIGHT-60:
                player_y = HEIGHT-60

            # Collision with food
            if is_collision(player_x, player_y, food_x, food_y, 25):
                score += 1
                food_x = random.randint(70, WIDTH-70)
                food_y = random.randint(70, HEIGHT-70)

            # Level system
            if score >= 9 and score < 19:
                level = 2
            elif score >= 19 and score < 29:
                level = 3
            elif score >= 29 and score < 39:
                level = 4
            elif score >= 39 and score < 50:
                level = 5

            # Food movement (proper bouncing)
            if level >= 2:
                food_x += food_dx
                food_y += food_dy

                if food_x <= 60 or food_x >= WIDTH-60:
                    food_dx *= -1
                if food_y <= 60 or food_y >= HEIGHT-60:
                    food_dy *= -1

            if score >= 50:
                win = True

        # Draw border
        pygame.draw.rect(screen, WHITE, (50,50,600,600), 3)

        # Draw player with correct head direction
        triangle = pygame.Surface((40, 40), pygame.SRCALPHA)

        # Draw triangle pointing RIGHT (default 0 degrees)
        pygame.draw.polygon(triangle, GREEN, [(40,20), (0,0), (0,40)])

        # Rotate correctly
        rotated = pygame.transform.rotate(triangle, player_angle)
        rect = rotated.get_rect(center=(player_x, player_y))

        screen.blit(rotated, rect)

        # Draw food
        pygame.draw.circle(screen, RED, (int(food_x),int(food_y)), food_size)

        # Draw score
        text = font.render(f"Score: {score}   Level: {level}", True, WHITE)
        screen.blit(text, (20, 20))

        # Win screen
        if win:
            win_text = big_font.render("YOU WIN!", True, WHITE)
            screen.blit(win_text, (WIDTH//2 - 150, HEIGHT//2 - 30))

        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


if sys.platform == "emscripten":
    asyncio.ensure_future(main())
else:
    asyncio.run(main())
