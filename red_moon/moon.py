"""The Red Moon character: its face, speech bubble, taunts and laughs."""

import math
import random

import pygame

from .dialogue import MOON_LINES
from .settings import (
    BLOOD, BUBBLE, BUBBLE_EDGE, BUBBLE_TEXT, EYE_CORE, EYE_GLOW, EYE_GLOW_DIM, MOON, MOON_CRACK,
    MOON_POS, MOON_RADIUS, MOON_SHADE, MOON_SOCKET, MOON_TALK_MS, MOON_TEETH, MOUTH_DARK, THROAT,
)


class MoonMixin:
    """Game methods for the Moon watching, talking and laughing."""

    def moon_laugh(self):
        laughs = self.music.get("laughs")
        if self.muted or not laughs:
            return
        options = [s for s in laughs if s is not self.last_laugh] or laughs
        sound = random.choice(options)
        self.last_laugh = sound
        self.moon_voice(sound, queue=True)

    def moon_voice(self, sound, queue=False):
        """Play sound on the Moon's voice channel. With queue=True it waits for the current line to finish."""
        now = pygame.time.get_ticks()
        length = int(sound.get_length() * 1000)
        channel = self.voice_channel
        if channel is None:
            sound.play()
            self.voice_until = now + length
        elif queue and channel.get_busy() and now < self.voice_until:
            channel.queue(sound)
            self.voice_until += length
        else:
            channel.play(sound)
            self.voice_until = now + length
        self.duck_until = max(self.duck_until, self.voice_until)

    def duck_music(self, sound):
        self.duck_until = pygame.time.get_ticks() + int(sound.get_length() * 1000)

    def moon_hush(self):
        """Close the speech bubble and cut off anything the Moon is still saying."""
        self.moon_until = 0
        self.voice_until = 0
        if self.voice_channel is not None:
            self.voice_channel.stop()

    def moon_say(self, reason):
        options = MOON_LINES[reason] + MOON_LINES["any"] + MOON_LINES.get(self.theme, [])
        options = [line for line in options if line != self.last_moon_line]
        self.moon_speak(random.choice(options))

    def moon_speak(self, line):
        self.moon_line = line
        self.last_moon_line = line
        talk_ms = MOON_TALK_MS
        sound = self.music.get(("say", line))
        if sound is not None and not self.muted:
            self.moon_voice(sound)
            talk_ms = max(talk_ms, int(sound.get_length() * 1000) + 700)
        self.moon_until = pygame.time.get_ticks() + talk_ms

    @staticmethod
    def wrap_text(text, font, max_width):
        lines, current = [], ""
        for word in text.split():
            trial = f"{current} {word}".strip()
            if font.size(trial)[0] <= max_width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
        return lines

    def draw_moon_face(self, center, R, t, mood, look=0.0):
        """Draw the moon at any size; mood is "idle", "talk", "scream", "dizzy", "hurt" or "dead"."""
        mx, my = center
        u = R / 60

        def P(x, y):
            return (round(mx + x * u), round(my + y * u))

        def S(v):
            return max(1, round(v * u))

        pygame.draw.circle(self.screen, MOON_SHADE, (mx, my), R)
        pygame.draw.circle(self.screen, MOON, P(-4, -4), R - S(6))
        for cx, cy, cr in ((-30, -44, 5), (46, 0, 5), (-44, 28, 5), (24, 44, 6)):
            pygame.draw.circle(self.screen, MOON_SHADE, P(cx, cy), S(cr))
        for crack in (((8, -59), (4, -48), (12, -40), (7, -30)), ((58, 14), (46, 18), (48, 28), (40, 34))):
            pygame.draw.lines(self.screen, MOON_CRACK, False, [P(x, y) for x, y in crack], S(2))
        if mood in ("hurt", "dead"):
            for crack in (((-52, -28), (-38, -22), (-34, -8), (-22, 0)), ((-6, 58), (-2, 46), (-10, 38))):
                pygame.draw.lines(self.screen, MOON_CRACK, False, [P(x, y) for x, y in crack], S(2))

        wide = {"talk": 1.2, "scream": 1.45, "dizzy": 1.1}.get(mood, 1.0)
        brow_raise = (wide - 1) * 14
        for side in (-1, 1):
            ex, ey = P(side * 22, -14)
            socket = pygame.Rect(0, 0, S(26 * wide), S(20 * wide))
            socket.center = (ex, ey)
            pygame.draw.ellipse(self.screen, MOON_SOCKET, socket)
            inner, outer = P(side * 4, -14 - brow_raise), P(side * 38, -27 - brow_raise)
            pygame.draw.polygon(self.screen, MOON, [P(side * 4, -34), P(side * 38, -38), outer, inner])
            pygame.draw.line(self.screen, MOON_CRACK, inner, outer, S(3))

            if mood == "dead":
                for dy in (-1, 1):
                    pygame.draw.line(self.screen, MOON_SHADE, (ex - S(7), ey - dy * S(6)), (ex + S(7), ey + dy * S(6)), S(3))
                continue

            drip = 6 + 10 * (0.5 + 0.5 * math.sin(t * 1.3 + side * 1.7))
            top = P(side * 20, -14 + 9 * wide)
            bottom = (top[0], top[1] + S(drip))
            pygame.draw.line(self.screen, BLOOD, top, bottom, S(3))
            pygame.draw.circle(self.screen, BLOOD, bottom, S(2.5))

            if mood == "hurt":
                tip, arm = ex - side * S(5), ex + side * S(7)
                pygame.draw.lines(self.screen, EYE_GLOW, False, [(arm, ey - S(6)), (tip, ey), (arm, ey + S(6))], S(3))
                continue

            px, py = ex + round(look * 5 * u), ey + S(2)
            if mood == "dizzy":
                spin = t * 9 + side
                px, py = ex + round(math.cos(spin) * 6 * u), ey + round(math.sin(spin) * 4 * u)
                sizes = (4, 2.5, 1)
            elif mood == "scream":
                sizes = (10, 6, 2.5)
            elif mood == "talk":
                sizes = (7 + random.random(), 4, 1.5)
            else:
                sizes = (6, 3.5, 1.3)
            for color, size in zip((EYE_GLOW_DIM, EYE_GLOW, EYE_CORE), sizes):
                pygame.draw.circle(self.screen, color, (px, py), S(size))

        if mood == "scream":
            open_amt, hw, base, lift = 38, 30, 16, 3
        elif mood == "talk":
            open_amt, hw, base, lift = 14 + 12 * (0.5 + 0.5 * math.sin(t * 16)), 34, 20, 8
        elif mood == "dizzy":
            open_amt, hw, base, lift = 16 + 4 * math.sin(t * 5), 30, 20, 0
        elif mood == "hurt":
            open_amt, hw, base, lift = 30, 28, 20, -5
        elif mood == "dead":
            open_amt, hw, base, lift = 6, 26, 26, -7
        else:
            open_amt, hw, base, lift = 9, 34, 20, 9

        def top_y(s):
            return base - lift * s * s

        def bottom_y(s):
            return top_y(s) + open_amt * (1 - s * s)

        steps = [-1 + 2 * i / 16 for i in range(17)]
        outline = [P(s * hw, top_y(s)) for s in steps] + [P(s * hw, bottom_y(s)) for s in reversed(steps)]
        pygame.draw.polygon(self.screen, MOUTH_DARK, outline)
        if open_amt > 20:
            throat = pygame.Rect(0, 0, S(hw), S(open_amt * 0.5))
            throat.center = P(0, base + open_amt * 0.55)
            pygame.draw.ellipse(self.screen, THROAT, throat)

        for count, edge, direction in ((8, top_y, 1), (7, bottom_y, -0.8)):
            for i in range(count):
                s0 = -1 + 2 * i / count
                s1 = s0 + 2 / count
                sm = (s0 + s1) / 2
                tooth = min(open_amt * (1 - sm * sm) * 0.55, 14)
                tip = P(sm * hw, edge(sm) + tooth * direction)
                pygame.draw.polygon(self.screen, MOON_TEETH, [P(s0 * hw, edge(s0)), P(s1 * hw, edge(s1)), tip])
        pygame.draw.polygon(self.screen, MOON_CRACK, outline, S(2))

    def draw_moon(self, t):
        now = pygame.time.get_ticks()
        talking = now < self.moon_until
        R = MOON_RADIUS
        mx, my = MOON_POS
        if talking:
            mx += random.randint(-2, 2)
            my += random.randint(-2, 2)
        else:
            my += round(math.sin(t * 1.2) * 4)

        self.moon_glow.set_alpha(255 if talking else 150 + int(105 * (0.5 + 0.5 * math.sin(t * 3))))
        self.screen.blit(self.moon_glow, self.moon_glow.get_rect(center=(mx, my)))

        cat_x = self.world_to_screen(self.player.rect).centerx
        look = max(-1.0, min(1.0, (cat_x - mx) / 250))
        self.draw_moon_face((mx, my), R, t, "talk" if talking else "idle", look)
        if talking:
            self.draw_bubble(mx, my, R)

    def draw_bubble(self, mx, my, R):
        lines = self.wrap_text(self.moon_line, self.small, 230)
        line_h = self.small.get_linesize()
        bubble = pygame.Rect(0, 0, max(self.small.size(line)[0] for line in lines) + 28, line_h * len(lines) + 18)
        if mx - R - 16 - bubble.w >= 8:
            bubble.midright = (mx - R - 16, my - 10)
            edge_x, tip_x = bubble.right - 2, mx - R + 4
        else:
            bubble.midleft = (mx + R + 16, my - 10)
            edge_x, tip_x = bubble.left + 2, mx + R - 4
        tail = [(edge_x, bubble.centery - 9), (edge_x, bubble.centery + 9), (tip_x, my + 6)]
        pygame.draw.rect(self.screen, BUBBLE, bubble, border_radius=12)
        pygame.draw.rect(self.screen, BUBBLE_EDGE, bubble, 2, border_radius=12)
        pygame.draw.polygon(self.screen, BUBBLE, tail)
        pygame.draw.line(self.screen, BUBBLE_EDGE, tail[0], tail[2], 2)
        pygame.draw.line(self.screen, BUBBLE_EDGE, tail[1], tail[2], 2)
        for i, line in enumerate(lines):
            s = self.small.render(line, True, BUBBLE_TEXT)
            jx, jy = random.randint(-1, 1), random.randint(-1, 1)
            self.screen.blit(s, (bubble.x + 14 + jx, bubble.y + 9 + i * line_h + jy))
