"""Orakel-Tests: die Kernroutinen gegen andere Rechenwege (ORACLE-PLAYBOOK §5, DEMO-PLAYBOOK §12).

Menge der sortierbaren Folgen für n = 1 bis 9 (n = 9: 362 880 Folgen, wenige Sekunden), auf fünf Wegen:
(1) die Maschine der Demo, (2) Mustersuche 231, (3) Rekursion s(p) = s(L) s(R) n (Bóna, Lemma 1.2), (4) alle Wörter aus „hinein“ und „hinaus“ als Vorzeichenfolgen,
davon die Inverse der Ausgaben, (5) die Catalan-Zahl aus ihrer Rekursion. Bei Zielgruppen: Zustandsrechnung gegen Maschine gegen strenge Mustersuche.
Die Wilson-Grenzen werden gegen scipy geprüft (scipy.stats.binomtest, nur im Test-Satz)."""

from itertools import permutations, product

import pytest

import sts_counting as K
import sts_machine as M
import sts_models as Mo

# ------------------------------------------------------------------------------------------------------------------------------------
# unabhängige Rechenwege


def muster_231(p):
    n = len(p)
    return any(p[k] < p[i] < p[j] for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))


def muster_312(p):
    n = len(p)
    return any(p[j] < p[k] < p[i] for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))


def west(p):
    """s(p) = s(L) s(R) n mit p = L n R: die Ausgabe der Stapelsortierung ohne Zwischenausgabe-Entscheidung (Bóna, Lemma 1.2)."""
    if not p:
        return ()
    n = max(p)
    i = p.index(n)
    return west(p[:i]) + west(p[i + 1:]) + (n,)


def dyck_ausgaben(n):
    """Alle Wörter aus n Mal „hinein“ und n Mal „hinaus“ (Vorzeichenfolgen), die den Stapel nie überziehen; die Ausgabe bei Eingabe 1…n."""
    ergebnis = []
    for wort in product((1, -1), repeat=2 * n):
        if sum(wort) != 0:
            continue
        hoehe, ok = 0, True
        for s in wort:
            hoehe += s
            if hoehe < 0:
                ok = False
                break
        if not ok:
            continue
        stapel, naechster, aus = [], 1, []
        for s in wort:
            if s == 1:
                stapel.append(naechster)
                naechster += 1
            else:
                aus.append(stapel.pop())
        ergebnis.append(tuple(aus))
    return ergebnis


def inverse(p):
    return tuple(p.index(v) + 1 for v in range(1, len(p) + 1))


def catalan_rekursion(n):
    c = [1]
    for m in range(1, n + 1):
        c.append(sum(c[k] * c[m - 1 - k] for k in range(m)))
    return c[n]


def menge_pruefen(n):
    alle = list(permutations(range(1, n + 1)))
    maschine = {p for p in alle if M.ist_sortierbar(p)}
    muster = {p for p in alle if not muster_231(p)}
    rekursion = {p for p in alle if west(p) == tuple(range(1, n + 1))}
    outs = dyck_ausgaben(n)
    invers = {inverse(o) for o in outs}
    assert maschine == muster == rekursion == invers, n
    assert len(maschine) == catalan_rekursion(n) == K.catalan(n)
    assert len(set(outs)) == len(outs) == K.catalan(n)              # Wort und Ausgabe entsprechen einander eindeutig
    erzeugbar = set(outs)
    assert erzeugbar == {p for p in alle if not muster_312(p)}
    assert {inverse(p) for p in maschine} == erzeugbar               # sortierbar genau dann, wenn die Inverse erzeugbar ist
    assert {p for p in maschine if p in erzeugbar} == {p for p in alle if not muster_231(p) and not muster_312(p)}
    assert len(maschine & erzeugbar) == 2 ** (n - 1)


@pytest.mark.parametrize("n", range(1, 8))
def test_fuenf_wege_gleiche_menge_bis_n_7(n):
    menge_pruefen(n)


@pytest.mark.parametrize("n", [8, 9])
def test_fuenf_wege_gleiche_menge_n_8_und_9(n):
    menge_pruefen(n)


def test_maschine_ueber_alle_folgen_n_9_gleich_catalan():
    assert K.zaehle_aufzaehlung(9) == 4862


def test_verzoegert_genau_eine_folge_n_bis_8():
    """Erst alles hinein, dann hinaus: die Ausgabe ist die Umkehr der Eingabe; sie ist 1…n nur für (n, …, 1)."""
    for n in range(1, 9):
        assert [p for p in permutations(range(1, n + 1)) if tuple(reversed(p)) == tuple(range(1, n + 1))] == [tuple(range(n, 0, -1))]


def test_jede_folge_hat_hoechstens_einen_weg_n_bis_7():
    for n in range(1, 8):
        for p in permutations(range(1, n + 1)):
            assert M.wege_zahl(p) == (1 if not muster_231(p) else 0)


def test_jede_folge_hat_hoechstens_einen_weg_n_8():
    for p in permutations(range(1, 9)):
        assert M.wege_zahl(p) == (1 if not muster_231(p) else 0)


def test_unsortierbare_gleichstaende_klein():
    """Von Hand: Wort 2, 3, 1 (strenges Muster) ist unsortierbar, 2, 2, 1 und 1, 1, 2 sind sortierbar."""
    assert not K.wort_sortierbar((2, 3, 1)) and K.wort_sortierbar((2, 2, 1)) and K.wort_sortierbar((1, 1, 2))


def kompositionen(n):
    if n == 0:
        yield ()
        return
    for erste in range(1, n + 1):
        for rest in kompositionen(n - erste):
            yield (erste,) + rest


def wort_muster_streng(w):
    n = len(w)
    return any(w[k] < w[i] < w[j] for i in range(n) for j in range(i + 1, n) for k in range(j + 1, n))


def test_gleichstaende_zustandsrechnung_gleich_maschine_gleich_strenge_mustersuche_n_bis_6():
    zaehler = 0
    for n in range(1, 7):
        for g in kompositionen(n):
            woerter = list(K.woerter(g))
            masch = sum(1 for w in woerter if K.wort_sortierbar(w))
            muster = sum(1 for w in woerter if not wort_muster_streng(w))
            zustand, _ = K.zaehle_woerter_zustand(g)
            assert masch == muster == zustand, g
            assert len(woerter) == K.anzahl_woerter(g), g
            zaehler += 1
    assert zaehler == 2 ** 6 - 1


def test_gleichstaende_alle_127_gruppenvektoren_bis_n_7():
    zaehler = 0
    for n in range(1, 8):
        for g in kompositionen(n):
            woerter = list(K.woerter(g))
            masch = sum(1 for w in woerter if K.wort_sortierbar(w))
            muster = sum(1 for w in woerter if not wort_muster_streng(w))
            assert masch == muster == K.zaehle_woerter_zustand(g)[0], g
            zaehler += 1
    assert zaehler == 127


def test_wilson_gegen_scipy():
    stats = pytest.importorskip("scipy.stats")
    for k, n in [(0, 1000), (5, 1000), (250, 1000), (999, 1000), (1000, 1000), (3609, 20000), (4, 10)]:
        ci = stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method="wilson")
        lo, hi = Mo.wilson(k, n)
        assert lo == pytest.approx(ci.low, abs=2e-4) and hi == pytest.approx(ci.high, abs=2e-4), (k, n)


def test_zeitgebunden_maske_gleich_nachspielen_der_ereignisse():
    E = Mo.exp_tabelle(7, 800, 11)
    for d in (0.5, 1.0, 4.0):
        ab = Mo.abfahrten(E, d)
        maske = Mo.zeitgebunden_maske(ab)
        assert list(maske) == [Mo.zeitgebunden_ok_simulation(z) for z in ab.tolist()]


def test_zeitgebunden_sortierbar_impliziert_rangfolge_sortierbar_0_verletzungen():
    E = Mo.exp_tabelle(8, 3000, 7)
    for d in (0.5, 1.0, 2.0, 4.0):
        ab = Mo.abfahrten(E, d)
        maske = Mo.zeitgebunden_maske(ab)
        raenge = Mo.raenge(ab).tolist()
        verletzungen = sum(1 for ok, r in zip(maske, raenge) if ok and not M.ist_sortierbar(r))
        assert verletzungen == 0


def test_raenge_gleich_sortieren_in_python():
    E = Mo.exp_tabelle(6, 300, 3)
    ab = Mo.abfahrten(E, 2.0)
    r = Mo.raenge(ab)
    for zeile_ab, zeile_r in zip(ab.tolist(), r.tolist()):
        ordnung = sorted(range(6), key=lambda i: zeile_ab[i])
        erwartet = [0] * 6
        for rang, i in enumerate(ordnung, start=1):
            erwartet[i] = rang
        assert zeile_r == erwartet and sorted(zeile_r) == list(range(1, 7))
