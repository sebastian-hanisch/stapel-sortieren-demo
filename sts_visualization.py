"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

from math import factorial

import plotly.graph_objects as go

import sts_constants as C
import sts_counting as K


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_stapel(stapel, hoehe: int = C.HAND_MAX):
    """Der Stapel als Säule, unten zuerst. Ein Wagen, der über einem kleineren liegt, ist rot: der kleinere muss zuerst hinaus und kann nicht mehr."""
    fig = go.Figure()
    for i, w in enumerate(stapel):
        schlecht = i > 0 and stapel[i - 1] < w
        fig.add_shape(type="rect", x0=0.25, x1=0.75, y0=i, y1=i + 0.92, line=dict(width=1, color="rgba(60,60,60,0.8)"),
                      fillcolor=C.COLOR_BAD if schlecht else C.COLOR_OK)
        fig.add_annotation(x=0.5, y=i + 0.46, text=f"<b>{w}</b>", showarrow=False, font=dict(color="white", size=16))
    fig.add_shape(type="line", x0=0.15, x1=0.85, y0=0, y1=0, line=dict(width=3, color="rgba(60,60,60,0.9)"))
    fig.update_xaxes(range=[0, 1], visible=False)
    fig.update_yaxes(range=[-0.2, hoehe + 0.4], visible=False)
    fig.update_layout(showlegend=False)
    return _base(fig, 300)


def build_anteil_ueber_n(n_gewaehlt: int, n_max: int = C.ANZAHL_N_MAX):
    """Anteil der Folgen, die ein Stapel sortiert, über n (logarithmische Achse): Ausgabe zwischendurch erlaubt gegen erst alles einlagern."""
    ns = list(range(1, n_max + 1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[float(K.anteil(n)) for n in ns], mode="lines+markers", name="sofort (Ausgabe zwischendurch)",
                             line=dict(color=C.COLOR_LINE, width=3), hovertemplate="n = %{x}: Anteil %{y:.3e}<extra></extra>"))
    fig.add_trace(go.Scatter(x=ns, y=[1 / factorial(n) for n in ns], mode="lines", name="verzögert (erst alles hinein)",
                             line=dict(color=C.COLOR_LINE2, width=2, dash="dot"), hovertemplate="n = %{x}: Anteil %{y:.3e}<extra></extra>"))
    fig.add_trace(go.Scatter(x=[n_gewaehlt], y=[float(K.anteil(n_gewaehlt))], mode="markers", name="gewähltes n",
                             marker=dict(size=14, color=C.COLOR_BAD, symbol="diamond"), hoverinfo="skip"))
    fig.update_xaxes(title_text="Wagen n")
    fig.update_yaxes(title_text="Anteil sortierbarer Folgen (logarithmisch)", type="log")
    return _base(fig)


def build_richtungen(vergleiche):
    """Gestapelte Säulen je n: in beiden Mengen, nur sortierbar, nur erzeugbar (Zähleinheit Folgen)."""
    ns = [v.n for v in vergleiche]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ns, y=[len(v.beide) for v in vergleiche], name="in beiden (2^(n−1))", marker_color=C.COLOR_OK))
    fig.add_trace(go.Bar(x=ns, y=[len(v.nur_sortierbar) for v in vergleiche], name="nur sortierbar", marker_color=C.COLOR_LINE))
    fig.add_trace(go.Bar(x=ns, y=[len(v.nur_erzeugbar) for v in vergleiche], name="nur erzeugbar", marker_color=C.COLOR_LINE2))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(title_text="Wagen n", type="category")
    fig.update_yaxes(title_text="Folgen")
    return _base(fig)


def build_gruppen(a):
    """Anteil sortierbarer Wörter: mit den gewählten Gruppen gegen lauter verschiedene Wagen (gleiches n)."""
    fig = go.Figure(go.Bar(x=["Wagen mit Zielgruppen", "lauter verschiedene Wagen"], y=[float(a.anteil) * 100, float(a.verschiedene) * 100],
                           marker_color=[C.COLOR_OK, C.COLOR_NEUTRAL], hovertemplate="%{x}: %{y:.3f} %<extra></extra>"))
    fig.update_yaxes(title_text="sortierbar (%)", range=[0, 105])
    return _base(fig, 280)


def build_modell(zeilen, exakt: float, n: int, d_gewaehlt: float, zeit: bool):
    """Anteil der Zufallsfolgen, die ein Stapel sortiert, über D (Modell V) mit Wilson-Band; Waagerechte: gleich wahrscheinliche Folgen (exakt)."""
    xs = [z["d"] for z in zeilen]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs + xs[::-1], y=[z["hi"] * 100 for z in zeilen] + [z["lo"] * 100 for z in zeilen][::-1], fill="toself", fillcolor=C.COLOR_BAND,
                             line=dict(width=0), hoverinfo="skip", name="Wilson-Band 95 %"))
    fig.add_trace(go.Scatter(x=xs, y=[z["anteil"] * 100 for z in zeilen], mode="lines+markers", line=dict(color=C.COLOR_LINE, width=3),
                             name="nur Rangfolge der Abfahrten", hovertemplate="D = %{x}: %{y:.1f} %<extra></extra>"))
    if zeit:
        fig.add_trace(go.Scatter(x=xs, y=[z["anteil_z"] * 100 for z in zeilen], mode="lines+markers", line=dict(color=C.COLOR_LINE2, width=3, dash="dot"),
                                 name="Abholzeitpunkt fest", hovertemplate="D = %{x}: %{y:.1f} %<extra></extra>"))
    fig.add_trace(go.Scatter(x=[xs[0], xs[-1]], y=[exakt * 100] * 2, mode="lines", line=dict(color="rgba(120,120,120,0.9)", width=2, dash="dash"),
                             name=f"alle Folgen gleich wahrscheinlich (n = {n}, exakt)", hovertemplate="exakt %{y:.3f} %<extra></extra>"))
    gewaehlt = next(z for z in zeilen if z["d"] == d_gewaehlt)
    fig.add_trace(go.Scatter(x=[d_gewaehlt], y=[gewaehlt["anteil"] * 100], mode="markers", marker=dict(size=14, color=C.COLOR_BAD, symbol="diamond"),
                             name="gewähltes D", hoverinfo="skip"))
    fig.update_xaxes(title_text="mittlere Verweilzeit D (in Ankunftsabständen, logarithmisch)", type="log", tickvals=xs, ticktext=[str(x).rstrip("0").rstrip(".").replace(".", ",") for x in xs])
    fig.update_yaxes(title_text="sortierbare Zufallsfolgen (%)", range=[0, 102])
    return _base(fig, 380)
