"""Sky Hill — a tiny original platformer (Python + Pygame).

Run:  python game.py
Keys: Left/Right to move, Space to jump. Click Play / Exit on menus (or Enter / Esc).
"""

import math
import random
import sys

import pygame

# --- Window & feel ---
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "Sky Hill"

# --- Player ---
PLAYER_W, PLAYER_H = 32, 40
MOVE_SPEED = 6
GRAVITY = 0.62
JUMP_VEL = -13.2
DOUBLE_JUMP_VEL = -11.5
AIR_JUMPS = 1
MAX_FALL = 16
START_LIVES = 5

# --- Enemies ---
STOMP_BOUNCE = -10
STOMP_POINTS = 50
# How far below an enemy's top the player's feet may have been last frame and still count as a stomp.
STOMP_TOLERANCE = 8

COIN_POINTS = 10

# --- Colors (friendly, original — not Nintendo palettes as a theme) ---
SKY = (16, 18, 26)
SKY_DARK = (32, 36, 50)
CAT = (250, 250, 252)
CAT_OUTLINE = (160, 168, 188)
CAT_EAR = (255, 170, 190)
CAT_EYE = (110, 214, 120)
CAT_PUPIL = (20, 24, 30)
CAT_NOSE = (255, 128, 158)
GRASS = (72, 160, 88)
DIRT = (139, 105, 68)
LAVA_ROCK = (58, 36, 40)
LAVA_CRACK = (214, 76, 30)
LAVA = (255, 112, 38)
LAVA_HOT = (255, 214, 96)
SNOW = (240, 246, 255)
ICE_ROCK = (92, 114, 150)
ICICLE = (196, 224, 255)
STAR_DRIFT = 120
MOVER = (104, 92, 168)
MOVER_TOP = (168, 150, 240)
COIN = (72, 226, 255)
COIN_EDGE = (22, 150, 196)
ENEMY = (214, 86, 78)
ENEMY_DARK = (168, 48, 52)
ENEMY_BROW = (70, 12, 20)
MOUTH = (48, 6, 14)
TEETH = (250, 246, 232)
PUPIL = (20, 10, 14)
POLE = (236, 236, 240)
FLAG = (255, 120, 72)
HUD_BG = (20, 40, 55)
WHITE = (255, 255, 255)

# --- Menu screens ---
MENU_PANEL = (22, 27, 48)
MENU_DIM = (160, 174, 204)
ACCENT_START = (72, 226, 255)
ACCENT_WIN = (255, 204, 92)
ACCENT_OVER = (255, 104, 110)
PLAY_BTN = (46, 204, 172)
PLAY_BTN_HOVER = (88, 236, 204)
PLAY_BTN_TEXT = (10, 28, 34)
EXIT_BTN = (255, 104, 110)
BUTTON_W, BUTTON_H = 190, 56

STATE_START = "start"
STATE_PLAY = "play"
STATE_WIN = "win"
STATE_OVER = "over"


def make_levels():
    """Three short side-scrolling hills as lists of rects and positions."""
    # Each platform: (x, y, w, h). Coins/enemies/goal are world coordinates.
    # Each mover: (x, y, w, h, axis, distance, speed) — travels from (x, y) along axis and back.
    return [
        {
            "name": "Sunny Slope",
            "theme": "grass",
            "width": 2200,
            "spawn": (80, 420),
            "goal": (2050, 360),
            "platforms": [
                (0, 520, 480, 80),
                (560, 470, 180, 28),
                (820, 420, 160, 28),
                (1360, 400, 180, 28),
                (1620, 460, 220, 28),
                (1880, 400, 320, 200),
            ],
            "movers": [
                (1010, 470, 130, 28, "x", 200, 1.5),
            ],
            "coins": [
                (220, 470),
                (610, 420),
                (870, 370),
                (1140, 420),
                (1420, 350),
                (1690, 410),
                (1960, 350),
            ],
            "enemies": [
                # x, y, patrol left, patrol right
                (620, 438, 560, 740),
                (1400, 368, 1360, 1540),
            ],
        },
        {
            "name": "Breezy Gaps",
            "theme": "lava",
            "width": 2600,
            "spawn": (80, 400),
            "goal": (2420, 280),
            "platforms": [
                (0, 500, 360, 100),
                (460, 450, 140, 28),
                (700, 380, 130, 28),
                (1200, 360, 160, 28),
                (1720, 350, 150, 28),
                (1980, 420, 180, 28),
                (2260, 320, 340, 280),
            ],
            "movers": [
                (860, 450, 120, 28, "x", 200, 1.6),
                (1480, 340, 140, 28, "y", 110, 1.2),
            ],
            "coins": [
                (180, 450),
                (500, 400),
                (740, 330),
                (980, 400),
                (1250, 310),
                (1520, 380),
                (1760, 300),
                (2040, 370),
                (2340, 270),
            ],
            "enemies": [
                (480, 418, 460, 600),
                (1220, 328, 1200, 1360),
                (2000, 388, 1980, 2160),
            ],
        },
        {
            "name": "Cloud Crest",
            "theme": "snow",
            "width": 2800,
            "spawn": (70, 380),
            "goal": (2620, 220),
            "platforms": [
                (0, 480, 300, 120),
                (380, 430, 120, 28),
                (780, 300, 120, 28),
                (1020, 380, 160, 28),
                (1500, 240, 110, 28),
                (1720, 320, 160, 28),
                (2220, 340, 150, 28),
                (2460, 260, 340, 340),
            ],
            "movers": [
                (580, 320, 110, 28, "y", 90, 1.1),
                (1200, 300, 100, 28, "x", 180, 1.6),
                (1980, 220, 130, 28, "y", 100, 1.2),
            ],
            "coins": [
                (140, 430),
                (410, 380),
                (610, 310),
                (810, 250),
                (1070, 330),
                (1320, 250),
                (1530, 190),
                (1760, 270),
                (2020, 210),
                (2260, 290),
                (2540, 210),
            ],
            "enemies": [
                (400, 398, 380, 500),
                (1040, 348, 1020, 1180),
                (1740, 288, 1720, 1880),
                (2240, 308, 2220, 2370),
            ],
        },
    ]


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(int(x), int(y), PLAYER_W, PLAYER_H)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.ground = None
        self.facing = 1
        self.air_jumps_left = AIR_JUMPS
        self.jump_held = False

    def reset(self, x, y):
        self.rect.topleft = (int(x), int(y))
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.ground = None
        self.facing = 1
        self.air_jumps_left = AIR_JUMPS
        self.jump_held = False

    def handle_input(self, keys):
        """Apply movement keys. Returns True when a mid-air (double) jump happened this frame."""
        self.vx = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -MOVE_SPEED
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = MOVE_SPEED
            self.facing = 1

        jump_down = bool(keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w])
        pressed = jump_down and not self.jump_held
        self.jump_held = jump_down
        if not pressed:
            return False
        if self.on_ground:
            self.vy = JUMP_VEL
            self.on_ground = False
            return False
        if self.air_jumps_left > 0:
            self.air_jumps_left -= 1
            self.vy = DOUBLE_JUMP_VEL
            return True
        return False

    def apply_gravity(self):
        self.vy = min(self.vy + GRAVITY, MAX_FALL)

    def move_and_collide(self, platforms):
        # Horizontal
        self.rect.x += int(round(self.vx))
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vx > 0:
                    self.rect.right = plat.left
                elif self.vx < 0:
                    self.rect.left = plat.right

        # Vertical
        self.rect.y += int(round(self.vy))
        self.on_ground = False
        self.ground = None
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vy > 0:
                    self.rect.bottom = plat.top
                    self.vy = 0
                    self.on_ground = True
                    self.ground = plat
                    self.air_jumps_left = AIR_JUMPS
                elif self.vy < 0:
                    self.rect.top = plat.bottom
                    self.vy = 0


class Walker:
    def __init__(self, x, y, left, right):
        self.rect = pygame.Rect(int(x), int(y), 34, 32)
        self.left = left
        self.right = right
        self.vx = 1.6
        self.chomp_phase = random.uniform(0, math.tau)

    def update(self):
        self.rect.x += int(round(self.vx))
        if self.rect.left <= self.left:
            self.rect.left = self.left
            self.vx = abs(self.vx)
        elif self.rect.right >= self.right:
            self.rect.right = self.right
            self.vx = -abs(self.vx)


class MovingPlatform:
    def __init__(self, x, y, w, h, axis, distance, speed):
        self.rect = pygame.Rect(x, y, w, h)
        self.origin = (x, y)
        self.axis = axis
        self.distance = distance
        self.speed = speed
        self.offset = 0.0

    def update(self):
        """Advance along the track and return how far the platform moved (dx, dy)."""
        self.offset += self.speed
        if self.offset <= 0 or self.offset >= self.distance:
            self.offset = max(0.0, min(self.offset, self.distance))
            self.speed = -self.speed
        old_x, old_y = self.rect.topleft
        ox, oy = self.origin
        if self.axis == "x":
            self.rect.x = ox + round(self.offset)
        else:
            self.rect.y = oy + round(self.offset)
        return self.rect.x - old_x, self.rect.y - old_y


class Particle:
    def __init__(self, x, y, vx, vy, color, life, size, gravity):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1


class FloatingText:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 45
        self.max_life = 45

    def update(self):
        self.y -= 1
        self.life -= 1


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui", 28)
        self.small = pygame.font.SysFont("segoeui", 20)
        self.title_font = pygame.font.SysFont("segoeui", 60, bold=True)
        self.button_font = pygame.font.SysFont("segoeui", 26, bold=True)
        self.levels = make_levels()
        self.state = STATE_START
        self.level_index = 0
        self.score = 0
        self.lives = START_LIVES
        self.camera_x = 0
        self.player = Player(80, 420)
        self.platforms = []
        self.movers = []
        self.coins = []
        self.enemies = []
        self.goal = pygame.Rect(0, 0, 16, 80)
        self.level_width = WIDTH
        self.level_name = ""
        self.theme = "grass"

        self.particles = []
        self.texts = []
        self.shake_time = 0
        self.shake_strength = 0
        self.shake_offset = (0, 0)

        rng = random.Random(7)
        self.stars = [
            (
                rng.uniform(0, WIDTH),
                rng.uniform(50, 380),
                rng.choice((1, 1, 1, 2)),
                rng.uniform(0.03, 0.2),
                rng.uniform(0, math.tau),
            )
            for _ in range(110)
        ]
        self.coin_glow = self.make_glow(COIN, 18)

    @staticmethod
    def make_glow(color, radius):
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(110 * (1 - r / radius))
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        return surf

    def load_level(self, index):
        data = self.levels[index]
        self.level_index = index
        self.level_name = data["name"]
        self.theme = data.get("theme", "grass")
        self.level_width = data["width"]
        self.movers = [MovingPlatform(*m) for m in data.get("movers", [])]
        self.platforms = [pygame.Rect(*p) for p in data["platforms"]]
        self.platforms += [m.rect for m in self.movers]
        self.coins = [pygame.Rect(cx, cy, 18, 18) for cx, cy in data["coins"]]
        self.enemies = [Walker(*e) for e in data["enemies"]]
        gx, gy = data["goal"]
        self.goal = pygame.Rect(gx, gy, 18, 88)
        self.player.reset(*data["spawn"])
        self.camera_x = 0
        self.particles = []
        self.texts = []

    def start_new_game(self):
        self.score = 0
        self.lives = START_LIVES
        self.load_level(0)
        self.state = STATE_PLAY

    def restart_current_level(self):
        self.load_level(self.level_index)

    def die(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_OVER
        else:
            self.restart_current_level()
            self.add_shake(10, 20)

    def stomp(self, enemy):
        self.player.vy = STOMP_BOUNCE
        self.player.on_ground = False
        self.player.air_jumps_left = AIR_JUMPS
        self.score += STOMP_POINTS
        self.burst(enemy.rect.centerx, enemy.rect.centery, ENEMY, count=20, speed=5)
        self.float_text(f"+{STOMP_POINTS}", enemy.rect.centerx, enemy.rect.top, ENEMY)
        self.add_shake(5, 10)

    def collect_coin(self, coin):
        self.score += COIN_POINTS
        self.burst(coin.centerx, coin.centery, COIN, count=12, speed=3, gravity=0.05)
        self.float_text(f"+{COIN_POINTS}", coin.centerx, coin.top, COIN)

    def burst(self, x, y, color, count, speed, gravity=0.25):
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            mag = random.uniform(0.3, 1.0) * speed
            self.particles.append(
                Particle(
                    x,
                    y,
                    math.cos(angle) * mag,
                    math.sin(angle) * mag - 1,
                    color,
                    life=random.randint(20, 40),
                    size=random.uniform(2, 4),
                    gravity=gravity,
                )
            )

    def float_text(self, text, x, y, color):
        self.texts.append(FloatingText(text, x, y, color))

    def add_shake(self, strength, frames):
        self.shake_strength = max(self.shake_strength, strength)
        self.shake_time = max(self.shake_time, frames)

    def update_effects(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        for t in self.texts:
            t.update()
        self.texts = [t for t in self.texts if t.life > 0]
        if self.shake_time > 0:
            self.shake_time -= 1
            s = self.shake_strength
            self.shake_offset = (random.randint(-s, s), random.randint(-s, s))
        else:
            self.shake_strength = 0
            self.shake_offset = (0, 0)

    def update_camera(self):
        target = self.player.rect.centerx - WIDTH // 3
        self.camera_x = max(0, min(target, self.level_width - WIDTH))

    def world_to_screen(self, rect):
        ox, oy = self.shake_offset
        return rect.move(-self.camera_x + ox, oy)

    def world_point_to_screen(self, x, y):
        ox, oy = self.shake_offset
        return int(x - self.camera_x + ox), int(y + oy)

    def update_play(self):
        self.update_effects()

        # Carry the player with the platform they were standing on last frame.
        for mover in self.movers:
            dx, dy = mover.update()
            if self.player.ground is mover.rect:
                self.player.rect.x += dx
                self.player.rect.y += dy

        keys = pygame.key.get_pressed()
        if self.player.handle_input(keys):
            feet = self.player.rect.midbottom
            self.burst(feet[0], feet[1], CAT, count=10, speed=2.5, gravity=0.02)
        self.player.apply_gravity()
        prev_bottom = self.player.rect.bottom
        self.player.move_and_collide(self.platforms)

        survivors = []
        for enemy in self.enemies:
            enemy.update()
            if not self.player.rect.colliderect(enemy.rect):
                survivors.append(enemy)
            elif prev_bottom <= enemy.rect.top + STOMP_TOLERANCE:
                self.stomp(enemy)
            else:
                self.die()
                return
        self.enemies = survivors

        remaining = []
        for coin in self.coins:
            if self.player.rect.colliderect(coin):
                self.collect_coin(coin)
            else:
                remaining.append(coin)
        self.coins = remaining

        if self.player.rect.colliderect(self.goal):
            if self.level_index + 1 >= len(self.levels):
                self.state = STATE_WIN
            else:
                self.load_level(self.level_index + 1)
            return

        if self.player.rect.top > HEIGHT + 80:
            self.die()
            return

        self.update_camera()

    def draw_background(self):
        self.screen.fill(SKY)
        t = pygame.time.get_ticks() / 1000
        for x, y, size, depth, phase in self.stars:
            sx = (x - (self.camera_x + t * STAR_DRIFT) * depth) % WIDTH
            glow = 150 + int(105 * (0.5 + 0.5 * math.sin(t * 2 + phase)))
            pygame.draw.circle(self.screen, (glow, glow, 255), (int(sx), int(y)), size)
        self.draw_shooting_star(t)
        # Soft distant hills (decoration only)
        pygame.draw.ellipse(self.screen, SKY_DARK, (-80 - self.camera_x // 8, 340, 420, 280))
        pygame.draw.ellipse(self.screen, SKY_DARK, (280 - self.camera_x // 8, 360, 500, 300))
        pygame.draw.ellipse(self.screen, SKY_DARK, (700 - self.camera_x // 8, 330, 460, 320))

    def draw_shooting_star(self, t):
        period, duration = 4.5, 0.9
        cycle, phase = divmod(t, period)
        if phase > duration:
            return
        rng = random.Random(int(cycle))
        x0, y0 = rng.uniform(250, WIDTH + 100), rng.uniform(50, 180)
        dx, dy = -320, 140
        progress = phase / duration
        head = (x0 + dx * progress, y0 + dy * progress)
        fade = math.sin(progress * math.pi)
        for i in range(10):
            k0, k1 = i / 10, (i + 1) / 10
            start = (head[0] - dx * 0.25 * k0, head[1] - dy * 0.25 * k0)
            end = (head[0] - dx * 0.25 * k1, head[1] - dy * 0.25 * k1)
            v = int(255 * fade * (1 - k0))
            pygame.draw.line(self.screen, (v, v, min(255, v + 30)), start, end, 2 if i < 3 else 1)

    def draw_platform(self, plat, t):
        r = self.world_to_screen(plat)
        if self.theme == "lava":
            pygame.draw.rect(self.screen, LAVA_ROCK, r)
            pulse = 0.6 + 0.4 * math.sin(t * 3 + plat.x * 0.01)
            crack = tuple(int(c * pulse) for c in LAVA_CRACK)
            for cx in range(plat.x + 16, plat.right - 10, 36):
                sx = r.x + (cx - plat.x)
                bottom = min(r.bottom - 2, r.y + 34)
                pygame.draw.lines(
                    self.screen, crack, False,
                    [(sx, r.y + 12), (sx + 5, r.y + 20), (sx - 3, r.y + 27), (sx + 2, bottom)], 2,
                )
            glow = pygame.Surface((r.w, 14), pygame.SRCALPHA)
            for i in range(14):
                pygame.draw.line(glow, (*LAVA, int(70 * pulse * (i / 14) ** 2)), (0, i), (r.w, i))
            self.screen.blit(glow, (r.x, r.y - 14))
            pygame.draw.rect(self.screen, LAVA, (r.x, r.y, r.w, 10))
            for bx in range(plat.x + 6, plat.right - 6, 14):
                sx = r.x + (bx - plat.x)
                wobble = math.sin(t * 4 + bx * 0.3)
                pygame.draw.ellipse(self.screen, LAVA_HOT, (sx, r.y + 3 + round(wobble * 2), 7, 3))
        elif self.theme == "snow":
            pygame.draw.rect(self.screen, ICE_ROCK, r)
            for ix in range(plat.x + 10, plat.right - 8, 22):
                sx = r.x + (ix - plat.x)
                length = 6 + (ix * 7) % 9
                pygame.draw.polygon(
                    self.screen, ICICLE, [(sx - 3, r.y + 10), (sx + 3, r.y + 10), (sx, r.y + 10 + length)]
                )
            pygame.draw.rect(self.screen, SNOW, (r.x, r.y - 2, r.w, 12), border_radius=4)
            for bx in range(plat.x + 4, plat.right - 2, 10):
                sx = r.x + (bx - plat.x)
                pygame.draw.circle(self.screen, SNOW, (sx, r.y + 9), 4)
        else:
            pygame.draw.rect(self.screen, DIRT, r)
            pygame.draw.rect(self.screen, GRASS, (r.x, r.y, r.w, 12))

    def draw_walker(self, enemy, t):
        r = self.world_to_screen(enemy.rect)
        near = abs(enemy.rect.centerx - self.player.rect.centerx) < 220
        chomp_speed = 18 if near else 9
        gap = round(5 * (0.5 + 0.5 * math.sin(t * chomp_speed + enemy.chomp_phase)))

        pygame.draw.rect(self.screen, ENEMY, r, border_radius=6)
        pygame.draw.rect(self.screen, ENEMY_DARK, r, 2, border_radius=6)

        facing = 1 if enemy.vx > 0 else -1
        for ex in (r.x + 6, r.x + 20):
            pygame.draw.rect(self.screen, WHITE, (ex, r.y + 6, 8, 7))
            pygame.draw.rect(self.screen, PUPIL, (ex + 3 + facing * 2, r.y + 8, 3, 4))
        pygame.draw.line(self.screen, ENEMY_BROW, (r.x + 4, r.y + 3), (r.x + 15, r.y + 7), 3)
        pygame.draw.line(self.screen, ENEMY_BROW, (r.right - 5, r.y + 3), (r.x + 19, r.y + 7), 3)

        tooth_h = 5
        left, right = r.x + 4, r.right - 4
        top = r.y + 15
        bottom = top + tooth_h * 2 + gap
        pygame.draw.rect(self.screen, MOUTH, (left, top, right - left, bottom - top), border_radius=3)
        teeth = 4
        w = (right - left) / teeth
        for i in range(teeth):
            x0 = left + i * w
            pygame.draw.polygon(self.screen, TEETH, [(x0, top), (x0 + w, top), (x0 + w / 2, top + tooth_h)])
        for i in range(teeth - 1):
            x0 = left + w / 2 + i * w
            pygame.draw.polygon(
                self.screen, TEETH, [(x0, bottom), (x0 + w, bottom), (x0 + w / 2, bottom - tooth_h)]
            )

    def draw_cat(self, t):
        """Draw the player as a white cat, facing right, then flip it if facing left."""
        p = self.player
        surf = pygame.Surface((48, 48), pygame.SRCALPHA)
        # Top-left of the player's hitbox inside the 48x48 sprite; ears and tail stick out of it.
        ox, oy = 8, 7
        moving = p.on_ground and p.vx != 0
        airborne = not p.on_ground

        sway = math.sin(t * (10 if moving else 3)) * 3
        tail = []
        for i in range(8):
            k = i / 7
            tail.append((ox + 5 - k * 11 + sway * k, oy + 30 - k * 18 - math.sin(k * math.pi) * 3))
        for x, y in tail:
            pygame.draw.circle(surf, CAT_OUTLINE, (round(x), round(y)), 4)
        for x, y in tail:
            pygame.draw.circle(surf, CAT, (round(x), round(y)), 3)

        step = math.sin(t * 16) if moving else 0.0
        for i, lx in enumerate((ox + 4, ox + 10, ox + 18, ox + 24)):
            if airborne:
                dx, lift = (-2 if i < 2 else 2), 2
            else:
                dx, lift = 0, max(0, round(2 * (step if i % 2 == 0 else -step)))
            leg = pygame.Rect(lx + dx, oy + 32, 5, 8 - lift)
            pygame.draw.rect(surf, CAT, leg, border_radius=2)
            pygame.draw.rect(surf, CAT_OUTLINE, leg, 1, border_radius=2)

        body = pygame.Rect(ox + 1, oy + 21, 30, 15)
        pygame.draw.ellipse(surf, CAT, body)
        pygame.draw.ellipse(surf, CAT_OUTLINE, body, 1)

        for outer, inner in (
            ([(ox + 8, oy + 9), (ox + 10, oy - 5), (ox + 18, oy + 4)],
             [(ox + 10, oy + 6), (ox + 11, oy - 1), (ox + 16, oy + 4)]),
            ([(ox + 20, oy + 4), (ox + 29, oy - 5), (ox + 31, oy + 9)],
             [(ox + 22, oy + 4), (ox + 28, oy - 1), (ox + 29, oy + 6)]),
        ):
            pygame.draw.polygon(surf, CAT, outer)
            pygame.draw.polygon(surf, CAT_OUTLINE, outer, 1)
            pygame.draw.polygon(surf, CAT_EAR, inner)

        head = pygame.Rect(ox + 6, oy + 2, 26, 21)
        pygame.draw.ellipse(surf, CAT, head)
        pygame.draw.ellipse(surf, CAT_OUTLINE, head, 1)

        blinking = (t % 4) < 0.12
        for cx in (ox + 15, ox + 25):
            cy = oy + 12
            if blinking:
                pygame.draw.line(surf, CAT_PUPIL, (cx - 2, cy), (cx + 2, cy), 1)
            else:
                pygame.draw.ellipse(surf, CAT_EYE, (cx - 2, cy - 3, 5, 7))
                pygame.draw.rect(surf, CAT_PUPIL, (cx, cy - 2, 2, 5))
                surf.set_at((cx - 1, cy - 2), WHITE)

        pygame.draw.polygon(surf, CAT_NOSE, [(ox + 19, oy + 16), (ox + 23, oy + 16), (ox + 21, oy + 18)])
        pygame.draw.line(surf, CAT_OUTLINE, (ox + 21, oy + 18), (ox + 19, oy + 20), 1)
        pygame.draw.line(surf, CAT_OUTLINE, (ox + 21, oy + 18), (ox + 23, oy + 20), 1)
        for y0, y1 in ((oy + 15, oy + 14), (oy + 17, oy + 19)):
            pygame.draw.line(surf, CAT_OUTLINE, (ox + 12, y0), (ox + 3, y1), 1)
            pygame.draw.line(surf, CAT_OUTLINE, (ox + 29, y0), (ox + 38, y1), 1)

        if p.facing < 0:
            surf = pygame.transform.flip(surf, True, False)
        pr = self.world_to_screen(p.rect)
        self.screen.blit(surf, (pr.x - ox, pr.y - oy))

    def draw_play(self):
        self.draw_background()
        t = pygame.time.get_ticks() / 1000
        mover_rects = [m.rect for m in self.movers]

        for plat in self.platforms:
            r = self.world_to_screen(plat)
            if any(plat is m for m in mover_rects):
                pygame.draw.rect(self.screen, MOVER, r, border_radius=6)
                pygame.draw.rect(self.screen, MOVER_TOP, (r.x, r.y, r.w, 8), border_radius=6)
            else:
                self.draw_platform(plat, t)

        for coin in self.coins:
            bob = int(3 * math.sin(t * 4 + coin.x * 0.05))
            r = self.world_to_screen(coin).move(0, bob)
            self.screen.blit(self.coin_glow, self.coin_glow.get_rect(center=r.center))
            pygame.draw.rect(self.screen, COIN, r, border_radius=4)
            pygame.draw.rect(self.screen, COIN_EDGE, r, 2, border_radius=4)

        for enemy in self.enemies:
            self.draw_walker(enemy, t)

        pole = self.world_to_screen(self.goal)
        pygame.draw.rect(self.screen, POLE, pole)
        flag = pygame.Rect(pole.right, pole.y + 8, 36, 22)
        pygame.draw.rect(self.screen, FLAG, flag)

        self.draw_cat(t)

        for p in self.particles:
            radius = max(1, round(p.size * p.life / p.max_life))
            pygame.draw.circle(self.screen, p.color, self.world_point_to_screen(p.x, p.y), radius)

        for ft in self.texts:
            s = self.small.render(ft.text, True, ft.color)
            s.set_alpha(int(255 * ft.life / ft.max_life))
            self.screen.blit(s, s.get_rect(center=self.world_point_to_screen(ft.x, ft.y)))

        bar = pygame.Rect(0, 0, WIDTH, 44)
        pygame.draw.rect(self.screen, HUD_BG, bar)
        hud = (
            f"  {self.level_name}    Score {self.score}    Lives {self.lives}    "
            f"Level {self.level_index + 1}/{len(self.levels)}"
        )
        self.screen.blit(self.small.render(hud, True, WHITE), (8, 10))

    def menu_buttons(self):
        cy = 452
        play = pygame.Rect(0, 0, BUTTON_W, BUTTON_H)
        play.center = (WIDTH // 2 - BUTTON_W // 2 - 14, cy)
        exit_ = pygame.Rect(0, 0, BUTTON_W, BUTTON_H)
        exit_.center = (WIDTH // 2 + BUTTON_W // 2 + 14, cy)
        return {"play": play, "exit": exit_}

    def button_at(self, pos):
        for name, rect in self.menu_buttons().items():
            if rect.collidepoint(pos):
                return name
        return None

    def draw_glow(self, rect, color, radius, layers, strength):
        area = rect.inflate(layers * 4, layers * 4)
        surf = pygame.Surface(area.size, pygame.SRCALPHA)
        for i in range(layers):
            ring = pygame.Rect(0, 0, rect.w + i * 4, rect.h + i * 4)
            ring.center = (area.w // 2, area.h // 2)
            alpha = int(strength * (1 - i / layers) ** 2)
            pygame.draw.rect(surf, (*color, alpha), ring, 2, border_radius=radius + i * 2)
        self.screen.blit(surf, area)

    def draw_button(self, rect, label, kind, hovered):
        r = rect.inflate(8, 6) if hovered else rect
        if kind == "play":
            self.draw_glow(r, PLAY_BTN, 14, 8, 150 if hovered else 90)
            pygame.draw.rect(self.screen, PLAY_BTN_HOVER if hovered else PLAY_BTN, r, border_radius=14)
            text_color = PLAY_BTN_TEXT
        else:
            if hovered:
                pygame.draw.rect(self.screen, EXIT_BTN, r, border_radius=14)
                text_color = WHITE
            else:
                pygame.draw.rect(self.screen, MENU_PANEL, r, border_radius=14)
                pygame.draw.rect(self.screen, EXIT_BTN, r, 3, border_radius=14)
                text_color = EXIT_BTN
        s = self.button_font.render(label, True, text_color)
        self.screen.blit(s, s.get_rect(center=r.center))

    def draw_menu(self, title, lines, accent, play_label):
        self.draw_background()

        panel = pygame.Rect(80, 60, WIDTH - 160, HEIGHT - 120)
        self.draw_glow(panel, accent, 22, 12, 120)

        body = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(body, (*MENU_PANEL, 235), body.get_rect(), border_radius=22)
        self.screen.blit(body, panel)
        pygame.draw.rect(self.screen, accent, panel, 2, border_radius=22)

        t = pygame.time.get_ticks() / 1000
        title_y = 128 + int(4 * math.sin(t * 2))
        halo = self.title_font.render(title, True, accent)
        halo.set_alpha(80)
        for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
            self.screen.blit(halo, halo.get_rect(center=(WIDTH // 2 + dx, title_y + dy)))
        title_s = self.title_font.render(title, True, WHITE)
        self.screen.blit(title_s, title_s.get_rect(center=(WIDTH // 2, title_y)))

        pygame.draw.line(self.screen, accent, (WIDTH // 2 - 120, 178), (WIDTH // 2 + 120, 178), 2)

        y = 218
        for i, line in enumerate(lines):
            color = accent if i == 0 else MENU_DIM
            s = self.font.render(line, True, color)
            self.screen.blit(s, s.get_rect(center=(WIDTH // 2, y)))
            y += 32

        mouse = pygame.mouse.get_pos()
        hovered = self.button_at(mouse)
        buttons = self.menu_buttons()
        self.draw_button(buttons["play"], play_label, "play", hovered == "play")
        self.draw_button(buttons["exit"], "Exit", "exit", hovered == "exit")

        hint = self.small.render("Enter to play  •  Esc to quit", True, MENU_DIM)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 514)))

    def draw_start(self):
        self.draw_menu(
            "Sky Hill",
            [
                "A tiny original platformer",
                "Move with Left / Right  (or A / D)",
                "Jump with Space  (or Up / W)",
                "Press jump again mid-air to double jump",
                "Collect glowing coins  •  Stomp red walkers",
                f"Reach the flag on each hill  •  {START_LIVES} lives",
            ],
            ACCENT_START,
            "Play",
        )

    def draw_win(self):
        self.draw_menu(
            "You made it!",
            [
                f"Final score: {self.score}",
                "All three hills of Sky Hill are clear.",
                "Think you can beat that score?",
            ],
            ACCENT_WIN,
            "Play again",
        )

    def draw_over(self):
        self.draw_menu(
            "Game over",
            [
                f"Score this run: {self.score}",
                "You lost to the red junkies!",
                "Try again before they invade.",
            ],
            ACCENT_OVER,
            "Try again",
        )

    def run(self):
        running = True
        cursor_is_hand = False
        while running:
            in_menu = self.state != STATE_PLAY
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RETURN and in_menu:
                        self.start_new_game()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and in_menu:
                    clicked = self.button_at(event.pos)
                    if clicked == "play":
                        self.start_new_game()
                    elif clicked == "exit":
                        running = False

            want_hand = self.state != STATE_PLAY and self.button_at(pygame.mouse.get_pos()) is not None
            if want_hand != cursor_is_hand:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if want_hand else pygame.SYSTEM_CURSOR_ARROW)
                cursor_is_hand = want_hand

            if self.state == STATE_PLAY:
                self.update_play()

            if self.state == STATE_START:
                self.draw_start()
            elif self.state == STATE_PLAY:
                self.draw_play()
            elif self.state == STATE_WIN:
                self.draw_win()
            else:
                self.draw_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit(0)


def main():
    Game().run()


if __name__ == "__main__":
    main()
