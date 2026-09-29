"""Sky Hill — a tiny original platformer (Python + Pygame).

Run:  python game.py
Keys: Left/Right to move, Space to jump, Enter/Space on menus.
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
MOVE_SPEED = 7
GRAVITY = 0.62
JUMP_VEL = -13.2
MAX_FALL = 16
START_LIVES = 3

# --- Enemies ---
STOMP_BOUNCE = -10
STOMP_POINTS = 50
# How far below an enemy's top the player's feet may have been last frame and still count as a stomp.
STOMP_TOLERANCE = 8

COIN_POINTS = 10

# --- Colors (friendly, original — not Nintendo palettes as a theme) ---
SKY = (16, 18, 26)
SKY_DARK = (32, 36, 50)
TEAL = (32, 168, 158)
TEAL_SHADOW = (18, 118, 112)
GRASS = (72, 160, 88)
DIRT = (139, 105, 68)
MOVER = (104, 92, 168)
MOVER_TOP = (168, 150, 240)
COIN = (72, 226, 255)
COIN_EDGE = (22, 150, 196)
ENEMY = (214, 86, 78)
ENEMY_DARK = (168, 48, 52)
POLE = (236, 236, 240)
FLAG = (255, 120, 72)
HUD_BG = (20, 40, 55)
WHITE = (255, 255, 255)
INK = (28, 48, 62)
SOFT = (235, 246, 252)

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

    def reset(self, x, y):
        self.rect.topleft = (int(x), int(y))
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.ground = None

    def handle_input(self, keys):
        self.vx = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -MOVE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = MOVE_SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = JUMP_VEL
            self.on_ground = False

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
                elif self.vy < 0:
                    self.rect.top = plat.bottom
                    self.vy = 0


class Walker:
    def __init__(self, x, y, left, right):
        self.rect = pygame.Rect(int(x), int(y), 34, 32)
        self.left = left
        self.right = right
        self.vx = 1.6

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
        self.big = pygame.font.SysFont("segoeui", 52, bold=True)
        self.small = pygame.font.SysFont("segoeui", 20)
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
        self.player.handle_input(keys)
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
            sx = (x - self.camera_x * depth) % WIDTH
            glow = 150 + int(105 * (0.5 + 0.5 * math.sin(t * 2 + phase)))
            pygame.draw.circle(self.screen, (glow, glow, 255), (int(sx), int(y)), size)
        # Soft distant hills (decoration only)
        pygame.draw.ellipse(self.screen, SKY_DARK, (-80 - self.camera_x // 8, 340, 420, 280))
        pygame.draw.ellipse(self.screen, SKY_DARK, (280 - self.camera_x // 8, 360, 500, 300))
        pygame.draw.ellipse(self.screen, SKY_DARK, (700 - self.camera_x // 8, 330, 460, 320))

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
                pygame.draw.rect(self.screen, DIRT, r)
                pygame.draw.rect(self.screen, GRASS, (r.x, r.y, r.w, 12))

        for coin in self.coins:
            bob = int(3 * math.sin(t * 4 + coin.x * 0.05))
            r = self.world_to_screen(coin).move(0, bob)
            self.screen.blit(self.coin_glow, self.coin_glow.get_rect(center=r.center))
            pygame.draw.rect(self.screen, COIN, r, border_radius=4)
            pygame.draw.rect(self.screen, COIN_EDGE, r, 2, border_radius=4)

        for enemy in self.enemies:
            r = self.world_to_screen(enemy.rect)
            pygame.draw.rect(self.screen, ENEMY, r, border_radius=4)
            pygame.draw.rect(self.screen, ENEMY_DARK, r, 2, border_radius=4)
            eye_y = r.y + 10
            pygame.draw.rect(self.screen, WHITE, (r.x + 6, eye_y, 8, 8))
            pygame.draw.rect(self.screen, WHITE, (r.x + 20, eye_y, 8, 8))

        pole = self.world_to_screen(self.goal)
        pygame.draw.rect(self.screen, POLE, pole)
        flag = pygame.Rect(pole.right, pole.y + 8, 36, 22)
        pygame.draw.rect(self.screen, FLAG, flag)

        pr = self.world_to_screen(self.player.rect)
        pygame.draw.rect(self.screen, TEAL, pr, border_radius=4)
        pygame.draw.rect(self.screen, TEAL_SHADOW, pr, 2, border_radius=4)

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

    def draw_center_panel(self, title, lines, hint):
        self.draw_background()
        panel = pygame.Rect(90, 90, WIDTH - 180, HEIGHT - 180)
        pygame.draw.rect(self.screen, SOFT, panel, border_radius=16)
        pygame.draw.rect(self.screen, TEAL, panel, 4, border_radius=16)

        title_s = self.big.render(title, True, INK)
        self.screen.blit(title_s, title_s.get_rect(center=(WIDTH // 2, 160)))

        y = 230
        for line in lines:
            s = self.font.render(line, True, INK)
            self.screen.blit(s, s.get_rect(center=(WIDTH // 2, y)))
            y += 36

        hint_s = self.small.render(hint, True, TEAL_SHADOW)
        self.screen.blit(hint_s, hint_s.get_rect(center=(WIDTH // 2, 470)))

    def draw_start(self):
        self.draw_center_panel(
            "Sky Hill",
            [
                "A tiny original platformer",
                "Move with Left / Right  (or A / D)",
                "Jump with Space  (or Up / W)",
                "Collect glowing coins  •  Stomp red walkers",
                "Reach the flag on each hill  •  3 lives",
            ],
            "Press Space or Enter to play",
        )

    def draw_win(self):
        self.draw_center_panel(
            "You made it!",
            [
                f"All three hills of Sky Hill are clear.",
                f"Final score: {self.score}",
            ],
            "Press Space or Enter to play again",
        )

    def draw_over(self):
        self.draw_center_panel(
            "Game over",
            [
                "Those walkers got the last laugh.",
                f"Score this run: {self.score}",
            ],
            "Press Space or Enter to try again",
        )

    def handle_menu_confirm(self):
        if self.state in (STATE_START, STATE_WIN, STATE_OVER):
            self.start_new_game()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if self.state != STATE_PLAY:
                            self.handle_menu_confirm()

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
