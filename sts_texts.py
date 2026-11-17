"""Feste Texte der App (Einleitung, Erklärung, Grenzen, Formeln). Zahlen stehen hier nur, wenn sie in tests/test_claims.py nachgerechnet werden."""

EINLEITUNG = """
Wagen (oder Container) kommen nacheinander an, jeder mit einem **Abholrang** von 1 bis n (1 wird zuerst abgeholt). Ein **Stapel** nimmt sie auf, zuletzt hinein,
zuerst hinaus, und darf zwischendurch ausgeben; das Ziel ist die Ausgabe 1, 2, …, n. Die Demo zählt, **welche Ankunftsfolgen** er damit sortiert
(genau die, die das Muster **231** vermeiden), wie klein dieser Anteil schon bei zehn Wagen ist und warum **Sortieren und Erzeugen** gleich viele, aber verschiedene Folgen ergeben.

**Die Ankunftsfolgen sind ausgedacht** (gleichverteilte Folgen und ein Ankunftsmodell mit Verweilzeit): ein **Modell, keine reale Ankunftsfolge** und kein Fall aus dem Betrieb.

Unten stehen fünf Experimente, die **Grenzen der Annahmen** und der Expander **📐 Mathematische Formulierung**.
"""

SO_FUNKTIONIERT = """
1. **Jeder ankommende Wagen kommt auf den Stapel.** Es gibt nur einen Stapel, zuletzt hinein, zuerst hinaus.
2. **Liegt oben der Wagen, der als Nächster abgeholt wird** (der kleinste Rang, der noch nicht ausgegeben ist), **geht er sofort hinaus.** Sonst bleibt er liegen und der nächste Wagen kommt.
3. **Der Stapel muss fallend bleiben:** unten der größere Rang, oben der kleinere. Ein Wagen darf nur auf einen größeren gelegt werden, denn ein kleinerer Wagen darunter
   müsste vor ihm hinaus und käme nicht mehr heran. Gelingt das nicht, gibt es drei Plätze i < j < k mit p_k < p_i < p_j: das ist das Muster **231**.
4. **Es gibt nie eine Wahl:** ein Wagen geht hinaus, sobald er gebraucht wird, und kommt sonst hinein. Darum hat jede sortierbare Folge genau einen Weg aus „hinein“ und „hinaus“
   (Experiment 1 zählt die Wege durch vollständige Wegsuche nach).
"""

KONVENTIONEN = r"""
| Symbol | Bedeutung |
|---|---|
| $n$ | Zahl der Wagen |
| $p = (p_1, \dots, p_n)$ | Ankunftsfolge: eine Anordnung der Zahlen $1, \dots, n$; $p_i$ ist der Abholrang des $i$-ten Wagens (1 wird zuerst abgeholt) |
| sortierbar | es gibt einen Weg aus „hinein“ und „hinaus“, der die Ausgabe $1, 2, \dots, n$ liefert (Ausgabe zwischendurch erlaubt, „sofort“) |
| erzeugbar | $q$ ist eine mögliche Ausgabe, wenn die Eingabe $1, 2, \dots, n$ durch den Stapel läuft |
| Muster 231 | Plätze $i < j < k$ mit $p_k < p_i < p_j$ |
| Muster 312 | Plätze $i < j < k$ mit $p_j < p_k < p_i$ |
| verzögert | erst alle $n$ Wagen hinein, danach nur noch hinaus |
| $C_n$ | Catalan-Zahl $\frac{1}{n+1}\binom{2n}{n}$ |
| Anteil | sortierbare Folgen geteilt durch alle $n!$ Folgen |
| $D$ | mittlere Verweilzeit im Modell V, in Ankunftsabständen |
"""

FORMELN = r"""
**Gegeben** sind $n$ und eine Ankunftsfolge $p$; **gesucht** ist, ob der Stapel $p$ zu $1, 2, \dots, n$ sortiert, wie viele Folgen er sortiert und wie das mit dem Erzeugen zusammenhängt.
Dieser Block gibt das Modell der Experimente vollständig an; Beweise stehen nicht hier; die Aussagen sind im Test an der Aufzählung aller Folgen bis $n = 9$ geprüft (bei Zielgruppen für alle Gruppenvektoren mit $n \le 7$).

**Sortieren.** Ein Stapel mit Ausgabe zwischendurch sortiert $p$ genau dann, wenn $p$ das Muster 231 vermeidet. Die Zahl dieser Folgen ist
$$C_n = \frac{1}{n+1}\binom{2n}{n}, \qquad \text{Anteil}(n) = \frac{C_n}{n!}, \qquad \frac{\text{Anteil}(n+1)}{\text{Anteil}(n)} = \frac{2(2n+1)}{(n+1)(n+2)}.$$

**Verzögert** (erst alles hinein, dann hinaus) sortiert der Stapel nur die Umkehrfolge $(n, n-1, \dots, 1)$: genau eine Folge.

**Erzeugen.** Die Ausgaben bei Eingabe $1, \dots, n$ sind genau die Folgen, die das Muster 312 vermeiden; ihre Zahl ist ebenfalls $C_n$. Mit $p^{-1}$ als Inverser von $p$ gilt:
$$p \text{ sortierbar} \iff p^{-1} \text{ erzeugbar}.$$
In beiden Mengen liegen genau $2^{\,n-1}$ Folgen.

**Wagen mit gleichem Ziel.** Gruppen $g_1, \dots, g_k$ mit $n = \sum g_v$ Wagen; gezählt werden verschiedene Wörter, ihre Zahl ist $n!/(g_1! \cdots g_k!)$. Sortierbar heißt: Ausgabe nichtfallend.
Das ist genau das Vermeiden des Musters 231 mit strengen Ungleichungen. Die Zustandsrechnung zählt diese Wörter, ohne sie aufzuzählen.

**Modell V (ausgedacht).** Wagen $i = 0, \dots, n-1$ kommt zur Zeit $i$ an und bleibt $Y_i$, mit $Y_i$ unabhängig exponentialverteilt mit Mittel $D$. Abfahrtszeit $a_i = i + Y_i$.
Der Abholrang von Wagen $i$ ist seine Position in der Reihenfolge der Abfahrten: $p_i = \#\{ j : a_j \le a_i \}$. Das Modell benutzt nur diese Rangfolge, der Stapel gibt frei aus.
Beim **festen Abholzeitpunkt** verlässt jeder Wagen den Stapel genau zur Zeit $a_i$ und muss dann oben liegen; das gelingt genau dann, wenn es kein Paar $i < j$ mit $j < a_i < a_j$ gibt.
Für $D \to \infty$ geht Modell V in gleichverteilte Folgen über, aber langsam: bei $n = 10$ und $D = 64$ liegt der Anteil in der Zufallsprobe noch über dem exakten Wert.

**Quellen** (nur so zitiert, wie sie gelesen sind). Stapelsortierbare Folgen und ihre Zahl: Bóna, „A survey of stack-sorting disciplines“, Electronic Journal of Combinatorics 9(2) (2003), #A1,
Satz 1.3 (Seite 3) und Lemma 1.2 (Wortlaut gelesen); dort wird das Ergebnis Knuth, *The Art of Computer Programming* Bd. 1, Abschnitt 2.2.1 zugeschrieben (Knuth nicht gelesen).
Erzeugen und Muster 312: Albert und Bousquet-Mélou, Einleitung zu „Permutations sortable by two stacks in parallel and quarter plane walks“ (2015; nur Einleitung gelesen).
Mehrere parallele Stapel, erst alles hinein, dann hinaus: Tarjan, Stanford CS-TR-71-213 (1971), Lemma 3 (Vorfassung gelesen; die Fassung im Journal of the ACM 1972 nicht).
Lehrbuchwissen sind die Aussagen zu Folgen ohne Gleichstände (231, Catalan, Erzeugen); die Zahlen zu Modell V und zu Wagen mit gleichem Ziel sind eigene Messungen in diesem Modell. Nichts davon ist inhaltlich neu; neu ist nur die Vorführbarkeit mit Zähleinheit.
"""

GRENZEN = """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Der Stapel darf zwischendurch ausgeben** | Muss erst alles eingelagert werden, sortiert er nur die Umkehrfolge (Experiment 2: 1 Folge statt C(n)). | [`patience-stapel-demo`](https://github.com/sebastian-hanisch/patience-stapel-demo) (mehrere Stapel, erst alles einlagern) |
| **Es gibt nur diese eine Maschine** | Zwei Stapel (in Serie, parallel), Pop-Stack und andere Maschinen sortieren andere Mengen von Folgen; hier steht nur der eine Stapel. | [`maschinen-vergleich-demo`](https://github.com/sebastian-hanisch/maschinen-vergleich-demo), [`mehrere-durchlaeufe-demo`](https://github.com/sebastian-hanisch/mehrere-durchlaeufe-demo), [`zwei-stapel-serie-demo`](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo) |
| **Alle Wagen haben verschiedene Ränge** | Mit gleichem Ziel mehrerer Wagen ist die Zahl nicht Catalan und hängt an den Gruppengrößen (Experiment 4). | in dieser Demo |
| **Die Ankunftsfolge ist gleichverteilt oder aus Modell V** | Beides ist ausgedacht: eine reale Ankunftsfolge gibt es in den gelesenen Quellen nicht; die Zahlen gelten nur in diesem Modell. | – |
| **Modell V benutzt nur die Rangfolge der Abfahrten** | Bindet man den Abholzeitpunkt (Schalter in Experiment 5), sinkt der Anteil stark. | in dieser Demo |
| **Die Stapelhöhe ist nicht begrenzt** | Bei begrenzter Höhe und Umstauen im Lager gilt die Aussage nicht ohne Weiteres. | [`sortierbar-umstauen-demo`](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo) |
"""
