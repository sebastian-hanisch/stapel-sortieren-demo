"""Zählen: Catalan-Zahlen und Anteile in Brüchen, Aufzählung aller Folgen, Zustandsrechnung für Wörter mit Zielgruppen (nur Standardbibliothek).

Zähleinheit überall: Folgen (Permutationen von 1…n) bzw. bei Zielgruppen verschiedene Wörter. Die Catalan-Zahlen selbst (erzeugende Funktion, Wachstum)
stehen in den Demos zum Abzählen; hier zählt der Anteil C(n)/n! und die Wörter mit Gleichständen."""

from fractions import Fraction
from functools import lru_cache
from itertools import permutations
from math import comb, factorial

import sts_machine as M


def catalan(n: int) -> int:
    return comb(2 * n, n) // (n + 1)


def anteil(n: int) -> Fraction:
    """Anteil der Folgen, die ein Stapel sortiert: C(n)/n! als exakter Bruch."""
    return Fraction(catalan(n), factorial(n))


def faktor_je_wagen(n: int) -> Fraction:
    """Anteil(n + 1) / Anteil(n) = 2(2n + 1) / ((n + 1)(n + 2))."""
    return Fraction(2 * (2 * n + 1), (n + 1) * (n + 2))


def einsvon(n: int) -> float:
    return factorial(n) / catalan(n)


def zaehle_aufzaehlung(n: int) -> int:
    """Maschine über alle n! Folgen (nur für kleine n)."""
    return sum(1 for p in permutations(range(1, n + 1)) if M.ist_sortierbar(p))


def menge_sortierbar(n: int) -> set[tuple[int, ...]]:
    return {p for p in permutations(range(1, n + 1)) if M.ist_sortierbar(p)}


def menge_erzeugbar(n: int) -> set[tuple[int, ...]]:
    return set(M.ausgaben_erzeugbar(n))


# ---------------------------------------------------------------------------------------------------------------------------------
# Wörter mit Zielgruppen
# ---------------------------------------------------------------------------------------------------------------------------------
def anzahl_woerter(gruppen) -> int:
    """Zahl der verschiedenen Wörter: n! geteilt durch das Produkt der g!."""
    z = factorial(sum(gruppen))
    for g in gruppen:
        z //= factorial(g)
    return z


def woerter(gruppen):
    """Alle verschiedenen Wörter: Wert v (1-basiert) kommt gruppen[v - 1]-mal vor. Erzeuger in lexikographischer Reihenfolge."""
    k = len(gruppen)
    n = sum(gruppen)
    rest = list(gruppen)
    wort: list[int] = []

    def rec():
        if len(wort) == n:
            yield tuple(wort)
            return
        for v in range(1, k + 1):
            if rest[v - 1]:
                rest[v - 1] -= 1
                wort.append(v)
                yield from rec()
                wort.pop()
                rest[v - 1] += 1

    yield from rec()


def wort_sortierbar(w) -> bool:
    """Maschine für Wörter: Ausgabe nichtfallend. Oben liegt der kleinste noch nicht ausgegebene Wert: hinaus."""
    offen: dict[int, int] = {}
    for x in w:
        offen[x] = offen.get(x, 0) + 1
    stapel: list[int] = []
    for x in w:
        stapel.append(x)
        while stapel:
            kleinster = min(v for v, c in offen.items() if c > 0)
            if stapel[-1] != kleinster:
                break
            offen[stapel.pop()] -= 1
    return not stapel


def zeuge_231_streng(w):
    """Erstes Vorkommen des Musters 231 mit strengen Ungleichungen (Plätze 1-basiert, Werte) oder None. Gleiche Werte bilden kein Muster."""
    n = len(w)
    for i in range(n):
        for j in range(i + 1, n):
            if w[j] > w[i]:
                for k in range(j + 1, n):
                    if w[k] < w[i]:
                        return (i + 1, j + 1, k + 1), (w[i], w[j], w[k])
    return None


def zaehle_woerter_zustand(gruppen) -> tuple[int, int]:
    """Zahl der sortierbaren Wörter und Zahl der besuchten Zustände, ohne Wörter aufzuzählen.

    Zustand = (Stapelinhalt, noch nicht gelesene Wagen je Wert). Nach jedem Lesen gibt die Maschine aus, was ausgegeben werden kann; die Fortsetzungen
    eines Zustands hängen nur vom Zustand ab und werden einmal gezählt. Ein Wert, der größer ist als die Spitze, würde einen kleineren Wagen
    blockieren: dieser Zweig zählt nicht."""
    k = len(gruppen)

    def ausgeben(stapel, rest):
        stapel = list(stapel)
        im_stapel = [0] * k
        for v in stapel:
            im_stapel[v - 1] += 1
        while stapel:
            kleinster = next((v for v in range(k) if rest[v] + im_stapel[v] > 0), None)
            if stapel[-1] != kleinster + 1:
                break
            im_stapel[stapel.pop() - 1] -= 1
        return tuple(stapel)

    @lru_cache(maxsize=None)
    def zaehle(stapel, rest):
        if not any(rest):
            return 0 if stapel else 1
        summe = 0
        for v in range(1, k + 1):
            if rest[v - 1] == 0:
                continue
            if stapel and v > stapel[-1]:
                continue
            neu_rest = rest[: v - 1] + (rest[v - 1] - 1,) + rest[v:]
            summe += zaehle(ausgeben(stapel + (v,), neu_rest), neu_rest)
        return summe

    start = tuple(gruppen)
    ergebnis = zaehle((), start)
    return ergebnis, zaehle.cache_info().currsize
