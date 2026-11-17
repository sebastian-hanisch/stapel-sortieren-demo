"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen: n = 0, 1, 2, einzelne Gruppe, Reglergrenzen, ungültige Eingabe."""

import pytest

import sts_counting as K
import sts_evaluation as ev
import sts_machine as M
import sts_models as Mo


def test_n_gleich_0_1_2_alle_folgen_sortierbar():
    assert K.catalan(0) == 1 and K.zaehle_aufzaehlung(0) == 1
    assert K.zaehle_aufzaehlung(1) == 1 and K.zaehle_aufzaehlung(2) == 2 == K.catalan(2)
    assert K.menge_erzeugbar(2) == {(1, 2), (2, 1)}


def test_n_gleich_3_ist_der_kleinste_fall_mit_unsortierbarer_folge():
    assert K.zaehle_aufzaehlung(3) == 5 < 6


def test_eine_einzige_gruppe_und_zwei_gruppen_sind_zu_100_prozent_sortierbar():
    for g in [(1,), (4,), (5,), (1, 1), (5, 5), (3, 2)]:
        a = ev.gruppen_analyse(g)
        assert a.sortierbar == a.woerter, g


def test_gruppen_grenzen_inklusive():
    assert ev.parse_gruppen("5, 5, 2")[0] == (5, 5, 2)            # genau 12 Wagen
    assert ev.parse_gruppen("1, 1, 1, 1, 1, 1")[0] == (1,) * 6     # genau 6 Gruppen
    assert ev.parse_gruppen("5, 5, 3")[0] is None                  # 13 Wagen
    assert ev.parse_gruppen("1")[0] == (1,) and ev.parse_gruppen("5")[0] == (5,)


def test_folge_laenge_zehn_ist_erlaubt_elf_nicht():
    assert M.parse_folge(", ".join(str(i) for i in range(1, 11)))[1] is None
    assert M.parse_folge(", ".join(str(i) for i in range(1, 12)))[0] is None


def test_regler_d_am_rand_und_kleinste_zahl_zufallsfolgen():
    z = ev.modell_tabelle(4, 1000, 1)
    assert z[0]["d"] == 0.25 and z[-1]["d"] == 64.0
    assert z[0]["anteil"] > 0.98 and all(0 <= r["anteil"] <= 1 for r in z)
    assert all(r["lo"] <= r["anteil"] <= r["hi"] for r in z)             # bei N = 1000 ist das Band breit, aber gültig


def test_zeitbindung_bei_sehr_kleinem_d_ist_nicht_100_prozent():
    """Bei D = 0,25 und n = 10 bleibt ein Wagen mit hoher Wahrscheinlichkeit nicht ganz kurz: der Anteil ist hoch, aber unter 100 %."""
    z = ev.modell_tabelle(10, 1000, 1301)
    assert 0.5 < z[0]["anteil_z"] < 1.0 and z[0]["anteil"] >= z[0]["anteil_z"]


def test_wilson_band_bei_n_gleich_1000_ist_breit():
    lo, hi = Mo.wilson(500, 1000)
    assert hi - lo == pytest.approx(0.062, abs=0.003)


def test_verzoegert_n_gleich_1_ist_eine_folge_und_anteil_1():
    assert ev.tabelle_anzahl(3, "verzögert")[0]["sortierbar"] == 1
    assert ev.zufallsprobe(3, 1000, 5, "verzögert")["exakt"] == pytest.approx(1 / 6)


def test_catalan_formel_grosse_n_ohne_aufzaehlung():
    assert K.catalan(30) == 3814986502092304 and ev.anzahl_zeile(30).zustand is None
