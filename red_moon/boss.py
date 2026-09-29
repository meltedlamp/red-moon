"""The final boss: the Moon's state, its projectiles, and the fight logic and drawing."""

import math
import random

import pygame

from .dialogue import MOON_DEFEAT_LINE, MOON_ENRAGE_LINE, MOON_HURT_LINES
from .entities import Particle, Walker
from .settings import (
    AIR_JUMPS, BLOOD, BOSS_ATTACKS_PER_DIVE, BOSS_DEATH_FRAMES, BOSS_ENRAGE_HP, BOSS_FLOOR_Y,
    BOSS_HOVER_Y, BOSS_HP, BOSS_INTRO_FRAMES, BOSS_LOW_Y, BOSS_POINTS, BOSS_RADIUS, DIZZY_STAR, ENEMY,
    EYE_CORE, EYE_GLOW, EYE_GLOW_DIM, HEIGHT, LAIR_CRACK, LAVA, LAVA_HOT, LAVA_ROCK, MOON, MOON_CRACK,
    MOON_SHADE, MOON_TEETH, STATE_WIN, STOMP_BOUNCE, WHITE, WIDTH,
)


class Boss:
    """The Moon's final form: hovers, attacks, then dives down dizzy so it can be stomped."""

    def __init__(self, hp=BOSS_HP):
        self.hp = hp
        self.x, self.y = WIDTH / 2, BOSS_HOVER_Y
        self.clock = 0
        self.attack = None
        self.attacks_done = 0
        self.hurt = 0
        self.laser_x = self.x
        self.laser_warn = 60
        self.dive_from = self.dive_to = (self.x, self.y)
        self.set("intro")

    def set(self, state):
        self.state = state
        self.timer = 0
        self.laser_on = False
        self.shake = 0

    @property
    def enraged(self):
        return self.hp <= BOSS_ENRAGE_HP


class BossShot:
    def __init__(self, x, y, vx, vy, kind):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.kind = kind
        self.r = 13 if kind == "meteor" else 9
        self.gravity = 0.25 if kind == "meteor" else 0.0

    def update(self):
        self.vy += self.gravity
        self.x += self.vx
        self.y += self.vy


class BossFightMixin:
    """Game methods that run and draw the Moon boss fight."""

    @staticmethod
    def circle_hits_rect(cx, cy, radius, rect):
        nx = max(rect.left, min(cx, rect.right))
        ny = max(rect.top, min(cy, rect.bottom))
        return (nx - cx) ** 2 + (ny - cy) ** 2 < radius * radius

    def update_boss(self, prev_bottom):
        """Run one frame of the boss fight. Returns True if the frame ended the level (death or victory)."""
        b = self.boss
        p = self.player
        b.timer += 1
        b.clock += 1
        if b.hurt > 0:
            b.hurt -= 1
        if b.state in ("dying", "gone"):
            return self.update_boss_death()

        if b.state in ("intro", "hover", "attack"):
            drift = 0.022 if b.enraged else 0.015
            b.x += (self.camera_x + WIDTH / 2 + 250 * math.sin(b.clock * drift) - b.x) * 0.06
            b.y += (BOSS_HOVER_Y + 10 * math.sin(b.clock * 0.05) - b.y) * 0.1

        if b.state == "intro":
            if b.timer >= BOSS_INTRO_FRAMES:
                b.set("hover")
        elif b.state == "hover":
            if b.timer >= (45 if b.enraged else 75):
                if b.attacks_done >= BOSS_ATTACKS_PER_DIVE:
                    b.set("dive")
                else:
                    choices = [a for a in ("spit", "laser", "meteors", "summon") if a != b.attack]
                    if len(self.enemies) >= 3 and "summon" in choices:
                        choices.remove("summon")
                    b.attack = random.choice(choices)
                    b.set("attack")
                    b.laser_x = b.x
                    b.laser_warn = 42 if b.enraged else 60
        elif b.state == "attack":
            if self.boss_attack(b):
                b.attacks_done += 1
                b.set("hover")
        elif b.state == "dive":
            windup = 30
            if b.timer <= windup:
                b.shake = 4
                if b.timer == windup:
                    b.dive_from = (b.x, b.y)
                    b.dive_to = (self.dive_spot(p.rect.centerx), BOSS_LOW_Y)
            else:
                k = min(1.0, (b.timer - windup) / 36)
                b.x = b.dive_from[0] + (b.dive_to[0] - b.dive_from[0]) * k * k
                b.y = b.dive_from[1] + (b.dive_to[1] - b.dive_from[1]) * k * k
                if k >= 1:
                    b.set("dizzy")
                    self.add_shake(12, 18)
                    self.burst(b.x, BOSS_FLOOR_Y, LAIR_CRACK, count=24, speed=5)
        elif b.state == "dizzy":
            if b.timer >= (130 if b.enraged else 170):
                b.dive_from = (b.x, b.y)
                b.set("rise")
        elif b.state == "rise":
            k = min(1.0, b.timer / 45)
            ease = 1 - (1 - k) ** 2
            b.y = b.dive_from[1] + (BOSS_HOVER_Y - b.dive_from[1]) * ease
            if k >= 1:
                b.attacks_done = 0
                b.set("hover")

        if self.circle_hits_rect(b.x, b.y, BOSS_RADIUS - 6, p.rect):
            if b.state == "dizzy" and p.vy > 0 and prev_bottom <= b.y - BOSS_RADIUS * 0.3:
                self.hit_boss()
            elif b.state in ("intro", "hover", "attack") or (b.state == "dive" and b.timer > 30):
                self.die("boss")
                return True

        if b.laser_on and self.in_laser(p.rect):
            self.die("boss")
            return True

        alive = []
        for s in self.shots:
            s.update()
            if s.kind == "meteor":
                if s.y > 0 and random.random() < 0.6:
                    self.particles.append(Particle(s.x, s.y - 6, random.uniform(-0.6, 0.6), -1, LAVA, 16, 3, 0))
                landing = self.meteor_landing(s)
                if s.y + s.r >= landing:
                    self.burst(s.x, landing, LAVA, count=14, speed=4)
                    self.add_shake(3, 6)
                    continue
            elif not (-40 < s.x - self.camera_x < WIDTH + 40 and -60 < s.y < HEIGHT + 40):
                continue
            elif any(plat.collidepoint(s.x, s.y) for plat in self.platforms):
                self.burst(s.x, s.y, MOON_TEETH, count=5, speed=2)
                continue
            if self.circle_hits_rect(s.x, s.y, s.r - 2, p.rect.inflate(-8, -6)):
                self.die("boss")
                return True
            alive.append(s)
        self.shots = alive
        return False

    def boss_attack(self, b):
        """Advance the current attack. Returns True once it has finished."""
        t = b.timer
        target = self.player.rect
        if b.attack == "spit":
            volleys = 4 if b.enraged else 3
            if t % 24 == 0 and t <= volleys * 24:
                mx, my = b.x, b.y + BOSS_RADIUS * 0.4
                aim = math.atan2(target.centery - my, target.centerx - mx)
                count = 5 if b.enraged else 3
                speed = 7 if b.enraged else 6
                for i in range(count):
                    angle = aim + (i - (count - 1) / 2) * 0.22
                    self.shots.append(BossShot(mx, my, math.cos(angle) * speed, math.sin(angle) * speed, "tooth"))
            return t > volleys * 24 + 30
        if b.attack == "laser":
            if t < b.laser_warn * 0.65:
                ex, ey, _ = self.laser_path()
                aim_x = ex + (target.centerx - ex) * (BOSS_FLOOR_Y - ey) / max(1, target.centery - ey)
                b.laser_x += (aim_x - b.laser_x) * 0.25
            b.laser_on = b.laser_warn <= t < b.laser_warn + 28
            if t == b.laser_warn:
                self.add_shake(6, 26)
            if b.laser_on and t % 3 == 0:
                end_x, end_y, _ = self.laser_end()
                self.burst(end_x, end_y, EYE_GLOW, count=3, speed=4)
            return t >= b.laser_warn + 40
        if b.attack == "meteors":
            if t == 1:
                count = 9 if b.enraged else 6
                left = self.camera_x + 30
                xs = [target.centerx] + [random.uniform(left, left + WIDTH - 60) for _ in range(count - 1)]
                random.shuffle(xs)
                for i, x in enumerate(xs):
                    self.shots.append(BossShot(x, -40 - i * 60, 0, 3, "meteor"))
            return t >= 110
        if t == 20:
            speed = 3.0 if b.enraged else 2.2
            for x, direction in ((self.camera_x + 30, 1), (self.camera_x + WIDTH - 64, -1)):
                walker = Walker(x, BOSS_FLOOR_Y - 32, 0, self.level_width, speed)
                walker.vx = speed * direction
                self.enemies.append(walker)
                self.burst(walker.rect.centerx, walker.rect.centery, ENEMY, count=16, speed=4)
        return t >= 60

    def meteor_landing(self, shot):
        tops = [p.top for p in self.platforms if p.left <= shot.x <= p.right and p.top >= shot.y - shot.r]
        return min(tops, default=HEIGHT + 100)

    def laser_path(self):
        b = self.boss
        eye_y = b.y - 14 * BOSS_RADIUS / 60
        return b.x, eye_y, b.laser_x

    def laser_end(self):
        """Where the beam stops: (x, y, fraction of the way to the floor). Ledges block it."""
        ex, ey, lx = self.laser_path()
        end_y = BOSS_FLOOR_Y
        for plat in self.platforms:
            if ey < plat.top < end_y:
                x = ex + (lx - ex) * (plat.top - ey) / (BOSS_FLOOR_Y - ey)
                if plat.left <= x <= plat.right:
                    end_y = plat.top
        frac = (end_y - ey) / (BOSS_FLOOR_Y - ey)
        return ex + (lx - ex) * frac, end_y, frac

    def in_laser(self, rect):
        ex, ey, lx = self.laser_path()
        if not ey <= rect.centery <= self.laser_end()[1]:
            return False
        frac = (rect.centery - ey) / (BOSS_FLOOR_Y - ey)
        beam_x = ex + (lx - ex) * frac
        return abs(rect.centerx - beam_x) < 5 + 19 * frac + rect.w / 2 - 6

    def dive_spot(self, x):
        """The open patch of floor nearest x where the dizzy Moon fits without overlapping a ledge."""
        spots = [
            cx for cx in range(BOSS_RADIUS, self.level_width - BOSS_RADIUS + 1, 8)
            if not any(self.circle_hits_rect(cx, BOSS_LOW_Y, BOSS_RADIUS, plat) for plat in self.platforms)
        ]
        return min(spots, key=lambda cx: abs(cx - x), default=x)

    def hit_boss(self):
        b = self.boss
        p = self.player
        b.hp -= 1
        b.hurt = 30
        p.vy = STOMP_BOUNCE * 1.25
        p.on_ground = False
        p.air_jumps_left = AIR_JUMPS
        self.burst(b.x, b.y - BOSS_RADIUS, MOON, count=26, speed=6)
        self.burst(b.x, b.y, BLOOD, count=16, speed=5)
        self.float_text("HIT!", b.x, b.y - BOSS_RADIUS - 10, EYE_GLOW)
        self.add_shake(12, 20)
        if b.hp <= 0:
            b.set("dying")
            self.shots = []
            self.enemies = []
            self.moon_speak(MOON_DEFEAT_LINE)
            return
        b.dive_from = (b.x, b.y)
        b.set("rise")
        b.attacks_done = 0
        if b.hp == BOSS_ENRAGE_HP:
            self.moon_speak(MOON_ENRAGE_LINE)
            self.moon_laugh()
        else:
            self.moon_speak(random.choice(MOON_HURT_LINES))

    def update_boss_death(self):
        b = self.boss
        if b.state == "dying":
            b.y -= 0.5
            b.shake = 2 + b.timer // 20
            if b.timer % 6 == 0:
                angle = random.uniform(0, math.tau)
                dist = random.uniform(0, BOSS_RADIUS)
                color = random.choice((MOON, MOON_SHADE, BLOOD, EYE_GLOW))
                self.burst(b.x + math.cos(angle) * dist, b.y + math.sin(angle) * dist, color, count=10, speed=4)
                self.add_shake(4, 6)
            if b.timer >= BOSS_DEATH_FRAMES:
                for color in (WHITE, MOON, MOON_SHADE, EYE_GLOW, BLOOD):
                    self.burst(b.x, b.y, color, count=30, speed=9, gravity=0.12)
                self.add_shake(18, 30)
                self.score += BOSS_POINTS
                self.float_text(f"+{BOSS_POINTS}", b.x, b.y, DIZZY_STAR)
                b.set("gone")
        elif b.timer >= 110:
            self.state = STATE_WIN
            return True
        return False

    def boss_mood(self):
        b = self.boss
        if b.state == "dying" or b.hurt > 0:
            return "hurt"
        if b.state == "dizzy":
            return "dizzy"
        if b.laser_on or (b.state == "dive" and b.timer > 30):
            return "scream"
        if b.state == "attack" or b.enraged or pygame.time.get_ticks() < self.moon_until:
            return "talk"
        return "idle"

    def draw_boss(self, t):
        b = self.boss
        if b.state == "gone":
            return
        R = BOSS_RADIUS
        x = round(b.x - self.camera_x) + random.randint(-b.shake, b.shake) + self.shake_offset[0]
        y = round(b.y) + random.randint(-b.shake, b.shake) + self.shake_offset[1]
        speed = 8 if b.enraged else 3
        self.moon_glow.set_alpha(150 + int(105 * (0.5 + 0.5 * math.sin(t * speed))))
        self.screen.blit(self.moon_glow, self.moon_glow.get_rect(center=(x, y)))
        look = max(-1.0, min(1.0, (self.player.rect.centerx - self.camera_x - x) / 250))
        self.draw_moon_face((x, y), R, t, self.boss_mood(), look)

        if b.state == "dizzy":
            for k in range(3):
                angle = t * 4 + k * math.tau / 3
                sx, sy = x + math.cos(angle) * R * 0.8, y - R - 12 + math.sin(angle) * 8
                pts = []
                for i in range(8):
                    rad = 7 if i % 2 == 0 else 3
                    a = i * math.pi / 4 + t * 3
                    pts.append((sx + math.cos(a) * rad, sy + math.sin(a) * rad))
                pygame.draw.polygon(self.screen, DIZZY_STAR, pts)
        if b.hurt > 0 and (b.hurt // 4) % 2 == 0:
            self.fx.fill((0, 0, 0, 0))
            pygame.draw.circle(self.fx, (255, 255, 255, 150), (x, y), R)
            self.screen.blit(self.fx, (0, 0))

    def draw_boss_attacks(self):
        b = self.boss
        self.fx.fill((0, 0, 0, 0))
        ex, ey, _ = self.laser_path()
        end_x, end_y, frac = self.laser_end()
        ox, oy = self.shake_offset
        ox -= self.camera_x
        ex, ey, end_x, end_y = ex + ox, ey + oy, end_x + ox, end_y + oy
        outer, core = 5 + 19 * frac, 2 + 7 * frac
        if b.state == "attack" and b.attack == "laser" and not b.laser_on and b.timer < b.laser_warn:
            alpha = 70 + int(70 * (0.5 + 0.5 * math.sin(b.timer * 0.9)))
            pygame.draw.line(self.fx, (*EYE_GLOW, alpha), (ex, ey), (end_x, end_y), 3)
            pygame.draw.ellipse(self.fx, (*EYE_GLOW, alpha), (end_x - outer, end_y - 5, outer * 2, 10), 2)
        if b.laser_on:
            pygame.draw.polygon(
                self.fx, (*EYE_GLOW, 200), [(ex - 5, ey), (ex + 5, ey), (end_x + outer, end_y), (end_x - outer, end_y)]
            )
            pygame.draw.polygon(
                self.fx, (*EYE_CORE, 230), [(ex - 2, ey), (ex + 2, ey), (end_x + core, end_y), (end_x - core, end_y)]
            )
        for s in self.shots:
            if s.kind == "meteor":
                landing = self.meteor_landing(s)
                if s.y < landing:
                    near = max(0.15, min(1.0, 1 - (landing - s.y) / 500))
                    w = 12 + 30 * near
                    pygame.draw.ellipse(self.fx, (*LAIR_CRACK, int(60 + 120 * near)), (s.x + ox - w / 2, landing + oy - 5, w, 10))
        self.screen.blit(self.fx, (0, 0))

        for s in self.shots:
            x, y = self.world_point_to_screen(s.x, s.y)
            if s.kind == "meteor":
                pygame.draw.circle(self.screen, LAVA, (x, y), s.r)
                pygame.draw.circle(self.screen, LAVA_HOT, (x - 2, y - 2), round(s.r * 0.55))
                pygame.draw.circle(self.screen, LAVA_ROCK, (x, y), s.r, 2)
            else:
                speed = math.hypot(s.vx, s.vy) or 1
                dx, dy = s.vx / speed, s.vy / speed
                tip = (x + dx * 14, y + dy * 14)
                left = (x - dx * 8 - dy * 7, y - dy * 8 + dx * 7)
                right = (x - dx * 8 + dy * 7, y - dy * 8 - dx * 7)
                pygame.draw.circle(self.screen, EYE_GLOW_DIM, (x, y), 11)
                pygame.draw.polygon(self.screen, MOON_TEETH, [tip, left, right])
                pygame.draw.polygon(self.screen, MOON_CRACK, [tip, left, right], 1)
