"""Das ausgedachte Ankunftsmodell: Zufallsfolgen, die ein Stapel sortiert (numpy und Standardbibliothek; Zufall nur über sts_rng).

**Modell, kein Fall.** Es gibt keine gemessene Ankunftsfolge hinter diesen Rechnungen; sie sind ausgedacht.

* Modell U: alle n! Folgen gleich wahrscheinlich.
* Modell V: Wagen i (i = 0…n−1) kommt zur Zeit i an und bleibt eine exponentialverteilte Zeit mit Mittel D (in Ankunftsabständen);
  Abfahrtszeit = i + Verweilzeit; der Abholrang eines Wagens ist seine Position in der Reihenfolge der Abfahrten. Das Modell benutzt **nur die Rangfolge**
  der Abfahrten; der Stapel darf frei ausgeben. Wird der Abholzeitpunkt festgehalten („zeitgebunden“: jeder Wagen verlässt den Stapel genau zu seiner
  Abfahrtszeit), ist das eine eigene Fassung dieses Modells.

Alle Verweilzeiten einer Rechnung kommen aus einer Tabelle von Exponentialzahlen mit Mittel 1; ein Wert von D skaliert sie (D · E ist bitgleich
`expovariate(D)` desselben Stroms), so teilen sich alle D-Werte dieselben Zufallszahlen."""

import math

import numpy as np

import sts_machine as M
from sts_rng import SplitMix64


def zufallsfolge_uniform(rng: SplitMix64, n: int) -> tuple[int, ...]:
    p = list(range(1, n + 1))
    rng.shuffle(p)
    return tuple(p)


def seed_uniform(seed: int, n: int) -> int:
    return seed + n


def seed_modell_v(seed: int, n: int) -> int:
    return seed * 1000 + n


def zufallsprobe_uniform(n: int, runs: int, seed: int, betriebsart: str = "sofort") -> int:
    """Zahl der Zufallsfolgen (von `runs`), die der Stapel sortiert; Betriebsart „verzögert“: nur die Umkehrfolge (n, …, 1)."""
    rng = SplitMix64(seed_uniform(seed, n))
    treffer = 0
    for _ in range(runs):
        p = zufallsfolge_uniform(rng, n)
        if betriebsart == "verzögert":
            treffer += all(p[i] > p[i + 1] for i in range(n - 1))
        else:
            treffer += M.ist_sortierbar(p)
    return treffer


def exp_tabelle(n: int, runs: int, seed: int) -> np.ndarray:
    """runs × n Exponentialzahlen mit Mittel 1 (exakter SplitMix64, auf jeder Plattform bitgleich)."""
    rng = SplitMix64(seed_modell_v(seed, n))
    werte = [rng.expovariate(1.0) for _ in range(runs * n)]
    return np.array(werte, dtype=float).reshape(runs, n)


def abfahrten(E: np.ndarray, D: float) -> np.ndarray:
    """Abfahrtszeit je Wagen: Ankunft i + Verweilzeit D · E."""
    n = E.shape[1]
    return np.arange(n, dtype=float)[None, :] + D * E


def raenge(ab: np.ndarray) -> np.ndarray:
    """Rang = Position in der Reihenfolge der Abfahrten (1 = fährt zuerst ab)."""
    ordnung = np.argsort(ab, axis=1, kind="stable")
    r = np.empty_like(ordnung)
    zeilen = np.arange(ab.shape[0])[:, None]
    r[zeilen, ordnung] = np.arange(1, ab.shape[1] + 1)[None, :]
    return r


def sortierbar_anzahl(r: np.ndarray) -> int:
    return sum(1 for zeile in r.tolist() if M.ist_sortierbar(zeile))


def zeitgebunden_maske(ab: np.ndarray) -> np.ndarray:
    """Ein Wagen verlässt den Stapel genau zu seiner Abfahrtszeit und muss dann oben liegen. Das gelingt genau dann, wenn sich keine zwei Aufenthalte
    kreuzen: kein Paar i < j mit j < ab_i < ab_j (Wagen j kommt, solange i liegt, und fährt nach i ab)."""
    n = ab.shape[1]
    ok = np.ones(ab.shape[0], dtype=bool)
    for i in range(n):
        for j in range(i + 1, n):
            ok &= ~((ab[:, i] > j) & (ab[:, i] < ab[:, j]))
    return ok


def zeitgebunden_ok_simulation(ab_zeile) -> bool:
    """Gleiche Frage durch Nachspielen der Ereignisse (Orakel der Maske): Ankunft i zur Zeit i, Abfahrt zur Abfahrtszeit, Abgabe nur von oben."""
    n = len(ab_zeile)
    ereignisse = [(float(i), 0, i) for i in range(n)] + [(float(ab_zeile[i]), 1, i) for i in range(n)]
    ereignisse.sort()
    stapel: list[int] = []
    for _, art, i in ereignisse:
        if art == 0:
            stapel.append(i)
        else:
            if not stapel or stapel[-1] != i:
                return False
            stapel.pop()
    return True


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson-Band (Anteil, 95 %) für k Treffer in n Versuchen."""
    p = k / n
    d = 1 + z * z / n
    mitte = (p + z * z / (2 * n)) / d
    halb = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return mitte - halb, mitte + halb
