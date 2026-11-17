"""Zahlenformat: Dezimalkomma, Gruppierung ab fünf Stellen, Prozent mit zwei bis drei gültigen Ziffern."""

from fractions import Fraction

import sts_format as F
import sts_models as Mo


def test_ganz_gruppiert_ab_fuenf_stellen():
    assert [F.ganz(x) for x in (0, 999, 1430, 9999, 10000, 16796, 3628800, -16796)] == ["0", "999", "1430", "9999", "10 000", "16 796", "3 628 800", "-16 796"]


def test_dez_und_prozent_mit_komma():
    assert F.dez(3.14159, 2) == "3,14" and F.dez(2.0, 0) == "2" and F.prozent(0.1397, 2) == "13,97 %" and F.prozent(1, 1) == "100,0 %"


def test_prozent_signifikant_stufen():
    assert [F.prozent_signifikant(x) for x in (0.35, 0.0851, 0.0355, 0.00463, 0.000434, 7.4e-6, 0.0)] == \
        ["35,0 %", "8,51 %", "3,55 %", "0,463 %", "0,0434 %", "7,4·10⁻⁴ %", "0 %"]


def test_potenz_und_bruch_und_folge():
    assert F.potenz(7.4e-6) == "7,4·10⁻⁶" and F.potenz(2.5e3) == "2,5·10³" and F.potenz(0) == "0"
    assert F.bruch(Fraction(19, 55)) == "19/55" and F.bruch(Fraction(4, 2)) == "2" and F.folge((3, 1, 2)) == "(3, 1, 2)"


def test_eins_von():
    assert F.eins_von(5.45) == "5,5" and F.eins_von(216.05) == "216" and F.eins_von(2302.76) == "2303" and F.eins_von(1.34e6) == "1 340 000"


def test_zufalls_seed_der_zufallsquellen():
    assert Mo.seed_uniform(1301, 6) == 1307 and Mo.seed_modell_v(1301, 10) == 1301010
