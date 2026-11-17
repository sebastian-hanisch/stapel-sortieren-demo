"""Gemeinsame Einstellungen: der Wurzelordner steht im Importpfad."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
