"""Everything the Moon says: death taunts, boss lines, jumpscare lines and its laughs."""

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

# --- Jumpscares between levels (shown on screen and spoken aloud) ---
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
