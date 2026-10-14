# Sprachausgabe: Piper-Stimmen ueber sherpa-onnx (offline). WAV-Dateien werden zwischengespeichert (cache\).
import os, hashlib, wave, sys, subprocess, shutil
import numpy as np
from paths import p, ensure

_KANDIDATEN = {"Ryan – männlich, tief": "en_US-ryan-medium", "Lessac – weiblich, klar": "en_US-lessac-medium"}
# Lessac liegt nur im privaten Aufbau. Seine Lizenz erlaubt keine Weitergabe, deshalb ist sie in der oeffentlichen Version nicht dabei.
VOICES = {k: v for k, v in _KANDIDATEN.items() if v == "en_US-ryan-medium" or os.path.isdir(p("voices", v))}
DE_LABEL = "Thorsten – Deutsch"
DE_VOICE = "de_DE-thorsten-medium"          # nur fuer den MP3-Export (deutsche Saetze)
ALL_VOICES = dict(VOICES); ALL_VOICES[DE_LABEL] = DE_VOICE
SR = 22050

def voice_dir(name):
    return p("voices", name)

def join_parts(name):
    """Grosse Stimmen liegen in Teilen (name.onnx.part1, part2 ...) und werden einmalig zusammengesetzt."""
    d = voice_dir(name); f = os.path.join(d, name + ".onnx")
    if os.path.exists(f):
        return True
    teile = sorted(x for x in (os.listdir(d) if os.path.isdir(d) else []) if x.startswith(name + ".onnx.part"))
    if not teile:
        return False
    tmp = f + ".tmp"
    with open(tmp, "wb") as out:
        for t in teile:
            with open(os.path.join(d, t), "rb") as src:
                shutil.copyfileobj(src, out)
    os.replace(tmp, f)
    return True

def espeak_dir(name):
    """Eigene espeak-Daten der Stimme, sonst die einer anderen Stimme (gleiche Daten fuer alle Sprachen)."""
    for n in [name] + list(VOICES.values()):
        e = os.path.join(voice_dir(n), "espeak-ng-data")
        if os.path.isdir(e):
            return e
    return os.path.join(voice_dir(name), "espeak-ng-data")

def voice_ok(name):
    d = voice_dir(name)
    return join_parts(name) and os.path.exists(os.path.join(d, "tokens.txt")) and os.path.isdir(espeak_dir(name))

def hoerhilfe(x, sr=SR, db_boost=4.0):
    """Hebt die hohen Toene (ca. 2,5-8 kHz) leicht an, gut bei Hochtonverlust."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1.0 / sr)
    t = np.clip((f - 2000.0) / 1500.0, 0, 1)
    g_db = db_boost * (t * t * (3 - 2 * t))
    g_db = np.where(f > 8000, db_boost * 0.5, g_db)
    y = np.fft.irfft(X * (10 ** (g_db / 20.0)), n=len(x)).astype(np.float32)
    return y

def _write(path, x):
    x = x / max(1e-6, float(np.abs(x).max())) * 0.9
    w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()

def wav_seconds(path):
    with wave.open(path) as w:
        return w.getnframes() / float(w.getframerate())

class Speaker:
    def __init__(self):
        self._tts = {}

    def _engine(self, name):
        if name not in self._tts:
            import sherpa_onnx as so
            d = voice_dir(name); join_parts(name)
            cfg = so.OfflineTtsConfig(model=so.OfflineTtsModelConfig(vits=so.OfflineTtsVitsModelConfig(
                model=os.path.join(d, name + ".onnx"), tokens=os.path.join(d, "tokens.txt"),
                data_dir=espeak_dir(name)), num_threads=4, provider="cpu"))
            self._tts[name] = so.OfflineTts(cfg)
        return self._tts[name]

    def wav_for(self, text, voice_label, speed=0.8, hoer=True):
        """Gibt den Pfad einer WAV-Datei fuer den Text zurueck (aus dem Cache oder neu erzeugt)."""
        name = ALL_VOICES[voice_label]
        key = hashlib.sha1(("%s|%s|%.2f|%d" % (text, name, speed, int(hoer))).encode("utf-8")).hexdigest()
        path = os.path.join(ensure("cache"), key + ".wav")
        if os.path.exists(path):
            return path
        a = self._engine(name).generate(text, sid=0, speed=float(speed))
        if not len(a.samples) or not a.sample_rate:
            raise RuntimeError("Keine Sprache erzeugt (Stimme %s, Text: %s)" % (name, text[:60]))
        x = np.array(a.samples, dtype=np.float32)
        if a.sample_rate != SR:
            x = np.interp(np.linspace(0, len(x), int(len(x) * SR / a.sample_rate), endpoint=False),
                          np.arange(len(x)), x).astype(np.float32)
        x = np.concatenate([x, np.zeros(int(SR * 0.15), dtype=np.float32)])
        if hoer:
            x = hoerhilfe(x)
        _write(path, x)
        return path

def play_async(path):
    """Spielt eine WAV-Datei ab (Windows: winsound, sonst aplay falls vorhanden)."""
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    elif shutil.which("aplay"):
        subprocess.Popen(["aplay", "-q", path])

def stop_play():
    if sys.platform == "win32":
        import winsound
        winsound.PlaySound(None, 0)


def wav_for_safe(speaker, text, voice_label, speed, hoer):
    return speaker.wav_for(text, voice_label, speed, hoer)
