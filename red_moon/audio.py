"""Builds all music loops, voiced jumpscares, laughs and Moon dialogue on a background thread."""

import pygame

from .dialogue import (
    LAUGHS, MOON_DEFEAT_LINE, MOON_ENRAGE_LINE, MOON_HURT_LINES, MOON_INTRO_LINES, MOON_LINES, SCARE_BOSS_LINE,
    SCARE_LINES,
)
from .synth import MUSIC_BOX, THUMP, make_stinger, note_freq, synth_track, track_to_sound
from .voice import demonize, laugh_ssml, speak_lines


# Semitones above A4 (440 Hz); None is a rest. A creepy music-box lullaby in A harmonic minor.
LULLABY = [
    12, 15, 19, 18, 19, 15, 12, None, 11, 14, 17, 15, 14, 11, 7, None,
    12, 15, 19, 20, 19, 18, 15, 12, 14, 11, 8, 7, 6, 7, None, None,
]
BOSS_STABS = [12, None, 13, None, 12, None, 18, None, 12, None, 13, None, 19, 18, 13, None]
BOSS_BASS = [0, 0, 0, 1] * 8
VOICE_BATCH = 16


def spoken(line):
    """Shouted words are written in capitals; lowercase them so the voice doesn't spell them out."""
    return " ".join(w.lower() if w.isupper() and len(w) > 1 else w for w in line.split())


def build_dialogue(store, rate, repeat):
    """Record every line the Moon says during play into store[("say", line)], a batch at a time."""
    lines = MOON_INTRO_LINES + [line for group in MOON_LINES.values() for line in group]
    lines = list(dict.fromkeys(lines + MOON_HURT_LINES + [MOON_ENRAGE_LINE, MOON_DEFEAT_LINE]))
    for i in range(0, len(lines), VOICE_BATCH):
        batch = lines[i:i + VOICE_BATCH]
        recorded = speak_lines({line: spoken(line) for line in batch}, rate)
        if not recorded:
            return
        for line in batch:
            if line in recorded:
                store[("say", line)] = track_to_sound(demonize(*recorded[line], rate), repeat)


def build_audio(store):
    """Synthesize the music, voiced jumpscares, laughs and Moon dialogue into store (runs on a background thread)."""
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
        build_dialogue(store, rate, repeat)
    except pygame.error:
        pass
