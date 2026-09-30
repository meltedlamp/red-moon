"""The cat, the chomping walkers, moving platforms and visual-effect particles."""

import math
import random

import pygame

from .settings import AIR_JUMPS, DOUBLE_JUMP_VEL, GRAVITY, JUMP_VEL, MAX_FALL, MOVE_SPEED, PLAYER_H, PLAYER_W


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
            return "ground"
        if self.air_jumps_left > 0:
            self.air_jumps_left -= 1
            self.vy = DOUBLE_JUMP_VEL
            return "air"
        return None

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
    def __init__(self, x, y, left, right, speed=2.0):
        self.rect = pygame.Rect(int(x), int(y), 34, 32)
        self.x = float(self.rect.x)
        self.left = left
        self.right = right
        self.vx = speed
        self.chomp_phase = random.uniform(0, math.tau)
        self.kind = "walker"

    def update(self, player=None, platforms=None):
        self.x += self.vx
        if self.x <= self.left:
            self.x = self.left
            self.vx = abs(self.vx)
        elif self.x + self.rect.w >= self.right:
            self.x = self.right - self.rect.w
            self.vx = -abs(self.vx)
        self.rect.x = round(self.x)


class Dropper:
    """Hangs still, wobbles when the cat walks under it, then drops slowly and sits."""

    WARN_FRAMES = 50
    TRIGGER = 48

    def __init__(self, x, y):
        self.rect = pygame.Rect(int(x), int(y), 28, 28)
        self.home_x = int(x)
        self.state = "hang"
        self.warn = 0
        self.vy = 0.0
        self.vx = 1
        self.kind = "dropper"
        self.chomp_phase = 0.0

    def update(self, player=None, platforms=None):
        if self.state == "rest":
            return
        if self.state == "hang":
            if player is None:
                return
            close = abs(player.rect.centerx - self.rect.centerx) < self.TRIGGER
            below = player.rect.top > self.rect.bottom
            if close and below:
                self.state = "warn"
                self.warn = self.WARN_FRAMES
            return
        if self.state == "warn":
            self.warn -= 1
            if self.warn <= 0:
                self.state = "fall"
                self.vy = 1.6
            return
        self.vy = min(self.vy + 0.03, 2.2)
        self.rect.y += int(round(self.vy))
        if not platforms:
            return
        for plat in platforms:
            feet_were = self.rect.bottom - self.vy
            if self.rect.colliderect(plat) and feet_were <= plat.top + 6:
                self.rect.bottom = plat.top
                self.vy = 0
                self.state = "rest"
                return


class Bush:
    """A soft shrub. Standing in it makes the Moon look away."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(int(x), int(y) - 46, 58, 46)


class Checkpoint:
    def __init__(self, x, y):
        self.spawn = (int(x), int(y))
        self.rect = pygame.Rect(int(x) + 8, int(y) - 28, 14, 68)
        self.reached = False


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
