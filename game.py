"""Sky Hill — a tiny original platformer (Python + Pygame).

Run:  python game.py
Keys: Left/Right to move, Space to jump, Enter/Space on menus.
"""

import sys

import pygame

# --- Window & feel ---
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "Sky Hill"

# --- Player ---
PLAYER_W, PLAYER_H = 32, 40
MOVE_SPEED = 5.2
GRAVITY = 0.62
JUMP_VEL = -13.2
MAX_FALL = 16
START_LIVES = 3

# --- Colors (friendly, original — not Nintendo palettes as a theme) ---
SKY = (148, 206, 235)
SKY_DARK = (110, 178, 220)
TEAL = (32, 168, 158)
TEAL_SHADOW = (18, 118, 112)
GRASS = (72, 160, 88)
DIRT = (139, 105, 68)
GOLD = (242, 196, 52)
GOLD_EDGE = (214, 160, 28)
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
                (1080, 470, 200, 28),
                (1360, 400, 180, 28),
                (1620, 460, 220, 28),
                (1880, 400, 320, 200),
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
                (940, 450, 150, 28),
                (1200, 360, 160, 28),
                (1480, 430, 140, 28),
                (1720, 350, 150, 28),
                (1980, 420, 180, 28),
                (2260, 320, 340, 280),
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
                (580, 360, 110, 28),
                (780, 300, 120, 28),
                (1020, 380, 160, 28),
                (1280, 300, 120, 28),
                (1500, 240, 110, 28),
                (1720, 320, 160, 28),
                (1980, 260, 130, 28),
                (2220, 340, 150, 28),
                (2460, 260, 340, 340),
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

    def reset(self, x, y):
        self.rect.topleft = (int(x), int(y))
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False

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
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vy > 0:
                    self.rect.bottom = plat.top
                    self.vy = 0
                    self.on_ground = True
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
        self.coins = []
        self.enemies = []
        self.goal = pygame.Rect(0, 0, 16, 80)
        self.level_width = WIDTH
        self.level_name = ""

    def load_level(self, index):
        data = self.levels[index]
        self.level_index = index
        self.level_name = data["name"]
        self.level_width = data["width"]
        self.platforms = [pygame.Rect(*p) for p in data["platforms"]]
        self.coins = [pygame.Rect(cx, cy, 18, 18) for cx, cy in data["coins"]]
        self.enemies = [Walker(*e) for e in data["enemies"]]
        gx, gy = data["goal"]
        self.goal = pygame.Rect(gx, gy, 18, 88)
        self.player.reset(*data["spawn"])
        self.camera_x = 0

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

    def update_camera(self):
        target = self.player.rect.centerx - WIDTH // 3
        self.camera_x = max(0, min(target, self.level_width - WIDTH))

    def world_to_screen(self, rect):
        return rect.move(-self.camera_x, 0)

    def update_play(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.apply_gravity()
        self.player.move_and_collide(self.platforms)

        for enemy in self.enemies:
            enemy.update()
            if self.player.rect.colliderect(enemy.rect):
                self.die()
                return

        remaining = []
        for coin in self.coins:
            if self.player.rect.colliderect(coin):
                self.score += 10
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
        # Soft distant hills (decoration only)
        pygame.draw.ellipse(self.screen, SKY_DARK, (-80 - self.camera_x // 8, 340, 420, 280))
        pygame.draw.ellipse(self.screen, SKY_DARK, (280 - self.camera_x // 8, 360, 500, 300))
        pygame.draw.ellipse(self.screen, SKY_DARK, (700 - self.camera_x // 8, 330, 460, 320))

    def draw_play(self):
        self.draw_background()

        for plat in self.platforms:
            r = self.world_to_screen(plat)
            pygame.draw.rect(self.screen, DIRT, r)
            pygame.draw.rect(self.screen, GRASS, (r.x, r.y, r.w, 12))

        for coin in self.coins:
            r = self.world_to_screen(coin)
            pygame.draw.rect(self.screen, GOLD, r, border_radius=4)
            pygame.draw.rect(self.screen, GOLD_EDGE, r, 2, border_radius=4)

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
                "Collect gold coins  •  Avoid red walkers",
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
