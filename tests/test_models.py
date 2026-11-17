"""Zufallsmodelle: Zufallsgenerator, Ränge, Modell V an Handwerten, Zufallsproben im Band."""

import numpy as np
import pytest

import sts_counting as K
import sts_machine as M
import sts_models as Mo
from sts_rng import SplitMix64


def test_splitmix64_bekannte_werte():
    """Referenzwerte des SplitMix64 mit Zufalls-Seed 0 (Standard-Testvektor: 0xE220A8397B1DCDAF, 0x6E789E6AA1B965F4)."""
    r = SplitMix64(0)
    assert r.next_u64() == 0xE220A8397B1DCDAF and r.next_u64() == 0x6E789E6AA1B965F4


def test_zufallsfolge_ist_eine_permutation_und_haengt_nur_am_zufalls_seed():
    for n in (1, 2, 5, 10):
        p = Mo.zufallsfolge_uniform(SplitMix64(5), n)
        assert sorted(p) == list(range(1, n + 1))
    assert Mo.zufallsfolge_uniform(SplitMix64(5), 8) == Mo.zufallsfolge_uniform(SplitMix64(5), 8)
    assert Mo.zufallsfolge_uniform(SplitMix64(5), 8) != Mo.zufallsfolge_uniform(SplitMix64(6), 8)


def test_exp_tabelle_mal_d_ist_bitgleich_expovariate_d():
    """D · E mit E aus Mittel 1 ist dieselbe Zahl wie expovariate(D) desselben Stroms: alle D-Werte teilen sich die Zufallszahlen."""
    E = Mo.exp_tabelle(4, 5, 7)
    for d in (0.25, 1.0, 8.0):
        rng = SplitMix64(Mo.seed_modell_v(7, 4))
        erwartet = np.array([rng.expovariate(d) for _ in range(20)]).reshape(5, 4)
        assert (d * E == erwartet).all()


def test_exp_tabelle_mittelwert_ist_eins_im_band():
    E = Mo.exp_tabelle(10, 4000, 3)
    assert E.shape == (4000, 10) and (E > 0).all()
    assert abs(E.mean() - 1.0) < 4 / np.sqrt(E.size)         # Standardfehler des Mittels ist 1/sqrt(Zahl der Werte)


def test_raenge_handbeispiel():
    """Ankunft zu den Zeiten 0, 1, 2; Abfahrten 2,6 / 3,5 / 2,2. Reihenfolge der Abfahrten: Wagen 2 (2,2) zuerst, dann Wagen 0 (2,6), dann Wagen 1 (3,5):
    Ränge (2, 3, 1). Das ist das Muster 231: ein Stapel schafft diese Folge nicht."""
    ab = np.array([[2.6, 3.5, 2.2]])
    assert Mo.raenge(ab).tolist() == [[2, 3, 1]]
    assert not M.ist_sortierbar((2, 3, 1))
    assert Mo.sortierbar_anzahl(np.array([[2, 3, 1], [1, 2, 3], [3, 2, 1]])) == 2


def test_zeitgebunden_handbeispiel():
    """Wagen 0 fährt bei 1,5 ab, Wagen 1 (Ankunft 1) bei 2,5: die Aufenthalte [0; 1,5] und [1; 2,5] kreuzen sich (1 < 1,5 < 2,5): nicht gelingend. Fährt Wagen 1 bei 1,2 ab: genestet."""
    assert not Mo.zeitgebunden_maske(np.array([[2.6, 3.5, 2.2]]))[0]     # [0; 2,6] und [1; 3,5] kreuzen sich
    assert not Mo.zeitgebunden_maske(np.array([[1.5, 2.5]]))[0]
    assert Mo.zeitgebunden_maske(np.array([[1.5, 1.2]]))[0]
    assert Mo.zeitgebunden_maske(np.array([[0.5, 1.5]]))[0]       # disjunkt: 0 fährt ab, bevor 1 kommt


def test_d_sehr_klein_gibt_fast_alle_folgen_sortierbar():
    E = Mo.exp_tabelle(8, 3000, 9)
    klein = Mo.sortierbar_anzahl(Mo.raenge(Mo.abfahrten(E, 0.05))) / 3000
    assert klein >= 0.99


def test_zufallsprobe_uniform_exakter_wert_im_wilson_band():
    for n in (6, 8):
        k = Mo.zufallsprobe_uniform(n, 20000, 1301)
        lo, hi = Mo.wilson(k, 20000)
        assert lo <= float(K.anteil(n)) <= hi


def test_zufallsprobe_verzoegert_findet_nur_die_umkehrfolge():
    assert Mo.zufallsprobe_uniform(3, 6000, 5, "verzögert") in range(800, 1300)           # Erwartung 1000 = 6000/3!
    assert Mo.zufallsprobe_uniform(10, 2000, 5, "verzögert") == 0


def test_wilson_randwerte():
    lo, hi = Mo.wilson(0, 1000)
    assert lo == pytest.approx(0.0, abs=1e-12) and 0 < hi < 0.005
    lo, hi = Mo.wilson(1000, 1000)
    assert hi == pytest.approx(1.0, abs=1e-12) and 0.995 < lo < 1
