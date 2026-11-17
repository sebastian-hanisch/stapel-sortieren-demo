"""Ein Stapel: welche Ankunftsfolgen er sortiert - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Fünf Experimente: ein Stapel von Hand (Zeuge für das Muster 231), wie viele Folgen er schafft, Sortieren gegen Erzeugen, Wagen mit gleichem Ziel,
ein ausgedachtes Ankunftsmodell. Aufbau nach DEMO-PLAYBOOK §2 (Schnellstart in der Seitenleiste, Regler beim Experiment, Kernfragen vor dem Expander).

Lauffähig mit: streamlit run app.py
"""

import pandas as pd
import streamlit as st

import sts_constants as C
import sts_counting as K
import sts_evaluation as ev
import sts_format as F
import sts_machine as M
import sts_texts as T
from sts_layout import dunkles_design, kopf_css
from sts_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
    zufallsfolge_in_feld,
)
from sts_visualization import build_anteil_ueber_n, build_gruppen, build_modell, build_richtungen, build_stapel

st.set_page_config(page_title="Ein Stapel – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _anzahl(n):
    return ev.anzahl_zeile(n)


@st.cache_data(show_spinner=False)
def _probe(n, runs, seed, betriebsart):
    return ev.zufallsprobe(n, runs, seed, betriebsart)


@st.cache_data(show_spinner=False)
def _vergleich(n):
    return ev.vergleich(n)


@st.cache_data(show_spinner=False)
def _gruppen(gruppen):
    return ev.gruppen_analyse(gruppen)


@st.cache_data(show_spinner=False)
def _modell(n, runs, seed):
    return ev.modell_tabelle(n, runs, seed)


def _d_text(d):
    return F.dez(d, 2).rstrip("0").rstrip(",")


def _schritte_text(schritte):
    return ", ".join(f"{s.aktion} {s.wagen}" for s in schritte)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sts_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🚂 Ein Stapel: welche Ankunftsfolgen er sortiert")
st.markdown(T.EINLEITUNG)

# erklaerseite:einfach:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/stapel-sortieren-erklaert.json, nicht von Hand ändern)
with st.expander("💬 In einfachen Worten"):
    st.markdown(
        """
Stellen Sie sich Wagen vor, die nacheinander ankommen und auf ein Abstellgleis geschoben werden, von dem immer nur der zuletzt hineingeschobene wieder herauskommt. Die Wagen sollen in der Reihenfolge ihrer Abholung weiterfahren. Die Demo zählt, welche Ankunftsfolgen das Gleis dafür ordnen kann, und zeigt, dass es nur Folgen schafft, die ein bestimmtes **Muster aus drei Wagen** vermeiden. Sie zeigt auch, dass **Sortieren** und **Erzeugen** gleich viele, aber verschiedene Folgen ergeben, wie sich die Zählung ändert, wenn mehrere Wagen dasselbe Ziel haben, und was ein ausgedachtes Ankunftsmodell mit Verweilzeit daran ändert. Alles gilt in diesem Modell, nicht in einem echten Betrieb.

[Ausführlich und verständlich erklärt, mit Fachteil](https://sebastianhanisch.net/stapel-sortieren-erklaert.html)
        """
    )
# erklaerseite:einfach:end

with st.expander("So funktioniert ein Stapel", expanded=True):
    st.markdown(T.SO_FUNKTIONIERT)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.caption("Die Regler der Experimente stehen beim jeweiligen Experiment. Hier steht nur der Zufalls-Seed für alle Zufallsproben und Zufallsfolgen.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neuen Zufalls-Seed würfeln", width="stretch", on_click=randomize_seed)
seed = int(seed)

# --- Kernfragen -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfragen")
st.markdown("**1.** Schafft ein Stapel diese Folge? **2.** Wie oft reicht ein Stapel überhaupt? **3.** Sortiert er dasselbe, was er erzeugt?")

# --- Experiment 1 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Schafft ein Stapel diese Folge?")
st.caption(f"Folge der Abholränge eintragen: jede Zahl von 1 bis n genau einmal, höchstens {C.HAND_MAX} Wagen; Trennzeichen Komma, Semikolon oder Leerzeichen.")
c1, c2 = st.columns([3, 2])
with c1:
    hand_text = st.text_input("Ankunftsfolge", key="hand_text", help="Der erste Wert ist der Abholrang des ersten Wagens, der ankommt.")
with c2:
    st.slider("Länge der Zufallsfolge", C.HAND_ZUFALL_MIN, C.HAND_ZUFALL_MAX, key="hand_zufall_n", help="Wirkt nur beim Knopf darunter.")
    st.button("🎲 Zufallsfolge aus dem Zufalls-Seed", on_click=zufallsfolge_in_feld, width="stretch", help="Würfelt aus Zufalls-Seed und Länge eine Folge ins Textfeld.")

folge, fehler = M.parse_folge(hand_text, C.HAND_MAX)
if fehler:
    st.error(fehler)
else:
    lauf = M.lauf(folge)
    total = len(lauf.schritte)
    st.session_state["schritt"] = min(int(st.session_state["schritt"]), total)
    schritt = st.slider("Schritt", C.SCHRITT_MIN, total, key="schritt", help="0 ist der Anfang; jeder Schritt legt einen Wagen auf den Stapel oder gibt einen aus.")
    aktuell = lauf.schritte[schritt - 1] if schritt else None
    stapel = aktuell.stapel if aktuell else ()
    ausgabe = aktuell.ausgabe if aktuell else ()
    angekommen = sum(1 for s in lauf.schritte[:schritt] if s.aktion == "hinein")
    spalte_bild, spalte_text = st.columns([2, 3])
    with spalte_bild:
        st.plotly_chart(build_stapel(stapel), width="stretch", key="stapel_chart")
    with spalte_text:
        st.markdown(f"**Schritt {schritt} von {total}:** " + (f"{aktuell.aktion} {aktuell.wagen}" if aktuell else "Anfang"))
        st.markdown(f"**Wartet noch:** {F.folge(folge[angekommen:]) if angekommen < len(folge) else '–'}")
        st.markdown(f"**Stapel (unten zuerst):** {F.folge(stapel) if stapel else 'leer'}")
        st.markdown(f"**Ausgabe bisher:** {F.folge(ausgabe) if ausgabe else '–'}")
        if aktuell and aktuell.verstoss:
            st.warning("Hier liegt ein Wagen auf einem kleineren (rot). Der kleinere muss vor ihm hinaus und kommt nicht mehr heran: ab jetzt kann die Folge nicht mehr sortiert werden.")
        wege = M.wege_zahl(folge)
        st.markdown(f"**Wege, die diese Folge sortieren** (vollständige Wegsuche über alle Wörter aus „hinein“ und „hinaus“): {wege}")
    art, text = ev.verdict_hand(lauf)
    getattr(st, art)(text)
    tabelle = pd.DataFrame({"Schritt": range(1, total + 1), "Aktion": [f"{s.aktion} {s.wagen}" for s in lauf.schritte],
                            "Stapel danach": [F.folge(s.stapel) if s.stapel else "leer" for s in lauf.schritte],
                            "Ausgabe danach": [F.folge(s.ausgabe) if s.ausgabe else "–" for s in lauf.schritte]})
    st.dataframe(tabelle, hide_index=True, width="stretch", height=min(38 + 35 * total, 320))

st.markdown("---")

# --- Experiment 2 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Wie viele Folgen schafft ein Stapel?")
st.caption("Anteil der Folgen, die ein Stapel sortiert. Bis n = 8 werden alle Folgen durchgespielt, bis n = 14 zählt eine Zustandsrechnung, darüber gilt nur die Formel in Brüchen.")
a1, a2, a3 = st.columns(3)
with a1:
    n2 = st.slider("Wagen n", *bounds("anzahl_n"), key="anzahl_n")
with a2:
    runs2 = st.slider("Zufallsprobe: Zahl der Zufallsfolgen", *bounds("anzahl_runs"), key="anzahl_runs", step=C.PROBE_SCHRITT)
with a3:
    betrieb = st.radio("Betriebsart", C.BETRIEBSARTEN, key="anzahl_betrieb", horizontal=True,
                       help="sofort: der Stapel darf zwischendurch ausgeben. verzögert: erst alle Wagen hinein, danach nur noch hinaus.")
zeile = _anzahl(int(n2))
probe = _probe(int(n2), int(runs2), seed, betrieb)
sortierbar2 = zeile.sortierbar if betrieb == "sofort" else 1
m1, m2, m3, m4 = st.columns(4)
m1.metric("Folgen insgesamt (n!)", F.ganz(zeile.fakultaet))
m2.metric(f"sortierbar ({betrieb})", F.ganz(sortierbar2))
m3.metric("Anteil", F.prozent_signifikant(sortierbar2 / zeile.fakultaet))
m4.metric("1 von", F.eins_von(zeile.fakultaet / sortierbar2))
st.caption(f"Rechenweg bei n = {zeile.n}: {zeile.methode}.")
st.plotly_chart(build_anteil_ueber_n(int(n2)), width="stretch", key="anteil_chart")
rows2 = ev.tabelle_anzahl(int(n2), betrieb)
tab2 = pd.DataFrame({
    "n": [r["n"] for r in rows2],
    "Folgen n!": [F.ganz(r["folgen"]) for r in rows2],
    "sortierbar": [F.ganz(r["sortierbar"]) for r in rows2],
    "Anteil": [F.prozent_signifikant(float(r["anteil"])) for r in rows2],
    "1 von": [F.eins_von(r["eins_von"]) for r in rows2],
    "Faktor gegen n − 1": [F.bruch(r["faktor"]) + f" = {F.dez(float(r['faktor']), 3)}" for r in rows2],
})
st.dataframe(tab2, hide_index=True, width="stretch", height=min(38 + 35 * len(rows2), 360))
art, text = ev.verdict_anzahl(zeile, probe, betrieb)
getattr(st, art)(text)

st.markdown("---")

# --- Experiment 3 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 3: Sortiert er dasselbe, was er erzeugt?")
st.caption("Sortieren: die Ankunftsfolge ist gegeben, die Ausgabe soll 1, 2, …, n sein. Erzeugen: die Eingabe ist 1, 2, …, n, gefragt sind die möglichen Ausgaben.")
n3 = st.slider("Wagen n", *bounds("richtung_n"), key="richtung_n")
v = _vergleich(int(n3))
if n3 <= C.AUSGESCHRIEBEN_MAX:
    k1, k2, k3 = st.columns(3)
    k1.markdown("**sortierbar** (Eingabe vermeidet 231)")
    k1.markdown(", ".join("".join(map(str, p)) for p in sorted(v.sortierbar)))
    k2.markdown("**erzeugbar** (Ausgabe vermeidet 312)")
    k2.markdown(", ".join("".join(map(str, p)) for p in sorted(v.erzeugbar)))
    k3.markdown(f"**in beiden** (2^(n−1) = {v.zweihochn})")
    k3.markdown(", ".join("".join(map(str, p)) for p in sorted(v.beide)))
else:
    beispiele = pd.DataFrame({
        "nur sortierbar (erste 6)": ["".join(map(str, p)) for p in sorted(v.nur_sortierbar)[:6]],
        "nur erzeugbar (erste 6)": ["".join(map(str, p)) for p in sorted(v.nur_erzeugbar)[:6]],
        "in beiden (erste 6)": ["".join(map(str, p)) for p in sorted(v.beide)[:6]],
    })
    st.dataframe(beispiele, hide_index=True, width="stretch")
vergleiche = [_vergleich(m) for m in range(C.RICHTUNG_N_MIN, C.RICHTUNG_N_MAX + 1)]
st.plotly_chart(build_richtungen(vergleiche), width="stretch", key="richtung_chart")
art, text = ev.verdict_richtung(v)
getattr(st, art)(text)
st.markdown("**Das kleinste Beispiel (n = 3):** 231 lässt sich erzeugen, aber nicht sortieren; 312 lässt sich sortieren, aber nicht erzeugen.")
zeilen3 = []
for f in ((2, 3, 1), (3, 1, 2)):
    sort_lauf = M.lauf(f)
    erz_schritte, erz_ok = M.erzeuge_weg(f)
    zeilen3.append({
        "Folge": F.folge(f),
        "Sortieren (Eingabe: diese Folge)": ("gelingt: " if sort_lauf.sortierbar else "scheitert: ") + _schritte_text(sort_lauf.schritte)
        + ("" if sort_lauf.sortierbar else f"; es bleibt {F.folge(sort_lauf.schritte[-1].stapel)} im Stapel"),
        "Erzeugen (Eingabe: 1, 2, 3)": ("gelingt: " if erz_ok else "scheitert: ") + _schritte_text(erz_schritte)
        + ("" if erz_ok else f"; oben liegt {erz_schritte[-1].stapel[-1]}, gewünscht ist {f[len(erz_schritte[-1].ausgabe)]}"),
    })
st.dataframe(pd.DataFrame(zeilen3), hide_index=True, width="stretch")

st.markdown("---")

# --- Experiment 4 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 4: Wagen mit gleichem Ziel")
st.caption(f"Gruppengrößen eintragen: je Gruppe 1 bis {C.GRUPPE_MAX_GROESSE} Wagen mit gleichem Ziel, höchstens {C.GRUPPEN_MAX_ANZAHL} Gruppen und {C.GRUPPEN_MAX_WAGEN} Wagen. "
           "Gruppe 1 fährt zuerst ab. Gezählt werden verschiedene Wörter.")
gruppen_text = st.text_input("Gruppengrößen", key="gruppen_text", help="Zum Beispiel 2, 2, 2, 2: vier Gruppen zu je zwei Wagen.")
gruppen, fehler4 = ev.parse_gruppen(gruppen_text)
if fehler4:
    st.error(fehler4)
else:
    ga = _gruppen(gruppen)
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Wagen n", ga.n)
    g2.metric("verschiedene Wörter", F.ganz(ga.woerter))
    g3.metric("sortierbar", F.ganz(ga.sortierbar))
    g4.metric("Anteil", F.prozent(float(ga.anteil), 2))
    st.plotly_chart(build_gruppen(ga), width="stretch", key="gruppen_chart")
    st.caption(f"Rechenweg: Zustandsrechnung mit {F.ganz(ga.zustaende)} Zuständen, ohne die Wörter aufzuzählen."
               + (f" Kontrolle durch Aufzählung aller {F.ganz(ga.woerter)} Wörter: {F.ganz(ga.kontrolle)} ({'stimmt überein' if ga.kontrolle == ga.sortierbar else 'ABWEICHUNG'})."
                  if ga.kontrolle is not None else f" Zur Kontrolle durch Aufzählung sind es zu viele Wörter (mehr als {F.ganz(C.AUFZAEHLUNG_WOERTER_MAX)})."))
    art, text = ev.verdict_gruppen(ga)
    getattr(st, art)(text)
    if ga.beispiel:
        wort, zeuge = ga.beispiel
        (i, j, k), (y, x, z) = zeuge
        st.markdown(f"**Beispiel eines unsortierbaren Wortes:** {F.folge(wort)}; Zeuge für das strenge Muster 231 an den Plätzen {ev.plaetze((i, j, k))} (Werte {y}, {x}, {z}).")
    else:
        st.markdown("**Beispiel:** mit höchstens zwei Gruppen gibt es kein unsortierbares Wort.")

st.markdown("---")

# --- Experiment 5 ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 5: Wie oft reicht ein Stapel bei Verweilzeit D? (Modell V, ausgedacht)")
st.caption("**Ausgedachtes Modell, keine reale Ankunftsfolge.** Wagen i kommt zur Zeit i und bleibt im Mittel D Ankunftsabstände; der Abholrang ist die Reihenfolge der Abfahrten. "
           "**Das Modell benutzt nur die Rangfolge der Abfahrten; der Stapel gibt frei aus.**")
e1, e2, e3, e4 = st.columns(4)
with e1:
    n5 = st.slider("Wagen n", *bounds("modell_n"), key="modell_n")
with e2:
    d5 = st.select_slider("Mittlere Verweilzeit D", options=C.D_WERTE, key="modell_d", format_func=_d_text, help="In Ankunftsabständen; je größer D, desto mehr ähnelt Modell V gleich wahrscheinlichen Folgen.")
with e3:
    runs5 = st.slider("Zufallsfolgen N", *bounds("modell_runs"), key="modell_runs", step=C.MODELL_RUNS_SCHRITT)
with e4:
    zeit5 = st.toggle("Abholzeitpunkt fest", key="modell_zeit", help="Jeder Wagen verlässt den Stapel genau zu seiner Abfahrtszeit: keine Wahlfreiheit. Ändert die Kurve und den Satz unten.")
sekunden = ev.schaetze_sekunden(int(n5), int(runs5))
with st.spinner(f"Rechne {F.ganz(int(n5) * int(runs5))} exakte Zufallszahlen, etwa {F.dez(sekunden, 0)} s (danach aus dem Zwischenspeicher) …"):
    zeilen5 = _modell(int(n5), int(runs5), seed)

exakt5 = float(K.anteil(int(n5)))
st.plotly_chart(build_modell(zeilen5, exakt5, int(n5), d5, bool(zeit5)), width="stretch", key="modell_chart")
tab5 = {"D": [_d_text(z["d"]) for z in zeilen5], "sortierbar (nur Rangfolge)": [F.dez(z["anteil"] * 100, 1) + " %" for z in zeilen5],
        "Band 95 %": [f"{F.dez(z['lo'] * 100, 1)} bis {F.dez(z['hi'] * 100, 1)} %" for z in zeilen5]}
if zeit5:
    tab5["sortierbar (Abholzeitpunkt fest)"] = [F.dez(z["anteil_z"] * 100, 1) + " %" for z in zeilen5]
st.dataframe(pd.DataFrame(tab5), hide_index=True, width="stretch", height=38 + 35 * len(zeilen5))
gewaehlt = next(z for z in zeilen5 if z["d"] == d5)
art, text = ev.verdict_modell(gewaehlt, int(n5), int(runs5), seed, bool(zeit5))
getattr(st, art)(text)

sync_query_params({k: st.session_state[k] for k in (
    "seed_input", "hand_text", "anzahl_n", "anzahl_runs", "anzahl_betrieb", "richtung_n", "gruppen_text", "modell_n", "modell_d", "modell_runs", "modell_zeit")})

st.markdown("---")

# --- Grenzen --------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(T.GRENZEN)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    # erklaerseite:lesehilfe:start (erzeugt von tools/set_demo_explainer.py (Website-Repo) aus tools/content/explainers/stapel-sortieren-erklaert.json, nicht von Hand ändern)
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind die Wagenzahl $n$ und eine Ankunftsfolge $p$ der Abholränge $1, \dots, n$. Gesucht ist, ob ein Stapel $p$ zu $1, 2, \dots, n$ sortiert, wie viele Folgen er sortiert und wie das mit dem Erzeugen zusammenhängt.

| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Wagen |
| $p = (p_1, \dots, p_n)$ | Ankunftsfolge: $p_i$ ist der Abholrang des $i$-ten ankommenden Wagens (1 wird zuerst abgeholt) |
| $p^{-1}$ | Inverse von $p$: Platz und Rang vertauscht |
| $C_n$ | Catalan-Zahl $\frac{1}{n+1}\binom{2n}{n}$: Zahl der Folgen, die ein Stapel sortiert |
| $\text{Anteil}(n)$ | sortierbare Folgen geteilt durch alle $n!$ Folgen |
| $g_1, \dots, g_k$ | Größen der Gruppen von Wagen mit gleichem Ziel (Gruppe 1 fährt zuerst ab) |
| $D$, $Y_i$, $a_i$ | Modell V: mittlere Verweilzeit, Verweilzeit und Abfahrtszeit von Wagen $i$ (in Ankunftsabständen) |

[Schritt für Schritt erklärt, mit Herleitung und Literatur](https://sebastianhanisch.net/stapel-sortieren-erklaert.html#fachleute)
        """
    )
    # erklaerseite:lesehilfe:end
    st.markdown(T.KONVENTIONEN)
    st.markdown(T.FORMELN)

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
