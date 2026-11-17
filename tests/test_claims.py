"""Claims-Tests: jede Zahl der README wird hier nachgerechnet (Ganzzahlen und Brüche exakt, Zufallsproben mit dem Zufalls-Seed der README als Band).

Die README nennt je Zeile der Tabelle „Befunde“ den Test. Zufallsproben laufen mit dem exakten SplitMix64 (keine C-Bibliothek) und sind auf jeder Plattform gleich;
trotzdem prüfen die Tests ein Band von ±0,5 Prozentpunkten um den Wert der README, damit ein anderer Python- oder numpy-Stand keine Zahl kippt.
Messungen, die nicht im Test stehen, nennt die README ausdrücklich („Messung dieser README, nicht im Test“)."""

import re
from fractions import Fraction
from itertools import permutations
from math import factorial
from pathlib import Path

import pytest

import sts_constants as C
import sts_counting as K
import sts_evaluation as ev
import sts_format as F
import sts_machine as M
import sts_models as Mo

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")


# ------------------------------------------------------------------------------------------------------------------------------------
# exakte Zählungen
def test_c1_catalan_und_anteile_n_1_bis_10():
    assert [K.catalan(n) for n in range(1, 11)] == [1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796]
    assert K.catalan(10) == 16796 and factorial(10) == 3628800
    assert float(K.anteil(10)) * 100 == pytest.approx(0.4629, abs=5e-5) and K.einsvon(10) == pytest.approx(216.05, abs=0.005)
    assert K.anteil(5) == Fraction(7, 20) and K.anteil(6) == Fraction(11, 60)
    for n, text in [(5, "35,0 %"), (6, "18,3 %"), (7, "8,51 %"), (8, "3,55 %"), (9, "1,34 %"), (10, "0,463 %"), (12, "0,0434 %"),
                    (15, "7,4·10⁻⁴ %"), (20, "2,7·10⁻⁷ %"), (30, "1,4·10⁻¹⁵ %")]:
        assert F.prozent_signifikant(float(K.anteil(n))) == text, n
    assert F.eins_von(K.einsvon(8)) == "28,2" and F.eins_von(K.einsvon(9)) == "74,6"


def test_c2_faktor_je_wagen():
    assert K.faktor_je_wagen(9) == Fraction(19, 55) and float(K.faktor_je_wagen(9)) == pytest.approx(0.345, abs=5e-4)
    assert float(K.faktor_je_wagen(5)) == pytest.approx(0.524, abs=5e-4) and float(K.faktor_je_wagen(29)) == pytest.approx(0.127, abs=5e-4)
    assert float(K.faktor_je_wagen(10)) == pytest.approx(0.318, abs=5e-4)
    assert all(K.anteil(n + 1) / K.anteil(n) == K.faktor_je_wagen(n) == Fraction(2 * (2 * n + 1), (n + 1) * (n + 2)) for n in range(1, 30))
    assert all(K.faktor_je_wagen(n + 1) < K.faktor_je_wagen(n) for n in range(2, 30))       # der Faktor fällt mit n (und ist nicht überall ein Drittel)


def test_c3_verzoegert_genau_eine_folge_n_bis_9():
    for n in range(1, 10):
        assert sum(1 for p in permutations(range(1, n + 1)) if all(p[i] > p[i + 1] for i in range(n - 1))) == 1
    assert ev.tabelle_anzahl(9, "verzögert")[-1]["sortierbar"] == 1


def test_c4_ein_weg_je_sortierbarer_folge_n_bis_8():
    for n in range(1, 9):
        wege = [M.wege_zahl(p) for p in permutations(range(1, n + 1))]
        assert sorted(set(wege)) == ([0, 1] if n >= 3 else [1])
        assert sum(wege) == K.catalan(n)


def test_c5_sortieren_gegen_erzeugen_tabelle_n_3_bis_9():
    erwartet = {3: (5, 4, 1), 4: (14, 8, 6), 5: (42, 16, 26), 6: (132, 32, 100), 7: (429, 64, 365), 8: (1430, 128, 1302), 9: (4862, 256, 4606)}
    for n, (sortierbar, beide, nur) in erwartet.items():
        v = ev.vergleich(n) if n <= 8 else None
        if v is None:
            s = {p for p in permutations(range(1, n + 1)) if M.ist_sortierbar(p)}
            e = set(M.ausgaben_erzeugbar(n))
            assert (len(s), len(s & e), len(s - e), len(e - s)) == (sortierbar, beide, nur, nur) and {M.inverse(p) for p in s} == e
        else:
            assert (len(v.sortierbar), len(v.erzeugbar), len(v.beide), len(v.nur_sortierbar), len(v.nur_erzeugbar)) == (sortierbar, sortierbar, beide, nur, nur)
            assert v.beide == v.sortierbar & v.erzeugbar and v.inverse_gleich
        assert beide == 2 ** (n - 1) and sortierbar - beide == nur


def test_c6_aufzaehlung_n_9_und_n_10_gierig():
    assert K.zaehle_aufzaehlung(9) == 4862
    assert sum(1 for p in permutations(range(1, 11)) if M.ist_sortierbar(p)) == 16796          # alle 3 628 800 Folgen, nur die Maschine


def test_c7_gruppen_tabelle():
    erwartet = {
        (2, 1, 1): (4, 12, 9), (2, 2, 2): (6, 90, 43), (3, 2, 1): (6, 60, 34), (2, 2, 2, 2): (8, 2520, 352), (3, 3, 1, 1): (8, 1120, 242),
        (5, 5): (10, 252, 252), (4, 3, 3): (10, 4200, 736), (3, 3, 2, 2): (10, 25200, 1594), (2, 2, 2, 2, 2): (10, 113400, 3114), (4, 3, 2, 1): (10, 12600, 1187),
    }
    for g, (n, woerter, sortierbar) in erwartet.items():
        a = ev.gruppen_analyse(g)
        assert (a.n, a.woerter, a.sortierbar) == (n, woerter, sortierbar), g
    prozent = {(2, 1, 1): "75,00 %", (2, 2, 2): "47,78 %", (3, 2, 1): "56,67 %", (2, 2, 2, 2): "13,97 %", (3, 3, 1, 1): "21,61 %", (5, 5): "100,00 %",
               (4, 3, 3): "17,52 %", (3, 3, 2, 2): "6,33 %", (2, 2, 2, 2, 2): "2,75 %", (4, 3, 2, 1): "9,42 %"}
    for g, text in prozent.items():
        assert F.prozent(float(ev.gruppen_analyse(g).anteil), 2) == text, g
    assert ev.gruppen_analyse((2, 1, 1)).verschiedene == Fraction(14, 24)
    zustaende = [ev.gruppen_analyse(g).zustaende for g in erwartet]
    assert min(zustaende) == 12 and max(zustaende) == 243
    assert K.zaehle_woerter_zustand((1,) * 10)[1] == 1024 and K.zaehle_woerter_zustand((1,) * 14)[0] == K.catalan(14) == 2674440


def test_c8_reihenfolge_der_gruppen_n_bis_10():
    vektoren, partitionen, abweichungen = 0, {}, 0
    for n in range(2, 11):
        for g in _kompositionen(n):
            z, _ = K.zaehle_woerter_zustand(g)
            schluessel = tuple(sorted(g, reverse=True))
            vektoren += 1
            if schluessel in partitionen:
                abweichungen += partitionen[schluessel] != z
            else:
                partitionen[schluessel] = z
    assert (vektoren, len(partitionen), abweichungen) == (1022, 137, 0)


def _kompositionen(n):
    if n == 0:
        yield ()
        return
    for erste in range(1, n + 1):
        for rest in _kompositionen(n - erste):
            yield (erste,) + rest


# ------------------------------------------------------------------------------------------------------------------------------------
# Zufallsproben und Modell V (Zufalls-Seed 1301)
def test_b1_zufallsprobe_gleichverteilt_n_50000():
    erwartet = {6: (9119, "18,24 %", -0.55), 8: (1811, "3,62 %", 0.91), 10: (244, "0,488 %", 0.83)}
    for n, (k, text, abstand) in erwartet.items():
        p = ev.zufallsprobe(n, 50000, 1301, "sofort")
        assert p["treffer"] == pytest.approx(k, abs=0.005 * 50000), n                  # Band ±0,5 Prozentpunkte
        assert p["im_band"] and abs(p["abstand_se"]) < 1.96 and p["abstand_se"] == pytest.approx(abstand, abs=0.3), n
        assert p["anteil"] * 100 == pytest.approx(float(text.replace(",", ".").rstrip(" %")), abs=0.5), n


MODELL_RANG = {                      # Prozent sortierbar, nur Rangfolge der Abfahrten, N = 10 000, Zufalls-Seed 1301
    6: {1.0: 94.98, 2.0: 77.06, 4.0: 53.49, 8.0: 36.57},
    8: {1.0: 93.19, 2.0: 66.69, 4.0: 34.12, 8.0: 15.68},
    10: {0.25: 100.0, 0.5: 99.6, 1.0: 91.09, 2.0: 56.81, 4.0: 21.4, 8.0: 6.1, 16.0: 2.1, 32.0: 1.12, 64.0: 0.71},
    20: {1.0: 80.2, 2.0: 25.12, 4.0: 1.53, 8.0: 0.05},
}
MODELL_ZEIT = {10: {0.5: 51.51, 1.0: 11.7, 2.0: 0.95, 4.0: 0.05, 8.0: 0.01}}


@pytest.fixture(scope="module")
def tabellen():
    return {n: {z["d"]: z for z in ev.modell_tabelle(n, 10000, 1301)} for n in (6, 8, 10, 20)}


def test_b2_modell_v_anteile_nur_rangfolge(tabellen):
    for n, werte in MODELL_RANG.items():
        for d, prozent in werte.items():
            assert tabellen[n][d]["anteil"] * 100 == pytest.approx(prozent, abs=0.5), (n, d)


def test_b3_modell_v_anteile_fester_abholzeitpunkt(tabellen):
    for n, werte in MODELL_ZEIT.items():
        for d, prozent in werte.items():
            assert tabellen[n][d]["anteil_z"] * 100 == pytest.approx(prozent, abs=0.5), (n, d)


def test_b4_anteil_faellt_mit_d_in_jeder_zeile_und_zeitbindung_nie_besser(tabellen):
    for n, zeilen in tabellen.items():
        ds = sorted(zeilen)
        assert all(zeilen[a]["anteil"] >= zeilen[b]["anteil"] for a, b in zip(ds, ds[1:])), n
        assert all(z["kz"] <= z["k"] for z in zeilen.values()), n
        assert all(z["anteil_z"] <= z["anteil"] for z in zeilen.values())
    assert len(tabellen) == 4 and all(len(z) == 9 for z in tabellen.values())                  # „alle 36 Zellen“: vier Zeilen mit je neun D-Werten
    assert [tabellen[20][d]["k"] for d in (16.0, 32.0, 64.0)] == [0, 0, 0]                    # „bei n = 20 ab D = 16 gleich 0“ (0 von 10 000)


def test_b5_zeitgebunden_impliziert_rangfolge_0_verletzungen_in_50000_folgen():
    verletzungen = 0
    folgen = 0
    E = Mo.exp_tabelle(10, 10000, 99)
    for d in (0.5, 1.0, 2.0, 4.0, 8.0):
        ab = Mo.abfahrten(E, d)
        maske = Mo.zeitgebunden_maske(ab)
        r = Mo.raenge(ab).tolist()
        verletzungen += sum(1 for ok, z in zip(maske, r) if ok and not M.ist_sortierbar(z))
        folgen += len(r)
    assert (verletzungen, folgen) == (0, 50000)


def test_b6_zweiter_zufalls_seed_n_10_hoechstens_0_6_prozentpunkte_abstand(tabellen):
    zweit = {z["d"]: z for z in ev.modell_tabelle(10, 10000, 20261117)}
    assert max(abs(zweit[d]["anteil"] - tabellen[10][d]["anteil"]) for d in zweit) * 100 <= 0.65
    assert max(abs(zweit[d]["anteil_z"] - tabellen[10][d]["anteil_z"]) for d in zweit) * 100 <= 0.65


def test_b7_bandbreite_je_zelle_hoechstens_2_prozentpunkte(tabellen):
    assert max(z["hi"] - z["lo"] for t in tabellen.values() for z in t.values()) < 0.02


def test_b8_n_10_d_64_noch_nicht_gleichverteilt(tabellen):
    z = tabellen[10][64.0]
    assert z["lo"] > float(K.anteil(10))                      # das Band liegt über dem exakten Wert 0,463 %: bei D = 64 ähnelt Modell V ihm noch nicht


# ------------------------------------------------------------------------------------------------------------------------------------
# README-Abgleich
def test_readme_nennt_die_testzahl_der_suite():
    import subprocess
    import sys

    ausgabe = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests", "-p", "no:cacheprovider"], cwd=ROOT, capture_output=True, text=True,
                             stdin=subprocess.DEVNULL, timeout=600).stdout
    zahl = int(re.search(r"(\d+) tests? collected", ausgabe).group(1))
    treffer = re.findall(r"\*\*(\d+) Tests\*\*", README)
    assert treffer and int(treffer[0]) == zahl, (treffer, zahl)


def test_readme_enthaelt_keine_planungswoerter_ausser_in_der_footer_zeile():
    text = "\n".join(z for z in README.splitlines() if "Mehr zu den Demos" not in z and "Mehr zur Reihe" not in z)
    for wort in ("Stück", "Linie", "Vormessung", "Plan Z", "V1", "sm_v", "Phase 0", "trägt", "tragen", "Saatwert", "Seed ", "geplant", "läuft lokal"):
        for zeile in text.splitlines():
            if wort == "Seed " and "Zufalls-Seed" in zeile:
                continue
            assert wort not in zeile, (wort, zeile[:120])
    assert not [z for z in README.splitlines() if "Website" in z and "offen" in z]


def test_readme_nennt_jede_claim_zahl_der_tabelle_und_den_live_link_als_marke():
    assert "TODO nach dem Deploy" in README
    for zahl in ("16 796", "3 628 800", "0,463 %", "19/55", "2^(n−1)", "352 von 2520", "1022"):
        assert zahl in README, zahl
