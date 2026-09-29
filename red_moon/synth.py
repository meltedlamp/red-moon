"""A tiny software synthesizer: sine oscillators, decaying notes, wind, and the jumpscare stinger."""

import math
import random
from array import array

import pygame


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
