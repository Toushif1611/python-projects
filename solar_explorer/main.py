import pygame, math, random, sys, os

pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(6)

CH_THRUST = pygame.mixer.Channel(0)
CH_SHOOT = pygame.mixer.Channel(1)
CH_HIT   = pygame.mixer.Channel(2)
CH_EXP   = pygame.mixer.Channel(3)
CH_LAND  = pygame.mixer.Channel(4)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
thrust_path = os.path.join(BASE_DIR, "sounds", "thrust.wav")
shoot_path = os.path.join(BASE_DIR, "sounds", "shoot.wav")
explosion_path = os.path.join(BASE_DIR, "sounds", "explosion.wav")
land_path = os.path.join(BASE_DIR, "sounds", "land.wav")
boss_path = os.path.join(BASE_DIR, "sounds", "boss_hit.wav")
mob_path = os.path.join(BASE_DIR, "sounds", "mob_hit.wav")

thrust_sound = pygame.mixer.Sound(thrust_path)
explosion_sound = pygame.mixer.Sound(explosion_path)
land_sound = pygame.mixer.Sound(land_path)
shoot_sound = pygame.mixer.Sound(shoot_path)
boss_sound = pygame.mixer.Sound(boss_path)
mob_sound = pygame.mixer.Sound(mob_path)

shoot_sound.set_volume(0.4)
explosion_sound.set_volume(0.6)
land_sound.set_volume(0.5)
thrust_sound.set_volume(0.4)
mob_sound.set_volume(0.35)
boss_sound.set_volume(0.6)

WIDTH, HEIGHT = 800,800
screen = pygame.display.set_mode((WIDTH,HEIGHT))
clock = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_DIR, "images")

ship_img = pygame.image.load(os.path.join(IMG_DIR, "ship.png")).convert_alpha()
mob_imgs = [
    pygame.image.load(os.path.join(IMG_DIR, "mob1.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "mob2.png")).convert_alpha()
]

boss_imgs = [
    pygame.image.load(os.path.join(IMG_DIR, "boss1.png")).convert_alpha(),
    pygame.image.load(os.path.join(IMG_DIR, "boss2.png")).convert_alpha()
]

mob_imgs = [pygame.transform.scale(i, (30,30)) for i in mob_imgs]
boss_imgs = [pygame.transform.scale(i, (90,90)) for i in boss_imgs]


ship_img = pygame.transform.scale(ship_img, (40,40))

WHITE=(255,255,255);BLACK=(0,0,0);RED=(255,60,60);YELLOW=(255,200,0)

font=pygame.font.SysFont("Arial",20)
big=pygame.font.SysFont("Arial",60)

# ================= CAMERA =================
camera_scale=1
target_scale=1
MIN_ZOOM=.45
MAX_ZOOM=1

# ================= STARS =================
stars = []
for _ in range(120):
    stars.append([random.randint(0,WIDTH), random.randint(0,HEIGHT), random.randint(1,3)])

# ================= PLANETS =================
planets=[
("Mercury",(180,180,180),80,6,.04,30),
("Venus",(255,150,0),120,8,.035,35),
("Earth",(0,120,255),160,9,.03,40),
("Mars",(255,70,70),200,7,.028,38),
("Jupiter",(200,170,120),260,14,.02,60),
("Saturn",(240,210,120),320,12,.018,55),
("Uranus",(160,255,255),380,10,.015,50),
("Neptune",(80,80,255),440,10,.012,50)
]

angles=[0]*8

# ================= SHIP =================
ship_pos=pygame.Vector2(0,-200)
ship_angle=-90
ship_radius=14

# ================= LANDER =================
lander_pos=pygame.Vector2(0,0)
lander_angle=-90
planet_cam=pygame.Vector2(0,0)
lander_radius=10

# ================= STATS =================
health = 100
score = 0
hit_timer = 0   # damage cooldown
fuel = 100
MAX_FUEL = 100
sound_hit_cd = 0
sound_exp_cd = 0
boss_spawned = False
boss_alive = False
boss_defeated_timer = 0
fireworks = []
asteroid_hit_timer = 0
boss_spawn_delay = 0
boss_fought = False
difficulty = 1
boss_level = 1
last_boss_score = 0
anim_tick = 0

# ================= STATE =================
scene = "solar"
current_planet=None
game_over=False
taking_off=False
launch_height=0
rapid_timer = 0
boss_warning = 0
switching_scene = False
respawn_lock = False

# ================= BULLETS =================
bullets=[]
boss_bullets = []
boss_shoot_timer = 0
NORMAL_FIRE_DELAY = 8
fire_delay = NORMAL_FIRE_DELAY
fire_timer = 0 

# ================= MOB =================
class Mob:
    def __init__(self,color,level=1,is_boss=False):
        self.is_boss = is_boss
        self.color = color
        self.level = level

        if self.is_boss:
            self.max_hp = 600 + difficulty * 180 + boss_level * 150
            self.radius = 45 + difficulty * 2
            self.speed = 1 + difficulty * 0.15

        else:
            self.max_hp = 40 + level * 25 + difficulty * 15
            self.radius = 14 + level
            self.speed = 1.0 + level * 0.25 + difficulty * 0.05

        self.fade = 255
        self.dead = False

        # -------------------------------
        # Create a base surface for drawing once
        size = self.radius * 2 + 4
        self.base_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            self.base_surf,
            color + (255,),
            (size//2, size//2),
            self.radius
        )

        # -------------------------------

        self.respawn(lander_pos.copy())
        self.spawn_timer = 60   # 1 second freeze
        self.dash_timer = 0
        self.approach_phase = True
        self.shoot_timer = 0

    def respawn(self, center):
        if self.is_boss:
            SAFE_DISTANCE = 420
            MAX_RANGE = 650

            while True:
                angle = random.uniform(0, math.tau)
                dist = random.uniform(SAFE_DISTANCE, MAX_RANGE)

                self.pos = center + pygame.Vector2(
                    math.cos(angle) * dist,
                    math.sin(angle) * dist
                )

                if SAFE_DISTANCE <= self.pos.distance_to(center) <= MAX_RANGE:
                    break

        else:
            SAFE_DISTANCE = 180
            while True:
                self.pos = pygame.Vector2(
                    random.randint(-350, 350),
                    random.randint(-350, 350)
                )
                if self.pos.distance_to(center) > SAFE_DISTANCE:
                    break

        self.hp = self.max_hp
        self.dead = False
        self.fade = 255
        if self.is_boss:
            self.spawn_timer = 60   # freeze every time boss appears
            self.approach_phase = True

    def update(self, target):

        if self.dead:
            return

        # ABSOLUTE SPAWN PROTECTION
        if self.is_boss and self.spawn_timer > 0:
            self.spawn_timer -= 1
            return  # stay still after spawn

        d = target - self.pos
        dist = d.length()

        if self.is_boss:

            hp_ratio = self.hp / self.max_hp

            # ===== PHASE 1 (Above 50%) =====
            if hp_ratio > 0.5:
                self.speed = 1.5
                shoot_delay = 45

            # ===== PHASE 2 (Rage Mode) =====
            else:
                self.speed = 2.4
                shoot_delay = 25   # faster shooting

            if dist != 0:
                direction = d.normalize()

                # --- Smart spacing ---
                if dist > 250:
                    self.pos += direction * self.speed
                elif dist > 90:
                    self.pos += direction.rotate(60) * 1.2
                else:
                    # rage smash
                    self.pos += direction * (self.speed * 3)

            # --- Predict player movement ---
            future_pos = target + direction * 20
            shoot_dir = (future_pos - self.pos)
            if shoot_dir.length() != 0:
                shoot_dir = shoot_dir.normalize()

            # --- Shooting ---
            self.shoot_timer += 1
            if self.shoot_timer >= shoot_delay:
                self.shoot_timer = 0

                pattern = random.choice(["single","spread","spiral"])

                if pattern == "single":
                    boss_bullets.append([self.pos.copy(), shoot_dir * 7])

                elif pattern == "spread":
                    for ang in (-20,0,20):
                        boss_bullets.append([self.pos.copy(), shoot_dir.rotate(ang) * 6])

                elif pattern == "spiral":
                    angle = pygame.time.get_ticks() / 5
                    vec = pygame.Vector2(1,0).rotate(angle)
                    boss_bullets.append([self.pos.copy(), vec * 5])

        else:
            if dist != 0:
                direction = d.normalize()

                # ---- AGGRESSION ZONE ----
                attack_range = 140
                collision_range = 60   # when very close → ram player

                if dist > attack_range:
                    # approach player
                    self.pos += direction * self.speed

                elif dist > collision_range:
                    # circle while closing in
                    self.pos += direction.rotate(45) * self.speed * 1.2

                else:
                    # FINAL RAM MODE (guaranteed collision)
                    self.pos += direction * (self.speed * 2)

                # ---- BULLET DODGE (only when far enough) ----
                if dist > collision_range:
                    for b in bullets:
                        if self.pos.distance_to(b[0]) < 60:
                            dodge_dir = (self.pos - b[0]).normalize()
                            self.pos += dodge_dir * 3

    def hit(self,damage):
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True

    def kill(self):
        self.dead = True

    def draw(self, cam):
        p = self.pos - cam + pygame.Vector2(WIDTH//2, HEIGHT//2)

        frame = (anim_tick // 15) % 2   # change every 10 frames

        if self.is_boss:
            img = boss_imgs[frame]
        else:
            img = mob_imgs[frame]

        img_fade = img.copy()
        img_fade.set_alpha(self.fade)

        rect = img_fade.get_rect(center=p)
        screen.blit(img_fade, rect)

        # Death fade
        if self.dead:
            self.fade -= 12
            if self.fade <= 0:
                if not self.is_boss:
                    self.respawn(lander_pos.copy())
                else:
                    return   # boss fully gone

        # Health bar
        if not self.dead:
            bar_w = 80 if self.is_boss else 32
            ratio = self.hp / self.max_hp
            pygame.draw.rect(screen, RED, (p.x - bar_w//2, p.y-30, bar_w, 5))
            pygame.draw.rect(screen, (0,255,0), (p.x - bar_w//2, p.y-30, bar_w * ratio, 5))

def spawn_mobs(name):
    level = ["Mercury","Venus","Earth","Mars","Jupiter","Saturn","Uranus","Neptune"].index(name)+1
    colors={
    "Mercury":(200,200,200),"Venus":(255,150,0),"Earth":(0,255,0),
    "Mars":(255,80,80),"Jupiter":(200,160,120),"Saturn":(255,220,120),
    "Uranus":(150,255,255),"Neptune":(100,100,255)}

    count = 3 + level + difficulty
    return [Mob(colors[name], level + difficulty//2) for _ in range(count)]


mobs=[]
# ================= EXPLOSIONS =================
explosions = []

def spawn_firework():
    return [pygame.Vector2(random.randint(0,WIDTH), random.randint(0,HEIGHT)),
            random.randint(20,40)]

# ================= ENVIRONMENT =================
env_particles=[]

# -------- POWER UPS --------
# outside loop, initialize once
planet_powerups = []

# ================= ASTEROIDS =================
asteroids = [pygame.Vector2(random.randint(-600,600), random.randint(-600,600)) for _ in range(14)]
asteroid_vel = [pygame.Vector2(random.uniform(-1.2,1.2),random.uniform(-1.2,1.2)) for _ in asteroids]

def reset_game():
    global score, health, fuel, scene, game_over
    global mobs, bullets, boss_bullets, explosions, fireworks
    global boss_alive, boss_spawned, boss_fought, boss_defeated_timer
    global difficulty, boss_level
    global ship_pos, ship_angle
    global lander_pos, planet_cam
    global camera_scale, target_scale
    global env_particles, planet_powerups
    global hit_timer, asteroid_hit_timer
    global land_key_lock, taking_off, launch_height

    # ---- stop looping sounds ----
    CH_THRUST.stop()

    # ---- stats ----
    score = 0
    health = 100
    fuel = MAX_FUEL
    difficulty = 1
    boss_level = 1

    # ---- positions ----
    ship_pos = pygame.Vector2(0, -200)
    ship_angle = -90

    lander_pos = pygame.Vector2(0, 0)
    planet_cam = pygame.Vector2(0, 0)

    camera_scale = 1
    target_scale = 1

    # ---- clear lists ----
    mobs.clear()
    bullets.clear()
    boss_bullets.clear()
    explosions.clear()
    fireworks.clear()
    env_particles.clear()
    planet_powerups.clear()

    # ---- flags ----
    boss_alive = False
    boss_spawned = False
    boss_fought = False
    boss_defeated_timer = 0

    hit_timer = 0
    asteroid_hit_timer = 0

    land_key_lock = False
    taking_off = False
    launch_height = 0

    scene = "solar"
    game_over = False

# ================= HELPERS =================
def world(pos):
    return pygame.Vector2(WIDTH//2+pos.x*camera_scale,HEIGHT//2+pos.y*camera_scale)

def hud(txt,y):
    screen.blit(font.render(txt,1,WHITE),(10,y))

land_key_lock = False

# ================= LOOP =================
while True:
    clock.tick(60)
    anim_tick += 1

    if sound_hit_cd > 0:
        sound_hit_cd -= 1
    if sound_exp_cd > 0:
        sound_exp_cd -= 1

    for e in pygame.event.get():
        if e.type==pygame.QUIT: sys.exit()

    keys=pygame.key.get_pressed()

    # ===== BOSS SCORE TRIGGER (MULTIPLES OF 200) =====
    if score >= 200 and score % 200 == 0 and score != last_boss_score:
        last_boss_score = score
        boss_spawned = True
        boss_warning = 120
        boss_spawn_delay = 120

    # ===== DIFFICULTY SCALING =====
    difficulty = 1 + score // 150
    difficulty = min(difficulty, 15)   # cap so it doesn't go insane

    if game_over:
        screen.fill(BLACK)
        screen.blit(big.render("GAME OVER",1,RED),(220,330))
        screen.blit(font.render("Press R to Respawn",1,WHITE),(290,410))

        if keys[pygame.K_r] and not respawn_lock:
            reset_game()
            respawn_lock = True

        if not keys[pygame.K_r]:
            respawn_lock = False

        pygame.display.update()
        continue

        if pygame.mouse.get_pressed()[0]:
            ship_pos = pygame.Vector2(0, -200)
            ship_angle = -90

            lander_pos = pygame.Vector2(0, 0)
            planet_cam = pygame.Vector2(0, 0)

            camera_scale = target_scale = 1

            health = 100
            score = 0
            hit_timer = 0

            bullets.clear()
            mobs.clear()

            scene = "solar"
            taking_off = False
            launch_height = 0
            game_over = False

        pygame.display.update()
        continue

    # ================= PLANET =================
    if scene=="planet":
        pygame.display.set_caption(current_planet[0])
        screen.fill(current_planet[1])
        # ---- planet environment ----
        # -------- PLANET ENVIRONMENTS --------

        if current_planet[0] == "Mercury":
            if random.random() < 0.4:
                env_particles.append([random.randint(0,WIDTH), random.randint(0,HEIGHT), random.uniform(-2,2)])

            for p in env_particles[:]:
                p[0] += p[2]
                pygame.draw.circle(screen,(255,200,100),(int(p[0]),int(p[1])),2)
                if p[0]<0 or p[0]>WIDTH:
                    env_particles.remove(p)

        elif current_planet[0] == "Venus":
            if random.random() < 0.3:
                env_particles.append([random.randint(0,WIDTH), 0])

            for p in env_particles[:]:
                p[1] += 4
                pygame.draw.circle(screen,(220,180,0),p,4)
                if p[1] > HEIGHT:
                    env_particles.remove(p)

        elif current_planet[0] == "Earth":
            if random.random() < 0.15:
                env_particles.append([0, random.randint(0,HEIGHT)])

            for p in env_particles[:]:
                p[0] += 2
                pygame.draw.circle(screen,(220,220,255),p,3)
                if p[0] > WIDTH:
                    env_particles.remove(p)

        elif current_planet[0] == "Mars":
            if random.random() < 0.5:
                env_particles.append([0, random.randint(0,HEIGHT)])

            for p in env_particles[:]:
                p[0] += 5
                pygame.draw.circle(screen,(255,100,100),p,3)
                if p[0] > WIDTH:
                    env_particles.remove(p)

        elif current_planet[0] == "Jupiter":
            if random.random() < 0.3:
                env_particles.append([WIDTH//2, HEIGHT//2, random.uniform(0,6)])

            for p in env_particles[:]:
                angle = p[2]
                p[0] += math.cos(angle)*3
                p[1] += math.sin(angle)*3
                pygame.draw.circle(screen,(200,160,120),(int(p[0]),int(p[1])),3)
                if abs(p[0]-WIDTH//2)>400:
                    env_particles.remove(p)

        elif current_planet[0] == "Saturn":
            if random.random() < 0.25:
                env_particles.append([random.randint(0,WIDTH), HEIGHT//2])

            for p in env_particles[:]:
                p[1] += random.uniform(-1,1)
                pygame.draw.circle(screen,(255,220,150),p,2)
                if p[1]<0 or p[1]>HEIGHT:
                    env_particles.remove(p)

        elif current_planet[0] == "Uranus":
            if random.random() < 0.4:
                env_particles.append([0, random.randint(0,HEIGHT)])

            for p in env_particles[:]:
                p[0] += 6
                pygame.draw.circle(screen,(150,255,255),p,2)
                if p[0] > WIDTH:
                    env_particles.remove(p)

        elif current_planet[0] == "Neptune":
            if random.random() < 0.35:
                env_particles.append([random.randint(0,WIDTH), random.randint(0,HEIGHT)])

            for p in env_particles[:]:
                pygame.draw.circle(screen,(80,80,255),p,2)

        # limit particles to avoid lag
        if len(env_particles) > 300:
            env_particles = env_particles[-300:]

        d=pygame.Vector2(math.cos(math.radians(lander_angle)),math.sin(math.radians(lander_angle)))

        if not taking_off:
            if keys[pygame.K_w]: lander_pos+=d*2.5
            if keys[pygame.K_s]: lander_pos-=d*2.5
            if keys[pygame.K_a]: lander_angle-=3
            if keys[pygame.K_d]: lander_angle+=3

        lander_screen=lander_pos-planet_cam+pygame.Vector2(WIDTH//2,HEIGHT//2)

        # camera boundary move
        margin = 120

        # FIX: Smooth camera instead of jump
        cam_speed = 0.1  # smaller = smoother
        if lander_screen.x < margin:
            planet_cam.x -= (margin - lander_screen.x) * cam_speed
        if lander_screen.x > WIDTH - margin:
            planet_cam.x += (lander_screen.x - (WIDTH - margin)) * cam_speed
        if lander_screen.y < margin:
            planet_cam.y -= (margin - lander_screen.y) * cam_speed
        if lander_screen.y > HEIGHT - margin:
            planet_cam.y += (lander_screen.y - (HEIGHT - margin)) * cam_speed


        # shooting
        if keys[pygame.K_SPACE] and not taking_off:
            fire_timer+=1
            if fire_timer>=fire_delay:
                bullets.append([lander_pos.copy(),d*6])
                CH_SHOOT.play(shoot_sound)
                fire_timer=0
        else:
            fire_timer = 0

        if rapid_timer > 0:
            rapid_timer -= 1
            fire_delay = 3
        else:
            fire_delay = NORMAL_FIRE_DELAY

        # -------- bullets --------
        # FIX: Avoid removing items while iterating
        to_remove = []
        for b in bullets:
            b[0] += b[1]
            if b[0].distance_to(lander_pos) > 800:
                to_remove.append(b)
                continue

            hit = False
            for m in mobs:
                if not m.dead and b[0].distance_to(m.pos) < m.radius + 3:
                    m.hit(20)

                    if sound_hit_cd == 0:
                        if m.is_boss:
                            CH_HIT.play(boss_sound)
                        else:
                            CH_HIT.play(mob_sound)
                        sound_hit_cd = 6

                    explosions.append([m.pos.copy(), 20])
                    # score ONLY if mob just died
                    if m.dead:
                        if sound_exp_cd == 0:
                            CH_EXP.play(explosion_sound)
                            sound_exp_cd = 10

                        if m.is_boss:
                            score += 100
                            boss_alive = False
                            boss_defeated_timer = 180
                            boss_bullets.clear()
                        else:
                            score += 10

                    hit = True
                    break

            if hit:
                to_remove.append(b)

        for b in to_remove:
            if b in bullets:
                bullets.remove(b)

        # -------- mobs --------
        if hit_timer > 0:
            hit_timer -= 1

        # ======== CINEMATIC BOSS SPAWN ========
        if boss_spawned and not boss_alive and boss_spawn_delay > 0:
            boss_spawn_delay -= 1

            if boss_spawn_delay == 0:
                # Remove all regular mobs
                mobs = [m for m in mobs if m.is_boss]

                # Create boss
                boss = Mob((255,0,255),8 + boss_level, True)
                boss.respawn(lander_pos.copy())

                mobs.append(boss)
                boss_alive = True
                boss_fought = True

        for m in mobs:
            m.update(lander_pos)
            m.draw(planet_cam)

            if not m.dead and m.pos.distance_to(lander_pos) < m.radius + lander_radius:
                if hit_timer == 0:
                    health -= 5
                    if sound_exp_cd == 0:
                        CH_EXP.play(explosion_sound)
                        sound_exp_cd = 10

                    hit_timer = 30   # ~0.5 second delay
                    if not m.is_boss:
                        m.kill()    # 👈 mob disappears with fade animation
                    # after bullets hit mobs loop
                    if m.is_boss and m.dead:
                        boss_alive = False
                        boss_defeated_timer = 180  # 3 seconds fireworks
                        boss_bullets.clear()

                    if health <= 0:
                        game_over = True

        # -------- slow regen --------
        if random.random() < 0.002:
            health = min(100, health + 5)

        for b in bullets:
            p=b[0]-planet_cam+pygame.Vector2(WIDTH//2,HEIGHT//2)
            pygame.draw.circle(screen,WHITE,p,3)

        # ===== BOSS BULLETS =====
        to_remove = []

        for bb in boss_bullets:
            bb[0] += bb[1]

            # remove far bullets
            if bb[0].distance_to(lander_pos) > 900:
                to_remove.append(bb)
                continue

            # hit lander
            if bb[0].distance_to(lander_pos) < lander_radius + 5:
                if hit_timer == 0:
                    health -= 6 + difficulty
                    if sound_exp_cd == 0:
                        CH_EXP.play(explosion_sound)
                        sound_exp_cd = 10

                    hit_timer = 25
                to_remove.append(bb)

        for bb in to_remove:
            if bb in boss_bullets:
                boss_bullets.remove(bb)

        # ===== GAME OVER CHECK =====
        if health <= 0:
            health = 0

        # draw them
        for bb in boss_bullets:
            p = bb[0] - planet_cam + pygame.Vector2(WIDTH//2, HEIGHT//2)
            pygame.draw.circle(screen, (255,80,80), p, 5)

        # inside planet loop
        if random.random() < 0.001:
            planet_powerups.append({
                "pos": pygame.Vector2(random.randint(-300,300), random.randint(-300,300)),
                "type": random.choice(["health","fuel","rapid"])
            })

        if len(planet_powerups) > 10:
            planet_powerups.pop(0)

        # draw and check collection
        for pu in planet_powerups[:]:
            p = pu["pos"] - planet_cam + pygame.Vector2(WIDTH//2, HEIGHT//2)
            pygame.draw.circle(screen, (0,255,255), p, 8)

            if lander_pos.distance_to(pu["pos"]) < 15:
                if pu["type"] == "health":
                    health = min(100, health + 25)
                elif pu["type"] == "fuel":
                    fuel = min(MAX_FUEL, fuel + 30)
                elif pu["type"] == "rapid":
                    rapid_timer += 300   # 5 seconds approx
                planet_powerups.remove(pu)  # remove after collection

        # lander
        tip=lander_screen+d*15
        left=lander_screen+d.rotate(140)*10
        right=lander_screen+d.rotate(-140)*10
        pygame.draw.polygon(screen,WHITE,[tip,left,right])

        # take off animation
        if keys[pygame.K_b] and not taking_off:
            taking_off=True

        if taking_off:
            launch_height += 6
            lander_pos.y -= 6

            if launch_height > 300:
                scene = "solar"

                # reset planet camera & lander
                lander_pos = pygame.Vector2(0,0)
                planet_cam = pygame.Vector2(0,0)

                # allow landing again
                land_key_lock = False
                current_planet = None

                # DO NOT reset boss_spawned here ❗
                boss_alive = False

                camera_scale = target_scale = 1
                taking_off = False
                launch_height = 0

        hud(f"Lander X:{int(lander_pos.x)} Y:{int(lander_pos.y)}",10)
        hud(f"Health: {health}",35)
        hud(f"Score: {score}",60)

        if boss_alive:
            boss = next(m for m in mobs if m.is_boss)
            bar_width = 400
            bar_x = WIDTH//2 - bar_width//2
            bar_y = 20

            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, 18))
            hp_ratio = boss.hp / boss.max_hp
            pygame.draw.rect(screen, (0,255,0), (bar_x, bar_y, bar_width * hp_ratio, 18))

            label = font.render("BOSS", True, WHITE)
            screen.blit(label, (bar_x - 50, bar_y))

        if boss_warning > 0:
            shake = random.randint(-4,4)
            text = big.render("BOSS APPROACHING!", True, RED)
            screen.blit(text, (150 + shake, 350))
            boss_warning -= 1
        
        # ======== FIREWORKS & VICTORY TEXT ========
        if boss_defeated_timer > 0:
            boss_defeated_timer -= 1

            # spawn fireworks randomly
            if random.random() < 0.3:
                fireworks.append(spawn_firework())

            # draw fireworks
            # FIX: Remove fireworks after drawing
            for f in fireworks:
                f[1] -= 2
                pygame.draw.circle(screen,
                    (random.randint(150,255), random.randint(150,255), 0),
                    f[0], f[1])
            # Remove all that have faded
            fireworks = [f for f in fireworks if f[1] > 0]

            # draw victory message
            win = big.render("YOU DEFEATED THE BOSS!", True, YELLOW)
            screen.blit(win, (120, 350))

        # go back to solar scene only after boss is defeated
        if boss_defeated_timer == 0 and boss_fought and not boss_alive:
            scene = "solar"
            boss_alive = False
            boss_spawned = False
            boss_fought = False
            land_key_lock = False
            boss_level += 1

        pygame.display.update()
        continue

    # ================= SOLAR =================
    pygame.display.set_caption("Solar System")
    screen.fill(BLACK)

    # asteroid hit cooldown
    if asteroid_hit_timer > 0:
        asteroid_hit_timer -= 1

    # ---- moving stars ----
    for s in stars:
        s[1] += s[2]*0.25
        if s[1] > HEIGHT:
            s[1] = 0
            s[0] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2])

    d=pygame.Vector2(math.cos(math.radians(ship_angle)),math.sin(math.radians(ship_angle)))

    if keys[pygame.K_w] and fuel > 0:
        ship_pos += d*3
        fuel = max(0, fuel - 0.2)

        if not CH_THRUST.get_busy():
            CH_THRUST.play(thrust_sound, loops=-1, fade_ms=80)

    else:
        CH_THRUST.fadeout(120)

    if keys[pygame.K_s]: ship_pos-=d*3
    if keys[pygame.K_a]: ship_angle-=3
    if keys[pygame.K_d]: ship_angle+=3
    
    if not keys[pygame.K_w]:
        fuel = min(MAX_FUEL, fuel + 0.05)

    ship_screen=world(ship_pos)

    touching=(ship_screen.x-ship_radius<=0 or ship_screen.x+ship_radius>=WIDTH or
              ship_screen.y-ship_radius<=0 or ship_screen.y+ship_radius>=HEIGHT)

    if touching: target_scale=max(MIN_ZOOM,target_scale-.015)
    else: target_scale=min(MAX_ZOOM,target_scale+.01)

    camera_scale+=(target_scale-camera_scale)*.08

    pygame.draw.circle(screen,YELLOW,world(pygame.Vector2(0,0)),int(25*camera_scale))

    for i,p in enumerate(planets):
        name,col,orbit,size,spd,grav=p
        pos=pygame.Vector2(orbit*math.cos(angles[i]),orbit*math.sin(angles[i]))

        dist = ship_pos.distance_to(pos)
        if dist < grav*4:
            if dist > 5:
                pull = (pos-ship_pos).normalize() * (grav/dist)*0.4
                ship_pos += pull

        pygame.draw.circle(screen,WHITE,world(pygame.Vector2(0,0)),int(orbit*camera_scale),1)
        pygame.draw.circle(screen,col,world(pos),max(2,int(size*camera_scale)))

        label=font.render(name,1,WHITE)
        screen.blit(label,world(pos)+pygame.Vector2(10,10))

        if ship_pos.distance_to(pos) < grav and keys[pygame.K_l] and not land_key_lock:
            CH_LAND.play(land_sound)
            land_key_lock = True
            # ======== SWITCH TO PLANET SCENE ========
            scene = "planet"
            current_planet = p

            # ======== RESET LANDER & CAMERA ========
            lander_pos = pygame.Vector2(0,0)
            planet_cam = pygame.Vector2(0,0)  # center lander

            # ======== CLEAR ARRAYS TO AVOID GLITCHES ========
            env_particles.clear()
            bullets.clear()
            explosions.clear()
            planet_powerups.clear()
            fireworks.clear()

            # ======== SPAWN MOBS ========
            name, col, orbit, size, spd, grav = p
            mobs = spawn_mobs(name)

            # ======== RESET CAMERA SCALE & TIMERS ========
            camera_scale = 1
            target_scale = 1
            hit_timer = 0
            rapid_timer = 0
            taking_off = False
            launch_height = 0

        angles[i]+=spd
    if not keys[pygame.K_l]:
        land_key_lock = False

    # ---- asteroids ----
    for i in range(len(asteroids)):
        asteroids[i] += asteroid_vel[i]
        asteroid_vel[i].rotate_ip(random.uniform(-0.3, 0.3))

        if asteroids[i].x > 700: asteroids[i].x = -700
        if asteroids[i].x < -700: asteroids[i].x = 700
        if asteroids[i].y > 700: asteroids[i].y = -700
        if asteroids[i].y < -700: asteroids[i].y = 700

    for a in asteroids:
        pos = world(a)
        pygame.draw.circle(screen, (150,150,150), pos, int(10*camera_scale))

        if ship_pos.distance_to(a) < 18 / camera_scale and asteroid_hit_timer == 0:
            health -= 4 + difficulty
            if sound_exp_cd == 0:
                CH_EXP.play(explosion_sound)
                sound_exp_cd = 10

            explosions.append([ship_pos.copy(), 30])
            asteroid_hit_timer = 30

            if health <= 0:
                game_over = True

    tip=ship_screen+d*15
    left=ship_screen+d.rotate(140)*10
    right=ship_screen+d.rotate(-140)*10
    rot = pygame.transform.rotate(ship_img, -ship_angle-90)
    rect = rot.get_rect(center=ship_screen)
    screen.blit(rot, rect)
    if keys[pygame.K_w] and fuel > 0:
        flame = ship_screen - d*12
        pygame.draw.circle(screen,(255,120,0),flame,5)

    

    hud(f"Spacecraft X:{int(ship_pos.x)} Y:{int(ship_pos.y)}",10)
    hud(f"Health: {health}",35)
    hud(f"Score: {score}",60)
    hud(f"Fuel: {int(fuel)}",85)

    # ---- explosions ----
    # FIX: Remove explosions after drawing
    for ex in explosions:
        ex[1] -= 2
        if scene=="solar":
            pos = world(ex[0])
        else:
            pos = ex[0] - planet_cam + pygame.Vector2(WIDTH//2,HEIGHT//2)
        pygame.draw.circle(screen,(255,random.randint(120,200),0),pos,ex[1])

    # Remove all faded explosions
    explosions = [ex for ex in explosions if ex[1] > 0]

    if health <= 0:
        game_over = True
  
    pygame.display.update()

Mob.update()