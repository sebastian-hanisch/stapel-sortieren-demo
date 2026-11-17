"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: laedt app.py mit den
Standardeinstellungen, klickt jeden Preset-Button und faehrt jeden Slider an seine Grenzen und prueft, dass
kein Python-Fehler auftritt - insbesondere `streamlit.errors.StreamlitDuplicateElementId` (mehrere
st.plotly_chart-Aufrufe ohne eindeutiges key= koennen zufaellig identischen Inhalt rendern und kollidieren)
und `StreamlitAPIException` bei Slidern mit berechneten Grenzen (min == max)."""

import os

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "\u25b6"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])



def test_standard_zeigt_das_verdikt_der_voreinstellung():
    at = _fresh_app()
    assert any("(3, 1, 2, 5, 4): **sortierbar**, höchster Stapel 2 Wagen" in e.value for e in at.success)


def test_ungueltige_folge_zeigt_meldung_statt_zahl_und_kein_schritt_regler():
    at = _fresh_app()
    at.text_input(key="hand_text").set_value("1, 1, 2").run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    assert any("mehrfach" in e.value for e in at.error)
    assert not [s for s in at.slider if s.key == "schritt"]
    # wieder gültig: der Regler ist zurück
    at.text_input(key="hand_text").set_value("2, 4, 1, 3, 5").run(timeout=TIMEOUT)
    assert any("**nicht sortierbar**" in e.value and "Plätzen 1 bis 3 (Werte 2, 4, 1)" in e.value for e in at.error)


def test_nicht_sortierbare_folge_warnt_beim_verstoss_schritt():
    at = _fresh_app()
    at.text_input(key="hand_text").set_value("2, 4, 1, 3, 5").run(timeout=TIMEOUT)
    at.slider(key="schritt").set_value(2).run(timeout=TIMEOUT)
    assert any("Hier liegt ein Wagen auf einem kleineren" in e.value for e in at.warning)
    at.slider(key="schritt").set_value(1).run(timeout=TIMEOUT)
    assert not any("Hier liegt ein Wagen auf einem kleineren" in e.value for e in at.warning)


def test_schritt_wird_bei_kuerzerer_folge_begrenzt():
    at = _fresh_app()
    at.text_input(key="hand_text").set_value("1, 2").run(timeout=TIMEOUT)
    assert not at.exception and at.slider(key="schritt").max == 4 and at.slider(key="schritt").value <= 4


def test_zufallsfolge_knopf_schreibt_eine_gueltige_folge_der_gewaehlten_laenge():
    at = _fresh_app()
    at.slider(key="hand_zufall_n").set_value(9).run(timeout=TIMEOUT)
    zuf = [b for b in at.button if b.label.startswith("🎲 Zufallsfolge")][0]
    zuf.click().run(timeout=TIMEOUT)
    assert not at.exception
    werte = [int(x) for x in at.text_input(key="hand_text").value.split(",")]
    assert sorted(werte) == list(range(1, 10))


def test_experiment_2_nennt_n_10_zahlen_und_rechenweg():
    at = _fresh_app()
    at.slider(key="anzahl_n").set_value(10).run(timeout=TIMEOUT)
    assert any("n = 10: 16 796 von 3 628 800 Folgen (0,463 %, 1 von 216)" in e.value for e in at.info)
    assert any("Zustandsrechnung und Formel stimmen überein" in c.value for c in at.caption)


def test_experiment_2_verzoegert_zeigt_eine_folge():
    at = _fresh_app()
    at.radio(key="anzahl_betrieb").set_value("verzögert").run(timeout=TIMEOUT)
    assert not at.exception
    assert any(m.label.startswith("sortierbar (verzögert)") and m.value == "1" for m in at.metric)


def test_experiment_3_n_3_zeigt_beide_mengen_ausgeschrieben():
    at = _fresh_app()
    at.slider(key="richtung_n").set_value(3).run(timeout=TIMEOUT)
    assert any("123, 132, 213, 312, 321" in m.value for m in at.markdown)
    assert any("123, 132, 213, 231, 321" in m.value for m in at.markdown)


def test_experiment_4_ungueltige_eingabe_und_gueltige():
    at = _fresh_app()
    at.text_input(key="gruppen_text").set_value("9, 1").run(timeout=TIMEOUT)
    assert any("1 bis 5" in e.value for e in at.error)
    at.text_input(key="gruppen_text").set_value("2, 2, 2, 2").run(timeout=TIMEOUT)
    assert any("352 von 2520 verschiedenen Wörtern" in e.value for e in at.info)


def test_experiment_5_zeitbindung_schalter_aendert_den_satz():
    at = _fresh_app()
    ohne = [e.value for e in at.info if "Modell" in e.value or "Ausgedachtes" in e.value]
    at.toggle(key="modell_zeit").set_value(True).run(timeout=TIMEOUT)
    mit = [e.value for e in at.info if "Ausgedachtes" in e.value]
    assert ohne and mit and "Abholzeitpunkt" not in ohne[0] and "Abholzeitpunkt" in mit[0]


def test_permalink_uebernimmt_werte_begrenzt():
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.query_params["an"] = "99"
    at.query_params["md"] = "4.0"
    at.query_params["folge"] = "2 4 1 3 5"
    at.run(timeout=TIMEOUT)
    assert not at.exception
    assert at.slider(key="anzahl_n").value == 30 and at.select_slider(key="modell_d").value == 4.0 and at.text_input(key="hand_text").value == "2 4 1 3 5"
