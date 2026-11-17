"""Kennzahlen und Verdikte der fünf Experimente. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text).

Zähleinheit: Folgen (Permutationen), bei Zielgruppen verschiedene Wörter, bei Zufallsproben Zufallsfolgen."""

from dataclasses import dataclass
from fractions import Fraction
from math import factorial

import sts_constants as C
import sts_counting as K
import sts_format as F
import sts_machine as M
import sts_models as Mo


# ---------------------------------------------------------------------------------------------------------------------------------
# Experiment 1: ein Stapel von Hand
# ---------------------------------------------------------------------------------------------------------------------------------
def plaetze(p: tuple[int, int, int]) -> str:
    i, j, k = p
    if j == i + 1 and k == j + 1:
        return f"{i} bis {k}"
    return f"{i}, {j} und {k}"


def verdict_hand(l: M.Lauf) -> tuple[str, str]:
    """Verdikt für eine Folge: sortierbar mit höchstem Stapel, sonst Verstoß und Zeuge für das Muster 231."""
    f = F.folge(l.folge)
    if l.sortierbar:
        return "success", f"{f}: **sortierbar**, höchster Stapel {l.hoechster_stapel} Wagen. Die Folge vermeidet das Muster 231."
    (i, j, k), (y, x, g) = l.zeuge
    return "error", (f"{f}: **nicht sortierbar**. Die {x} (Platz {j}) liegt über der {y} (Platz {i}), aber die {y} muss vor der {x} hinaus; "
                     f"die {g} (Platz {k}) kommt erst später und muss noch vor der {y} hinaus. "
                     f"Zeuge für das Muster 231 an den Plätzen {plaetze((i, j, k))} (Werte {y}, {x}, {g}).")


# ---------------------------------------------------------------------------------------------------------------------------------
# Experiment 2: wie viele Folgen schafft ein Stapel
# ---------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Anzahl:
    n: int
    fakultaet: int
    sortierbar: int                 # Catalan(n)
    anteil: Fraction
    eins_von: float
    faktor: Fraction | None         # Anteil(n) / Anteil(n − 1)
    methode: str
    aufzaehlung: int | None         # Maschine über alle n! Folgen (nur n ≤ AUFZAEHLUNG_MAX)
    zustand: int | None             # Zustandsrechnung (nur n ≤ ZUSTAND_MAX)


def anzahl_zeile(n: int) -> Anzahl:
    c = K.catalan(n)
    auf = K.zaehle_aufzaehlung(n) if n <= C.AUFZAEHLUNG_MAX else None
    zust = K.zaehle_woerter_zustand((1,) * n)[0] if n <= C.ZUSTAND_MAX else None
    if auf is not None:
        methode = "alle Folgen durchgespielt, Zustandsrechnung und Formel stimmen überein"
    elif zust is not None:
        methode = "Zustandsrechnung und Formel stimmen überein"
    else:
        methode = "nur die Formel (zu viele Folgen zum Durchspielen)"
    faktor = K.anteil(n) / K.anteil(n - 1) if n >= 2 else None
    return Anzahl(n, factorial(n), c, K.anteil(n), K.einsvon(n), faktor, methode, auf, zust)


def tabelle_anzahl(n_bis: int, betriebsart: str) -> list[dict]:
    """Zeilen n = 3 … n_bis: Folgen, sortierbar (je nach Betriebsart), Anteil, „1 von x“, Faktor je zusätzlichem Wagen."""
    zeilen = []
    for n in range(C.ANZAHL_N_MIN, n_bis + 1):
        def schafft(m):
            return K.catalan(m) if betriebsart == "sofort" else 1

        anteil = Fraction(schafft(n), factorial(n))
        vorher = Fraction(schafft(n - 1), factorial(n - 1))
        zeilen.append({"n": n, "folgen": factorial(n), "sortierbar": schafft(n), "anteil": anteil, "eins_von": factorial(n) / schafft(n),
                       "faktor": anteil / vorher})
    return zeilen


def zufallsprobe(n: int, runs: int, seed: int, betriebsart: str) -> dict:
    k = Mo.zufallsprobe_uniform(n, runs, seed, betriebsart)
    lo, hi = Mo.wilson(k, runs)
    exakt = float(K.anteil(n)) if betriebsart == "sofort" else 1 / factorial(n)
    se = (exakt * (1 - exakt) / runs) ** 0.5
    return {"n": n, "runs": runs, "seed": seed, "treffer": k, "anteil": k / runs, "lo": lo, "hi": hi, "exakt": exakt,
            "abstand_se": (k / runs - exakt) / se if se > 0 else 0.0, "im_band": lo <= exakt <= hi, "betriebsart": betriebsart}


def verdict_anzahl(z: Anzahl, probe: dict | None, betriebsart: str) -> tuple[str, str]:
    kopf = (f"n = {z.n}: {F.ganz(z.sortierbar)} von {F.ganz(z.fakultaet)} Folgen "
            f"({F.prozent_signifikant(float(z.anteil))}, 1 von {F.eins_von(z.eins_von)}) sortiert ein Stapel mit Ausgabe zwischendurch.")
    teile = [kopf]
    if z.faktor is not None:
        teile.append(f"Der Anteil von n = {z.n - 1} auf n = {z.n} ändert sich um den Faktor {F.bruch(z.faktor)} = {F.dez(float(z.faktor), 3)}.")
    teile.append("Muss erst alles eingelagert werden und dann ausgegeben, sortiert der Stapel genau eine Folge, die Umkehrfolge "
                 f"({z.n}, …, 1): Anteil 1/{F.ganz(z.fakultaet)}.")
    if probe is not None:
        a = "sofort" if betriebsart == "sofort" else "verzögert"
        band = "im" if probe["im_band"] else "außerhalb des"
        teile.append(f"Zufallsprobe (Betriebsart {a}, {F.ganz(probe['runs'])} Zufallsfolgen, Zufalls-Seed {probe['seed']}): "
                     f"{F.ganz(probe['treffer'])} Treffer, {F.dez(probe['anteil'] * 100, 3)} %; der exakte Wert {F.dez(probe['exakt'] * 100, 3)} % liegt {band} Wilson-Band "
                     f"({F.dez(probe['lo'] * 100, 3)} bis {F.dez(probe['hi'] * 100, 3)} %).")
    return "info", " ".join(teile)


# ---------------------------------------------------------------------------------------------------------------------------------
# Experiment 3: sortieren oder erzeugen
# ---------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Vergleich:
    n: int
    sortierbar: frozenset
    erzeugbar: frozenset
    beide: frozenset
    nur_sortierbar: frozenset
    nur_erzeugbar: frozenset
    inverse_gleich: bool            # {Inverse von p : p sortierbar} == erzeugbar
    zweihochn: int                  # 2^(n−1)


def vergleich(n: int) -> Vergleich:
    s = frozenset(K.menge_sortierbar(n))
    e = frozenset(K.menge_erzeugbar(n))
    return Vergleich(n, s, e, s & e, s - e, e - s, {M.inverse(p) for p in s} == set(e), 2 ** (n - 1))


def verdict_richtung(v: Vergleich) -> tuple[str, str]:
    gleich = "gleich viele" if len(v.sortierbar) == len(v.erzeugbar) else "verschieden viele"
    inv = "Die Inverse jeder sortierbaren Folge ist erzeugbar und umgekehrt" if v.inverse_gleich else "Die Inverse-Beziehung gilt hier NICHT"
    return "warning", (f"n = {v.n}: {F.ganz(len(v.sortierbar))} Folgen sortierbar, {F.ganz(len(v.erzeugbar))} erzeugbar ({gleich}), aber nur {F.ganz(len(v.beide))} = 2^{v.n - 1} "
                       f"in beiden Mengen. {F.ganz(len(v.nur_sortierbar))} Folgen sortiert der Stapel, ohne dass er sie erzeugen kann, und {F.ganz(len(v.nur_erzeugbar))} umgekehrt. "
                       f"{inv} (alle Folgen mit n = {v.n}). Die Zahl allein zeigt die Richtung nicht: nur die Mengen unterscheiden sich.")


# ---------------------------------------------------------------------------------------------------------------------------------
# Experiment 4: Wagen mit gleichem Ziel
# ---------------------------------------------------------------------------------------------------------------------------------
def parse_gruppen(text: str) -> tuple[tuple[int, ...] | None, str | None]:
    teile = [t for t in text.replace(";", " ").replace(",", " ").split() if t]
    if not teile:
        return None, "Bitte Gruppengrößen eingeben, zum Beispiel 2, 2, 2, 2."
    try:
        g = tuple(int(t) for t in teile)
    except ValueError:
        return None, "Die Gruppengrößen müssen ganze Zahlen sein, getrennt durch Komma, Semikolon oder Leerzeichen."
    if len(g) > C.GRUPPEN_MAX_ANZAHL:
        return None, f"Höchstens {C.GRUPPEN_MAX_ANZAHL} Gruppen."
    if any(x < 1 or x > C.GRUPPE_MAX_GROESSE for x in g):
        return None, f"Jede Gruppe hat 1 bis {C.GRUPPE_MAX_GROESSE} Wagen."
    if sum(g) > C.GRUPPEN_MAX_WAGEN:
        return None, f"Höchstens {C.GRUPPEN_MAX_WAGEN} Wagen insgesamt (hier {sum(g)})."
    return g, None


@dataclass(frozen=True)
class GruppenAnalyse:
    gruppen: tuple[int, ...]
    n: int
    woerter: int
    sortierbar: int
    zustaende: int
    anteil: Fraction
    verschiedene: Fraction              # Anteil bei lauter verschiedenen Wagen: C(n)/n!
    sortierbar_absteigend: int          # Zahl bei absteigend geordneten Gruppengrößen
    kontrolle: int | None               # Zahl durch Durchspielen der Maschine (nur bis AUFZAEHLUNG_WOERTER_MAX Wörter)
    beispiel: tuple | None              # (Wort, Zeuge) eines unsortierbaren Wortes


def beispiel_unsortierbar(gruppen):
    """Ein unsortierbares Wort mit dem Zeugen für das strenge Muster 231: 2, 3, 1 und dann der Rest aufsteigend (braucht mindestens drei Gruppen)."""
    if len(gruppen) < 3:
        return None
    rest = []
    for v, g in enumerate(gruppen, start=1):
        rest += [v] * (g - (1 if v <= 3 else 0))
    wort = (2, 3, 1) + tuple(sorted(rest))
    return wort, K.zeuge_231_streng(wort)


def gruppen_analyse(gruppen: tuple[int, ...]) -> GruppenAnalyse:
    n = sum(gruppen)
    w = K.anzahl_woerter(gruppen)
    z, zustaende = K.zaehle_woerter_zustand(gruppen)
    absteigend, _ = K.zaehle_woerter_zustand(tuple(sorted(gruppen, reverse=True)))
    kontrolle = None
    if w <= C.AUFZAEHLUNG_WOERTER_MAX:
        kontrolle = sum(1 for wort in K.woerter(gruppen) if K.wort_sortierbar(wort))
    return GruppenAnalyse(gruppen, n, w, z, zustaende, Fraction(z, w), K.anteil(n), absteigend, kontrolle, beispiel_unsortierbar(gruppen))


def verdict_gruppen(a: GruppenAnalyse) -> tuple[str, str]:
    g = ", ".join(str(x) for x in a.gruppen)
    verschieden = K.catalan(a.n)
    text = (f"Gruppen {g} (n = {a.n}): {F.ganz(a.sortierbar)} von {F.ganz(a.woerter)} verschiedenen Wörtern sortierbar ({F.prozent(float(a.anteil), 2)}), "
            f"gegen {F.ganz(verschieden)} von {F.ganz(factorial(a.n))} ({F.prozent_signifikant(float(a.verschiedene))}) bei lauter verschiedenen Wagen (Folgen statt Wörter, anderes Maß). ")
    if len(a.gruppen) <= 2:
        text += "Mit höchstens zwei verschiedenen Werten sind alle Wörter sortierbar, denn das Muster 231 braucht drei verschiedene Werte. "
    elif all(x == 1 for x in a.gruppen):
        text += "Das sind lauter verschiedene Wagen: die Zahl ist Catalan. "
    else:
        text += "Die Zahl ist nicht Catalan und hängt an den Gruppengrößen. "
    text += (f"Bei absteigend geordneten Gruppengrößen sind es {F.ganz(a.sortierbar_absteigend)}"
             + (" (gleich)." if a.sortierbar_absteigend == a.sortierbar else " (anders!)."))
    return "info", text


# ---------------------------------------------------------------------------------------------------------------------------------
# Experiment 5: Modell V
# ---------------------------------------------------------------------------------------------------------------------------------
def schaetze_sekunden(n: int, runs: int) -> float:
    return n * runs * C.SEKUNDEN_JE_ZUFALLSZAHL


def modell_tabelle(n: int, runs: int, seed: int) -> list[dict]:
    """Je D: Anteil der Zufallsfolgen, die ein Stapel nach der Rangfolge der Abfahrten sortiert, und Anteil bei festem Abholzeitpunkt (zeitgebunden)."""
    E = Mo.exp_tabelle(n, runs, seed)
    zeilen = []
    for d in C.D_WERTE:
        ab = Mo.abfahrten(E, d)
        k = Mo.sortierbar_anzahl(Mo.raenge(ab))
        kz = int(Mo.zeitgebunden_maske(ab).sum())
        lo, hi = Mo.wilson(k, runs)
        loz, hiz = Mo.wilson(kz, runs)
        zeilen.append({"d": d, "k": k, "anteil": k / runs, "lo": lo, "hi": hi, "kz": kz, "anteil_z": kz / runs, "lo_z": loz, "hi_z": hiz})
    return zeilen


def verdict_modell(zeile: dict, n: int, runs: int, seed: int, zeit: bool) -> tuple[str, str]:
    exakt = float(K.anteil(n))
    d = F.dez(zeile["d"], 2).rstrip("0").rstrip(",")
    text = (f"n = {n}, nur Rangfolge der Abfahrten (der Stapel gibt frei aus): {F.dez(zeile['anteil'] * 100, 1)} % der Zufallsfolgen sind sortierbar "
            f"bei D = {d} (Band {F.dez(zeile['lo'] * 100, 1)} bis {F.dez(zeile['hi'] * 100, 1)} %, {F.ganz(runs)} Zufallsfolgen, Zufalls-Seed {seed}); "
            f"bei lauter gleich wahrscheinlichen Folgen sind es {F.prozent_signifikant(exakt)}. ")
    if zeit:
        text += (f"Bei festem Abholzeitpunkt (jeder Wagen verlässt den Stapel genau zu seiner Abfahrtszeit) sind es nur {F.dez(zeile['anteil_z'] * 100, 1)} % "
                 f"(Band {F.dez(zeile['lo_z'] * 100, 1)} bis {F.dez(zeile['hi_z'] * 100, 1)} %). ")
    text += "Ausgedachtes Modell, keine reale Ankunftsfolge."
    return "info", text
