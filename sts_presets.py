"""Permalink (Begrenzen), Presets und Zufalls-Seed-Button.

Alle Regler der fünf Experimente stehen in SETTING_SPECS: ein Preset ist aktiv, wenn jeder Regler dem Preset (sonst der Voreinstellung) entspricht. Ein Preset lädt ein
vollständiges Beispiel: alle Regler, die es nicht nennt, gehen auf die Voreinstellung zurück. Reine Ansichtsregler (Schritt, Länge der Zufallsfolge) ändern nichts
am Ergebnis und stehen deshalb nicht in SETTING_SPECS."""

import random
from dataclasses import dataclass

import streamlit as st

import sts_constants as C
from sts_models import zufallsfolge_uniform
from sts_rng import SplitMix64


def _bool(s) -> bool:
    return str(s).strip().lower() in ("1", "true", "ja")


def _text(s) -> str:
    return str(s)[:60]


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: object
    default: object
    lo: float | None = None
    hi: float | None = None
    step: int | None = None
    options: tuple | None = None


SETTING_SPECS = {
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "hand_text": SettingSpec("folge", _text, C.DEFAULT_HAND_TEXT),
    "anzahl_n": SettingSpec("an", int, C.DEFAULT_ANZAHL_N, C.ANZAHL_N_MIN, C.ANZAHL_N_MAX),
    "anzahl_runs": SettingSpec("ar", int, C.DEFAULT_PROBE_N, C.PROBE_N_MIN, C.PROBE_N_MAX, C.PROBE_SCHRITT),
    "anzahl_betrieb": SettingSpec("ab", str, C.DEFAULT_BETRIEB, options=C.BETRIEBSARTEN),
    "richtung_n": SettingSpec("rn", int, C.DEFAULT_RICHTUNG_N, C.RICHTUNG_N_MIN, C.RICHTUNG_N_MAX),
    "gruppen_text": SettingSpec("gr", _text, C.DEFAULT_GRUPPEN),
    "modell_n": SettingSpec("mn", int, C.DEFAULT_MODELL_N, C.MODELL_N_MIN, C.MODELL_N_MAX),
    "modell_d": SettingSpec("md", float, C.DEFAULT_D, options=C.D_WERTE),
    "modell_runs": SettingSpec("mr", int, C.DEFAULT_MODELL_RUNS, C.MODELL_RUNS_MIN, C.MODELL_RUNS_MAX, C.MODELL_RUNS_SCHRITT),
    "modell_zeit": SettingSpec("mz", _bool, False),
}
PRESET_KEYS = set(SETTING_SPECS)
ANSICHT_REGLER = ("schritt", "hand_zufall_n")      # ändern nichts am Ergebnis, stehen nicht in SETTING_SPECS


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default
    st.session_state.setdefault("schritt", 2 * C.HAND_MAX)
    st.session_state.setdefault("hand_zufall_n", C.DEFAULT_HAND_ZUFALL)


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def _begrenze(spec: SettingSpec, value):
    if spec.options is not None:
        return value if value in spec.options else spec.default
    if spec.lo is not None:
        value = max(spec.lo, value)
    if spec.hi is not None:
        value = min(spec.hi, value)
    if spec.step:
        value = spec.lo + round((value - spec.lo) / spec.step) * spec.step
    return value


def load_permalink_settings():
    """Einmal je Sitzung: Werte aus der Adresszeile übernehmen, auf die Reglergrenzen begrenzt."""
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
            except (ValueError, TypeError):
                continue
            st.session_state[state_key] = _begrenze(spec, value)
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}; die Adresszeile spiegelt die Konfiguration."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def apply_preset(name):
    """Alle Regler auf die Voreinstellung, dann die Werte des Presets; der Schritt springt ans Ende der Folge."""
    for state_key, spec in SETTING_SPECS.items():
        st.session_state[state_key] = spec.default
    for state_key, value in C.PRESETS[name].items():
        st.session_state[state_key] = value
    st.session_state["schritt"] = 2 * C.HAND_MAX


def aktives_preset():
    """Name des Presets, dessen Werte GENAU den aktuellen Einstellungen entsprechen, sonst None (zustandslos)."""
    for name, preset in C.PRESETS.items():
        if all(st.session_state.get(state_key, spec.default) == preset.get(state_key, spec.default) for state_key, spec in SETTING_SPECS.items()):
            return name
    return None


def sidebar_presets():
    """Schnellstart oben in der Seitenleiste; das aktive Preset ist hervorgehoben (`type="primary"`)."""
    st.header("🎯 Schnellstart")
    st.caption("Ein Beispiel laden (die übrigen Regler gehen auf die Voreinstellung zurück); das Ergebnis steht beim jeweiligen Experiment:")
    aktiv = aktives_preset()
    for name in C.PRESETS:
        st.button(
            name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}",
            type="primary" if aktiv == name else "secondary",
        )


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)


def zufallsfolge_in_feld():
    """Würfelt aus Zufalls-Seed und Länge eine Folge und schreibt sie ins Textfeld von Experiment 1."""
    n = int(st.session_state.get("hand_zufall_n", C.DEFAULT_HAND_ZUFALL))
    seed = int(st.session_state.get("seed_input", C.DEFAULT_SEED))
    p = zufallsfolge_uniform(SplitMix64(seed + 17 * n), n)
    st.session_state["hand_text"] = ", ".join(str(x) for x in p)
    st.session_state["schritt"] = 2 * C.HAND_MAX
