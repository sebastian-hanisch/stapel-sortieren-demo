"""Die Maschine „ein Stapel“: Schritte, Zeuge für das Muster 231, Erzeugen mit Eingabe 1…n (nur Standardbibliothek).

Vereinbarung (überall gleich): Die Ankunftsfolge p = (p1, …, pn) ordnet die Zahlen 1…n an; die Zahl ist der Abholrang (1 wird zuerst abgeholt).
Die Maschine ist ein Stapel (zuletzt hinein, zuerst hinaus); Ausgeben zwischendurch ist erlaubt. „Sortierbar“ heißt: es gibt einen Weg, der die Ausgabe
1, 2, …, n liefert. Das ist bei diesem Stapel genau dann der Fall, wenn die Folge das Muster 231 vermeidet (Plätze i < j < k mit p_k < p_i < p_j).
Erzeugbar sind die Ausgaben, die entstehen, wenn die Eingabe 1…n durch den Stapel läuft; sie vermeiden das Muster 312.
Quelle der Aussagen: Lehrbuchwissen über stapelsortierbare Permutationen (nach Quellenbericht Knuth, Bóna 2003); die Routinen hier sind eigene Rechnung."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Schritt:
    aktion: str                 # "hinein" oder "hinaus"
    wagen: int
    stapel: tuple[int, ...]     # Inhalt nach dem Schritt, unten zuerst
    ausgabe: tuple[int, ...]    # bisher ausgegebene Wagen
    verstoss: bool = False      # hinein auf einen kleineren Wagen: der Stapel ist nicht mehr fallend


@dataclass(frozen=True)
class Lauf:
    folge: tuple[int, ...]
    schritte: tuple[Schritt, ...]
    sortierbar: bool
    hoechster_stapel: int
    erster_verstoss: int | None                       # Index in `schritte`, sonst None
    zeuge: tuple[tuple[int, int, int], tuple[int, int, int]] | None   # (Plätze 1-basiert, Werte)


def parse_folge(text: str, max_laenge: int = 10) -> tuple[tuple[int, ...] | None, str | None]:
    """Text wie „3, 1, 2“ oder „3 1 2“ oder „3;1;2“ in eine Folge; (Folge, None) oder (None, Fehlermeldung)."""
    teile = [t for t in text.replace(";", " ").replace(",", " ").split() if t]
    if not teile:
        return None, "Bitte eine Folge eingeben, zum Beispiel 3, 1, 2, 5, 4."
    try:
        werte = tuple(int(t) for t in teile)
    except ValueError:
        return None, "Die Folge darf nur ganze Zahlen enthalten, getrennt durch Komma, Semikolon oder Leerzeichen."
    n = len(werte)
    if n > max_laenge:
        return None, f"Die Folge ist zu lang: höchstens {max_laenge} Wagen."
    for w in werte:
        if w < 1 or w > n:
            return None, f"Die Zahl {w} liegt nicht zwischen 1 und {n}: bei {n} Wagen muss jede Zahl von 1 bis {n} genau einmal vorkommen."
    for w in sorted(set(werte)):
        if werte.count(w) > 1:
            return None, f"Die Zahl {w} kommt mehrfach vor: jede Zahl von 1 bis {n} muss genau einmal vorkommen."
    return werte, None


def lauf(p) -> Lauf:
    """Gierige Maschine: Jeder Wagen kommt hinein; liegt oben der gerade gebrauchte Wagen, geht er sofort hinaus.
    Merkt den ersten Verstoß (Wagen auf einen kleineren gelegt, der nicht hinaus kann) und leitet daraus den Zeugen 231 ab."""
    p = tuple(p)
    stapel: list[int] = []
    ausgabe: list[int] = []
    gebraucht = 1
    schritte: list[Schritt] = []
    erster = None
    zeuge = None
    for j, x in enumerate(p):
        verstoss = bool(stapel) and stapel[-1] < x
        if verstoss and erster is None:
            y = stapel[-1]
            i = p.index(y)
            k = p.index(gebraucht)        # der gebrauchte Wagen ist noch nicht angekommen und kleiner als y
            zeuge = ((i + 1, j + 1, k + 1), (y, x, gebraucht))
            erster = len(schritte)
        stapel.append(x)
        schritte.append(Schritt("hinein", x, tuple(stapel), tuple(ausgabe), verstoss))
        while stapel and stapel[-1] == gebraucht:
            y = stapel.pop()
            ausgabe.append(y)
            gebraucht += 1
            schritte.append(Schritt("hinaus", y, tuple(stapel), tuple(ausgabe)))
    hoechster = max((len(s.stapel) for s in schritte), default=0)
    return Lauf(p, tuple(schritte), not stapel, hoechster, erster, zeuge)


def ist_sortierbar(p) -> bool:
    """Schnelle Fassung derselben Maschine ohne Schrittliste."""
    stapel = []
    gebraucht = 1
    for x in p:
        stapel.append(x)
        while stapel and stapel[-1] == gebraucht:
            stapel.pop()
            gebraucht += 1
    return not stapel


def hat_231(p) -> bool:
    """Mustersuche: Plätze i < j < k mit p[k] < p[i] < p[j]."""
    n = len(p)
    for i in range(n):
        for j in range(i + 1, n):
            if p[j] > p[i]:
                for k in range(j + 1, n):
                    if p[k] < p[i]:
                        return True
    return False


def hat_312(p) -> bool:
    """Mustersuche: Plätze i < j < k mit p[j] < p[k] < p[i]."""
    n = len(p)
    for i in range(n):
        for j in range(i + 1, n):
            if p[j] < p[i]:
                for k in range(j + 1, n):
                    if p[j] < p[k] < p[i]:
                        return True
    return False


def inverse(p) -> tuple[int, ...]:
    q = [0] * len(p)
    for i, v in enumerate(p):
        q[v - 1] = i + 1
    return tuple(q)


def ausgaben_erzeugbar(n: int) -> list[tuple[int, ...]]:
    """Alle Ausgaben bei Eingabe 1…n: jedes Wort aus „hinein“ und „hinaus“, das den Stapel nie überzieht (Dyck-Wörter), einmal durchgespielt."""
    ergebnis: list[tuple[int, ...]] = []

    def rec(naechster, stapel, aus):
        if len(aus) == n:
            ergebnis.append(tuple(aus))
            return
        if naechster <= n:
            rec(naechster + 1, stapel + [naechster], aus)
        if stapel:
            rec(naechster, stapel[:-1], aus + [stapel[-1]])

    rec(1, [], [])
    return ergebnis


def erzeuge_weg(ziel) -> tuple[list[Schritt], bool]:
    """Erzeugen: Eingabe 1…n, gewünscht ist die Ausgabe `ziel`. Der Stapel gibt aus, was oben liegt und als Nächstes gewünscht ist, sonst kommt der nächste Wagen hinein.
    Schritte und Erfolg; bei Misserfolg endet die Liste an der Stelle, an der der gewünschte Wagen nicht oben liegt und nichts mehr eingegeben werden kann."""
    ziel = tuple(ziel)
    n = len(ziel)
    stapel: list[int] = []
    ausgabe: list[int] = []
    schritte: list[Schritt] = []
    naechster = 1
    while len(ausgabe) < n:
        wunsch = ziel[len(ausgabe)]
        if stapel and stapel[-1] == wunsch:
            y = stapel.pop()
            ausgabe.append(y)
            schritte.append(Schritt("hinaus", y, tuple(stapel), tuple(ausgabe)))
        elif naechster <= n:
            stapel.append(naechster)
            schritte.append(Schritt("hinein", naechster, tuple(stapel), tuple(ausgabe)))
            naechster += 1
        else:
            return schritte, False
    return schritte, True


def wege_zahl(p) -> int:
    """Zahl der Wörter aus „hinein“ und „hinaus“, die p nach 1…n sortieren (ein Wagen darf nur hinaus, wenn er der gebrauchte ist). Vollständige Wegsuche."""
    n = len(p)

    def rec(i, stapel, gebraucht):
        if gebraucht > n:
            return 1
        summe = 0
        if stapel and stapel[-1] == gebraucht:
            summe += rec(i, stapel[:-1], gebraucht + 1)
        if i < n:
            summe += rec(i + 1, stapel + (p[i],), gebraucht)
        return summe

    return rec(0, (), 1)
