"""Zahlen im deutschen Format: Dezimalkomma, Gruppierung mit Leerzeichen ab fünf Stellen (DIN 5008)."""

from fractions import Fraction


def ganz(n: int) -> str:
    """16796 → „16 796“, 1430 → „1430“."""
    s = str(abs(int(n)))
    if len(s) >= 5:
        gruppen = []
        while s:
            gruppen.append(s[-3:])
            s = s[:-3]
        s = " ".join(reversed(gruppen))
    return ("-" if n < 0 else "") + s


def dez(x: float, stellen: int = 2) -> str:
    return f"{x:.{stellen}f}".replace(".", ",")


def prozent(anteil: float, stellen: int = 1) -> str:
    """Anteil 0…1 als Prozentangabe, z. B. 0,4629 → „0,463 %“ bei drei Stellen."""
    return f"{dez(anteil * 100, stellen)} %"


def prozent_signifikant(anteil: float) -> str:
    """Prozent mit zwei bis drei gültigen Ziffern: 35,0 % · 18,3 % · 3,55 % · 0,463 % · 0,0434 %; darunter in Zehnerpotenz-Schreibweise (7,4·10⁻⁴ %)."""
    if anteil == 0:
        return "0 %"
    v = anteil * 100
    if v >= 10:
        return prozent(anteil, 1)
    if v >= 1:
        return prozent(anteil, 2)
    if v >= 0.1:
        return prozent(anteil, 3)
    if v >= 0.01:
        return prozent(anteil, 4)
    return f"{potenz(v)} %"


def potenz(x: float) -> str:
    """Kleine Zahl in der Schreibweise 7,4·10⁻⁶."""
    if x == 0:
        return "0"
    mant, exp = f"{x:.1e}".split("e")
    hoch = str(abs(int(exp))).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{mant.replace('.', ',')}·10{'⁻' if int(exp) < 0 else ''}{hoch}"


def bruch(f: Fraction) -> str:
    return f"{f.numerator}/{f.denominator}" if f.denominator != 1 else str(f.numerator)


def folge(p) -> str:
    return "(" + ", ".join(str(x) for x in p) + ")"


def eins_von(x: float) -> str:
    """„1 von x“: unter 100 mit einer Nachkommastelle (5,5), sonst ganzzahlig gerundet (216)."""
    return dez(x, 1) if x < 100 else ganz(round(x))
