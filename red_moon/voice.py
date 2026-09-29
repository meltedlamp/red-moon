"""The Moon's voice: records lines with the built-in Windows speech engine and makes them sound evil."""

import math
import os
import subprocess
import sys
import tempfile
import wave
from array import array

from .synth import SINE_TABLE


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
