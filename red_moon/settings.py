"""Tunable constants: window, physics, colours, timings and game states."""

# --- Window & feel ---
WIDTH, HEIGHT = 800, 600
FPS = 60
TITLE = "The Red Moon"
# Title-screen Exit in the browser returns here. The desktop app still closes.
ARCADE_URL = "https://meltedlamp.github.io/melted-arcade/"

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
CHECK_POLE = (210, 230, 255)
CHECK_FLAG = (90, 190, 255)
CHECK_LIT = (80, 230, 160)
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
    "grave": (150, 170, 130),
    "lair": BUBBLE_EDGE,
}
GRAVE_DIRT = (36, 34, 30)
GRAVE_GRASS = (42, 52, 36)
GRAVE_SKY = (6, 7, 12)
GRAVE_HILL = (14, 16, 20)
STONE = (168, 164, 150)
STONE_EDGE = (96, 92, 84)
BUSH = (48, 120, 64)
BUSH_DARK = (24, 64, 36)
BUSH_LIGHT = (110, 176, 90)

# --- The Moon (watches you from the sky and whispers when you die) ---
MOON_POS = (672, 138)
MOON_RADIUS = 60
MOON_GROW = 12
MOON_GROW_STEPS = 3
MOON_TALK_MS = 3400
MOON_FLASH_MS = 450

# --- Jumpscare between levels ---
SCARE_DARK_MS = 320
SCARE_FACE_MS = 1150
SCARE_FADE_MS = 380
SCARE_MAX_FACE_MS = 2600
SCARE_RADIUS = 205

# --- Background music (synthesized at startup, loops forever) ---
MUSIC_VOLUME = 0.45
MUSIC_FADE_MS = 1500
LAUGH_DUCK = 0.3  # music volume multiplier while the Moon laughs

# --- Final boss: the Moon itself ---
BOSS_ARENA_WIDTH = 1800
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
STATE_PAUSE = "pause"
