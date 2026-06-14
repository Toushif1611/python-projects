import math
import random
import pygame
from pygame.math import Vector2

WIDTH, HEIGHT = 1180, 760
FPS = 120
BG = (17, 18, 24)
GRID = (30, 34, 46)
TEXT = (235, 238, 246)
MUTED = (180, 188, 210)
ACCENT = (110, 165, 255)
TRACER_COLOR = (255, 200, 120)
WARN = (255, 215, 105)
HERO_COLOR = (85, 225, 120)
STATE_COLORS = {
    "seek": (239, 92, 92),
    "flank": (255, 160, 70),
    "ambush": (170, 115, 255),
    "panic": (90, 220, 255),
}
BRAIN_TYPES = ["hunter", "flanker", "trickster"]
NUM_ENEMIES = 10
HERO_RADIUS = 16
ENEMY_RADIUS = 13
HERO_MAX_SPEED = 7.0
ENEMY_BASE_SPEED = 3.5
HERO_FORCE = 0.25
ENEMY_FORCE_BASE = 0.15
SAFE_DISTANCE = 150
BULLET_RADIUS = 5
BULLET_SPEED = 1200.0
BULLET_LIFETIME = 2.0
FIRE_DELAY = 0.06
ENEMY_FIRE_MIN = 1.2
ENEMY_FIRE_MAX = 2.0
OBSTACLE_COLOR = (70, 74, 94)
HERO_MAX_HEALTH = 100
HEALTH_BAR_BG = (55, 58, 74)
HEALTH_BAR_FILL = (95, 220, 140)

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


def circle_rect_distance(circle_pos, rect):
    nearest_x = clamp(circle_pos.x, rect.left, rect.right)
    nearest_y = clamp(circle_pos.y, rect.top, rect.bottom)
    return Vector2(circle_pos.x - nearest_x, circle_pos.y - nearest_y)


def circle_rect_collision(circle_pos, radius, rect):
    offset = circle_rect_distance(circle_pos, rect)
    return offset.length_squared() <= (radius * radius)


def resolve_circle_rect_overlap(pos, radius, rect):
    offset = circle_rect_distance(pos, rect)
    dist = offset.length()
    if dist == 0:
        offset = pos - Vector2(rect.center)
        if offset.length_squared() == 0:
            offset = Vector2(1, 0)
        dist = offset.length()
    overlap = radius - dist
    if overlap > 0:
        pos += offset.normalize() * (overlap + 1)
    return pos


def intercept_target(shooter_pos, target_pos, target_vel, speed):
    offset = target_pos - shooter_pos
    a = target_vel.length_squared() - speed * speed
    b = 2 * target_vel.dot(offset)
    c = offset.length_squared()
    if abs(a) < 1e-6:
        if abs(b) < 1e-6:
            return target_pos
        t = c / b
        if t <= 0:
            return target_pos
        return target_pos + target_vel * t

    disc = b * b - 4 * a * c
    if disc < 0:
        return target_pos
    sqrt_disc = math.sqrt(disc)
    times = [(-b - sqrt_disc) / (2 * a), (-b + sqrt_disc) / (2 * a)]
    valid = [t for t in times if t > 0]
    if not valid:
        return target_pos
    return target_pos + target_vel * min(valid)


def line_clear(a, b, obstacles, step=12):
    # return True if segment a->b does not intersect any obstacle (sampled check)
    a = Vector2(a)
    b = Vector2(b)
    dist = a.distance_to(b)
    if dist == 0:
        return True
    steps = max(4, int(dist // step))
    for i in range(1, steps + 1):
        t = i / (steps + 1)
        p = a.lerp(b, t)
        for ob in obstacles:
            if circle_rect_collision(p, 2, ob.rect):
                return False
    return True


def find_nearest_opening(shooter_pos, target_pos, obstacles, sample_interval=16, padding=6):
    # scan obstacle perimeters for candidate openings that have line-of-sight
    best = None
    best_dist = float('inf')
    for ob in obstacles:
        rect = ob.rect
        # sample top and bottom edges
        for x in range(rect.left + padding, rect.right - padding, sample_interval):
            for y in (rect.top - padding, rect.bottom + padding):
                p = Vector2(x, y)
                if line_clear(shooter_pos, p, obstacles) and line_clear(p, target_pos, obstacles):
                    d = shooter_pos.distance_to(p)
                    if d < best_dist:
                        best = p
                        best_dist = d
        # sample left and right edges
        for y in range(rect.top + padding, rect.bottom - padding, sample_interval):
            for x in (rect.left - padding, rect.right + padding):
                p = Vector2(x, y)
                if line_clear(shooter_pos, p, obstacles) and line_clear(p, target_pos, obstacles):
                    d = shooter_pos.distance_to(p)
                    if d < best_dist:
                        best = p
                        best_dist = d
    return best


class Victim:
    def __init__(self):
        self.pos = Vector2(WIDTH / 2, HEIGHT / 2)
        self.vel = Vector2()
        self.radius = HERO_RADIUS
        self.intelligence = 0.60
        self.manual_mode = False
        self.alive = True
        self.survival_time = 0.0
        self.health = HERO_MAX_HEALTH
        self.max_health = HERO_MAX_HEALTH

    def take_damage(self, amount):
        if not self.alive:
            return
        self.health = max(0, self.health - amount)
        if self.health == 0:
            self.alive = False

    def aim_target(self, enemies=None, target_pos=None):
        if target_pos is not None:
            return Vector2(target_pos)

        if not enemies:
            return self.pos + Vector2(1, 0)

        def intercept_time(enemy):
            offset = enemy.pos - self.pos
            a = enemy.vel.length_squared() - BULLET_SPEED * BULLET_SPEED
            b = 2 * enemy.vel.dot(offset)
            c = offset.length_squared()
            if abs(a) < 1e-6:
                if abs(b) < 1e-6:
                    return float("inf")
                t = c / b
                return t if t > 0 else float("inf")
            discriminant = b * b - 4 * a * c
            if discriminant < 0:
                return float("inf")
            sqrt_disc = math.sqrt(discriminant)
            times = [(-b - sqrt_disc) / (2 * a), (-b + sqrt_disc) / (2 * a)]
            valid_times = [t for t in times if t > 0]
            return min(valid_times) if valid_times else float("inf")

        target = min(enemies, key=intercept_time)
        return intercept_target(self.pos, target.pos, target.vel, BULLET_SPEED)

    def shoot(self, target_pos=None, enemies=None):
        aim = self.aim_target(enemies=enemies, target_pos=target_pos)
        direction = Vector2(aim) - self.pos
        if direction.length_squared() == 0:
            direction = Vector2(1, 0)
        start = self.pos + direction.normalize() * (self.radius + BULLET_RADIUS + 2)
        return Bullet(start, direction, owner="hero")

    def avoid_obstacles(self, obstacles):
        steer = Vector2()
        for obstacle in obstacles:
            offset = circle_rect_distance(self.pos, obstacle.rect)
            dist = offset.length()
            if dist == 0:
                offset = self.pos - Vector2(obstacle.rect.center)
                if offset.length_squared() == 0:
                    offset = Vector2(1, 0)
                dist = offset.length()
            if dist < self.radius + 60:
                steer += offset.normalize() * ((self.radius + 60 - dist) / (self.radius + 60)) * 1.8
            if dist < self.radius:
                self.pos = resolve_circle_rect_overlap(self.pos, self.radius, obstacle.rect)
        return steer

    def update(self, enemies, keys, obstacles):
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
        steering += self.avoid_obstacles(obstacles) * 0.18
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

    # ambush: compute an intercept point using enemy speed and approach from the side
    def ambush_target(self, hero):
        # compute intercept time using quadratic formula with enemy speed
        shooter = self.pos
        target_pos = hero.pos
        target_vel = hero.vel
        s = max(0.001, self.brain["speed"])
        offset = target_pos - shooter
        a = target_vel.length_squared() - s * s
        b = 2 * target_vel.dot(offset)
        c = offset.length_squared()
        t = None
        if abs(a) < 1e-6:
            if abs(b) > 1e-6:
                tt = c / b
                if tt > 0:
                    t = tt
        else:
            disc = b * b - 4 * a * c
            if disc >= 0:
                sqrt_disc = math.sqrt(disc)
                times = [(-b - sqrt_disc) / (2 * a), (-b + sqrt_disc) / (2 * a)]
                times = [tt for tt in times if tt > 0]
                if times:
                    t = min(times)

        if t is None:
            # fallback: short predictive intercept in front of hero
            pred = 0.8 + 0.6 * self.brain["prediction"]
            intercept = hero.pos + hero.vel * (25 * pred)
        else:
            intercept = hero.pos + hero.vel * t

        # lateral flank offset so ambusher doesn't approach directly head-on
        to_intercept = intercept - self.pos
        if to_intercept.length_squared() == 0:
            side = Vector2(1, 0)
        else:
            side = Vector2(-to_intercept.y, to_intercept.x).normalize()

        flank_base = 40 + 30 * self.brain.get("flank", 0.6)
        flank_strength = flank_base * (1.2 if self.brain["type"] in ["flanker", "trickster"] else 0.8)
        offset_vec = side * flank_strength * self.brain.get("flank_side", 1)

        ambush_pos = intercept + offset_vec
        return ambush_pos - self.pos

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
        self.fire_timer = random.uniform(ENEMY_FIRE_MIN, ENEMY_FIRE_MAX)

    def update(self, hero, enemies, dt, obstacles):
        self.choose_state(hero, enemies)

        bullet = None
        self.fire_timer = max(0.0, self.fire_timer - dt)
        if self.fire_timer <= 0.0 and hero.alive:
            if self.pos.distance_to(hero.pos) < 520 and self.state != "panic":
                bullet = self.shoot_at(hero)
            self.fire_timer = random.uniform(ENEMY_FIRE_MIN, ENEMY_FIRE_MAX)

        # reuse previous motive as a “memory” if the state didn’t change much
        if self.state == "seek":
            motive = self.pursue(hero)
        elif self.state == "flank":
            motive = self.flank_target(hero)
        elif self.state == "ambush":
            motive = self.ambush_target(hero)
        else:
            motive = self.panic_target(hero)

        # if hero is not visible, attempt to move toward a nearby opening
        try:
            occluded = not line_clear(self.pos, hero.pos, obstacles)
        except Exception:
            occluded = False
        if occluded and self.state in ("seek", "ambush", "flank"):
            opening = find_nearest_opening(self.pos, hero.pos, obstacles)
            if opening is not None:
                motive = opening - self.pos

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

        # improved obstacle avoidance: add a forward lookahead and lateral detour
        obstacle_avoid = Vector2()
        lookahead = 80
        vel_dir = self.vel.normalize() if self.vel.length_squared() else Vector2(1, 0)
        ahead_point = self.pos + vel_dir * (self.radius + lookahead)
        for obstacle in obstacles:
            # basic distance-based avoidance
            offset = circle_rect_distance(self.pos, obstacle.rect)
            dist = offset.length()
            if dist == 0:
                offset = self.pos - Vector2(obstacle.rect.center)
                if offset.length_squared() == 0:
                    offset = Vector2(1, 0)
                dist = offset.length()

            if dist < self.radius + 60:
                obstacle_avoid += offset.normalize() * ((self.radius + 60 - dist) / (self.radius + 60)) * 1.5

            # if an obstacle is detected along the movement direction, add a stronger lateral steer
            if circle_rect_collision(ahead_point, self.radius, obstacle.rect):
                # vector from obstacle center to self, then lateral direction
                center = Vector2(obstacle.rect.center)
                to_center = center - self.pos
                if to_center.length_squared() == 0:
                    lateral = Vector2(-vel_dir.y, vel_dir.x)
                else:
                    lateral = Vector2(-to_center.y, to_center.x).normalize()
                # choose flank side preference when available
                side_mul = self.brain.get("flank_side", 1)
                obstacle_avoid += lateral * side_mul * 2.2 * ((self.radius + lookahead - dist) / (self.radius + lookahead))

            # if overlapping, nudge out
            if dist < self.radius:
                self.pos = resolve_circle_rect_overlap(self.pos, self.radius, obstacle.rect)

        # total steering = all behaviors combined
        steering = (motive + separation + cohesion + wander + obstacle_avoid) - self.vel
        limit(steering, self.brain["force"])
        self.vel += steering
        limit(self.vel, self.brain["speed"])
        self.pos += self.vel

        # clamp to screen bounds
        self.pos.x = clamp(self.pos.x, self.radius, WIDTH - self.radius)
        self.pos.y = clamp(self.pos.y, self.radius, HEIGHT - self.radius)
        return bullet

    def draw(self, surf):
        color = self.brain["color"]
        pygame.draw.circle(surf, color, self.pos, self.radius)
        pygame.draw.circle(surf, STATE_COLORS[self.state], self.pos, self.radius + 4, 2)
        eye = self.vel.normalize() * 7 if self.vel.length_squared() else Vector2(6, 0)
        pygame.draw.circle(surf, (255, 255, 255), self.pos + eye, 3)
        label = small.render(self.brain["type"][0].upper(), True, TEXT)
        surf.blit(label, (self.pos.x - 5, self.pos.y - 9))


    def shoot_at(self, hero):
        direction = hero.pos - self.pos
        if direction.length_squared() == 0:
            direction = Vector2(1, 0)
        start = self.pos + direction.normalize() * (self.radius + BULLET_RADIUS + 2)
        return Bullet(start, direction, owner="enemy")


def draw_grid(surf):
    for x in range(0, WIDTH, 40):
        pygame.draw.line(surf, GRID, (x, 0), (x, HEIGHT), 1)
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(surf, GRID, (0, y), (WIDTH, y), 1)


class Bullet:
    def __init__(self, pos, direction, owner="hero"):
        self.pos = Vector2(pos)
        self.start = Vector2(pos)
        self.prev_pos = Vector2(pos)
        self.vel = direction.normalize() * BULLET_SPEED if direction.length_squared() else Vector2(BULLET_SPEED, 0)
        self.radius = BULLET_RADIUS
        self.life = BULLET_LIFETIME
        self.flash_time = 0.08
        self.alive = True
        self.owner = owner

    def update(self, dt, obstacles=None):
        self.prev_pos = Vector2(self.pos)
        self.pos += self.vel * dt
        self.life -= dt
        self.flash_time = max(0.0, self.flash_time - dt)
        if self.life <= 0:
            self.alive = False
        if (
            self.pos.x < -self.radius or self.pos.x > WIDTH + self.radius or
            self.pos.y < -self.radius or self.pos.y > HEIGHT + self.radius
        ):
            self.alive = False
        if obstacles:
            for obstacle in obstacles:
                if circle_rect_collision(self.pos, self.radius, obstacle.rect):
                    self.alive = False
                    break

    def draw(self, surf):
        if self.prev_pos.distance_to(self.pos) > 0:
            pygame.draw.line(surf, TRACER_COLOR, self.prev_pos, self.pos, 6)
            pygame.draw.line(surf, ACCENT, self.prev_pos, self.pos, 3)
        pygame.draw.circle(surf, (255, 255, 255), self.pos, self.radius)
        if self.flash_time > 0:
            flash_radius = int(6 + self.flash_time * 25)
            pygame.draw.circle(surf, (255, 220, 140), self.start, flash_radius)
            pygame.draw.circle(surf, (255, 255, 255), self.start, max(2, flash_radius // 3))


class Obstacle:
    def __init__(self, rect):
        self.rect = rect

    def draw(self, surf):
        pygame.draw.rect(surf, OBSTACLE_COLOR, self.rect, border_radius=6)
        pygame.draw.rect(surf, (255, 255, 255), self.rect, 2, border_radius=6)


def create_house_layout():
    rects = [
        # outer walls with openings
        pygame.Rect(220, 140, 740, 24),
        pygame.Rect(220, 596, 325, 24),
        pygame.Rect(635, 596, 325, 24),
        pygame.Rect(220, 140, 24, 480),
        pygame.Rect(936, 140, 24, 480),

        # inner partitions with door openings
        pygame.Rect(450, 140, 24, 180),
        pygame.Rect(700, 140, 24, 180),
        pygame.Rect(400, 320, -180, -24),
        pygame.Rect(653, 320, -180, -24),
        pygame.Rect(790, 260, 90, 24),
        pygame.Rect(570, 456, 100, 24),
        pygame.Rect(400, 456, 100, 24),
        pygame.Rect(800, 456, 90, 24),
        pygame.Rect(790, 456, 24, 165),
    ]
    return [Obstacle(rect) for rect in rects]


def reset_world():
    hero = Victim()
    enemies = [Enemy(i) for i in range(NUM_ENEMIES)]
    obstacles = create_house_layout()
    for enemy in enemies:
        while enemy.pos.distance_to(hero.pos) < 180 or any(circle_rect_collision(enemy.pos, enemy.radius, o.rect) for o in obstacles):
            enemy.pos = enemy.spawn_position()
    return hero, enemies, obstacles


def process_events(hero, enemies, bullets, fire_timer):
    keys = pygame.key.get_pressed()
    running = True
    reset_requested = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                reset_requested = True
            elif event.key == pygame.K_m:
                hero.manual_mode = not hero.manual_mode
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                hero.intelligence = min(1.0, hero.intelligence + 0.05)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                hero.intelligence = max(0.0, hero.intelligence - 0.05)
            elif event.key == pygame.K_SPACE and hero.alive and fire_timer <= 0.0:
                target = pygame.mouse.get_pos() if hero.manual_mode else None
                bullets.append(hero.shoot(target_pos=target, enemies=enemies if not hero.manual_mode else None))
                fire_timer = FIRE_DELAY
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hero.alive and hero.manual_mode and fire_timer <= 0.0:
                bullets.append(hero.shoot(target_pos=event.pos))
                fire_timer = FIRE_DELAY

    return keys, fire_timer, running, reset_requested


def resolve_bullet_collisions(hero, enemies, bullets):
    active_bullets = []
    for bullet in bullets:
        if not bullet.alive:
            continue

        if bullet.owner == "hero":
            for enemy in enemies:
                if bullet.pos.distance_to(enemy.pos) < bullet.radius + enemy.radius:
                    bullet.alive = False
                    enemies.remove(enemy)
                    break
        elif hero.alive and bullet.pos.distance_to(hero.pos) < bullet.radius + hero.radius:
            bullet.alive = False
            hero.take_damage(10)

        if bullet.alive:
            active_bullets.append(bullet)

    return active_bullets


def draw_hud(surf, hero, enemies, bullets, obstacles):
    surf.fill(BG)
    draw_grid(surf)
    for obstacle in obstacles:
        obstacle.draw(surf)
    for enemy in enemies:
        enemy.draw(surf)
    for bullet in bullets:
        bullet.draw(surf)
    hero.draw(surf)

    bar_x, bar_y, bar_w, bar_h = 22, 18, 270, 22
    pygame.draw.rect(surf, HEALTH_BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=8)
    pygame.draw.rect(
        surf,
        HEALTH_BAR_FILL,
        (bar_x, bar_y, int(bar_w * (hero.health / hero.max_health)), bar_h),
        border_radius=8,
    )
    pygame.draw.rect(surf, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

    lines = [
        f"Health: {int(hero.health)}/{hero.max_health}   Intelligence: {hero.intelligence:.2f}   (+ / - to change)",
        f"Mode: {'MANUAL' if hero.manual_mode else 'AUTO AI'} (M to toggle)  Survival time: {hero.survival_time:.1f}s   Enemies: {len(enemies)}  Bullets: {len(bullets)}",
        "Goal: avoid collisions with all enemies.",
        "Press SPACE to fire bullets.",
        "Each enemy has its own brain: aggression, caution, prediction, pack bias, flank bias.",
        "States: seek, flank, ambush, panic. Ring color shows current state.",
        "Enemy letters: H=hunter, F=flanker, T=trickster.",
        "Controls: M toggle manual, WASD/Arrows move in manual mode, R reset, Esc quit.",
    ]
    if not hero.alive:
        lines.append("COLLISION! Press R to restart.")

    for i, text in enumerate(lines):
        color = WARN if "COLLISION" in text else TEXT if i < 2 else MUTED
        img = font.render(text, True, color) if i < 2 else small.render(text, True, color)
        surf.blit(img, (22, 54 + i * 27))

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
        pygame.draw.circle(surf, col, (x, y + 9), 7)
        surf.blit(small.render(txt, True, TEXT), (x + 16, y))


hero, enemies, obstacles = reset_world()
bullets = []
hero_fire_timer = 0.0
running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    hero_fire_timer = max(0.0, hero_fire_timer - dt)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_r:
                hero, enemies, obstacles = reset_world()
            elif event.key == pygame.K_m:
                hero.manual_mode = not hero.manual_mode
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                hero.intelligence = min(1.0, hero.intelligence + 0.05)
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                hero.intelligence = max(0.0, hero.intelligence - 0.05)
            elif event.key == pygame.K_SPACE and hero.alive:
                if hero_fire_timer <= 0.0:
                    target = pygame.mouse.get_pos() if hero.manual_mode else None
                    bullets.append(hero.shoot(target_pos=target, enemies=enemies if not hero.manual_mode else None))
                    hero_fire_timer = FIRE_DELAY
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if hero.alive and hero.manual_mode and hero_fire_timer <= 0.0:
                bullets.append(hero.shoot(target_pos=event.pos))
                hero_fire_timer = FIRE_DELAY

    if hero.alive:
        hero.update(enemies, keys, obstacles)
        for enemy in enemies:
            new_bullet = enemy.update(hero, enemies, dt, obstacles)
            if new_bullet is not None:
                bullets.append(new_bullet)

        for enemy in enemies:
            if hero.pos.distance_to(enemy.pos) < hero.radius + enemy.radius:
                hero.take_damage(28)
                enemy.pos = enemy.spawn_position()
                while enemy.pos.distance_to(hero.pos) < 180:
                    enemy.pos = enemy.spawn_position()
                if not hero.alive:
                    break

    for bullet in bullets:
        bullet.update(dt, obstacles)

    for bullet in bullets:
        if not bullet.alive:
            continue
        if bullet.owner == "hero":
            for enemy in enemies:
                if bullet.pos.distance_to(enemy.pos) < bullet.radius + enemy.radius:
                    bullet.alive = False
                    enemies.remove(enemy)
                    break
        else:
            if hero.alive and bullet.pos.distance_to(hero.pos) < bullet.radius + hero.radius:
                bullet.alive = False
                hero.take_damage(10)

    bullets = [bullet for bullet in bullets if bullet.alive]

    screen.fill(BG)
    draw_grid(screen)
    for obstacle in obstacles:
        obstacle.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    for bullet in bullets:
        bullet.draw(screen)
    hero.draw(screen)

    bar_x, bar_y, bar_w, bar_h = 22, 18, 270, 22
    pygame.draw.rect(screen, HEALTH_BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=8)
    pygame.draw.rect(
        screen,
        HEALTH_BAR_FILL,
        (bar_x, bar_y, int(bar_w * (hero.health / hero.max_health)), bar_h),
        border_radius=8,
    )
    pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

    lines = [
        f"Health: {int(hero.health)}/{hero.max_health}   Intelligence: {hero.intelligence:.2f}   (+ / - to change)",
        f"Mode: {'MANUAL' if hero.manual_mode else 'AUTO AI'} (M to toggle)  Survival time: {hero.survival_time:.1f}s   Enemies: {len(enemies)}  Bullets: {len(bullets)}",
        
        "Goal: avoid collisions with all enemies.",
        "Press SPACE to fire bullets.",
        "Each enemy has its own brain: aggression, caution, prediction, pack bias, flank bias.",
        "States: seek, flank, ambush, panic. Ring color shows current state.",
        "Enemy letters: H=hunter, F=flanker, T=trickster.",
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