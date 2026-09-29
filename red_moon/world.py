"""Drawing the playable world: sky, themed floors, walkers, the cat and the HUD."""

import math
import random

import pygame

from .settings import (
    BOSS_HP, BOSS_RADIUS, BUBBLE, BUBBLE_EDGE, BUBBLE_TEXT, CANDY_A, CANDY_B, CAT, CAT_EAR, CAT_EYE,
    CAT_NOSE, CAT_OUTLINE, CAT_PUPIL, COIN, COIN_EDGE, CRYSTAL, CRYSTAL_ROCK, CRYSTAL_SHINE,
    CRYSTAL_TOP, DIRT, ENEMY, ENEMY_BROW, ENEMY_DARK, EYE_GLOW, FLAG, FROSTING, GRASS, HUD_BG, ICE_ROCK,
    ICICLE, LAIR_CRACK, LAIR_HILL, LAIR_ROCK, LAIR_SKY, LAIR_TOP, LAVA, LAVA_CRACK, LAVA_HOT, LAVA_ROCK,
    MOON_FLASH_MS, MOUTH, MOVER, MOVER_TOP, POLE, PUPIL, SAND, SANDSTONE, SANDSTONE_LINE, SKY, SKY_DARK,
    SNOW, SPRINKLES, STAR_DRIFT, STATE_PLAY, STATE_SCARE, TEETH, WHITE, WIDTH,
)


class WorldRenderMixin:
    """Game methods that draw a level while it's being played."""

    def draw_background(self):
        lair = self.boss is not None and self.state in (STATE_PLAY, STATE_SCARE)
        self.screen.fill(LAIR_SKY if lair else SKY)
        t = pygame.time.get_ticks() / 1000
        for x, y, size, depth, phase in self.stars:
            sx = (x - (self.camera_x + t * STAR_DRIFT) * depth) % WIDTH
            glow = 150 + int(105 * (0.5 + 0.5 * math.sin(t * 2 + phase)))
            color = (glow, glow // 3, glow // 3) if lair else (glow, glow, 255)
            pygame.draw.circle(self.screen, color, (int(sx), int(y)), size)
        self.draw_shooting_star(t)
        # Soft distant hills (decoration only)
        hill = LAIR_HILL if lair else SKY_DARK
        pygame.draw.ellipse(self.screen, hill, (-80 - self.camera_x // 8, 340, 420, 280))
        pygame.draw.ellipse(self.screen, hill, (280 - self.camera_x // 8, 360, 500, 300))
        pygame.draw.ellipse(self.screen, hill, (700 - self.camera_x // 8, 330, 460, 320))

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
        self.draw_floor(self.world_to_screen(plat), plat.x, t, self.theme)

    def draw_floor(self, r, seed_x, t, theme):
        """Draw a themed floor block at screen rect r. seed_x (a world x) keeps its details fixed as it scrolls."""
        s = self.screen

        def spots(start, end_margin, step):
            for wx in range(seed_x + start, seed_x + r.w - end_margin, step):
                yield wx, r.x + (wx - seed_x)

        if theme == "lava":
            pygame.draw.rect(s, LAVA_ROCK, r)
            pulse = 0.6 + 0.4 * math.sin(t * 3 + seed_x * 0.01)
            crack = tuple(int(c * pulse) for c in LAVA_CRACK)
            bottom = min(r.bottom - 2, r.y + 34)
            for _, sx in spots(16, 10, 36):
                pygame.draw.lines(s, crack, False, [(sx, r.y + 12), (sx + 5, r.y + 20), (sx - 3, r.y + 27), (sx + 2, bottom)], 2)
            glow = pygame.Surface((r.w, 14), pygame.SRCALPHA)
            for i in range(14):
                pygame.draw.line(glow, (*LAVA, int(70 * pulse * (i / 14) ** 2)), (0, i), (r.w, i))
            s.blit(glow, (r.x, r.y - 14))
            pygame.draw.rect(s, LAVA, (r.x, r.y, r.w, 10))
            for wx, sx in spots(6, 6, 14):
                wobble = math.sin(t * 4 + wx * 0.3)
                pygame.draw.ellipse(s, LAVA_HOT, (sx, r.y + 3 + round(wobble * 2), 7, 3))
        elif theme == "snow":
            pygame.draw.rect(s, ICE_ROCK, r)
            for wx, sx in spots(10, 8, 22):
                length = 6 + (wx * 7) % 9
                pygame.draw.polygon(s, ICICLE, [(sx - 3, r.y + 10), (sx + 3, r.y + 10), (sx, r.y + 10 + length)])
            pygame.draw.rect(s, SNOW, (r.x, r.y - 2, r.w, 12), border_radius=4)
            for _, sx in spots(4, 2, 10):
                pygame.draw.circle(s, SNOW, (sx, r.y + 9), 4)
        elif theme == "sand":
            pygame.draw.rect(s, SANDSTONE, r)
            for y in range(r.y + 18, r.bottom - 4, 10):
                pygame.draw.line(s, SANDSTONE_LINE, (r.x, y), (r.right - 1, y), 1)
            for wx, sx in spots(9, 6, 17):
                pygame.draw.circle(s, SANDSTONE_LINE, (sx, r.y + 14 + (wx * 5) % 12), 2)
            pygame.draw.rect(s, SAND, (r.x, r.y, r.w, 11))
            s.set_clip(pygame.Rect(r.x, r.y - 8, r.w, 20))
            for wx, sx in spots(0, -12, 24):
                pygame.draw.ellipse(s, SAND, (sx - 12, r.y - 3 - (wx % 3), 26, 9))
            s.set_clip(None)
        elif theme == "candy":
            pygame.draw.rect(s, CANDY_B, r)
            s.set_clip(r)
            for wx, sx in spots(-r.h - 20, -20, 20):
                if (wx // 20) % 2 == 0:
                    pygame.draw.polygon(s, CANDY_A, [(sx, r.bottom), (sx + 10, r.bottom), (sx + 10 + r.h, r.y), (sx + r.h, r.y)])
            s.set_clip(None)
            pygame.draw.rect(s, FROSTING, (r.x, r.y - 1, r.w, 11), border_radius=5)
            for wx, sx in spots(8, 6, 19):
                drip = 3 + (wx * 3) % 7
                pygame.draw.rect(s, FROSTING, (sx - 3, r.y + 6, 6, drip + 4), border_radius=3)
            for wx, sx in spots(5, 5, 9):
                color = SPRINKLES[(wx // 9) % len(SPRINKLES)]
                pygame.draw.rect(s, color, (sx, r.y + 2 + (wx % 3) * 2, 4, 2))
        elif theme == "crystal":
            pygame.draw.rect(s, CRYSTAL_ROCK, r)
            pulse = 0.55 + 0.45 * math.sin(t * 2.5 + seed_x * 0.02)
            glow_color = tuple(int(c * pulse + CRYSTAL_ROCK[i] * (1 - pulse)) for i, c in enumerate(CRYSTAL))
            for wx, sx in spots(12, 12, 30):
                cy = r.y + 16 + (wx * 3) % 8
                if cy + 8 < r.bottom:
                    pygame.draw.polygon(s, glow_color, [(sx, cy - 6), (sx + 4, cy), (sx, cy + 7), (sx - 4, cy)])
            pygame.draw.rect(s, CRYSTAL_TOP, (r.x, r.y, r.w, 9))
            pygame.draw.line(s, CRYSTAL_SHINE, (r.x + 2, r.y + 1), (r.right - 3, r.y + 1), 2)
            for wx, sx in spots(10, 8, 26):
                h = 5 + (wx * 7) % 6
                pygame.draw.polygon(s, CRYSTAL_SHINE, [(sx - 3, r.y + 9), (sx + 3, r.y + 9), (sx, r.y + 9 + h)])
        elif theme == "lair":
            pygame.draw.rect(s, LAIR_ROCK, r)
            pulse = 0.55 + 0.45 * math.sin(t * 3 + seed_x * 0.013)
            crack = tuple(int(c * pulse) for c in LAIR_CRACK)
            bottom = min(r.bottom - 2, r.y + 30)
            for _, sx in spots(14, 10, 42):
                pygame.draw.lines(s, crack, False, [(sx, r.y + 8), (sx - 4, r.y + 15), (sx + 3, r.y + 22), (sx - 2, bottom)], 2)
            if r.h >= 50:
                for wx, sx in spots(30, 30, 90):
                    if (t + wx * 0.37) % 4 > 0.18:
                        for dx in (0, 9):
                            pygame.draw.circle(s, EYE_GLOW, (sx + dx, r.y + 40), 2)
            pygame.draw.rect(s, LAIR_TOP, (r.x, r.y, r.w, 7))
            pygame.draw.line(s, crack, (r.x, r.y + 7), (r.right - 1, r.y + 7), 2)
        else:
            pygame.draw.rect(s, DIRT, r)
            pygame.draw.rect(s, GRASS, (r.x, r.y, r.w, 12))

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

    def draw_flash(self, color, alpha):
        if alpha <= 0:
            return
        self.overlay.fill(color)
        self.overlay.set_alpha(min(255, int(alpha)))
        self.screen.blit(self.overlay, (0, 0))

    def draw_play(self):
        self.draw_background()
        t = pygame.time.get_ticks() / 1000
        if not self.boss:
            self.draw_moon(t)
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

        if self.goal:
            pole = self.world_to_screen(self.goal)
            pygame.draw.rect(self.screen, POLE, pole)
            flag = pygame.Rect(pole.right, pole.y + 8, 36, 22)
            pygame.draw.rect(self.screen, FLAG, flag)

        if self.boss:
            self.draw_boss(t)
            self.draw_boss_attacks()

        self.draw_cat(t)

        for p in self.particles:
            radius = max(1, round(p.size * p.life / p.max_life))
            pygame.draw.circle(self.screen, p.color, self.world_point_to_screen(p.x, p.y), radius)

        for ft in self.texts:
            s = self.small.render(ft.text, True, ft.color)
            s.set_alpha(int(255 * ft.life / ft.max_life))
            self.screen.blit(s, s.get_rect(center=self.world_point_to_screen(ft.x, ft.y)))

        if self.boss:
            b = self.boss
            if self.moon_until > pygame.time.get_ticks() and b.state != "gone":
                self.draw_bubble(round(b.x - self.camera_x), round(b.y), BOSS_RADIUS)
            if b.state == "gone":
                self.draw_flash(WHITE, 255 * (1 - b.timer / 60))

        since_death = pygame.time.get_ticks() - self.death_flash_at
        self.draw_flash((170, 0, 16), 110 * (1 - since_death / MOON_FLASH_MS))

        bar = pygame.Rect(0, 0, WIDTH, 44)
        pygame.draw.rect(self.screen, HUD_BG, bar)
        hud = (
            f"  {self.level_name}    Score {self.score}    Lives {self.lives}    "
            f"Level {self.level_index + 1}/{len(self.levels)}"
        )
        self.screen.blit(self.small.render(hud, True, WHITE), (8, 10))

        if self.boss and self.boss.state != "gone":
            label = self.tiny.render("THE MOON", True, BUBBLE_TEXT)
            self.screen.blit(label, label.get_rect(center=(WIDTH // 2, 58)))
            hp_bar = pygame.Rect(250, 70, 300, 12)
            pygame.draw.rect(self.screen, BUBBLE, hp_bar, border_radius=6)
            filled = hp_bar.copy()
            filled.w = round(hp_bar.w * max(0, self.boss.hp) / BOSS_HP)
            if filled.w:
                pygame.draw.rect(self.screen, EYE_GLOW, filled, border_radius=6)
            pygame.draw.rect(self.screen, BUBBLE_EDGE, hp_bar, 2, border_radius=6)
