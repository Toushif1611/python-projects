import pygame
import math
import random
import sys

pygame.init()

# -------------------- SCREEN & COLORS --------------------
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle Arena")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 35)

BLACK = (0, 0, 0)
BLUE = (50, 150, 255)
RED = (255, 60, 60)
GREEN = (0, 255, 0)
GRAY = (120, 120, 120)

# -------------------- SETTINGS --------------------
PLAYER_RADIUS = 15
ENEMY_RADIUS = 15
PLAYER_SPEED = 300
enemy_speed = 300           # dynamized by difficulty
BULLET_SPEED = 520
reload_time = 2000
difficulty_scale = 1

# -------------------- BULLET --------------------

class Bullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - 4, y - 4, 8, 8)
        self.dx = dx
        self.dy = dy

    def move(self, dt):
        self.x += self.dx * dt
        self.y += self.dy * dt
        self.rect.center = (int(self.x), int(self.y))

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)


player_bullets = []
enemy_bullets = []


# -------------------- HELPERS --------------------
def draw_text(text, color, x, y):
    screen.blit(font.render(text, True, color), (x, y))


def draw_health_bar(x, y, health, color):
    pygame.draw.rect(screen, GRAY, (x, y, 200, 20))
    pygame.draw.rect(screen, color, (x, y, 2 * health, 20))


def check_wall_collision(rect):
    return any(rect.colliderect(w) for w in walls)


def move_entity(pos, dx, dy, radius, clamp=True):
    # Move X
    new_rect = pygame.Rect(pos[0] + dx - radius, pos[1] - radius, radius * 2, radius * 2)
    if not check_wall_collision(new_rect):
        pos[0] += dx

    # Move Y
    new_rect = pygame.Rect(pos[0] - radius, pos[1] + dy - radius, radius * 2, radius * 2)
    if not check_wall_collision(new_rect):
        pos[1] += dy

    if clamp:
        pos[0] = max(radius, min(WIDTH - radius, pos[0]))
        pos[1] = max(radius, min(HEIGHT - radius, pos[1]))


def dodge(entity_pos, bullets, radius=ENEMY_RADIUS):
    dx = dy = 0
    threats = 0
    for b in bullets:
        dist = math.hypot(entity_pos[0] - b.rect.centerx, entity_pos[1] - b.rect.centery)
        if dist < 200:
            threats += 1
            perp_x = -b.dy
            perp_y = b.dx
            mag = math.hypot(perp_x, perp_y)
            if mag != 0:
                dx += perp_x / mag
                dy += perp_y / mag

    mag = math.hypot(dx, dy)
    if mag != 0:
        dx /= mag
        dy /= mag
    return dx, dy, threats


def intercept_vector(src, tgt, tgt_vel, speed):
    tx, ty = tgt
    sx, sy = src
    vx, vy = tgt_vel
    dx = tx - sx
    dy = ty - sy
    a = vx * vx + vy * vy - speed * speed
    b = 2 * (dx * vx + dy * vy)
    c = dx * dx + dy * dy

    if abs(a) < 1e-6:
        if abs(b) < 1e-6:
            return 0, 0
        t = -c / b
        if t <= 0:
            return dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
    else:
        disc = b * b - 4 * a * c
        if disc < 0:
            return dx / math.hypot(dx, dy), dy / math.hypot(dx, dy)
        t1 = (-b + math.sqrt(disc)) / (2 * a)
        t2 = (-b - math.sqrt(disc)) / (2 * a)
        t = min(t for t in (t1, t2) if t > 0) if any(t > 0 for t in (t1, t2)) else max(t1, t2)

    aim_x = dx + vx * t
    aim_y = dy + vy * t
    mag = math.hypot(aim_x, aim_y)
    if mag == 0:
        return 0, 0
    return aim_x / mag, aim_y / mag


# -------------------- ENTITIES & GAME STATE --------------------
player = {
    "pos": [150, 300],
    "health": 100,
    "ammo": 10,
    "reloading": False,
    "reload_start": 0,
    "vel": [0, 0]
}

enemy = {
    "pos": [750, 300],
    "health": 100,
    "ammo": 10,
    "reloading": False,
    "reload_start": 0,
    "state": "attack",
    "last_shot": 0,
    "fire_delay": 400,
    "strafe_dir": 1
}

walls = [
    pygame.Rect(420, 150, 120, 40),
    pygame.Rect(420, 410, 120, 40),
    pygame.Rect(200, 200, 40, 200),
    pygame.Rect(660, 200, 40, 200),
]


# -------------------- RESET / DIFFICULTY --------------------
def reset_round(win=False):
    global difficulty_scale, enemy_speed

    # Scale difficulty on win
    if win:
        difficulty_scale += 0.2
    else:
        difficulty_scale = 1

    enemy_speed = 5 * difficulty_scale
    enemy["fire_delay"] = max(150, int(400 / difficulty_scale))

    # Reset player
    player["pos"] = [150, 300]
    player["health"] = 100
    player["ammo"] = 10
    player["reloading"] = False
    player["reload_start"] = 0
    player["vel"] = [0, 0]

    # Reset enemy
    enemy["pos"] = [750, 300]
    enemy["health"] = 100
    enemy["ammo"] = 10
    enemy["reloading"] = False
    enemy["reload_start"] = 0
    enemy["state"] = "attack"
    enemy["last_shot"] = 0
    enemy["strafe_dir"] = 1

    # Clear bullets
    player_bullets.clear()
    enemy_bullets.clear()


reset_round()  # initial setup


# -------------------- MAIN GAME LOOP --------------------
running = True
while running:
    ms = clock.tick(60)
    dt = ms / 1000.0
    screen.fill(BLACK)
    now = pygame.time.get_ticks()

    # -------------------- EVENTS --------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Player fire
            if event.key == pygame.K_SPACE and player["ammo"] > 0 and not player["reloading"]:
                dx = enemy["pos"][0] - player["pos"][0]
                dy = enemy["pos"][1] - player["pos"][1]
                angle = math.atan2(dy, dx)
                player_bullets.append(Bullet(
                    player["pos"][0], player["pos"][1],
                    math.cos(angle) * BULLET_SPEED,
                    math.sin(angle) * BULLET_SPEED
                ))
                player["ammo"] -= 1

            # Player reload
            if event.key == pygame.K_r and not player["reloading"]:
                player["reloading"] = True
                player["reload_start"] = now

    # -------------------- PLAYER MOVE --------------------
    old_x, old_y = player["pos"][0], player["pos"][1]

    dx = dy = 0
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]: dy -= PLAYER_SPEED * dt
    if keys[pygame.K_s]: dy += PLAYER_SPEED * dt
    if keys[pygame.K_a]: dx -= PLAYER_SPEED * dt
    if keys[pygame.K_d]: dx += PLAYER_SPEED * dt

    move_entity(player["pos"], dx, dy, PLAYER_RADIUS)

    # Update player velocity (approx. pixels per second)
    player["vel"][0] = (player["pos"][0] - old_x) * 60
    player["vel"][1] = (player["pos"][1] - old_y) * 60

    # -------------------- ENEMY AI --------------------
    dx = player["pos"][0] - enemy["pos"][0]
    dy = player["pos"][1] - enemy["pos"][1]
    dist = math.hypot(dx, dy)

    if dist != 0:
        dx /= dist
        dy /= dist

    dodge_x, dodge_y, threats = dodge(enemy["pos"], player_bullets)

    SAFE_DISTANCE = 220
    MAX_DISTANCE = 400

    # Decide enemy state
    if enemy["health"] < 50 and enemy["ammo"] == 0:
        enemy["state"] = "hide"
    else:
        enemy["state"] = "attack"
    # Trigger reload if out of ammo (any state)
    if enemy["ammo"] == 0 and not enemy["reloading"]:
        enemy["reloading"] = True
        enemy["reload_start"] = now

    if enemy["state"] == "attack":
        move_x = move_y = 0

        if dist > MAX_DISTANCE:
            move_x = dx * enemy_speed * dt
            move_y = dy * enemy_speed * dt
        elif dist < SAFE_DISTANCE:
            move_x = -dx * enemy_speed * dt
            move_y = -dy * enemy_speed * dt
        else:
            perp_x = -dy
            perp_y = dx
            move_x = perp_x * enemy_speed * dt * enemy["strafe_dir"]
            move_y = perp_y * enemy_speed * dt * enemy["strafe_dir"]

        if threats > 0:
            move_x = (move_x + dodge_x * 4) / 2
            move_y = (move_y + dodge_y * 4) / 2

        move_entity(enemy["pos"], move_x, move_y, ENEMY_RADIUS)

        # Shoot with prediction
        if dist < MAX_DISTANCE and enemy["ammo"] > 0 and now - enemy["last_shot"] > enemy["fire_delay"]:
            tgt_vel = tuple(player["vel"])
            vx, vy = intercept_vector(enemy["pos"], player["pos"], tgt_vel, BULLET_SPEED)
            if vx == 0 and vy == 0:
                angle = math.atan2(player["pos"][1] - enemy["pos"][1],
                                   player["pos"][0] - enemy["pos"][0])
                vx, vy = math.cos(angle), math.sin(angle)

            enemy_bullets.append(Bullet(
                enemy["pos"][0], enemy["pos"][1],
                vx * BULLET_SPEED,
                vy * BULLET_SPEED
            ))
            enemy["ammo"] -= 1
            enemy["last_shot"] = now

    elif enemy["state"] == "hide":
        best_wall = None
        best_dist = float("inf")
        for w in walls:
            d = math.hypot(w.centerx - enemy["pos"][0], w.centery - enemy["pos"][1])
            if d < best_dist:
                best_dist = d
                best_wall = w

        if best_wall:
            dx = best_wall.centerx - enemy["pos"][0]
            dy = best_wall.centery - enemy["pos"][1]
            mag = math.hypot(dx, dy)
            if mag != 0:
                dx /= mag
                dy /= mag
            move_entity(enemy["pos"], dx * enemy_speed, dy * enemy_speed, ENEMY_RADIUS)

        if enemy["ammo"] == 0 and not enemy["reloading"]:
            enemy["reloading"] = True
            enemy["reload_start"] = now

    # -------------------- RELOAD --------------------
    if player["reloading"] and now - player["reload_start"] > reload_time:
        player["ammo"] = 10
        player["reloading"] = False

    if enemy["reloading"] and now - enemy["reload_start"] > reload_time:
        enemy["ammo"] = 10
        enemy["reloading"] = False

    # -------------------- BULLETS UPDATE --------------------
    player_rect = pygame.Rect(
        player["pos"][0] - PLAYER_RADIUS,
        player["pos"][1] - PLAYER_RADIUS,
        2*PLAYER_RADIUS, 2*PLAYER_RADIUS
    )

    enemy_rect = pygame.Rect(
        enemy["pos"][0] - ENEMY_RADIUS,
        enemy["pos"][1] - ENEMY_RADIUS,
        2*ENEMY_RADIUS, 2*ENEMY_RADIUS
    )

    # Player bullets
    for b in player_bullets[:]:
        b.move(dt)
        if b.rect.colliderect(enemy_rect):
            enemy["health"] -= 5
            player_bullets.remove(b)
        elif not screen.get_rect().colliderect(b.rect) or check_wall_collision(b.rect):
            player_bullets.remove(b)
        else:
            b.draw()

    # Enemy bullets
    for b in enemy_bullets[:]:
        b.move(dt)
        if b.rect.colliderect(player_rect):
            player["health"] -= 5
            enemy_bullets.remove(b)
        elif not screen.get_rect().colliderect(b.rect) or check_wall_collision(b.rect):
            enemy_bullets.remove(b)
        else:
            b.draw()

    # -------------------- DRAW --------------------
    for w in walls:
        pygame.draw.rect(screen, GRAY, w)

    pygame.draw.circle(screen, BLUE, player["pos"], PLAYER_RADIUS)
    pygame.draw.circle(screen, RED, enemy["pos"], ENEMY_RADIUS)

    draw_text(f"HP: {player['health']}", BLUE, 20, 20)
    draw_text(f"Ammo: {player['ammo']}", BLUE, 20, 60)
    draw_text(f"Enemy HP: {enemy['health']}", RED, 650, 20)

    # -------------------- GAME OVER / WIN --------------------
    if enemy["health"] <= 0:
        draw_text("YOU WIN!", RED, WIDTH//2 - 100, HEIGHT//2)
        pygame.display.update()
        pygame.time.delay(2000)
        reset_round(win=True)
        continue

    if player["health"] <= 0:
        draw_text("YOU LOSE!", RED, WIDTH//2 - 100, HEIGHT//2)
        pygame.display.update()
        pygame.time.delay(2000)
        reset_round(win=False)
        continue

    pygame.display.update()

pygame.quit()
sys.exit()
