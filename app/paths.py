# Alle Pfade liegen relativ zum Programmordner (USB-tauglich, nichts in AppData).
import os, sys

def base_dir():
    if getattr(sys, "frozen", False):          # fertige EXE
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def p(*parts):
    return os.path.join(base_dir(), *parts)

def ensure(*parts):
    d = p(*parts)
    os.makedirs(d, exist_ok=True)
    return d
