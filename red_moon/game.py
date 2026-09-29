"""The Game class: state machine, level loading, gameplay updates and the main loop."""

import math
import random
import sys
import threading

import pygame

from .audio import build_audio
from .boss import Boss, BossFightMixin
from .dialogue import MOON_INTRO_LINES
from .entities import FloatingText, MovingPlatform, Particle, Player, Walker
from .levels import make_levels
from .menus import MenuMixin
from .moon import MoonMixin
from .scare import ScareMixin
from .settings import (
    AIR_JUMPS, CAT, COIN, COIN_POINTS, ENEMY, FPS, HEIGHT, LAUGH_DUCK, MOON_GLOW, MOON_RADIUS,
    MUSIC_FADE_MS, MUSIC_VOLUME, SCARE_FACE_MS, SCARE_RADIUS, START_LIVES, STATE_OVER, STATE_PLAY,
    STATE_SCARE, STATE_SELECT, STATE_START, STATE_WIN, STOMP_BOUNCE, STOMP_POINTS, STOMP_TOLERANCE,
    TITLE, WIDTH,
)
from .world import WorldRenderMixin


class Game(MoonMixin, ScareMixin, BossFightMixin, WorldRenderMixin, MenuMixin):
    """The whole game. Drawing and feature logic live in the mixins it inherits from."""

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
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
        self.start_level = 0
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
        self.moon_glow = self.make_glow(MOON_GLOW, MOON_RADIUS + 44)
        self.moon_line = ""
        self.last_moon_line = ""
        self.moon_until = 0

        self.overlay = pygame.Surface((WIDTH, HEIGHT))
        self.scare_glow = self.make_glow(MOON_GLOW, SCARE_RADIUS + 90)
        self.scare_start = 0
        self.scare_next = 0
        self.scare_line = ""
        self.scare_screamed = False
        self.scare_face_ms = SCARE_FACE_MS

        self.music = {}
        self.music_track = None
        self.music_channel = None
        self.muted = False
        self.duck_until = 0
        self.last_laugh = None
        if pygame.mixer.get_init():
            pygame.mixer.set_reserved(1)
            self.music_channel = pygame.mixer.Channel(0)
            threading.Thread(target=build_audio, args=(self.music,), daemon=True).start()

        self.fx = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.tiny = pygame.font.SysFont("segoeui", 17)
        self.boss = None
        self.shots = []
        self.death_flash_at = -10**6

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
        self.goal = pygame.Rect(*data["goal"], 18, 88) if data["goal"] else None
        self.player.reset(*data["spawn"])
        self.camera_x = 0
        self.particles = []
        self.texts = []
        self.shots = []
        self.boss = Boss() if data.get("boss") else None
        if self.boss:
            self.moon_speak(random.choice(MOON_INTRO_LINES))

    def start_new_game(self, level=0):
        self.moon_until = 0
        self.score = 0
        self.lives = START_LIVES
        self.start_level = level
        self.load_level(level)
        self.state = STATE_PLAY

    def restart_current_level(self):
        # Damage dealt to the Moon sticks between lives so the fight stays winnable.
        boss_hp = self.boss.hp if self.boss else None
        self.load_level(self.level_index)
        if self.boss and boss_hp:
            self.boss.hp = boss_hp

    def die(self, reason):
        self.lives -= 1
        self.moon_laugh()
        if self.lives <= 0:
            self.state = STATE_OVER
        else:
            self.restart_current_level()
            self.add_shake(10, 20)
            self.moon_say(reason)
            self.death_flash_at = pygame.time.get_ticks()

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
                self.die("enemy")
                return
        self.enemies = survivors

        remaining = []
        for coin in self.coins:
            if self.player.rect.colliderect(coin):
                self.collect_coin(coin)
            else:
                remaining.append(coin)
        self.coins = remaining

        if self.boss:
            if self.update_boss(prev_bottom):
                return
        elif self.player.rect.colliderect(self.goal):
            if self.level_index + 1 >= len(self.levels):
                self.state = STATE_WIN
            else:
                self.start_scare(self.level_index + 1)
            return

        if self.player.rect.top > HEIGHT + 80:
            self.die("fall")
            return

        self.update_camera()

    def update_music(self):
        channel = self.music_channel
        if channel is None:
            return
        if self.state == STATE_SCARE:
            channel.pause()
            return
        want = "boss" if self.boss and self.state == STATE_PLAY else "creep"
        sound = self.music.get(want)
        if sound is None:
            return
        channel.unpause()
        if self.music_track != want or not channel.get_busy():
            channel.play(sound, loops=-1, fade_ms=MUSIC_FADE_MS)
            self.music_track = want
        ducked = pygame.time.get_ticks() < self.duck_until
        channel.set_volume(0 if self.muted else MUSIC_VOLUME * (LAUGH_DUCK if ducked else 1))

    def run(self):
        running = True
        cursor_is_hand = False
        while running:
            in_menu = self.state in (STATE_START, STATE_WIN, STATE_OVER, STATE_SELECT)
            replay_level = 0 if self.state == STATE_START else self.start_level
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == STATE_SELECT:
                            self.state = STATE_START
                        else:
                            running = False
                    elif event.key == pygame.K_RETURN and in_menu and self.state != STATE_SELECT:
                        self.start_new_game(replay_level)
                    elif event.key == pygame.K_m:
                        self.muted = not self.muted
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and in_menu:
                    clicked = self.button_at(event.pos)
                    if clicked == "play":
                        self.start_new_game(replay_level)
                    elif clicked == "levels":
                        self.state = STATE_SELECT
                    elif clicked == "back":
                        self.state = STATE_START
                    elif clicked and clicked.startswith("level"):
                        self.start_new_game(int(clicked[len("level"):]))
                    elif clicked == "exit":
                        running = False

            in_menu = self.state in (STATE_START, STATE_WIN, STATE_OVER, STATE_SELECT)
            want_hand = in_menu and self.button_at(pygame.mouse.get_pos()) is not None
            if want_hand != cursor_is_hand:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if want_hand else pygame.SYSTEM_CURSOR_ARROW)
                cursor_is_hand = want_hand

            if self.state == STATE_PLAY:
                self.update_play()
            elif self.state == STATE_SCARE:
                self.update_scare()
            self.update_music()

            if self.state == STATE_START:
                self.draw_start()
            elif self.state == STATE_PLAY:
                self.draw_play()
            elif self.state == STATE_SCARE:
                self.draw_scare()
            elif self.state == STATE_WIN:
                self.draw_win()
            elif self.state == STATE_SELECT:
                self.draw_select()
            else:
                self.draw_over()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit(0)


def main():
    Game().run()
