# Ein Stapel: welche Ankunftsfolgen er sortiert – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-stapel-sortieren-demo.streamlit.app/)** -->

Eine von mehreren Demos zu **Sortiermaschinen und Permutationen** (Kombinatorik) für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Sie ist der Ausgangspunkt der Demos zu diesem Thema:
Sie führt die einfachste Maschine ein, **einen Stapel**, dazu die Ankunftsfolge und die Vereinbarungen (Container-Stapel fallend, Eingabe vermeidet das Muster 231, erzeugbare Ausgaben vermeiden 312), die
die Nachbar-Demos übernehmen. Wagen (oder Container) kommen nacheinander an, jeder mit einem **Abholrang** 1 bis n; der Stapel darf zwischendurch ausgeben, das Ziel ist die Ausgabe 1, 2, …, n.
Nachbarn: [`maschinen-vergleich-demo`](https://github.com/sebastian-hanisch/maschinen-vergleich-demo) (dieselbe Zählung für zehn Maschinen, die Spalte „ein Stapel“ ist diese Demo),
[`mehrere-durchlaeufe-demo`](https://github.com/sebastian-hanisch/mehrere-durchlaeufe-demo) (Pop-Stack mit mehreren Durchläufen),
[`zwei-stapel-serie-demo`](https://github.com/sebastian-hanisch/zwei-stapel-serie-demo) (zwei Stapel hintereinander),
[`patience-stapel-demo`](https://github.com/sebastian-hanisch/patience-stapel-demo) (mehrere Stapel, erst alles einlagern),
[`sortierbar-umstauen-demo`](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo) (die Menge dieser Demo als Ankunftsfolge im Lager).

**Das Ankunftsmodell ist ausgedacht** und ein **Modell, keine reale Ankunftsfolge**: gelesene Quellen liefern keine echte Ankunftsfolge. Gerechnet wird mit gleichverteilten Folgen (Modell U) und mit einem Modell V, in dem
jeder Wagen eine exponentialverteilte Zeit mit Mittel D (in Ankunftsabständen) im Stapel liegt und sein Abholrang die Reihenfolge der Abfahrten ist.

## Warum dieses Problem

Wer eine Ankunftsfolge nur über einen Stapel sortieren kann, fragt sich zuerst: **Schafft er diese Folge? Wie oft reicht ein Stapel überhaupt? Sortiert er dasselbe, was er erzeugt?**
Antwort in diesem Modell, Zähleinheit Folgen: Ein Stapel mit Ausgabe zwischendurch sortiert genau die Folgen, die das Muster 231 vermeiden, Catalan(n) viele: bei n = 10 sind das 16 796 von 3 628 800 Folgen (0,463 %, 1 von 216);
bei n = 6 sind es 132 von 720 (18,3 %). Der Anteil sinkt mit jedem weiteren Wagen um den Faktor 2(2n + 1)/((n + 1)(n + 2)): 19/55 = 0,345 von n = 9 auf 10, 0,524 von n = 5 auf 6, 0,127 von n = 29 auf 30. Muss erst alles eingelagert werden,
bevor ausgegeben wird, sortiert der Stapel genau eine Folge, die Umkehrfolge (n, …, 1), bei jedem n von 1 bis 9. Die Falle ist die Richtung: **Sortieren und Erzeugen** geben gleich viele Folgen (132 bei n = 6), aber verschiedene;
nur 2^(n−1) (32 bei n = 6) liegen in beiden Mengen, 100 Folgen sortiert der Stapel, ohne sie erzeugen zu können, und umgekehrt. Im ausgedachten Modell V (nur die Rangfolge der Abfahrten zählt, der Stapel gibt frei aus) sind bei
n = 10 und 10 000 Zufallsfolgen (Zufalls-Seed 1301) 91,1 % sortierbar bei D = 1, 56,8 % bei D = 2, 21,4 % bei D = 4 und 6,1 % bei D = 8; muss der Stapel jeden Wagen genau zu seiner Abfahrtszeit abgeben, sind es bei D = 1 nur 11,7 %.
Wagen mit gleichem Ziel ändern die Zahl und machen sie ungleich Catalan (n = 8, vier Gruppen zu je 2: 13,97 % der 2520 verschiedenen Wörter, gegen 3,55 % der 40 320 Folgen bei lauter verschiedenen Wagen; anderes Maß).
Alles gilt in diesem Modell, bei diesen Parametern; die Zähleinheit steht je Aussage dabei. **Lehrbuchwissen** sind die Aussagen zu Folgen ohne Gleichstände (Muster 231, Catalan, Erzeugen); die Zahlen zu Modell V und zu Wagen mit gleichem Ziel sind eigene Messungen in diesem Modell. Nichts davon ist inhaltlich neu; neu ist nur die Vorführbarkeit mit Zähleinheit.

## Modell

* **Ankunftsfolge** p = (p₁, …, pₙ): eine Anordnung der Zahlen 1…n; pᵢ ist der Abholrang des i-ten ankommenden Wagens (1 wird zuerst abgeholt). **Maschine:** ein Stapel (zuletzt hinein, zuerst hinaus) mit Ausgabe zwischendurch.
  **Sortierbar** heißt: es gibt einen Weg aus „hinein“ und „hinaus“ mit der Ausgabe 1, 2, …, n. **Betriebsart „sofort“:** Ausgabe zwischendurch erlaubt. **„Verzögert“:** erst alle n Wagen hinein, danach nur noch hinaus.
* **Container-Stapel fallend:** unten der größere Rang, oben der kleinere; ein Wagen darf nur auf einen größeren gelegt werden. Das ist keine zusätzliche Regel, sondern folgt aus dem Ziel: Liegt x über einem kleineren y, muss y vor x hinaus
  und kommt nicht mehr heran.
* **Muster 231:** Plätze i < j < k mit pₖ < pᵢ < pⱼ. **Sortierbar genau dann, wenn die Folge 231 vermeidet.** Der Zeuge, den die App zeigt, kommt aus dem ersten Verstoß der Maschine: der Wagen x liegt auf dem kleineren y, und der gebrauchte
  Wagen kommt erst später.
* **Erzeugbar:** die Ausgaben bei Eingabe 1, 2, …, n über alle Wörter aus „hinein“ und „hinaus“. Sie vermeiden das Muster **312**. Mit der Inversen p⁻¹ gilt: p sortierbar genau dann, wenn p⁻¹ erzeugbar.
* **Ein Weg je Folge:** ein Wagen geht hinaus, sobald er gebraucht wird, und kommt sonst hinein; es gibt nie eine Wahl. Darum hat jede sortierbare Folge genau einen Weg, jede andere keinen (Beweisskizze; als Aufzählung für n ≤ 8 geprüft).
* **Wagen mit gleichem Ziel:** Gruppen g₁, …, g_k (Gruppe 1 fährt zuerst ab); gezählt werden verschiedene Wörter, ihre Zahl ist n!/(g₁! ⋯ g_k!); die Ausgabe muss nichtfallend sein. Das ist das Vermeiden des Musters 231 mit strengen Ungleichungen.
* **Modell U:** alle n! Folgen gleich wahrscheinlich. **Modell V:** Wagen i = 0…n−1 kommt zur Zeit i an, bleibt eine unabhängige exponentialverteilte Zeit mit Mittel D, Abfahrtszeit aᵢ = i + Verweilzeit; der Abholrang von Wagen i ist seine Position in der
  Reihenfolge der Abfahrten. **Das Modell benutzt nur die Rangfolge der Abfahrten; der Stapel gibt frei aus.** **Fester Abholzeitpunkt** (Schalter in Experiment 5) ist eine eigene Fassung dieses Modells, keine Quellenaussage: jeder Wagen verlässt den Stapel
  genau zur Zeit aᵢ und muss dann oben liegen; das gelingt genau dann, wenn kein Paar i < j mit j < aᵢ < aⱼ existiert.
* Der 📐-Expander der App enthält die Formeln als vollständiges Modell (ohne Beweise).

## Methodik

* **Maschine** (`sts_machine.py`): gierig, jeder Wagen kommt hinein, liegt oben der gebrauchte Wagen, geht er hinaus; die Schrittliste und der Zeuge kommen aus demselben Lauf. **Zählen** (`sts_counting.py`): Catalan und Anteile in Brüchen
  (`fractions`); bis n = 8 werden alle n! Folgen durchgespielt, bis n = 14 zählt eine **Zustandsrechnung** (Zustand = Stapelinhalt und noch nicht gelesene Wagen je Wert; die Fortsetzungen eines Zustands werden einmal gezählt), darüber gilt nur die Formel.
  Die Zustandsrechnung zählt auch Wörter mit Zielgruppen, ohne sie aufzuzählen; zur Kontrolle spielt die App bis 20 000 Wörter durch die Maschine.
* **Zufall** nur über den ganzzahligen SplitMix64 (`sts_rng.py`, geprüfte Vorlage, unverändert kopiert; `expovariate` und `shuffle` ohne Logarithmus und Zufall der C-Bibliothek): Zufallsproben sind auf jeder Plattform gleich. Zufalls-Seed in der Seitenleiste.
  Gleichverteilte Folgen: Zufalls-Seed + n; Modell V: Zufalls-Seed · 1000 + n.
* **Modell V** (`sts_models.py`): alle Verweilzeiten einer Rechnung stammen aus einer Tabelle von Exponentialzahlen mit Mittel 1; D · E ist bitgleich `expovariate(D)` desselben Stroms, so teilen sich alle D-Werte dieselben Zufallszahlen.
  Der Rang ergibt sich aus der Sortierung der Abfahrtszeiten, die Sortierbarkeit aus der Maschine; die Bänder sind Wilson-Bänder (95 %).
* **Rechenzeit** (Messung dieser README, nicht im Test; eine CPU, Windows, Python 3.14): Experiment 1 bis 4 unter 0,1 s, die Zufallsprobe in Experiment 2 bei n = 30 und 50 000 Zufallsfolgen etwa 0,7 s; Experiment 5 braucht für die Tabelle der Exponentialzahlen etwa
  38 µs je Zahl: n = 10 mit 5 000 Zufallsfolgen etwa 1,9 s, n = 10 mit 10 000 etwa 4,5 s, n = 20 mit 10 000 etwa 9 s. Die App zeigt die geschätzte Zeit an; das Ergebnis liegt danach im Zwischenspeicher, ein Wechsel von D oder des Schalters rechnet nicht neu.
  Die Streamlit Cloud ist langsamer. Nichts ist vorgerechnet oder eingefroren.

## Befunde (gemessen, keine Behauptungen)

Zähleinheit: Folgen (Permutationen) bzw. bei Zielgruppen verschiedene Wörter, bei Zufallsproben Zufallsfolgen. Die Spalte „Test“ nennt den Test in `tests/test_claims.py`, der genau diese Zahl prüft (Ganzzahlen und Brüche exakt, Zufallsproben mit einer Testtoleranz von ±0,5 Prozentpunkten um den Wert der README; das ist die Toleranz des Tests und kein Konfidenzband, die Wilson-Bänder sind je Zelle unter 2 Prozentpunkte breit, und ein anderer Zufalls-Seed weicht bis 0,59 Prozentpunkte ab, siehe die Zeilen „Anderer Zufalls-Seed“ und „Breite der Bänder“).

| Frage | Befund | Test |
|---|---|---|
| Wie viele Folgen sortiert ein Stapel (sofort)? | Catalan: 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16 796 für n = 1 bis 10; fünf unabhängige Rechenwege geben dieselbe **Menge** (n ≤ 9) | `test_c1`, `test_oracle_stapel_sortieren.py` |
| Welcher Anteil? | n = 5: 35,0 %; 6: 18,3 % (11/60); 7: 8,51 %; 8: 3,55 % (1 von 28,2); 9: 1,34 % (1 von 74,6); 10: **0,463 %** (16 796 von 3 628 800, 1 von 216); 12: 0,0434 %; 15: 7,4·10⁻⁴ %; 20: 2,7·10⁻⁷ %; 30: 1,4·10⁻¹⁵ % | `test_c1`, `test_c6` (n = 9 und 10 durchgespielt) |
| Faktor je zusätzlichem Wagen | 2(2n + 1)/((n + 1)(n + 2)), in Brüchen für n = 1 bis 29: 0,524 (n = 5 → 6), **19/55 = 0,345** (n = 9 → 10), 0,127 (n = 29 → 30); der Faktor fällt mit n | `test_c2` |
| Betriebsart verzögert | genau **eine** Folge (n, …, 1) für n = 1 bis 9, gegen C(n) bei „sofort“ | `test_c3` |
| Wege je Folge | jede sortierbare Folge hat genau einen Weg, jede andere keinen: alle Folgen n ≤ 8 | `test_c4` |
| Sortieren gegen Erzeugen | je C(n) Folgen; in beiden Mengen genau 2^(n−1): 4, 8, 16, **32**, 64, 128, 256 für n = 3 bis 9; nur sortierbar 1, 6, 26, **100**, 365, 1302, 4606 (ebenso viele nur erzeugbar); p sortierbar ⇔ p⁻¹ erzeugbar (n ≤ 9) | `test_c5` |
| Wörter mit Zielgruppen | (2, 1, 1): 9 von 12 (75,00 %); (2, 2, 2): 43 von 90; (3, 2, 1): 34 von 60; **(2, 2, 2, 2): 352 von 2520 (13,97 %)**; (3, 3, 1, 1): 242 von 1120 (21,61 %); (5, 5): 252 von 252; (4, 3, 3): 736 von 4200 (17,52 %); (3, 3, 2, 2): 1594 von 25 200 (6,33 %); (2, 2, 2, 2, 2): 3114 von 113 400 (2,75 %); (4, 3, 2, 1): 1187 von 12 600 (9,42 %); zum Vergleich lauter verschiedene Wagen bei n = 8: 3,55 %, bei n = 10: 0,463 %; die Zustandsrechnung hat 12 bis 243 Zustände in diesen Fällen (1024 bei zehn verschiedenen Wagen) | `test_c7` |
| Reihenfolge der Gruppen | in allen 1022 geordneten Gruppenvektoren mit n ≤ 10 (137 verschiedene Partitionen) ist die Zahl gleich der bei absteigend geordneten Größen, 0 Abweichungen (**Messung, kein Beweis**) | `test_c8` |
| Zufallsprobe, gleichverteilt (Zufalls-Seed 1301, 50 000 Zufallsfolgen) | n = 6: 9119 Treffer (18,24 %), n = 8: 1811 (3,62 %), n = 10: 244 (0,488 %); der exakte Wert liegt in allen drei Wilson-Bändern (Abstand −0,55, +0,91, +0,83 Standardfehler) | `test_b1` |
| Modell V, nur Rangfolge (10 000 Zufallsfolgen, Zufalls-Seed 1301) | n = 10, D = 0,5 / 1 / 2 / 4 / 8 / 16 / 32 / 64: 99,6 / **91,1** / **56,8** / **21,4** / **6,1** / 2,1 / 1,1 / 0,71 %; n = 6, D = 1 / 2 / 4 / 8: 95,0 / 77,1 / 53,5 / 36,6 %; n = 8: 93,2 / 66,7 / 34,1 / 15,7 %; n = 20: 80,2 / 25,1 / 1,5 / 0,05 % | `test_b2` |
| Modell V, fester Abholzeitpunkt (dieselben Zufallsfolgen) | n = 10, D = 0,5 / 1 / 2 / 4 / 8: 51,5 / **11,7** / 0,95 / 0,05 / 0,01 %; nie über dem Anteil „nur Rangfolge“ (alle 36 Zellen: die vier Zeilen n = 6, 8, 10, 20 mit je neun D-Werten von 0,25 bis 64); zeitgebunden sortierbar ⇒ nach Rangfolge sortierbar, 0 Verletzungen in 50 000 Zufallsfolgen | `test_b3`, `test_b4`, `test_b5` |
| Verlauf in D | der Anteil nimmt mit D in jeder der vier Zeilen (n = 6, 8, 10, 20) nicht zu (bei n = 20 ab D = 16 gleich 0, das heißt 0 von 10 000 Zufallsfolgen; die Tabelle oben nennt für n = 20 nur D = 1, 2, 4, 8, gerechnet werden neun D-Werte von 0,25 bis 64), 0 Verletzungen; gemessen an gemeinsamen Zufallszahlen für alle D, kein bewiesener Satz | `test_b4` |
| Anderer Zufalls-Seed | n = 10, Zufalls-Seed 20261117: in keiner der neun Zellen (D = 0,25 bis 64) weicht der Anteil um mehr als 0,6 Prozentpunkte ab (gemessen 0,59 bei D = 4; die Testtoleranz ist hier 0,65, sonst 0,5), bei festem Abholzeitpunkt höchstens 0,54 | `test_b6` |
| Breite der Bänder | je Zelle (10 000 Zufallsfolgen) unter 2 Prozentpunkte | `test_b7` |
| Wann ähnelt Modell V den gleichverteilten Folgen? | bei n = 10, D = 64 und diesen 10 000 Zufallsfolgen noch nicht: 0,71 % mit Band über dem exakten Wert 0,463 %; die Annäherung für D → ∞ ist langsam | `test_b8` |

Messungen dieser README, die **nicht** im Test stehen: die Rechenzeiten (Abschnitt Methodik). Der Satz „n = 20 schon bei D = 2 ein Viertel“ meint 25,1 % (Zufalls-Seed 1301, 10 000 Zufallsfolgen, `test_b2`), „bei D = 8 praktisch null“ meint 0,05 %.

**Negativbefund (bleibt stehen):** Die Zahl der Folgen zeigt die Richtung nicht. Wer nur zählt, sieht in beiden Richtungen Catalan und hält die Mengen für gleich; sie unterscheiden sich bei n = 6 in 100 von 132 Folgen. Ebenso gilt „fast sortiert“ in Modell V nur bei kleiner Verweilzeit: bei n = 20 ist der Anteil schon bei D = 2 auf 25,1 % gefallen.

## Befunde und Korrekturen gegenüber der ersten Rechnung

* **Das Modell V braucht eine Voraussetzung im Satz:** es benutzt nur die Rangfolge der Abfahrten, der Stapel gibt frei aus. Mit festem Abholzeitpunkt sinkt der Anteil bei n = 10, D = 1 von 91,1 % auf 11,7 % (siehe Tabelle). Jede Aussage der App zu Modell V nennt das.
* **„Jeder weitere Wagen senkt den Anteil auf etwa ein Drittel“ gilt nur um n = 9 und 10.** Der Faktor 2(2n + 1)/((n + 1)(n + 2)) fällt mit n: 0,524 bei n = 5 → 6, 0,345 bei n = 9 → 10, 0,127 bei n = 29 → 30. Die App nennt den Faktor je n.
* **Die Zufallszahlen sind andere:** der exakte SplitMix64 mit gemeinsamen Zufallszahlen für alle D-Werte gibt andere Zufallsfolgen als die erste Rechnung; einzelne Zellen unterscheiden sich im Rahmen ihrer Bänder (bis zu 1 Prozentpunkt). Die Zahlen oben sind die dieser Demo; das Band ist der Befund, nicht die zweite Stelle.
* **Die Obergrenze der Zufallsprobe in der App ist 50 000 Zufallsfolgen** (die erste Rechnung nahm 200 000); die Zahlen oben stammen aus 50 000.
* **Die Reihenfolge der Gruppengrößen ist bis n ≤ 10 gemessen** (1022 Vektoren, im Test), nicht bis n ≤ 11: die Messung mit n ≤ 11 braucht rund 25 s und gehört nicht in die Testsuite. Beweis fehlt.
* **Aufzählung aller Folgen** gelingt bis n = 10 in wenigen Sekunden (n = 9: 362 880 Folgen im Test); die Live-Grenze der App bleibt n = 8 (Rücksicht auf die Streamlit Cloud), darüber zählt die Zustandsrechnung bis n = 14.

## Quellen

Nur so zitiert, wie sie gelesen sind (Wortlaut gelesen, wenn nicht anders vermerkt):

* Bóna, „A survey of stack-sorting disciplines“, Electronic Journal of Combinatorics 9(2) (2003), #A1: Satz 1.3 (Seite 3) und Lemma 1.2 zum Stapel und den Folgen, die 231 vermeiden; dort Knuth zugeschrieben.
* Albert, Bousquet-Mélou, „Permutations sortable by two stacks in parallel and quarter plane walks“, European Journal of Combinatorics 43 (2015): nur Einleitung gelesen (Erzeugen, Muster 312).
* Tarjan, „The Switchyard Problem: Sorting Using Networks of Queues and Stacks“, Stanford CS-TR-71-213 (1971), Lemma 3: bei m parallelen Stapeln, erst alles hinein, dann hinaus; Vorfassung gelesen.
* OEIS A000108 (Catalan-Zahlen) und A011782 (2^(n−1)), Wortlaut abgerufen am 2026-11-17.
* **Nicht gelesen:** Knuth, *The Art of Computer Programming* Bd. 1, Abschnitt 2.2.1 (nach Quellenbericht Übung 2.2.1-5), und Tarjan, Journal of the ACM 19 (1972); beide sind hier nur über Dritte genannt.
* Lehrbuchwissen sind die Aussagen zu Folgen ohne Gleichstände (231, Catalan, Erzeugen); die Zahlen zu Modell V und zu Wagen mit gleichem Ziel sind eigene Messungen dieser Demo. Nichts ist inhaltlich neu; neu ist nur die Vorführbarkeit mit Zähleinheit.

## Abgrenzung zu Nachbar-Demos

* **Catalan-Zahlen, erzeugende Funktion, Wachstum, Ziehen unter Dyck-Wörtern:** nur Verweis auf [`symbolische-methode-demo`](https://github.com/sebastian-hanisch/symbolische-methode-demo), [`asymptotik-demo`](https://github.com/sebastian-hanisch/asymptotik-demo) und
  [`gleichverteilt-ziehen-demo`](https://github.com/sebastian-hanisch/gleichverteilt-ziehen-demo). Die Zahl 16 796 steht dort wie hier (n = 10) als Querprobe, nicht als Neuheit. Eigen in dieser Demo (nicht als inhaltlich neu behauptet): der **Anteil** C(n)/n!, die Vereinbarung (231 beim Sortieren, 312 beim Erzeugen),
  der eine Weg je Folge, die Mengen-Orakel an der Aufzählung aller n! Folgen, die Wörter mit Zielgruppen und das Modell V; neu ist nur die Vorführbarkeit mit Zähleinheit.
* **Statistiken von Permutationen** (Inversionen, Abstiege, Zyklen): [`zaehlen-nach-parameter-demo`](https://github.com/sebastian-hanisch/zaehlen-nach-parameter-demo); hier eine Eigenschaft („ein Stapel sortiert sie“), keine Statistik.
* **Der Stapel als Lagerplatz** ([`mehrhafenstau-demo`](https://github.com/sebastian-hanisch/mehrhafenstau-demo), [`stapelplanung-demo`](https://github.com/sebastian-hanisch/stapelplanung-demo)): dort kein Zwischenausgeben, hier eine Maschine.
  Patience und die längste wachsende Teilfolge gehören zu [`patience-stapel-demo`](https://github.com/sebastian-hanisch/patience-stapel-demo).
* **Radix und Gleise** in [`ablaufberg-demo`](https://github.com/sebastian-hanisch/ablaufberg-demo): kein Bezug zum Muster 231. **Umstauen im Lager** in [`sortierbar-umstauen-demo`](https://github.com/sebastian-hanisch/sortierbar-umstauen-demo): hier weder behauptet noch angedeutet.
* **Mehrere Durchläufe, Pop-Stack, zwei Stapel:** nicht hier. Die Schnittmenge „sortierbar und erzeugbar“ (2^(n−1) Folgen) wird nur genannt.

## Ehrliche Grenzen

* **Das Ankunftsmodell ist ausgedacht.** Modell V mit exponentialverteilter Verweilzeit ist gesetzt, nicht aus Daten; andere Verteilungen (feste Verweilzeit, Gruppen) sind nicht gemessen. Wagen mit gleichem Ziel im Modell V sind nicht gemessen.
* **Anteile in Modell V sind Zufallsproben** (kein exakter Wert): 10 000 Zufallsfolgen je Zelle, Wilson-Band; in der README stehen n = 6, 8, 10 und 20, in der App n = 4 bis 20. Bei festem Abholzeitpunkt gibt es keine Formel.
  **Einordnung zweier Zellen des Zufalls-Seeds 1301** (Nachmessung 2026-11-17 mit einem unabhängigen Zufallsstrom, nicht Teil der Demo): Bei n = 6 liegen die Anteile D = 1 und D = 2 (95,0 und 77,1 %) rund drei Standardfehler unter der Referenz mit 300 000 Folgen (95,65 und 78,30 %); der Strom dieses Zufalls-Seeds hat bei n = 6 ein Mittel der Verweilzeiten von 1,0121 statt 1. 40 andere Zufalls-Seeds mit je 10 000 Folgen streuen bei D = 1 um 95,68 %. Bei festem Abholzeitpunkt, n = 10, D = 1 liegen die 11,7 % gut zwei Standardfehler über der Referenz von 10,94 % (600 000 Folgen); 60 andere Zufalls-Seeds ergeben im Mittel 10,93 %. Die Abweichungen sind Ziehungen dieses einen Zufalls-Seeds, kein Rechenfehler der Demo; die Wilson-Bänder dieser Zellen schließen den Referenzwert nicht ein. Ebenfalls nachgemessen: n = 6 mit D = 4 und D = 8, n = 8 mit D = 1, 2, 4 und 8 sowie n = 10 mit D = 1, 2 und 4 (nur Rangfolge); alle liegen innerhalb von zwei Standardfehlern der Referenz. Die übrigen Zellen der Tabelle sind nicht nachgemessen.
* **Gleichstände: keine Formel** für die Zahl der sortierbaren Wörter; die Zustandsrechnung zählt, sie beweist nichts. Die Unabhängigkeit von der Reihenfolge der Gruppen ist Messung (n ≤ 10), kein Beweis, der Grund ist nicht untersucht.
  Der Anteil über Wörter ist ein anderes Maß als der Anteil über Folgen von einzeln benannten Wagen.
* **„Ein Weg je Folge“** ist für n ≤ 8 aufgezählt und sonst durch die Beweisskizze (Ausgabe nur beim gebrauchten Wagen, Einlagern sonst erzwungen) begründet; „2^(n−1) in beiden Mengen“ ist bis n = 9 aufgezählt.
* **Die Stapelhöhe ist nicht begrenzt**, Umstauen und Zeitbedarf kommen nicht vor.
* **Browser-Verhalten** (Kleben des Kopfes, Darstellung der Plotly-Diagramme) sieht der AppTest nicht; die Schrittanzeige ist per AppTest geprüft, nicht mit echtem Mausklick.
* **Plattform:** Zahlen unter Windows, Python 3.14; Ganzzahlen und Brüche sind plattformfest, Zufallsproben mit dem exakten SplitMix64 ebenfalls (Linux-Prüfung siehe Verifikation).

## Verifikation

Die Suite hat **185 Tests** (`pytest --collect-only -q tests`); der Test `test_readme_nennt_die_testzahl_der_suite` hält die Zahl aktuell.

- **Kern:** Maschine gegen Handbeispiele (die Schrittfolgen von (3, 1, 2, 5, 4) und (2, 4, 1, 3, 5) Zug um Zug), Zeuge für das Muster 231 für alle Folgen n ≤ 7, Erzeugen gegen alle Wörter, Zustandsrechnung gegen Handwerte (Wörter aus 1, 1, 2, 3: unsortierbar sind 2311, 2131, 1231) (`tests/test_machine.py`, `tests/test_counting.py`).
- **Orakel:** `tests/test_oracle_stapel_sortieren.py`: die Menge der sortierbaren Folgen auf fünf Wegen (Maschine, Mustersuche 231, Rekursion s(p) = s(L) s(R) n, inverse Ausgaben aller Wörter aus „hinein“ und „hinaus“, Catalan-Rekursion) für n = 1 bis 9 (362 880 Folgen);
  Zielgruppen: Zustandsrechnung gegen Maschine gegen strenge Mustersuche in allen 127 geordneten Gruppenvektoren mit n ≤ 7; Wilson-Band gegen `scipy.stats.binomtest`; fester Abholzeitpunkt gegen Nachspielen der Ereignisse.
- **Eigenschaften:** Streichen eines Wagens (n = 9), Inverse, neuer größter Wagen am Ende, neuer kleinster vorn, Anteil fällt mit n, Zusammenlegen benachbarter Ränge (n ≤ 6), Reihenfolge der Gruppen (n ≤ 9), Zufalls-Seed, Anteil nimmt mit D nicht zu (`tests/test_eigenschaften_stapel_sortieren.py`).
- **Literatur:** Catalan-Zahlen (A000108) und 2^(n−1) (A011782) (`tests/test_literatur_stapel_sortieren.py`).
- **Verdikte** an handgesetzten Werten (`tests/test_verdicts.py`), **Randfälle** (n = 0, 1, 2, eine und zwei Gruppen, Reglergrenzen; `tests/test_edge_cases.py`), **Claims** (jede Zahl dieser README; `tests/test_claims.py`).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an beiden Rändern), ungültige Eingaben, Schrittanzeige, Permalink (`tests/test_app.py`); **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben, jede Reglerwirkung hebt die Markierung auf (`tests/test_layout.py`).
- **Presets, Footer, Laufzeit-Importe:** `tests/test_presets.py`, `tests/test_footer.py`, `tests/test_runtime_imports.py`.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Kernfragen, fünf Experimente, Grenzen, Formeln |
| `requirements-dev.txt` | Laufzeit plus pytest und scipy (nur für das Wilson-Orakel) |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt): streamlit, numpy, pandas, plotly |
| `sts_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `sts_counting.py` | Catalan, Anteile in Brüchen, Aufzählung, Zustandsrechnung, Wörter mit Zielgruppen |
| `sts_evaluation.py` | Kennzahlen und Verdikte der fünf Experimente (reine Funktionen) |
| `sts_format.py` | Zahlen im deutschen Format |
| `sts_layout.py` | Fester Kopf (Stylesheet) |
| `sts_machine.py` | Der Stapel: Schritte, Zeuge für das Muster 231, Erzeugen, Eingabeprüfung |
| `sts_models.py` | Zufallsfolgen, Modell V, fester Abholzeitpunkt, Wilson-Band |
| `sts_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `sts_rng.py` | SplitMix64 (geprüfte Vorlage, unverändert kopiert) |
| `sts_texts.py` | Feste Texte der App (Einleitung, Erklärung, Grenzen, Formeln) |
| `sts_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Kern, Orakel, Eigenschaften, Literatur, Verdikte, Randfälle, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

* **Ein Beweis** des Satzes (Stapel sortiert genau 231-vermeidende Folgen) und des Weges je Folge: nur Lehrbuchverweis und Aufzählung bis n = 9.
* **Eine Formel** für die Wörter mit Zielgruppen und **Gleichstände im Modell V.**
* **Mehrere Maschinen, Durchläufe, parallele oder hintereinandergeschaltete Stapel** und eine **begrenzte Stapelhöhe**: das gehört zu den Nachbar-Demos (Abschnitt Abgrenzung).
* **Catalan-Zahlen über erzeugende Funktion, Wachstum, Muster-Klassen:** nur Verweis.
* **PDF-Export:** nicht vorgesehen; die Seite ist ein Rechenwerkzeug, keine Auswertung für den Versand.
* **Vorgerechnete oder eingefrorene Tabellen:** keine, alles rechnet live.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, pandas und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
