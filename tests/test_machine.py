"""Die Maschine an Handbeispielen (jede Schrittfolge von Hand nachgerechnet), Zeuge für das Muster 231, Erzeugen, Eingabeprüfung."""

from itertools import permutations

import pytest

import sts_machine as M


def test_handbeispiel_sortierbar_3_1_2_5_4():
    """3 hinein; 1 hinein und hinaus; 2 hinein und hinaus; oben liegt die 3, gebraucht wird die 3: hinaus; 5 hinein; 4 hinein und hinaus; 5 hinaus."""
    l = M.lauf((3, 1, 2, 5, 4))
    assert l.sortierbar
    assert [f"{s.aktion} {s.wagen}" for s in l.schritte] == ["hinein 3", "hinein 1", "hinaus 1", "hinein 2", "hinaus 2", "hinaus 3",
                                                           "hinein 5", "hinein 4", "hinaus 4", "hinaus 5"]
    assert l.schritte[-1].ausgabe == (1, 2, 3, 4, 5)
    assert l.hoechster_stapel == 2
    assert l.zeuge is None and l.erster_verstoss is None


def test_handbeispiel_nicht_sortierbar_2_4_1_3_5():
    """2 hinein; 4 hinein (auf der 2: größer auf kleiner); 1 hinein und hinaus; gebraucht wird die 2, oben liegt die 4: nichts geht mehr, es bleibt (2, 4, 3, 5)."""
    l = M.lauf((2, 4, 1, 3, 5))
    assert not l.sortierbar
    assert [f"{s.aktion} {s.wagen}" for s in l.schritte][:4] == ["hinein 2", "hinein 4", "hinein 1", "hinaus 1"]
    assert l.schritte[3].stapel == (2, 4)
    assert l.schritte[-1].stapel == (2, 4, 3, 5) and l.schritte[-1].ausgabe == (1,)
    assert l.erster_verstoss == 1 and l.schritte[1].verstoss          # der zweite Schritt: 4 auf 2
    assert l.zeuge == ((1, 2, 3), (2, 4, 1))                          # Plätze 1 bis 3, Werte 2, 4, 1


def test_zeuge_ist_immer_ein_vorkommen_des_musters_231_und_fehlt_genau_bei_sortierbaren():
    for n in range(1, 8):
        for p in permutations(range(1, n + 1)):
            l = M.lauf(p)
            assert l.sortierbar == (not M.hat_231(p)) == M.ist_sortierbar(p)
            if l.sortierbar:
                assert l.zeuge is None
            else:
                (i, j, k), (a, b, c) = l.zeuge
                assert i < j < k and (p[i - 1], p[j - 1], p[k - 1]) == (a, b, c) and c < a < b


def test_zeuge_nur_beim_ersten_verstoss_und_verstoss_nur_hinein_auf_kleineren():
    l = M.lauf((2, 3, 1))
    assert [s.verstoss for s in l.schritte] == [False, True, False, False]  # hinein 2, hinein 3 (Verstoß), hinein 1, hinaus 1
    assert l.zeuge == ((1, 2, 3), (2, 3, 1))


def test_hoechster_stapel_der_umkehrfolge_ist_n():
    """Erst alles hinein, dann hinaus: bei (n, …, 1) liegen alle n Wagen im Stapel."""
    assert M.lauf((5, 4, 3, 2, 1)).hoechster_stapel == 5
    assert M.lauf((1, 2, 3)).hoechster_stapel == 1


def test_randfaelle_n_gleich_1_und_2():
    assert M.lauf((1,)).sortierbar and M.lauf((1,)).hoechster_stapel == 1
    assert M.lauf((1, 2)).sortierbar and M.lauf((2, 1)).sortierbar
    assert M.lauf(()).sortierbar and M.lauf(()).schritte == ()


def test_erzeugen_231_gelingt_312_scheitert():
    """Eingabe 1, 2, 3: für 231 hinein 1, hinein 2, hinaus 2, hinein 3, hinaus 3, hinaus 1. Für 312 liegt nach dem Hinausgeben der 3 oben die 2, nicht die 1."""
    schritte, ok = M.erzeuge_weg((2, 3, 1))
    assert ok and [f"{s.aktion} {s.wagen}" for s in schritte] == ["hinein 1", "hinein 2", "hinaus 2", "hinein 3", "hinaus 3", "hinaus 1"]
    schritte, ok = M.erzeuge_weg((3, 1, 2))
    assert not ok and schritte[-1].stapel == (1, 2) and schritte[-1].ausgabe == (3,)


def test_erzeugen_gierig_gleich_alle_wege_und_inverse_beziehung():
    for n in range(1, 7):
        alle = set(M.ausgaben_erzeugbar(n))
        for q in permutations(range(1, n + 1)):
            assert M.erzeuge_weg(q)[1] == (q in alle) == M.ist_sortierbar(M.inverse(q))


def test_wege_zahl():
    assert M.wege_zahl((3, 1, 2)) == 1 and M.wege_zahl((2, 3, 1)) == 0
    assert M.wege_zahl((1, 2, 3)) == 1


def test_inverse():
    assert M.inverse((2, 3, 1)) == (3, 1, 2) and M.inverse(M.inverse((4, 1, 3, 2))) == (4, 1, 3, 2)


@pytest.mark.parametrize("text,erwartet", [
    ("3, 1, 2", (3, 1, 2)), ("3 1 2", (3, 1, 2)), ("3;1;2", (3, 1, 2)), (" 3 ,1;  2 ", (3, 1, 2)), ("1", (1,)),
])
def test_parse_folge_akzeptiert_trennzeichen(text, erwartet):
    assert M.parse_folge(text) == (erwartet, None)


@pytest.mark.parametrize("text,stichwort", [
    ("", "eingeben"), ("   ", "eingeben"), ("1, 2, a", "ganze Zahlen"), ("1, 1, 2", "mehrfach"), ("1, 2, 5", "liegt nicht zwischen"),
    ("0, 1", "liegt nicht zwischen"), ("1 2 3 4 5 6 7 8 9 10 11", "zu lang"), ("2, 3", "liegt nicht zwischen"),
])
def test_parse_folge_lehnt_ungueltiges_mit_meldung_ab(text, stichwort):
    folge, fehler = M.parse_folge(text)
    assert folge is None and stichwort in fehler
