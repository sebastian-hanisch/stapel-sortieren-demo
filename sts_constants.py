"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# Experiment 1: ein Stapel von Hand
HAND_MAX = 10                       # längste Folge für Texteingabe und Zufallsfolge
DEFAULT_HAND_TEXT = "3, 1, 2, 5, 4"
HAND_ZUFALL_MIN, HAND_ZUFALL_MAX = 4, 10
DEFAULT_HAND_ZUFALL = 7
SCHRITT_MIN = 0

# Experiment 2: wie viele Folgen schafft ein Stapel
ANZAHL_N_MIN, ANZAHL_N_MAX, DEFAULT_ANZAHL_N = 3, 30, 6
AUFZAEHLUNG_MAX = 8                 # bis hierhin werden alle n! Folgen durchgespielt
ZUSTAND_MAX = 14                    # bis hierhin zählt die Zustandsrechnung, darüber nur die Formel in Brüchen
PROBE_N_MIN, PROBE_N_MAX, DEFAULT_PROBE_N = 1000, 50000, 20000
PROBE_SCHRITT = 1000
BETRIEBSARTEN = ("sofort", "verzögert")
DEFAULT_BETRIEB = "sofort"

# Experiment 3: sortieren oder erzeugen
RICHTUNG_N_MIN, RICHTUNG_N_MAX, DEFAULT_RICHTUNG_N = 3, 8, 6
AUSGESCHRIEBEN_MAX = 4              # bis hierhin stehen beide Mengen ausgeschrieben da

# Experiment 4: Wagen mit gleichem Ziel
GRUPPEN_MAX_ANZAHL = 6
GRUPPE_MAX_GROESSE = 5
GRUPPEN_MAX_WAGEN = 12
DEFAULT_GRUPPEN = "3, 2, 1"
AUFZAEHLUNG_WOERTER_MAX = 20000     # so viele Wörter werden zur Kontrolle durch die Maschine gespielt

# Experiment 5: Modell V
MODELL_N_MIN, MODELL_N_MAX, DEFAULT_MODELL_N = 4, 20, 10
D_WERTE = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0)
DEFAULT_D = 2.0
MODELL_RUNS_MIN, MODELL_RUNS_MAX, DEFAULT_MODELL_RUNS = 1000, 10000, 5000
MODELL_RUNS_SCHRITT = 1000
SEKUNDEN_JE_ZUFALLSZAHL = 38e-6     # Größenordnung des exakten Exponentialgenerators (eine CPU)

SEED_MAX, DEFAULT_SEED = 999999, 1301

# Farben
COLOR_OK = "#2F6B65"
COLOR_BAD = "#B5483A"
COLOR_NEUTRAL = "rgba(150,150,150,0.55)"
COLOR_LINE = "#4c78a8"
COLOR_LINE2 = "#e08a2c"
COLOR_BAND = "rgba(76,120,168,0.18)"

# Presets: jedes lädt ein vollständiges Beispiel; alle nicht genannten Regler gehen auf die Voreinstellung zurück.
PRESET_STANDARD = "Ein Stapel von Hand: sortierbar (3, 1, 2, 5, 4)"
PRESETS = {
    PRESET_STANDARD: {"hand_text": DEFAULT_HAND_TEXT},
    "… nicht sortierbar (2, 4, 1, 3, 5)": {"hand_text": "2, 4, 1, 3, 5"},
    "Wie viele Folgen? n = 10": {"anzahl_n": 10},
    "Sortieren oder Erzeugen? n = 3": {"richtung_n": 3},
    "Zielgruppen 2, 2, 2, 2": {"gruppen_text": "2, 2, 2, 2"},
    "Modell V: D = 1": {"modell_d": 1.0},
    "Modell V: D = 4": {"modell_d": 4.0},
    "Zeitbindung: D = 1": {"modell_d": 1.0, "modell_zeit": True},
}
PRESET_HELP = {
    PRESET_STANDARD: "Experiment 1: fünf Wagen (3, 1, 2, 5, 4); der Stapel schafft es, der höchste Stapel hat 2 Wagen.",
    "… nicht sortierbar (2, 4, 1, 3, 5)": "Experiment 1: die 4 liegt über der 2, die 2 muss aber zuerst hinaus; Zeuge für das Muster 231 an den Plätzen 1 bis 3.",
    "Wie viele Folgen? n = 10": "Experiment 2: 10 Wagen, 3 628 800 Folgen; wie viele davon sortiert ein Stapel?",
    "Sortieren oder Erzeugen? n = 3": "Experiment 3: bei 3 Wagen beide Mengen ausgeschrieben; 231 ist erzeugbar, aber nicht sortierbar, 312 umgekehrt.",
    "Zielgruppen 2, 2, 2, 2": "Experiment 4: 8 Wagen in vier Gruppen zu je 2 mit gleichem Ziel; gezählt werden verschiedene Wörter.",
    "Modell V: D = 1": "Experiment 5: ausgedachtes Ankunftsmodell, Wagen bleiben im Mittel 1 Ankunftsabstand; Anteil der Zufallsfolgen, die ein Stapel sortiert.",
    "Modell V: D = 4": "Experiment 5: Wagen bleiben im Mittel 4 Ankunftsabstände; der Anteil fällt deutlich.",
    "Zeitbindung: D = 1": "Experiment 5: wie D = 1, aber jeder Wagen verlässt den Stapel genau zu seiner Abfahrtszeit (keine Wahlfreiheit).",
}
