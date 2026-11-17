"""Literaturwerte (ORACLE-PLAYBOOK §5.1): nur Werte, die in einer eingesehenen Quelle stehen.

* Catalan-Zahlen 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796 (n = 1 bis 10): OEIS A000108, am 2026-11-17 im Wortlaut abgerufen.
* 2^(n−1) = 1, 2, 4, 8, 16, 32, 64 (Folgen, die ein Pop-Stack in einem Durchlauf sortiert, und hier: Folgen in beiden Mengen, Sortieren und Erzeugen): OEIS A011782, am 2026-11-17 abgerufen.
  Die Gleichheit beider Mengen für n ≤ 8 ist eine eigene Rechnung dieser Demo, keine Quellenaussage.
* Der Satz „ein Stapel mit Ausgabe zwischendurch sortiert genau die Folgen, die 231 vermeiden, ihre Zahl ist Catalan“: Bóna, „A survey of stack-sorting disciplines“, Electron. J. Combin. 9(2)
  (2003), #A1, Satz 1.3 (Seite 3); hier als Menge bis n = 9 nachgerechnet (tests/test_oracle_stapel_sortieren.py).
* Nicht eingesehen und darum kein Test: Knuth, TAOCP Bd. 1 § 2.2.1; Tarjan, JACM 1972."""

import sts_counting as K
import sts_machine as M


def test_catalan_gleich_oeis_a000108():
    assert [K.zaehle_aufzaehlung(n) for n in range(1, 9)] == [1, 2, 5, 14, 42, 132, 429, 1430]
    assert [K.catalan(n) for n in range(1, 11)] == [1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796]


def test_schnittmenge_gleich_oeis_a011782():
    from itertools import permutations

    for n in range(1, 8):
        erzeugbar = set(M.ausgaben_erzeugbar(n))
        beide = sum(1 for p in permutations(range(1, n + 1)) if M.ist_sortierbar(p) and p in erzeugbar)
        assert beide == [1, 2, 4, 8, 16, 32, 64][n - 1]
