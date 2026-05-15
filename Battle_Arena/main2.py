import math
import random
import pygame
from pygame.math import Vector2

WIDTH, HEIGHT = 1180, 760
FPS = 60
BG = (17, 18, 24)
GRID = (30, 34, 46)
TEXT = (235, 238, 246)
MUTED = (180, 188, 210)
ACCENT = (110, 165, 255)
WARN = (255, 215, 105)
HERO_COLOR = (85, 225, 120)
STATE_COLORS = {
    "seek": (239, 92, 92),
    "flank": (255, 160, 70),
    "ambush": (170, 115, 255),
    "panic": (90, 220, 255),
}
BRAIN_TYPES = ["hunter", "flanker", "trickster", "coward"]
NUM_ENEMIES = 10
HERO_RADIUS = 16
ENEMY_RADIUS = 13
HERO_MAX_SPEED = 5.0
ENEMY_BASE_SPEED = 2.15
HERO_FORCE = 0.17
ENEMY_FORCE_BASE = 0.085
SAFE_DISTANCE = 150
LOOKAHEAD = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Victim vs Enemy")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)
small = pygame.font.SysFont("consolas", 15)


def clamp(value, low, high):
    return max(low, min(high, value))


def limit(vec, amount):
    if vec.length() > amount:
        vec.scale_to_length(amount)
    return vec


class Victim:
    def __init__(self):
        self.pos = Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = Vector2()
        self.radius = HERO_RADIUS
        self.intelligence = 0.60
        self.manual_mode = False
        self.alive = True
        self.survival_time = 0.0

    def update(self, enemies, keys):
        if not self.alive:
            return
        desired = Vector2()
        if self.manual_mode:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                desired.x -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                desired.x += 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                desired.y -= 1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                desired.y += 1
            if desired.length_squared() > 0:
                desired = desired.normalize() * HERO_MAX_SPEED
        else:
            danger = Vector2()
            trap_avoid = Vector2()
            center_bias = Vector2(WIDTH / 2 - self.pos.x, HEIGHT / 2 - self.pos.y) * 0.002

            for enemy in enemies:
                offset = self.pos - enemy.pos
                dist = max(offset.length(), 0.001)
                predicted_enemy = enemy.pos + enemy.vel * enemy.brain["prediction"] * (0.6 + self.intelligence)
                future_offset = self.pos - predicted_enemy
                future_dist = max(future_offset.length(), 0.001)
                if dist < SAFE_DISTANCE * 1.8:
                    danger += offset.normalize() * (SAFE_DISTANCE / dist) ** 1.7 * enemy.brain["aggression"]
                if future_dist < SAFE_DISTANCE * 1.7:
                    danger += future_offset.normalize() * (SAFE_DISTANCE / future_dist) ** 2.15 * (0.4 + self.intelligence)

            for i in range(len(enemies)):
                for j in range(i + 1, len(enemies)):
                    gap_center = (enemies[i].pos + enemies[j].pos) / 2
                    diff = self.pos - gap_center
                    d = max(diff.length(), 0.001)
                    if d < SAFE_DISTANCE * 1.55:
                        trap_avoid += diff.normalize() * (SAFE_DISTANCE / d) ** 1.3

            smart = danger * (0.55 + self.intelligence * 1.55) + trap_avoid * self.intelligence + center_bias * (1 - 0.35 * self.intelligence)
            if smart.length_squared() > 0:
                desired = smart.normalize() * HERO_MAX_SPEED * (0.78 + self.intelligence * 0.38)

        steering = desired - self.vel
        limit(steering, HERO_FORCE)
        self.vel += steering
        limit(self.vel, HERO_MAX_SPEED)
        self.pos += self.vel
        self.pos.x = clamp(self.pos.x, self.radius, WIDTH - self.radius)
        self.pos.y = clamp(self.pos.y, self.radius, HEIGHT - self.radius)
        self.survival_time += 1 / FPS

    def draw(self, surf):
        pygame.draw.circle(surf, HERO_COLOR, self.pos, self.radius)
        pygame.draw.circle(surf, (255, 255, 255), self.pos, self.radius, 2)
        head = self.vel.normalize() * 20 if self.vel.length_squared() else Vector2(18, 0)
        pygame.draw.line(surf, (255, 255, 255), self.pos, self.pos + head, 3)


class Enemy:
    def __init__(self, idx):
        self.idx = idx
        self.pos = self.spawn_position()
        ang = random.random() * math.tau
        self.vel = Vector2(math.cos(ang), math.sin(ang))
        self.radius = ENEMY_RADIUS
        self.brain = self.make_brain()
        self.state = "seek"
        self.state_timer = random.uniform(40, 180)
        self.wander_angle = random.random() * math.tau
        self.last_seen = Vector2(self.pos)
        # extra memory for smoother state transitions
        self.last_target = Vector2()

    def spawn_position(self):
        margin = 45
        side = random.choice([0, 1, 2, 3])
        if side == 0:
            return Vector2(random.randint(margin, WIDTH - margin), margin)
        if side == 1:
            return Vector2(WIDTH - margin, random.randint(margin, HEIGHT - margin))
        if side == 2:
            return Vector2(random.randint(margin, WIDTH - margin), HEIGHT - margin)
        return Vector2(margin, random.randint(margin, HEIGHT - margin))

    def make_brain(self):
        brain_type = BRAIN_TYPES[self.idx % len(BRAIN_TYPES)]
        presets = {
            "hunter": dict(
                aggression=1.40,
                caution=0.40,
                prediction=1.0,
                pack=0.60,
                flank=0.2,
                color=(245, 90, 90),
            ),
            "flanker": dict(
                aggression=0.90,
                caution=0.65,
                prediction=1.45,
                pack=0.85,
                flank=1.55,
                color=(255, 155, 75),
            ),
            "trickster": dict(
                aggression=1.00,
                caution=0.55,
                prediction=1.25,
                pack=0.40,
                flank=1.75,
                color=(175, 120, 255),
            ),
            "coward": dict(
                aggression=0.65,
                caution=1.55,
                prediction=0.80,
                pack=1.25,
                flank=0.40,
                color=(80, 220, 255),
            ),
        }
        brain = presets[brain_type].copy()
        brain["type"] = brain_type
        brain["speed"] = ENEMY_BASE_SPEED * random.uniform(0.92, 1.15)
        brain["force"] = ENEMY_FORCE_BASE * random.uniform(0.9, 1.18)
        brain["personal_space"] = random.uniform(30, 55)
        brain["panic_distance"] = random.uniform(60, 115)
        brain["decision_bias"] = random.uniform(-0.18, 0.18)
        brain["flank_side"] = random.choice([-1, 1])  # pick left or right flank
        return brain

    def choose_state(self, hero, enemies):
        to_hero = hero.pos - self.pos
        dist = to_hero.length()
        self.state_timer -= 1

        close_allies = sum(
            1 for e in enemies
            if e is not self and e.pos.distance_to(self.pos) < 130
        )

        # score each state using brain traits
        score_seek = (
            self.brain["aggression"] * 1.15 +
            (180 - dist) / 220
        )

        score_flank = (
            self.brain["flank"] * 1.25 +
            close_allies * 0.20 +
            self.brain["prediction"] * 0.30
        )

        score_ambush = (
            self.brain["prediction"] * 1.15 +
            max(0, dist - 120) / 260 +
            self.brain["decision_bias"]
        )

        score_panic = (
            self.brain["caution"] * 1.35 +
            max(0, 95 - dist) / 75 -
            close_allies * 0.15
        )

        # panic: if very close and highly cautious, panic anyway
        if dist < self.brain["panic_distance"] * 0.9 and score_panic > 1.5:
            self.state = "panic"
            self.state_timer = random.randint(25, 60)
        # cooldown: if timer is up, switch to best state
        elif self.state_timer <= 0:
            best = max(
                [("seek", score_seek),
                 ("flank", score_flank),
                 ("ambush", score_ambush),
                 ("panic", score_panic)],
                key=lambda x: x[1],
            )[0]
            self.state = best
            self.state_timer = random.randint(40, 120)

        self.last_seen = Vector2(hero.pos)

    def separation(self, enemies):
        steer = Vector2()
        personal_space = self.brain["personal_space"]
        for other in enemies:
            if other is self:
                continue
            diff = self.pos - other.pos
            d = diff.length()
            if 0 < d < personal_space:
                steer += diff.normalize() * (personal_space - d) / personal_space
        return steer

    # better predictive pursue: steer toward where hero will be
    def pursue(self, hero):
        # hunter + trickster aim directly ahead; others are a bit slower
        extra = 1.0
        if self.brain["type"] in ["hunter", "trickster"]:
            extra = 1.2
        return hero.pos + hero.vel * (20 + 35 * self.brain["prediction"] * extra) - self.pos

    # flank: aim to the side, behind hero’s predicted path
    def flank_target(self, hero):
        to_hero = hero.pos - self.pos
        if to_hero.length_squared() == 0:
            return Vector2()

        # side vector: try to circle around hero
        side = Vector2(-to_hero.y, to_hero.x)
        if side.length_squared() == 0:
            side = Vector2(1, 0)

        side = side.normalize()
        offset_amount = 100 * self.brain["flank"] * self.brain["flank_side"]
        offset = side * offset_amount

        # 20% more prediction for flanking types
        extra = 1.0
        if self.brain["type"] in ["flanker", "trickster"]:
            extra = 1.2

        future_hero = hero.pos + hero.vel * (25 + 40 * self.brain["prediction"] * extra)
        return (future_hero + offset) - self.pos

    # ambush: aim to intercept ahead of hero
    def ambush_target(self, hero):
        extra = 1.0
        if self.brain["type"] in ["flanker", "trickster"]:
            extra = 1.3
        future = hero.pos + hero.vel * (60 + 45 * self.brain["prediction"] * extra)
        return future - self.pos

    # panic: dodge sideways and outward, not just straight back
    def panic_target(self, hero):
        # try to move away and slightly perpendicular to hero
        away = self.pos - hero.pos
        if away.length_squared() == 0:
            away = Vector2(-1, -1)

        # add a bit of sideways movement
        side = Vector2(-away.y, away.x).normalize()
        mix = away.normalize() * 0.8 + side * 0.5
        mix.normalize_ip()
        return mix * 180  # strong “get away” impulse

    def update(self, hero, enemies):
        self.choose_state(hero, enemies)

        # reuse previous motive as a “memory” if the state didn’t change much
        if self.state == "seek":
            motive = self.pursue(hero)
        elif self.state == "flank":
            motive = self.flank_target(hero)
        elif self.state == "ambush":
            motive = self.ambush_target(hero)
        else:
            motive = self.panic_target(hero)

        # normalize to desired speed only if non‑zero
        if motive.length_squared() > 0:
            motive = motive.normalize() * self.brain["speed"]

        # separation from other enemies
        separation = self.separation(enemies) * (1.2 + self.brain["pack"] * 0.8)

        # cohesion: gently follow nearby allies
        cohesion = Vector2()
        allies = [e for e in enemies if e is not self and e.pos.distance_to(self.pos) < 150]
        if allies:
            center = sum((e.pos for e in allies), Vector2()) / len(allies)
            cohesion = (center - self.pos)
            if cohesion.length_squared() > 0:
                # weaker than separation so they don’t just clump
                cohesion.scale_to_length(self.brain["speed"] * 0.35 * self.brain["pack"])

        # smooth wandering: small noise to prevent “too perfect” paths
        wander = Vector2(math.cos(self.wander_angle), math.sin(self.wander_angle)) * 0.18
        self.wander_angle += random.uniform(-0.25, 0.25)

        # total steering = all behaviors combined
        steering = (motive + separation + cohesion + wander) - self.vel
        limit(steering, self.brain["force"])
        self.vel += steering
        limit(self.vel, self.brain["speed"])
        self.pos += self.vel

        # clamp to screen bounds
        self.pos.x = clamp(self.pos.x, self.radius, WIDTH - self.radius)
        self.pos.y = clamp(self.pos.y, self.radius, HEIGHT - self.radius)

    def draw(self, surf):
        color = self.brain["color"]
        pygame.draw.circle(surf, color, self.pos, self.radius)
        pygame.draw.circle(surf, STATE_COLORS[self.state], self.pos, self.radius + 4, 2)
        eye = self.vel.normalize() * 7 if self.vel.length_squared() else Vector2(6, 0)
        pygame.draw.circle(surf, (255, 255, 255), self.pos + eye, 3)
        label = small.render(self.brain["type"][0].upper(), True, TEXT)
        surf.blit(label, (self.pos.x - 5, self.pos.y - 9))

def draw_grid(surf):
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surf, GRID, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surf, GRID, (0, y), (WIDTH, y), 1)


def reset_world():
    hero = Victim()
    enemies = [Enemy(i) for i in range(NUM_ENEMIES)]
    for enemy in enemies:
        while enemy.pos.distance_to(hero.pos) < 180:
            enemy.pos = enemy.spawn_position()
    return hero, enemies


hero, enemies = reset_world()
running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                hero, enemies = reset_world()
            elif event.key == pygame.K_m:
                hero.manual_mode = not hero.manual_mode
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                hero.intelligence = min(1.0, hero.intelligence + 0.05)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                hero.intelligence = max(0.0, hero.intelligence - 0.05)

    if hero.alive:
        hero.update(enemies, keys)
        for enemy in enemies:
            enemy.update(hero, enemies)
            if hero.pos.distance_to(enemy.pos) < hero.radius + enemy.radius:
                hero.alive = False

    screen.fill(BG)
    draw_grid(screen)
    for enemy in enemies:
        enemy.draw(screen)
    hero.draw(screen)

    bar_x, bar_y, bar_w, bar_h = 22, 18, 270, 22
    pygame.draw.rect(screen, (55, 58, 74), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
    pygame.draw.rect(screen, ACCENT, (bar_x, bar_y, int(bar_w * hero.intelligence), bar_h), border_radius=8)
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

    lines = [
        f"Victim intelligence: {hero.intelligence:.2f}   (+ / - to change)",
        f"Mode: {'MANUAL' if hero.manual_mode else 'AUTO AI'} (M to toggle)  Survival time: {hero.survival_time:.1f}s   Enemies: {len(enemies)}",
        
        "Goal: avoid collisions with all enemies.",
        "Each enemy has its own brain: aggression, caution, prediction, pack bias, flank bias.",
        "States: seek, flank, ambush, panic. Ring color shows current state.",
        "Enemy letters: H=hunter, F=flanker, T=trickster, C=coward.",
        "Controls: M toggle manual, WASD/Arrows move in manual mode, R reset, Esc quit.",
    ]
    if not hero.alive:
        lines.append("COLLISION! Press R to restart.")

    for i, text in enumerate(lines):
        color = WARN if "COLLISION" in text else TEXT if i < 2 else MUTED
        img = font.render(text, True, color) if i < 2 else small.render(text, True, color)
        screen.blit(img, (22, 54 + i * 27))

    legend_y = HEIGHT - 110
    legends = [
        (STATE_COLORS["seek"], "seek = direct pursuit"),
        (STATE_COLORS["flank"], "flank = side attack"),
        (STATE_COLORS["ambush"], "ambush = predictive intercept"),
        (STATE_COLORS["panic"], "panic = temporary retreat"),
    ]
    for i, (col, txt) in enumerate(legends):
        x = 22 + (i % 2) * 260
        y = legend_y + (i // 2) * 30
        pygame.draw.circle(screen, col, (x, y + 9), 7)
        screen.blit(small.render(txt, True, TEXT), (x + 16, y))

    pygame.display.flip()

pygame.quit()