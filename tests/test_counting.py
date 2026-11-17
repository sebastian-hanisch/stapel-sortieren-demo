"""Zählen an Handrechnungen: Catalan, Anteile in Brüchen, Wörter mit Zielgruppen."""

from fractions import Fraction
from itertools import permutations
from math import factorial

import pytest

import sts_counting as K
import sts_machine as M


def test_catalan_rekursion_von_hand_n_5():
    """C(5) = 1·14 + 1·5 + 2·2 + 5·1 + 14·1 = 42."""
    assert 1 * 14 + 1 * 5 + 2 * 2 + 5 * 1 + 14 * 1 == K.catalan(5) == 42
    assert [K.catalan(n) for n in range(1, 11)] == [1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796]
    assert all(sum(K.catalan(k) * K.catalan(n - 1 - k) for k in range(n)) == K.catalan(n) for n in range(1, 13))


def test_anteile_als_brueche():
    assert K.anteil(5) == Fraction(7, 20) and K.anteil(6) == Fraction(11, 60) and K.anteil(8) == Fraction(143, 4032)
    assert K.faktor_je_wagen(9) == Fraction(19, 55)
    assert K.anteil(10) / K.anteil(9) == Fraction(19, 55)


def test_faktor_je_wagen_gleich_anteilsquotient_fuer_n_1_bis_29():
    assert all(K.anteil(n + 1) / K.anteil(n) == K.faktor_je_wagen(n) for n in range(1, 30))


def test_einsvon_n_10():
    assert K.einsvon(10) == pytest.approx(216.05, abs=0.005)


def test_aufzaehlung_n_gleich_catalan_bis_7():
    for n in range(1, 8):
        assert K.zaehle_aufzaehlung(n) == K.catalan(n)


def test_zustandsrechnung_lauter_verschiedene_gleich_catalan_bis_14():
    for n in range(1, 15):
        assert K.zaehle_woerter_zustand((1,) * n)[0] == K.catalan(n)


def test_anzahl_woerter_von_hand():
    assert K.anzahl_woerter((2, 1, 1)) == 12                 # 4!/2!
    assert K.anzahl_woerter((2, 2, 2, 2)) == 2520            # 8!/16
    assert K.anzahl_woerter((5, 5)) == 252                   # 10!/(5!·5!)
    assert K.anzahl_woerter((1,) * 5) == 120


def test_woerter_aufzaehlung_hat_keine_doppelten():
    w = list(K.woerter((2, 1, 1)))
    assert len(w) == len(set(w)) == 12 and sorted(w) == w


def test_gruppen_2_1_1_von_hand():
    """Wörter aus 1, 1, 2, 3: unsortierbar sind genau die mit 2 vor 3 und einer 1 hinter der 3: 2311, 2131, 1231 (von 6 Wörtern mit 2 vor 3 haben 3 eine 1 hinter der 3)."""
    woerter = list(K.woerter((2, 1, 1)))
    unsortierbar = [w for w in woerter if not K.wort_sortierbar(w)]
    assert sorted("".join(map(str, w)) for w in unsortierbar) == ["1231", "2131", "2311"]
    assert K.zaehle_woerter_zustand((2, 1, 1))[0] == 9
    assert len([w for w in woerter if w.index(2) < w.index(3)]) == 6


def test_zustandsrechnung_bekannte_werte():
    assert K.zaehle_woerter_zustand((2, 2, 2))[0] == 43 and K.anzahl_woerter((2, 2, 2)) == 90
    assert K.zaehle_woerter_zustand((3, 2, 1))[0] == 34 and K.anzahl_woerter((3, 2, 1)) == 60


def test_zwei_gruppen_sind_immer_sortierbar_weil_231_drei_werte_braucht():
    for g in [(5, 5), (3, 4), (1, 5), (2, 2)]:
        assert K.zaehle_woerter_zustand(g)[0] == K.anzahl_woerter(g)
    assert K.zaehle_woerter_zustand((5,))[0] == 1


def test_zeuge_231_streng_gleiche_werte_bilden_kein_muster():
    assert K.zeuge_231_streng((2, 2, 1)) is None             # 2, 2, 1: zweite 2 ist nicht größer
    assert K.zeuge_231_streng((2, 3, 1)) == ((1, 2, 3), (2, 3, 1))
    assert K.zeuge_231_streng((1, 1, 2, 2)) is None


def test_menge_sortierbar_und_erzeugbar_n_3():
    alle = set(permutations((1, 2, 3)))
    assert K.menge_sortierbar(3) == alle - {(2, 3, 1)}
    assert K.menge_erzeugbar(3) == alle - {(3, 1, 2)}


def test_wort_sortierbar_stimmt_mit_der_folgenmaschine_bei_lauter_verschiedenen_ueberein():
    for p in permutations(range(1, 6)):
        assert K.wort_sortierbar(p) == M.ist_sortierbar(p)
