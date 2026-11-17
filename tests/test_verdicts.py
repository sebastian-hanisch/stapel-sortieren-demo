"""Verdikte an von Hand gesetzten Werten: jede Zahl im Text und jede Art (success, error, warning, info) steht hier."""

from fractions import Fraction

import numpy as np

import sts_counting as K
import sts_evaluation as ev
import sts_machine as M


def test_verdict_hand_sortierbar():
    art, text = ev.verdict_hand(M.lauf((3, 1, 2, 5, 4)))
    assert art == "success"
    assert text == "(3, 1, 2, 5, 4): **sortierbar**, höchster Stapel 2 Wagen. Die Folge vermeidet das Muster 231."


def test_verdict_hand_nicht_sortierbar_nennt_zeuge_und_plaetze():
    art, text = ev.verdict_hand(M.lauf((2, 4, 1, 3, 5)))
    assert art == "error"
    assert "**nicht sortierbar**" in text
    assert "Die 4 (Platz 2) liegt über der 2 (Platz 1), aber die 2 muss vor der 4 hinaus" in text
    assert "die 1 (Platz 3) kommt erst später" in text
    assert "Plätzen 1 bis 3 (Werte 2, 4, 1)" in text


def test_plaetze_zusammenhaengend_und_getrennt():
    assert ev.plaetze((1, 2, 3)) == "1 bis 3" and ev.plaetze((1, 3, 6)) == "1, 3 und 6"


def test_verdict_hand_zeuge_nicht_zusammenhaengend():
    art, text = ev.verdict_hand(M.lauf((2, 5, 3, 4, 1)))     # 2 auf 5 (Platz 2); gebraucht 1 an Platz 5
    assert art == "error" and "Plätzen 1, 2 und 5 (Werte 2, 5, 1)" in text


def test_verdict_anzahl_n_10_nennt_zahlen_und_faktor():
    z = ev.anzahl_zeile(10)
    art, text = ev.verdict_anzahl(z, None, "sofort")
    assert art == "info"
    assert "n = 10: 16 796 von 3 628 800 Folgen (0,463 %, 1 von 216)" in text
    assert "von n = 9 auf n = 10 ändert sich um den Faktor 19/55 = 0,345" in text
    assert "Anteil 1/3 628 800" in text


def test_verdict_anzahl_zufallsprobe_im_und_ausserhalb_des_bands():
    z = ev.anzahl_zeile(6)
    im_band = {"runs": 1000, "seed": 7, "treffer": 183, "anteil": 0.183, "exakt": 11 / 60, "lo": 0.16, "hi": 0.21, "im_band": True}
    art, text = ev.verdict_anzahl(z, im_band, "sofort")
    assert "183 Treffer, 18,300 %" in text and "liegt im Wilson-Band (16,000 bis 21,000 %)" in text and "Zufalls-Seed 7" in text
    ausser = dict(im_band, im_band=False)
    assert "liegt außerhalb des Wilson-Band" in ev.verdict_anzahl(z, ausser, "sofort")[1]


def test_tabelle_anzahl_zeilen_und_betriebsart():
    zeilen = ev.tabelle_anzahl(5, "sofort")
    assert [r["n"] for r in zeilen] == [3, 4, 5] and [r["sortierbar"] for r in zeilen] == [5, 14, 42]
    assert zeilen[2]["anteil"] == Fraction(7, 20) and zeilen[2]["faktor"] == Fraction(7, 20) / Fraction(14, 24)
    verz = ev.tabelle_anzahl(5, "verzögert")
    assert [r["sortierbar"] for r in verz] == [1, 1, 1] and verz[2]["anteil"] == Fraction(1, 120) and verz[2]["faktor"] == Fraction(1, 5)


def test_anzahl_zeile_rechenwege_nach_n():
    z8, z12, z20 = ev.anzahl_zeile(8), ev.anzahl_zeile(12), ev.anzahl_zeile(20)
    assert z8.aufzaehlung == z8.zustand == z8.sortierbar == 1430
    assert z12.aufzaehlung is None and z12.zustand == z12.sortierbar == 208012
    assert z20.aufzaehlung is None and z20.zustand is None and z20.sortierbar == 6564120420
    assert "Formel" in z20.methode and "Zustandsrechnung" in z12.methode and "durchgespielt" in z8.methode


def test_verdict_richtung_n_6():
    art, text = ev.verdict_richtung(ev.vergleich(6))
    assert art == "warning"
    assert "132 Folgen sortierbar, 132 erzeugbar (gleich viele), aber nur 32 = 2^5 in beiden Mengen" in text
    assert "100 Folgen sortiert der Stapel, ohne dass er sie erzeugen kann, und 100 umgekehrt" in text
    assert "Die Inverse jeder sortierbaren Folge ist erzeugbar und umgekehrt (alle Folgen mit n = 6)" in text


def test_vergleich_n_3_von_hand():
    v = ev.vergleich(3)
    assert v.sortierbar == frozenset({(1, 2, 3), (1, 3, 2), (2, 1, 3), (3, 1, 2), (3, 2, 1)})
    assert v.erzeugbar == frozenset({(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 2, 1)})
    assert v.nur_sortierbar == {(3, 1, 2)} and v.nur_erzeugbar == {(2, 3, 1)} and len(v.beide) == 4 == v.zweihochn and v.inverse_gleich


def test_parse_gruppen():
    assert ev.parse_gruppen("2, 2, 2, 2") == ((2, 2, 2, 2), None)
    assert ev.parse_gruppen("3;2 1")[0] == (3, 2, 1)
    for text, stichwort in [("", "eingeben"), ("a, b", "ganze Zahlen"), ("1, 1, 1, 1, 1, 1, 1", "Höchstens 6 Gruppen"), ("0, 2", "1 bis 5"), ("6", "1 bis 5"),
                            ("5, 5, 5", "Höchstens 12 Wagen")]:
        g, fehler = ev.parse_gruppen(text)
        assert g is None and stichwort in fehler, text


def test_gruppen_2_2_2_2_zahlen_und_verdikt():
    a = ev.gruppen_analyse((2, 2, 2, 2))
    assert (a.n, a.woerter, a.sortierbar, a.kontrolle, a.sortierbar_absteigend) == (8, 2520, 352, 352, 352)
    assert a.verschiedene == Fraction(143, 4032)
    art, text = ev.verdict_gruppen(a)
    assert art == "info"
    assert "352 von 2520 verschiedenen Wörtern sortierbar (13,97 %)" in text and "gegen 1430 von 40 320 (3,55 %) bei lauter verschiedenen Wagen" in text
    assert "nicht Catalan" in text and "Bei absteigend geordneten Gruppengrößen sind es 352 (gleich)." in text


def test_gruppen_kontrolle_durch_aufzaehlung_bei_wenigen_woertern():
    a = ev.gruppen_analyse((2, 1, 1))
    assert a.kontrolle == a.sortierbar == 9 and a.woerter == 12


def test_gruppen_zwei_gruppen_und_lauter_verschiedene():
    a = ev.gruppen_analyse((5, 5))
    assert a.sortierbar == a.woerter == 252
    assert "alle Wörter sortierbar" in ev.verdict_gruppen(a)[1] and "das Muster 231 braucht drei verschiedene Werte" in ev.verdict_gruppen(a)[1]
    b = ev.gruppen_analyse((1, 1, 1, 1))
    assert b.sortierbar == 14 and "die Zahl ist Catalan" in ev.verdict_gruppen(b)[1]


def test_beispiel_unsortierbar_ist_wirklich_unsortierbar_und_hat_die_richtigen_gruppen():
    for g in [(1, 1, 1), (2, 2, 2), (3, 2, 1), (1, 1, 1, 1, 1), (5, 1, 4), (2, 3, 1, 2, 4)]:
        wort, zeuge = ev.beispiel_unsortierbar(g)
        assert not K.wort_sortierbar(wort) and zeuge is not None
        assert sorted(wort) == sorted(v for v, c in enumerate(g, start=1) for _ in range(c))
    assert ev.beispiel_unsortierbar((3, 3)) is None


def test_verdict_modell_ohne_und_mit_zeitbindung():
    zeile = {"d": 1.0, "anteil": 0.909, "lo": 0.903, "hi": 0.914, "anteil_z": 0.107, "lo_z": 0.10, "hi_z": 0.113}
    art, text = ev.verdict_modell(zeile, 10, 10000, 1301, False)
    assert art == "info"
    assert "90,9 % der Zufallsfolgen sind sortierbar bei D = 1 (Band 90,3 bis 91,4 %, 10 000 Zufallsfolgen, Zufalls-Seed 1301)" in text
    assert "sind es 0,463 %" in text and text.endswith("Ausgedachtes Modell, keine reale Ankunftsfolge.") and "Abholzeitpunkt" not in text
    text2 = ev.verdict_modell(zeile, 10, 10000, 1301, True)[1]
    assert "nur 10,7 % (Band 10,0 bis 11,3 %)" in text2


def test_verdict_modell_d_mit_nachkommastelle():
    zeile = {"d": 0.25, "anteil": 1.0, "lo": 0.99, "hi": 1.0, "anteil_z": 0.9, "lo_z": 0.89, "hi_z": 0.91}
    assert "bei D = 0,25 " in ev.verdict_modell(zeile, 10, 1000, 1, False)[1]


def test_modell_tabelle_zeilen_und_sekunden():
    z = ev.modell_tabelle(5, 200, 3)
    assert [r["d"] for r in z][:3] == [0.25, 0.5, 1.0] and all(r["lo"] <= r["anteil"] <= r["hi"] and r["kz"] <= r["k"] for r in z)
    assert ev.schaetze_sekunden(10, 5000) == np.float64(10 * 5000 * 38e-6)
