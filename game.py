"""The Red Moon — a tiny original platformer (Python + Pygame).

Run:  python game.py
Keys: Left/Right to move, Space to jump. Click Play / Exit on menus (or Enter / Esc).
"""

import math
import os
import random
import subprocess
import sys
import tempfile
import threading
import wave
from array import array

import pygame

# --- Window & feel ---
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "The Red Moon"

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
MOON = (228, 218, 190)
MOON_SHADE = (170, 156, 134)
MOON_CRACK = (96, 78, 70)
MOON_SOCKET = (14, 4, 8)
MOON_GLOW = (200, 24, 40)
MOON_TEETH = (238, 230, 204)
EYE_GLOW = (255, 40, 48)
EYE_GLOW_DIM = (120, 10, 20)
EYE_CORE = (255, 220, 200)
BLOOD = (150, 8, 22)
MOUTH_DARK = (22, 0, 6)
THROAT = (100, 0, 14)
BUBBLE = (24, 6, 12)
BUBBLE_EDGE = (200, 30, 44)
BUBBLE_TEXT = (255, 156, 156)
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
LEVELS_BTN = (178, 150, 255)
CARD_BG = (32, 38, 66)
BUTTON_W, BUTTON_H = 170, 56

# --- Floor themes (one per level) ---
SAND = (238, 204, 132)
SANDSTONE = (190, 142, 88)
SANDSTONE_LINE = (164, 118, 70)
CANDY_A = (255, 120, 164)
CANDY_B = (255, 236, 242)
FROSTING = (255, 196, 224)
SPRINKLES = ((255, 90, 90), (90, 200, 255), (255, 220, 70), (120, 230, 140), (190, 130, 255))
CRYSTAL_ROCK = (18, 42, 46)
CRYSTAL = (96, 244, 176)
CRYSTAL_TOP = (52, 184, 146)
CRYSTAL_SHINE = (196, 255, 228)
THEME_ACCENT = {
    "grass": (96, 190, 110),
    "lava": (255, 112, 38),
    "snow": (200, 226, 255),
    "sand": SAND,
    "candy": (255, 140, 190),
    "crystal": CRYSTAL,
    "lair": BUBBLE_EDGE,
}

# --- The Moon (watches you from the sky and whispers when you die) ---
MOON_POS = (672, 138)
MOON_RADIUS = 60
MOON_TALK_MS = 3400
MOON_FLASH_MS = 450
MOON_LINES = {
    "enemy": [
        "My junkies were starving. Thank you.",
        "Feel those teeth? That's MY smile.",
        "They bite. I told them to.",
        "One less life. I'm keeping it.",
        "Chewed up. Spit out. Again.",
        "The junkies say you taste like fear.",
        "I sent them for you. Only you.",
        "Every bite makes them hungrier.",
        "Crunch. I heard that from up here.",
        "They never stop. Neither do I.",
        "Your life belongs to the teeth now.",
        "Closer, little cat. They're waiting.",
    ],
    "fall": [
        "The dark below has no bottom.",
        "Fall forever. I'll watch.",
        "Something down there caught you.",
        "Nobody hears you scream down there.",
        "The void opened its mouth. You obeyed.",
        "Down you go. Into the black.",
        "Gravity is mine. So are you.",
        "Keep falling. It never ends.",
        "The pit whispers your name now.",
        "I let go of you. On purpose.",
        "Below the hills, hungry things wait.",
        "Your echo is still falling.",
    ],
    "any": [
        "I see you. I always see you.",
        "Nine lives. I'm collecting all of them.",
        "Don't look up. Too late.",
        "There is no morning here.",
        "I was here before the stars.",
        "Run, little cat. Run.",
        "I can hear your heart. Faster.",
        "Every death feeds me.",
        "Your lives are running out. Tick. Tock.",
        "Nobody escapes the night.",
        "I've been watching since level one.",
        "Soon it will be my turn to play.",
    ],
    "grass": [
        "The grass grows over your grave.",
        "Sleep in the grass. Forever.",
        "The hill remembers every fall.",
    ],
    "lava": [
        "Burn, little cat. Burn.",
        "The fire whispers my name.",
        "Ashes. Just like the last one.",
    ],
    "snow": [
        "Frozen. Like all the others.",
        "The cold has fingers. Feel them?",
        "Your paw prints end here.",
    ],
    "sand": [
        "The sand swallows everything.",
        "Buried. Nobody will find you.",
        "The dunes are made of lost cats.",
    ],
    "candy": [
        "Sweet treats rot the soul.",
        "Too sweet. Too dead.",
        "The candy is made of screams.",
    ],
    "crystal": [
        "The crystals keep your reflection.",
        "Trapped in the glass forever.",
        "Shine... then shatter.",
    ],
    "boss": [
        "Did you really think you could win?",
        "My sky. My rules. My cat.",
        "Dodge THIS. Oh wait, you didn't.",
        "You came all this way just to die.",
        "Kneel before the night.",
        "Again. I could do this forever.",
    ],
    "lair": [
        "Welcome to my lair. Stay forever.",
        "No one leaves my lair.",
        "The floor is still warm from the last cat.",
    ],
}
MOON_INTRO_LINES = [
    "So... you finally came to me.",
    "At last. Just you and me, little cat.",
    "You survived my hills. You won't survive ME.",
]
MOON_HURT_LINES = [
    "ARGH! You'll pay for that!",
    "You DARE touch me?!",
    "My face! MY BEAUTIFUL FACE!",
    "Impossible... a CAT?!",
    "That... actually hurt.",
]
MOON_ENRAGE_LINE = "Enough games. Now I'm ANGRY."
MOON_DEFEAT_LINE = "No... NO! The night... is ending..."

# --- Jumpscare between levels ---
SCARE_DARK_MS = 320
SCARE_FACE_MS = 1150
SCARE_FADE_MS = 380
SCARE_MAX_FACE_MS = 2600
SCARE_RADIUS = 205

# --- Background music (synthesized at startup, loops forever) ---
MUSIC_VOLUME = 0.45
MUSIC_FADE_MS = 1500
# Semitones above A4 (440 Hz); None is a rest. A creepy music-box lullaby in A harmonic minor.
LULLABY = [
    12, 15, 19, 18, 19, 15, 12, None, 11, 14, 17, 15, 14, 11, 7, None,
    12, 15, 19, 20, 19, 18, 15, 12, 14, 11, 8, 7, 6, 7, None, None,
]
BOSS_STABS = [12, None, 13, None, 12, None, 18, None, 12, None, 13, None, 19, 18, 13, None]
BOSS_BASS = [0, 0, 0, 1] * 8
SCARE_LINES = [
    "I SEE YOU",
    "YOU CAN'T HIDE",
    "RUN.",
    "I'M RIGHT BEHIND YOU",
    "DON'T LOOK UP",
    "THE NIGHT IS HUNGRY",
    "THERE IS NO ESCAPE",
    "COME CLOSER...",
]
SCARE_BOSS_LINE = "COME AND FACE ME"
# Evil laughs as (syllable, SSML pitch) sequences; the first one ends every jumpscare.
LAUGHS = [
    [("Mwa", "medium"), ("ha", "high"), ("ha", "high"), ("ha", "medium"), ("ha", "low"), ("ha", "x-low"), ("ha", "x-low")],
    [("Ha", "high"), ("ha", "medium"), ("ha", "medium"), ("ha", "low"), ("ha", "low"), ("ha", "x-low")],
    [("Heh", "low"), ("heh", "low"), ("heh", "x-low"), ("heh", "x-low"), ("heh", "x-low")],
]
LAUGH_DUCK = 0.3

# --- Final boss: the Moon itself ---
BOSS_HP = 5
BOSS_ENRAGE_HP = 2
BOSS_RADIUS = 56
BOSS_HOVER_Y = 150
BOSS_LOW_Y = 476
BOSS_FLOOR_Y = 540
BOSS_POINTS = 500
BOSS_ATTACKS_PER_DIVE = 3
BOSS_INTRO_FRAMES = 150
BOSS_DEATH_FRAMES = 180
LAIR_SKY = (22, 6, 12)
LAIR_HILL = (46, 12, 22)
LAIR_ROCK = (26, 10, 14)
LAIR_TOP = (132, 30, 40)
LAIR_CRACK = (255, 60, 40)
DIZZY_STAR = (255, 226, 110)

STATE_START = "start"
STATE_PLAY = "play"
STATE_WIN = "win"
STATE_OVER = "over"
STATE_SELECT = "select"
STATE_SCARE = "scare"


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
        {
            "name": "Dusty Dunes",
            "theme": "sand",
            "width": 3000,
            "spawn": (80, 400),
            "goal": (2850, 220),
            "platforms": [
                (0, 500, 380, 100),
                (470, 440, 150, 28),
                (700, 380, 140, 28),
                (930, 450, 200, 28),
                (1220, 380, 120, 28),
                (1560, 420, 180, 28),
                (1820, 350, 140, 28),
                (2040, 290, 140, 28),
                (2260, 360, 160, 28),
                (2700, 300, 300, 300),
            ],
            "movers": [
                (1360, 400, 100, 28, "x", 90, 1.4),
                (2500, 260, 120, 28, "y", 110, 1.2),
            ],
            "coins": [
                (200, 450),
                (530, 390),
                (760, 330),
                (1010, 400),
                (1270, 330),
                (1400, 350),
                (1640, 370),
                (1880, 300),
                (2100, 240),
                (2330, 310),
                (2550, 210),
                (2780, 250),
            ],
            "enemies": [
                (260, 468, 180, 380),
                (960, 418, 930, 1130),
                (1600, 388, 1560, 1740),
                (2290, 328, 2260, 2420),
            ],
        },
        {
            "name": "Sugar Rush",
            "theme": "candy",
            "width": 3200,
            "spawn": (80, 380),
            "goal": (3040, 200),
            "platforms": [
                (0, 480, 320, 120),
                (420, 420, 130, 28),
                (960, 340, 130, 28),
                (1180, 400, 150, 28),
                (1620, 300, 140, 28),
                (1850, 360, 120, 28),
                (2400, 260, 150, 28),
                (2640, 330, 130, 28),
                (2860, 280, 340, 320),
            ],
            "movers": [
                (620, 380, 110, 28, "x", 160, 1.8),
                (1420, 280, 110, 28, "y", 120, 1.3),
                (2040, 320, 100, 28, "x", 180, 2.0),
            ],
            "coins": [
                (160, 430),
                (470, 370),
                (680, 330),
                (820, 330),
                (1010, 290),
                (1240, 350),
                (1460, 230),
                (1680, 250),
                (1900, 310),
                (2100, 270),
                (2250, 270),
                (2460, 210),
                (2690, 280),
                (2950, 230),
            ],
            "enemies": [
                # x, y, patrol left, patrol right, speed
                (200, 448, 150, 320, 2.5),
                (980, 308, 960, 1090, 2.5),
                (1640, 268, 1620, 1760, 2.5),
                (2420, 228, 2400, 2550, 2.5),
            ],
        },
        {
            "name": "Crystal Caverns",
            "theme": "crystal",
            "width": 3400,
            "spawn": (70, 360),
            "goal": (3260, 200),
            "platforms": [
                (0, 460, 300, 140),
                (400, 400, 110, 28),
                (610, 330, 100, 28),
                (1000, 300, 150, 28),
                (1250, 360, 100, 28),
                (1810, 250, 140, 28),
                (2050, 320, 110, 28),
                (2260, 250, 110, 28),
                (2660, 280, 160, 28),
                (2910, 340, 110, 28),
                (3100, 280, 300, 320),
            ],
            "movers": [
                (800, 270, 100, 28, "y", 130, 1.5),
                (1430, 300, 100, 28, "x", 200, 2.2),
                (2460, 200, 110, 28, "y", 150, 1.6),
            ],
            "coins": [
                (140, 410),
                (440, 350),
                (645, 280),
                (835, 220),
                (1060, 250),
                (1285, 310),
                (1480, 250),
                (1640, 250),
                (1860, 200),
                (2090, 270),
                (2300, 200),
                (2500, 150),
                (2720, 230),
                (2950, 290),
                (3180, 230),
            ],
            "enemies": [
                (200, 428, 160, 300, 3.0),
                (1020, 268, 1000, 1150, 3.0),
                (1830, 218, 1810, 1950, 3.0),
                (2680, 248, 2660, 2820, 3.0),
            ],
        },
        {
            "name": "The Moon's Lair",
            "theme": "lair",
            "boss": True,
            "width": WIDTH,
            "spawn": (80, 480),
            "goal": None,
            "platforms": [
                (0, BOSS_FLOOR_Y, WIDTH, 60),
                (90, 405, 150, 22),
                (560, 405, 150, 22),
                (325, 280, 150, 22),
                # Invisible walls keep the fight on one screen.
                (-40, -400, 40, 1000),
                (WIDTH, -400, 40, 1000),
            ],
            "coins": [(156, 365), (626, 365), (391, 240)],
            "enemies": [],
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
    def __init__(self, x, y, left, right, speed=2.0):
        self.rect = pygame.Rect(int(x), int(y), 34, 32)
        self.x = float(self.rect.x)
        self.left = left
        self.right = right
        self.vx = speed
        self.chomp_phase = random.uniform(0, math.tau)

    def update(self):
        self.x += self.vx
        if self.x <= self.left:
            self.x = self.left
            self.vx = abs(self.vx)
        elif self.x + self.rect.w >= self.right:
            self.x = self.right - self.rect.w
            self.vx = -abs(self.vx)
        self.rect.x = round(self.x)


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


SINE_TABLE = [math.sin(i * math.tau / 4096) for i in range(4096)]


def note_freq(semitones):
    return 440 * 2 ** (semitones / 12)


def synth_track(seconds, rate, drones, notes, wind, seed, loop=True):
    """Mix a seamless loop (or a one-shot if loop=False): three drone sines, decaying notes and soft wind.

    drones: three (freq, amp) pairs whose freq * seconds is a whole number, so the loop has no click.
    notes: (start_sec, freq, amp, decay_sec, [(harmonic, amp), ...]).
    """
    n = int(seconds * rate)
    buf = [0.0] * n
    table = SINE_TABLE
    (f1, a1), (f2, a2), (f3, a3) = drones
    i1, i2, i3 = (f * 4096 / rate for f in (f1, f2, f3))
    swell_inc = 2 * 4096 / n
    p1 = p2 = p3 = swell = 0.0
    for i in range(n):
        p1 += i1
        p2 += i2
        p3 += i3
        swell += swell_inc
        v = a1 * table[int(p1) & 4095] + a2 * table[int(p2) & 4095] + a3 * table[int(p3) & 4095]
        buf[i] = v * (0.75 + 0.25 * table[int(swell) & 4095])

    for start, freq, amp, decay, harmonics in notes:
        i0 = int(start * rate)
        length = min(int(decay * 5 * rate), n)
        end = i0 + length if loop else min(i0 + length, n)
        fall = math.exp(-1 / (decay * rate))
        for mult, harm_amp in harmonics:
            inc = freq * mult * 4096 / rate
            phase = 0.0
            env = amp * harm_amp
            # Tails past the end wrap to the start so the loop point is seamless.
            for j in range(i0, end):
                phase += inc
                buf[j % n] += env * table[int(phase) & 4095]
                env *= fall

    if wind:
        rng = random.Random(seed)
        fade = rate // 10
        noise = []
        low = 0.0
        for _ in range(n + fade):
            low += (rng.uniform(-1, 1) - low) * 0.03
            noise.append(low)
        # Crossfade the extra tail into the start so the noise loops without a click.
        for i in range(fade):
            k = i / fade
            noise[i] = noise[i] * k + noise[n + i] * (1 - k)
        gust = 0.0
        for i in range(n):
            gust += swell_inc
            buf[i] += noise[i] * wind * (0.6 + 0.4 * table[int(gust) & 4095])
    return buf


def track_to_sound(buf, repeat):
    peak = max(abs(v) for v in buf) or 1.0
    scale = 0.85 * 32767 / peak
    ints = [int(v * scale) for v in buf]
    return pygame.mixer.Sound(buffer=array("h", [v for v in ints for _ in range(repeat)]).tobytes())


MUSIC_BOX = [(1, 1.0), (2, 0.3), (3, 0.12)]
THUMP = [(1, 1.0), (2, 0.4)]


def make_stinger(rate):
    """The jumpscare hit, built from the same instruments as the music: drone swell, clashing chord, boom, heartbeat."""
    seconds = 2.4
    drone = synth_track(seconds, rate, ((55, 0.5), (55.375, 0.45), (82.5, 0.25)), [], 3.0, 3, loop=False)
    n = len(drone)
    for i in range(n):
        drone[i] *= math.exp(-3 * i / n)
    notes = [(0.0, 40, 1.6, 0.45, THUMP)]
    for semi in (0, 1, 6, 12, 13, 18, 19):
        notes.append((0.0, note_freq(semi), 0.3, 0.7, MUSIC_BOX))
    for k, t in enumerate((0.7, 0.98, 1.5, 1.78)):
        notes.append((t, 48 - k % 2 * 4, 0.9 * (1 - k * 0.2), 0.07, THUMP))
    hits = synth_track(seconds, rate, ((0, 0), (0, 0), (0, 0)), notes, 0, 0, loop=False)
    return [a + b for a, b in zip(drone, hits)]


def laugh_ssml(syllables):
    """SSML for an evil laugh: each (syllable, pitch) is spoken quickly at its own pitch level."""
    parts = "".join(f"<prosody pitch='{pitch}'>{word}</prosody> " for word, pitch in syllables)
    return (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        f"<prosody rate='fast'>{parts}</prosody></speak>"
    )


def speak_lines(texts, rate):
    """Record {key: text or SSML} with the built-in Windows voice.

    Returns {key: (samples, sample_rate)}; empty if speech isn't available.
    """
    if sys.platform != "win32":
        return {}
    voices = {}
    with tempfile.TemporaryDirectory() as folder:
        paths = {key: os.path.join(folder, f"line{i}.wav") for i, key in enumerate(texts)}
        script = [
            "Add-Type -AssemblyName System.Speech",
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer",
            "$s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Male)",
            "$s.Rate = -2",
            f"$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo({rate}, "
            "[System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)",
        ]
        for key, path in paths.items():
            text = texts[key].replace("'", "''")
            speak = "SpeakSsml" if texts[key].startswith("<speak") else "Speak"
            script.append(f"$s.SetOutputToWaveFile('{path}', $fmt); $s.{speak}('{text}')")
        script.append("$s.Dispose()")
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", "; ".join(script)],
                capture_output=True,
                timeout=60,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, subprocess.SubprocessError):
            return {}
        for key, path in paths.items():
            try:
                with wave.open(path, "rb") as w:
                    if w.getsampwidth() != 2 or w.getnchannels() != 1:
                        continue
                    raw = array("h")
                    raw.frombytes(w.readframes(w.getnframes()))
                    loud = [i for i, v in enumerate(raw) if abs(v) > 650]
                    if not loud:
                        continue
                    pad = w.getframerate() // 40
                    clip = raw[max(0, loud[0] - pad):loud[-1] + pad]
                    voices[key] = ([v / 32768 for v in clip], w.getframerate())
            except (OSError, EOFError, wave.Error):
                continue
    return voices


def demonize(samples, src_rate, rate, pitch=0.92, growl=0.5, drive=1.8, echo=0.0):
    """Turn a plain recorded voice into the Moon's: deeper, growling and distorted.

    The defaults keep words understandable; laughs use a deeper pitch, more growl and an echo.
    """
    step = src_rate * pitch / rate
    count = int((len(samples) - 1) / step)
    deep = []
    for i in range(count):
        pos = i * step
        k = int(pos)
        deep.append(samples[k] + (samples[k + 1] - samples[k]) * (pos - k))
    growl_inc = 38 * 4096 / rate
    phase = 0.0
    voice = []
    for v in deep:
        phase += growl_inc
        voice.append(v * (1 - growl) + v * SINE_TABLE[int(phase) & 4095] * growl * 1.3)
    if echo:
        delay = int(0.11 * rate)
        voice += [0.0] * (delay * 4)
        for i in range(delay, len(voice)):
            voice[i] += voice[i - delay] * echo
    peak = max(abs(v) for v in voice) or 1.0
    return [math.tanh(v / peak * drive) for v in voice]


def build_audio(store):
    """Synthesize the music loops and the voiced jumpscares into store (runs on a background thread)."""
    init = pygame.mixer.get_init()
    if not init or init[1] != -16:
        return
    freq, _, channels = init
    factor = 2 if freq >= 32000 else 1
    rate = freq // factor
    repeat = channels * factor
    box = MUSIC_BOX
    thump = THUMP
    try:
        notes = []
        for step, semi in enumerate(LULLABY):
            if semi is not None:
                notes.append((step * 0.5, note_freq(semi), 0.22, 0.35, box))
        for beat in range(8):
            notes.append((beat * 2.0, 48, 0.9, 0.07, thump))
            notes.append((beat * 2.0 + 0.28, 44, 0.6, 0.07, thump))
        creep = synth_track(16, rate, ((55, 0.3), (55.375, 0.25), (82.5, 0.1)), notes, 4.0, 1)
        store["creep"] = track_to_sound(creep, repeat)

        notes = []
        for step, semi in enumerate(BOSS_STABS):
            if semi is not None:
                notes.append((step * 0.5, note_freq(semi), 0.18, 0.25, box))
        for step, semi in enumerate(BOSS_BASS):
            notes.append((step * 0.25, note_freq(semi - 24), 0.35, 0.16, [(1, 1.0), (2, 0.5), (3, 0.3)]))
        for beat in range(16):
            notes.append((beat * 0.5, 48, 0.9, 0.06, thump))
        boss = synth_track(8, rate, ((41.25, 0.3), (41.5, 0.25), (61.875, 0.12)), notes, 3.0, 2)
        store["boss"] = track_to_sound(boss, repeat)

        stinger = make_stinger(rate)
        store["scare"] = track_to_sound(stinger, repeat)
        start = int(0.35 * rate)
        ramp = int(0.03 * rate)
        gap = int(0.1 * rate)
        texts = {line: line.capitalize() for line in SCARE_LINES + [SCARE_BOSS_LINE]}
        texts.update({("laugh", i): laugh_ssml(syllables) for i, syllables in enumerate(LAUGHS)})
        recorded = speak_lines(texts, rate)
        laughs = [
            demonize(*recorded[("laugh", i)], rate, pitch=0.8, growl=0.7, drive=2.4, echo=0.35)
            for i in range(len(LAUGHS))
            if ("laugh", i) in recorded
        ]
        for line in SCARE_LINES + [SCARE_BOSS_LINE]:
            if line not in recorded:
                continue
            voice = demonize(*recorded[line], rate)
            end = start + len(voice)
            laugh = laughs[0] if laughs else []
            total = end + gap + len(laugh)
            mix = [0.0] * max(len(stinger), total)
            for i, v in enumerate(stinger):
                # The hit lands first, then the music nearly drops out while the Moon speaks and laughs.
                inside = min(i - (start - ramp), total + ramp - i) / ramp
                mix[i] = v * (0.55 - 0.47 * max(0.0, min(1.0, inside)))
            for i, v in enumerate(voice):
                mix[start + i] += v
            for i, v in enumerate(laugh):
                mix[end + gap + i] += v * 0.9
            store[("voice_ms", line)] = 1000 * end / rate
            store[("scare", line)] = track_to_sound(mix, repeat)
        store["laughs"] = [track_to_sound(laugh, repeat) for laugh in laughs]
    except pygame.error:
        pass


class Game:
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

    def moon_laugh(self):
        laughs = self.music.get("laughs")
        if self.muted or not laughs:
            return
        options = [s for s in laughs if s is not self.last_laugh] or laughs
        sound = random.choice(options)
        self.last_laugh = sound
        sound.play()
        self.duck_music(sound)

    def duck_music(self, sound):
        self.duck_until = pygame.time.get_ticks() + int(sound.get_length() * 1000)

    def moon_say(self, reason):
        options = MOON_LINES[reason] + MOON_LINES["any"] + MOON_LINES.get(self.theme, [])
        options = [line for line in options if line != self.last_moon_line]
        self.moon_speak(random.choice(options))

    def moon_speak(self, line):
        self.moon_line = line
        self.last_moon_line = line
        self.moon_until = pygame.time.get_ticks() + MOON_TALK_MS

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
            b.x += (WIDTH / 2 + 250 * math.sin(b.clock * drift) - b.x) * 0.06
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
                    b.dive_to = (max(300, min(p.rect.centerx, 500)), BOSS_LOW_Y)
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
            elif not (-40 < s.x < WIDTH + 40 and -60 < s.y < HEIGHT + 40):
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
                b.laser_x += (target.centerx - b.laser_x) * 0.25
            b.laser_on = b.laser_warn <= t < b.laser_warn + 28
            if t == b.laser_warn:
                self.add_shake(6, 26)
            if b.laser_on and t % 3 == 0:
                self.burst(b.laser_x, BOSS_FLOOR_Y, EYE_GLOW, count=3, speed=4)
            return t >= b.laser_warn + 40
        if b.attack == "meteors":
            if t == 1:
                count = 9 if b.enraged else 6
                xs = [target.centerx] + [random.uniform(30, WIDTH - 30) for _ in range(count - 1)]
                random.shuffle(xs)
                for i, x in enumerate(xs):
                    self.shots.append(BossShot(x, -40 - i * 60, 0, 3, "meteor"))
            return t >= 110
        if t == 20:
            speed = 3.0 if b.enraged else 2.2
            for x, direction in ((30, 1), (WIDTH - 64, -1)):
                walker = Walker(x, BOSS_FLOOR_Y - 32, 0, WIDTH, speed)
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

    def in_laser(self, rect):
        ex, ey, lx = self.laser_path()
        if rect.centery < ey:
            return False
        frac = (rect.centery - ey) / (BOSS_FLOOR_Y - ey)
        beam_x = ex + (lx - ex) * frac
        return abs(rect.centerx - beam_x) < 5 + 19 * frac + rect.w / 2 - 6

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
        x = round(b.x) + random.randint(-b.shake, b.shake) + self.shake_offset[0]
        y = round(b.y) + random.randint(-b.shake, b.shake) + self.shake_offset[1]
        speed = 8 if b.enraged else 3
        self.moon_glow.set_alpha(150 + int(105 * (0.5 + 0.5 * math.sin(t * speed))))
        self.screen.blit(self.moon_glow, self.moon_glow.get_rect(center=(x, y)))
        look = max(-1.0, min(1.0, (self.player.rect.centerx - x) / 250))
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
        ex, ey, lx = self.laser_path()
        ox, oy = self.shake_offset
        ex, ey, lx = ex + ox, ey + oy, lx + ox
        floor = BOSS_FLOOR_Y + oy
        if b.state == "attack" and b.attack == "laser" and not b.laser_on and b.timer < b.laser_warn:
            alpha = 70 + int(70 * (0.5 + 0.5 * math.sin(b.timer * 0.9)))
            pygame.draw.line(self.fx, (*EYE_GLOW, alpha), (ex, ey), (lx, floor), 3)
            pygame.draw.ellipse(self.fx, (*EYE_GLOW, alpha), (lx - 24, floor - 5, 48, 10), 2)
        if b.laser_on:
            pygame.draw.polygon(self.fx, (*EYE_GLOW, 200), [(ex - 5, ey), (ex + 5, ey), (lx + 24, floor), (lx - 24, floor)])
            pygame.draw.polygon(self.fx, (*EYE_CORE, 230), [(ex - 2, ey), (ex + 2, ey), (lx + 9, floor), (lx - 9, floor)])
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

    def draw_flash(self, color, alpha):
        if alpha <= 0:
            return
        self.overlay.fill(color)
        self.overlay.set_alpha(min(255, int(alpha)))
        self.screen.blit(self.overlay, (0, 0))

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
                self.draw_bubble(round(b.x), round(b.y), BOSS_RADIUS)
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

    def menu_buttons(self):
        if self.state == STATE_SELECT:
            return self.select_buttons()
        buttons = {}
        for i, name in enumerate(("play", "levels", "exit")):
            rect = pygame.Rect(0, 0, BUTTON_W, BUTTON_H)
            rect.center = (WIDTH // 2 + (i - 1) * (BUTTON_W + 20), 452)
            buttons[name] = rect
        return buttons

    def select_buttons(self):
        buttons = {}
        cols, card_w, card_h, gap = 4, 136, 118, 14
        left = (WIDTH - (cols * card_w + (cols - 1) * gap)) // 2
        for i, level in enumerate(self.levels):
            row, col = divmod(i, cols)
            span = 2 if level.get("boss") else 1
            width = span * card_w + (span - 1) * gap
            buttons[f"level{i}"] = pygame.Rect(left + col * (card_w + gap), 200 + row * (card_h + 14), width, card_h)
        back = pygame.Rect(0, 0, 150, 48)
        back.center = (WIDTH // 2, 494)
        buttons["back"] = back
        return buttons

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
        elif kind == "levels":
            if hovered:
                self.draw_glow(r, LEVELS_BTN, 14, 8, 130)
                pygame.draw.rect(self.screen, LEVELS_BTN, r, border_radius=14)
                text_color = PLAY_BTN_TEXT
            else:
                pygame.draw.rect(self.screen, MENU_PANEL, r, border_radius=14)
                pygame.draw.rect(self.screen, LEVELS_BTN, r, 3, border_radius=14)
                text_color = LEVELS_BTN
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

    def draw_menu(self, title, lines, accent, play_label, moon_mood):
        self.draw_panel(title, accent)

        t = pygame.time.get_ticks() / 1000
        mx, my, R = 694, 96, 50
        if moon_mood == "talk":
            mx += random.randint(-2, 2)
            my += random.randint(-2, 2)
            laugh = self.tiny.render("HA! HA! HA!", True, EYE_GLOW)
            self.screen.blit(laugh, laugh.get_rect(center=(mx + random.randint(-2, 2), my + R + 20)))
        else:
            my += round(math.sin(t * 1.2) * 3)
        if moon_mood != "dead":
            self.moon_glow.set_alpha(150 + int(105 * (0.5 + 0.5 * math.sin(t * 3))))
            self.screen.blit(self.moon_glow, self.moon_glow.get_rect(center=(mx, my)))
        look = max(-1.0, min(1.0, (pygame.mouse.get_pos()[0] - mx) / 250))
        self.draw_moon_face((mx, my), R, t, moon_mood, look)

        y = 218
        for i, line in enumerate(lines):
            color = accent if i == 0 else MENU_DIM
            s = self.font.render(line, True, color)
            self.screen.blit(s, s.get_rect(center=(WIDTH // 2, y)))
            y += 32

        hovered = self.button_at(pygame.mouse.get_pos())
        buttons = self.menu_buttons()
        self.draw_button(buttons["play"], play_label, "play", hovered == "play")
        self.draw_button(buttons["levels"], "Levels", "levels", hovered == "levels")
        self.draw_button(buttons["exit"], "Exit", "exit", hovered == "exit")

        hint = self.small.render("Enter to play  •  M to mute  •  Esc to quit", True, MENU_DIM)
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 514)))

    def draw_select(self):
        self.draw_panel("Choose a level", ACCENT_START)
        hovered = self.button_at(pygame.mouse.get_pos())
        t = pygame.time.get_ticks() / 1000
        for i, level in enumerate(self.levels):
            name = f"level{i}"
            card = self.select_buttons()[name]
            accent = THEME_ACCENT[level["theme"]]
            is_hover = hovered == name
            if is_hover:
                card = card.inflate(8, 8)
                self.draw_glow(card, accent, 14, 8, 140)
            pygame.draw.rect(self.screen, CARD_BG, card, border_radius=14)
            pygame.draw.rect(self.screen, accent, card, 3 if is_hover else 2, border_radius=14)

            if level.get("boss"):
                text_x = card.x + (card.w - 96) // 2
                num = self.button_font.render("Final Boss", True, accent)
                self.screen.blit(num, num.get_rect(midtop=(text_x, card.y + 22)))
                label = self.small.render(level["name"], True, WHITE if is_hover else MENU_DIM)
                self.screen.blit(label, label.get_rect(midtop=(text_x, card.y + 58)))
                mood = "talk" if is_hover else "idle"
                self.draw_moon_face((card.right - 54, card.centery), 38, t, mood, -0.6)
                continue

            num = self.button_font.render(f"Level {i + 1}", True, accent)
            self.screen.blit(num, num.get_rect(midtop=(card.centerx, card.y + 12)))
            label = self.tiny.render(level["name"], True, WHITE if is_hover else MENU_DIM)
            self.screen.blit(label, label.get_rect(midtop=(card.centerx, card.y + 48)))
            swatch = pygame.Rect(card.x + 12, card.bottom - 34, card.w - 24, 22)
            self.screen.set_clip(card.inflate(-6, -6))
            self.draw_floor(swatch, 1000 + i * 37, t, level["theme"])
            self.screen.set_clip(None)

        self.draw_button(self.select_buttons()["back"], "Back", "levels", hovered == "back")

    def draw_panel(self, title, accent):
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

    def draw_start(self):
        self.draw_menu(
            TITLE,
            [
                "Beware the moon. It is watching.",
                "Move with Left / Right  (or A / D)",
                "Jump with Space  (or Up / W)",
                "Press jump again mid-air to double jump",
                "Collect glowing coins  •  Stomp red walkers",
                f"Clear 6 hills, then defeat the Moon  •  {START_LIVES} lives",
            ],
            ACCENT_START,
            "Play",
            "idle",
        )

    def draw_win(self):
        self.draw_menu(
            "Victory!",
            [
                f"Final score: {self.score}",
                "The Moon is defeated. Morning comes.",
                "Think you can beat that score?",
            ],
            ACCENT_WIN,
            "Play again",
            "dead",
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
            "talk",
        )

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


if __name__ == "__main__":
    main()
