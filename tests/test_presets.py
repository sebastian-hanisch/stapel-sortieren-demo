"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Voreinstellung, Permalink-Begrenzung."""

import pytest

import sts_constants as C
import sts_machine as M
import sts_presets as P
import sts_evaluation as ev


def test_jedes_preset_hat_einen_hilfetext_und_nur_bekannte_regler():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) <= set(P.SETTING_SPECS), name
        assert C.PRESET_HELP[name]


def test_preset_werte_liegen_in_den_reglergrenzen():
    for name, preset in C.PRESETS.items():
        for key, value in preset.items():
            spec = P.SETTING_SPECS[key]
            assert P._begrenze(spec, value) == value, (name, key)


def test_standard_preset_ist_die_voreinstellung():
    standard = C.PRESETS[next(iter(C.PRESETS))]
    assert next(iter(C.PRESETS)) == C.PRESET_STANDARD
    assert all(standard.get(k, spec.default) == spec.default for k, spec in P.SETTING_SPECS.items())


def test_kein_zweites_preset_gleicht_der_voreinstellung():
    """Sonst könnten zwei Presets gleichzeitig aktiv sein, und das zweite würde nie hervorgehoben."""
    voreinstellung = {k: spec.default for k, spec in P.SETTING_SPECS.items()}
    for name, preset in list(C.PRESETS.items())[1:]:
        assert {**voreinstellung, **preset} != voreinstellung, name


def test_presets_sind_untereinander_verschieden():
    voll = [tuple(sorted({**{k: s.default for k, s in P.SETTING_SPECS.items()}, **p}.items())) for p in C.PRESETS.values()]
    assert len(set(voll)) == len(voll)


def test_handfolgen_der_presets_sind_gueltig_und_wie_beschrieben():
    assert M.lauf(M.parse_folge(C.PRESETS[C.PRESET_STANDARD]["hand_text"])[0]).sortierbar
    nicht = M.parse_folge(C.PRESETS["… nicht sortierbar (2, 4, 1, 3, 5)"]["hand_text"])[0]
    assert nicht == (2, 4, 1, 3, 5) and not M.lauf(nicht).sortierbar
    assert ev.parse_gruppen(C.PRESETS["Zielgruppen 2, 2, 2, 2"]["gruppen_text"])[0] == (2, 2, 2, 2)


def test_permalink_begrenzung_und_einrasten():
    runs = P.SETTING_SPECS["modell_runs"]
    assert P._begrenze(runs, 99999) == C.MODELL_RUNS_MAX and P._begrenze(runs, 0) == C.MODELL_RUNS_MIN and P._begrenze(runs, 3400) == 3000
    assert P._begrenze(P.SETTING_SPECS["modell_d"], 3.0) == C.DEFAULT_D and P._begrenze(P.SETTING_SPECS["modell_d"], 4.0) == 4.0
    assert P._begrenze(P.SETTING_SPECS["anzahl_betrieb"], "x") == C.DEFAULT_BETRIEB
    assert P._begrenze(P.SETTING_SPECS["anzahl_n"], 99) == C.ANZAHL_N_MAX and P._begrenze(P.SETTING_SPECS["richtung_n"], 1) == C.RICHTUNG_N_MIN


def test_bool_und_textcaster():
    assert P._bool("True") and P._bool("1") and not P._bool("False") and not P._bool("0")
    assert len(P._text("x" * 100)) == 60


def test_url_parameter_sind_eindeutig():
    namen = [s.url_param for s in P.SETTING_SPECS.values()]
    assert len(namen) == len(set(namen))


def test_voreinstellung_n_ist_nicht_gleich_dem_preset_n():
    assert C.PRESETS["Wie viele Folgen? n = 10"]["anzahl_n"] != C.DEFAULT_ANZAHL_N and C.PRESETS["Sortieren oder Erzeugen? n = 3"]["richtung_n"] != C.DEFAULT_RICHTUNG_N
