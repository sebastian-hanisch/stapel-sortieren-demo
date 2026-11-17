"""Layout (DEMO-PLAYBOOK §2): fester Kopf, Schnellstart oben in der Seitenleiste, aktives Preset hervorgehoben, Regler beim Experiment.

Die Hervorhebung ist zustandslos (`aktives_preset` vergleicht jeden Regler aus SETTING_SPECS mit dem Preset). Der Test unten stellt sicher, dass wirklich JEDER Regler der
Seite dort steht (bis auf die reinen Ansichtsregler): sonst bliebe das Preset trotz Änderung markiert."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import sts_constants as C
import sts_presets as P

APP = str(Path(__file__).resolve().parent.parent / "app.py")
REGLER_ARTEN = ("slider", "number_input", "select_slider", "selectbox", "radio", "toggle", "checkbox", "text_input")


def _app() -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _typen(at) -> dict:
    """Button-Typ je Preset-Name (die Preset-Buttons der Seitenleiste)."""
    return {b.label: b.proto.type for b in at.sidebar.button if b.label in C.PRESETS}


def _regler(at, key):
    for ort in (at.main, at.sidebar):
        for art in REGLER_ARTEN:
            try:
                return getattr(ort, art)(key=key)
            except KeyError:
                continue
    raise AssertionError(f"Regler {key} steht nicht auf der Seite")


def _anderer_wert(key, regler):
    spec = P.SETTING_SPECS[key]
    if spec.options is not None:
        return next(o for o in spec.options if o != regler.value)
    if key in ("hand_text", "gruppen_text"):
        return "1, 2, 3" if key == "hand_text" else "1, 1, 1"
    if isinstance(spec.default, bool):
        return not regler.value
    if spec.lo is not None:
        return spec.hi if regler.value != spec.hi else spec.lo
    raise AssertionError(key)


def test_presets_stehen_in_der_seitenleiste_und_nicht_im_hauptbereich():
    at = _app()
    assert [b.label for b in at.sidebar.button][: len(C.PRESETS)] == list(C.PRESETS)  # die ersten Buttons der Seitenleiste
    assert not [b for b in at.main.button if b.label in C.PRESETS]


def test_titel_steht_im_festen_kopf():
    at = _app()
    assert "st-key-kopf" in " ".join(h.proto.body for h in at.get("html"))  # das Stylesheet setzt an der Klasse des Containers an
    assert at.title[0].value


def test_experimentregler_stehen_im_hauptbereich_nur_der_zufalls_seed_in_der_seitenleiste():
    at = _app()
    assert {w.key for art in REGLER_ARTEN for w in getattr(at.sidebar, art) if w.key} == {"seed_input"}
    for key in P.SETTING_SPECS:
        if key != "seed_input":
            _regler(at, key)  # wirft, wenn der Regler fehlt
    assert {w.key for art in REGLER_ARTEN for w in getattr(at.main, art) if w.key} >= set(P.SETTING_SPECS) - {"seed_input"}


def test_beim_start_ist_genau_das_standard_preset_hervorgehoben():
    typen = _typen(_app())
    assert [name for name, typ in typen.items() if typ == "primary"] == [next(iter(C.PRESETS))]


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_angeklicktes_preset_ist_hervorgehoben_und_bleibt_es_im_naechsten_lauf(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]
    at.run()
    assert [n for n, typ in _typen(at).items() if typ == "primary"] == [name]


def test_jeder_regler_der_seite_steht_in_setting_specs_ausser_den_ansichtsreglern():
    at = _app()
    schluessel = {w.key for ort in (at.main, at.sidebar) for art in REGLER_ARTEN for w in getattr(ort, art) if w.key}
    fehlt = schluessel - set(P.SETTING_SPECS) - set(P.ANSICHT_REGLER)
    assert not fehlt, f"Regler {sorted(fehlt)} fehlen in SETTING_SPECS: ihre Änderung hebt das aktive Preset nicht auf"
    assert set(P.ANSICHT_REGLER) <= schluessel


@pytest.mark.parametrize("state_key", list(P.SETTING_SPECS))
def test_jede_aenderung_eines_reglers_hebt_die_hervorhebung_auf(state_key):
    at = _app()
    regler = _regler(at, state_key)
    regler.set_value(_anderer_wert(state_key, regler)).run()
    assert not at.exception, [str(e) for e in at.exception]
    assert "primary" not in _typen(at).values()
    # erneutes Anklicken markiert wieder
    name = next(iter(C.PRESETS))
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert _typen(at)[name] == "primary"


def test_ansichtsregler_heben_die_hervorhebung_nicht_auf():
    at = _app()
    at.slider(key="schritt").set_value(3).run()
    assert _typen(at)[C.PRESET_STANDARD] == "primary"
    at.slider(key="hand_zufall_n").set_value(5).run()
    assert _typen(at)[C.PRESET_STANDARD] == "primary"
