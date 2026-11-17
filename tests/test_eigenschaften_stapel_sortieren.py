"""Eigenschaftstests (metamorph): Aussagen über das Verfahren, die gelten müssen, ohne dass man das einzelne Ergebnis kennt (ORACLE-PLAYBOOK §5.2).

Zufall nur aus dem SplitMix64 der Demo, feste Zufalls-Seeds."""

from itertools import permutations

import sts_counting as K
import sts_machine as M
import sts_models as Mo
import sts_evaluation as ev
from sts_rng import SplitMix64


def zufallsfolgen(n, anzahl, seed):
    rng = SplitMix64(seed)
    return [Mo.zufallsfolge_uniform(rng, n) for _ in range(anzahl)]


def neu_nummerieren(werte):
    rang = {v: r for r, v in enumerate(sorted(werte), start=1)}
    return tuple(rang[v] for v in werte)


def test_sortierbare_folge_bleibt_beim_streichen_eines_wagens_sortierbar():
    """Mustervermeidung ist unter Streichen abgeschlossen: Wagen streichen, die übrigen neu nummerieren."""
    gesehen = 0
    for p in zufallsfolgen(9, 4000, 11):
        if not M.ist_sortierbar(p):
            continue
        gesehen += 1
        for i in range(len(p)):
            q = neu_nummerieren(p[:i] + p[i + 1:])
            assert M.ist_sortierbar(q), (p, i)
    assert gesehen >= 20          # n = 9: Anteil 1,3 %, also etwa 50 von 4000: die Aussage wird wirklich benutzt


def test_inverse_einer_sortierbaren_folge_ist_erzeugbar():
    for n in (5, 6):
        erz = set(M.ausgaben_erzeugbar(n))
        for p in permutations(range(1, n + 1)):
            if M.ist_sortierbar(p):
                assert M.inverse(p) in erz


def test_neuer_groesster_wagen_am_ende_aendert_die_sortierbarkeit_nicht():
    for p in zufallsfolgen(8, 300, 5):
        assert M.ist_sortierbar(p) == M.ist_sortierbar(p + (9,))


def test_neuer_kleinster_wagen_am_anfang_aendert_die_sortierbarkeit_nicht():
    """Ein Wagen mit Rang 1 vorn kann sofort hinaus."""
    for p in zufallsfolgen(8, 300, 6):
        q = (1,) + tuple(v + 1 for v in p)
        assert M.ist_sortierbar(q) == M.ist_sortierbar(p)


def test_anteil_faellt_mit_n_exakt_und_in_der_zufallsprobe():
    assert all(K.anteil(n + 1) < K.anteil(n) for n in range(2, 30))
    anteile = [Mo.zufallsprobe_uniform(n, 6000, 1301) / 6000 for n in (4, 6, 8)]
    assert anteile[0] > anteile[1] > anteile[2]


def test_zusammenlegen_zweier_benachbarter_werte_macht_keine_sortierbare_folge_unsortierbar():
    """Wagen mit den Rängen v und v + 1 bekommen dasselbe Ziel; als Wort (strenge Ungleichungen) bleibt die Folge sortierbar. Alle Folgen mit n ≤ 6."""
    for n in range(3, 7):
        for p in permutations(range(1, n + 1)):
            if M.ist_sortierbar(p):
                for v in range(1, n):
                    wort = tuple(x if x <= v else x - 1 for x in p)
                    assert K.wort_sortierbar(wort), (p, v)


def kompositionen(n):
    if n == 0:
        yield ()
        return
    for erste in range(1, n + 1):
        for rest in kompositionen(n - erste):
            yield (erste,) + rest


def test_zahl_sortierbarer_woerter_haengt_nicht_an_der_reihenfolge_der_gruppen_n_bis_9():
    """Messung, kein Beweis: in allen geordneten Gruppenvektoren mit n ≤ 9 ist die Zahl gleich der bei absteigend geordneten Größen."""
    vektoren = 0
    for n in range(2, 10):
        nach_partition = {}
        for g in kompositionen(n):
            z, _ = K.zaehle_woerter_zustand(g)
            schluessel = tuple(sorted(g, reverse=True))
            vektoren += 1
            assert nach_partition.setdefault(schluessel, z) == z, g
    assert vektoren == sum(2 ** (n - 1) for n in range(2, 10))


def test_gleicher_zufalls_seed_gleiche_ausgabe_und_anderer_seed_andere():
    a = ev.modell_tabelle(6, 500, 4)
    b = ev.modell_tabelle(6, 500, 4)
    c = ev.modell_tabelle(6, 500, 5)
    assert a == b and a != c


def test_modell_v_anteil_faellt_mit_d_im_band():
    """Über n = 6, 8, 10 und die feste Tabelle (alle D teilen die Zufallszahlen): von einem D-Wert zum nächsten steigt der Anteil nie um mehr als 1 Prozentpunkt."""
    for n in (6, 8, 10):
        zeilen = ev.modell_tabelle(n, 3000, 1301)
        for a, b in zip(zeilen, zeilen[1:]):
            assert b["anteil"] <= a["anteil"] + 0.01, (n, a["d"], b["d"])


def test_zeitbindung_ist_nie_besser_als_nur_rangfolge():
    for n in (6, 10):
        for z in ev.modell_tabelle(n, 2000, 3):
            assert z["kz"] <= z["k"]


def test_ergebnis_haengt_nicht_an_der_reihenfolge_der_unabhaengigen_zeilen():
    """Zeilen der Zufallstabelle vertauschen: der Anteil sortierbarer Zeilen bleibt gleich."""
    E = Mo.exp_tabelle(8, 1000, 2)
    ab = Mo.abfahrten(E, 2.0)
    k1 = Mo.sortierbar_anzahl(Mo.raenge(ab))
    k2 = Mo.sortierbar_anzahl(Mo.raenge(ab[::-1]))
    assert k1 == k2
