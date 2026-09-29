"""The jumpscare shown between levels."""

import random

import pygame

from .dialogue import SCARE_BOSS_LINE, SCARE_LINES
from .settings import (
    BUBBLE_EDGE, EYE_GLOW, HEIGHT, SCARE_DARK_MS, SCARE_FACE_MS, SCARE_FADE_MS, SCARE_MAX_FACE_MS,
    SCARE_RADIUS, STATE_PLAY, STATE_SCARE, WIDTH,
)


class ScareMixin:
    """Game methods for the between-level jumpscare."""

    def start_scare(self, next_level):
        self.state = STATE_SCARE
        self.scare_next = next_level
        self.scare_start = pygame.time.get_ticks()
        self.scare_line = SCARE_BOSS_LINE if self.levels[next_level].get("boss") else random.choice(SCARE_LINES)
        self.scare_screamed = False
        voice_ms = self.music.get(("voice_ms", self.scare_line), 0)
        self.scare_face_ms = int(min(SCARE_MAX_FACE_MS, max(SCARE_FACE_MS, voice_ms + 250)))

    def update_scare(self):
        elapsed = pygame.time.get_ticks() - self.scare_start
        if not self.scare_screamed and elapsed >= SCARE_DARK_MS:
            self.scare_screamed = True
            sound = self.music.get(("scare", self.scare_line)) or self.music.get("scare")
            if sound and not self.muted:
                sound.play()
                self.duck_music(sound)
        if elapsed >= SCARE_DARK_MS + self.scare_face_ms + SCARE_FADE_MS:
            self.moon_until = 0
            self.load_level(self.scare_next)
            self.state = STATE_PLAY

    def draw_scare(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.scare_start
        if elapsed < SCARE_DARK_MS:
            self.draw_play()
            self.draw_flash((0, 0, 0), 255 * elapsed / SCARE_DARK_MS)
            return

        face_t = elapsed - SCARE_DARK_MS
        self.screen.fill((0, 0, 0))
        grow = min(1.0, face_t / 140)
        R = round(SCARE_RADIUS * (0.3 + 0.7 * (1 - (1 - grow) ** 3)))
        jitter = 10 if face_t < 450 else 3
        cx = WIDTH // 2 + random.randint(-jitter, jitter)
        cy = 290 + random.randint(-jitter, jitter)
        self.screen.blit(self.scare_glow, self.scare_glow.get_rect(center=(cx, cy)))
        self.draw_moon_face((cx, cy), R, now / 1000, "scream")

        for _ in range(10):
            y = random.randrange(HEIGHT - 6)
            strip = self.screen.subsurface((0, y, WIDTH, random.randint(2, 6))).copy()
            self.screen.blit(strip, (random.randint(-30, 30), y))

        boss_next = self.levels[self.scare_next].get("boss")
        label = self.font.render("FINAL LEVEL" if boss_next else f"Level {self.scare_next + 1}", True, BUBBLE_EDGE)
        self.screen.blit(label, label.get_rect(center=(WIDTH // 2, 40)))
        words = self.title_font.render(self.scare_line, True, EYE_GLOW)
        self.screen.blit(words, words.get_rect(center=(WIDTH // 2 + random.randint(-3, 3), 548 + random.randint(-3, 3))))

        self.draw_flash((200, 0, 20), 190 * (1 - face_t / 220))
        self.draw_flash((0, 0, 0), 255 * (face_t - self.scare_face_ms) / SCARE_FADE_MS)
