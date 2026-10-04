# Gruppenphase + K.-o.: die Fußball-WM-Struktur

Sechstes Stück der **Turnierplanung**-Linie der "Konzepte"-Reihe von [sebastianhanisch.net](https://sebastianhanisch.net).
Interaktive Demo: `streamlit run app.py`.

**[→ Demo live ausprobieren](https://sebastianhanisch-group-knockout-demo.streamlit.app/)**

## Ergebnis in Kürze

Kombiniert Stück 1 (Rundenturnier/Zirkelmethode, hier in 4er-Gruppen) und Stück 2 (K.-o.-System mit
Setzliste) - wie bei einer Fußball-Weltmeisterschaft. Zeigt zusätzlich ein echtes Entwurfsproblem: die
**"Schande von Gijón"** (WM 1982) - Deutschland und Österreich kannten das Ergebnis des zeitversetzt
ausgetragenen Parallelspiels (Algerien-Chile), bevor sie selbst spielten, und konnten gezielt auf das für
beide passende Ergebnis hinspielen. Seither schreibt die FIFA gleichzeitigen Anstoß der letzten
Gruppenspiele vor.

- **Theoretisch** (alle 243 möglichen Ergebnis-Vorgeschichten einer 4er-Gruppe gleich wahrscheinlich
  angenommen): **10,7 %** hätten einen echten Informationsvorteil (genau das 1982er-Muster), weitere
  **7,0 %** wären kollusionsanfällig gewesen, egal ob gleichzeitig gespielt wird.
- **Simuliert** über 24.000 Elo-gewichtete Gruppen (echte Stärkeunterschiede statt Gleichverteilung): nur
  **0,55 %** echter Informationsvorteil, weitere 0,17 % wären ohnehin kollusionsanfällig gewesen - unter
  realistischen Stärkeunterschieden sind knappe, mehrdeutige Tabellenlagen deutlich seltener als bei rein
  zufälligen Ergebnissen.
- Über 4.000 simulierte Turniere je Gruppenzahl erreicht das laut Rating stärkste Team der gesamten
  Teilnehmerliste bei 4 Gruppen in **91,6 %** der Fälle die K.-o.-Runde, gewinnt aber nur in **67,6 %**
  der Fälle überhaupt seine eigene Gruppe.

## Was die Demo zeigt

1. **Wachsendes Beispiel**: Gruppentabelle füllt sich Runde für Runde, mit Kollusions-Warnung nach der
   letzten Runde; anschließend K.-o.-Baum nach Gruppenplatzierung.
2. **📐 Wie oft ist eine echte Gijón-Situation möglich?**: theoretische vs. simulierte Kollusionsrate.
3. **🔬 Experiment**: wie gut filtert eine schwache (nur 3 Spiele) Gruppenphase das stärkste Team heraus?
4. **🚧 Wo die Annahmen enden**: Punkte-only-Tabelle, feste Gruppengröße 4, vereinfachte K.-o.-Setzliste.

## Modell und Verfahren

- **Gruppenphase** (`gko_group.py`): identische Zirkelmethode-Konstruktion wie Stück 1, fest für 4
  Teams (3 Runden). Punkte 3/1/0, Remis-Wahrscheinlichkeit 25 % (grobe, literaturübliche Näherung), Rest
  nach Elo-Erwartungswert auf Sieg/Niederlage verteilt.
- **Kollusionsanalyse** (`gko_group.analyse_final_round_collusion`): sei Spiel A das zuerst ausgetragene,
  Spiel B das zweite Spiel der letzten Runde. Für jedes der drei möglichen Ergebnisse von B wird geprüft,
  ob beide B-Teams danach echt (nicht nur durch eine Gleichstand-Regel) unter den besten zwei liegen. Für
  **mindestens ein, aber nicht alle drei** Ergebnisse: echter Informationsvorteil. Für **alle drei**:
  Gleichzeitigkeit wäre wirkungslos gewesen. `theoretical_collusion_rates()` rechnet die kombinatorische
  Referenzlinie über alle 3⁴·3 = 243 möglichen Vorgeschichten exakt durch.
- **K.-o.-Runde** (`gko_bracket.py`): identische Setzlisten-Rekursion wie Stück 2, Setzplätze aus
  Gruppensiegern (nach Rating sortiert) gefolgt von Gruppenzweiten - eine bewusste Vereinfachung
  gegenüber echten Turnieren (siehe "Wo die Annahmen enden"). Kein Remis im K.-o. (Verlängerung/Elfmeter
  erzwingen einen Sieger).
- **Quellen**: Ergebnisse der WM 1982, Gruppe 2 (Wikipedia, "Disgrace of Gijón") - West Germany 1-0
  Austria (25. Juni 1982), nachdem Algerien sein Spiel gegen Chile bereits am Vortag beendet hatte.

## Was diese Demo nicht kann

Nur Punkte, keine Tordifferenz (siehe "Wo die Annahmen enden") - das kann die gemessene
Kollusions-Häufigkeit leicht überschätzen, da manche Gleichstände real eindeutig aufgebrochen würden.
Feste Gruppengröße 4; größere Gruppen haben eine andere letzte-Runde-Struktur (mehr als 2 gleichzeitige
Spiele), hier nicht behandelt.

## Verifikation

- **Strukturell** (`tests/test_group.py`, `tests/test_bracket.py`): Zirkelmethode deckt alle 6 Paarungen
  ab, Setzliste reproduziert die bekannte 16er-Tafel, Freilose treffen automatisch die Topplätze.
- **Historischer Cross-Check**: `theoretical_collusion_rates()` gegen die von Hand nachvollzogene
  243-Kombinationen-Enumeration (Regressionstest `test_theoretical_collusion_rates_sum_to_one_and_match_measured_values`).
  Presets "Echte Gijón-Situation" (Zufalls-Seed 27, Gruppe 3) und "Gleichzeitigkeit wäre wirkungslos
  gewesen" (Zufalls-Seed 506, Gruppe 2) sind als Regressionstests fixiert.
- **Sweeps** (`tests/test_claims.py`): simulierte Kollusionsrate liegt deutlich unter der theoretischen
  Referenz, Rang-Erhaltungsraten bei n=4 Gruppen gegen konkrete Messwerte.

## Dateistruktur

```
app.py                Streamlit-Oberfläche
gko_constants.py       Regler-Grenzen, Presets
gko_scenario.py         Team-Ratings, Gruppenauslosung
gko_elo.py               Elo-Erwartungswert
gko_group.py             Gruppenphase + Kollusionsanalyse
gko_bracket.py           K.-o.-Setzliste + Simulation
gko_tournament.py        Gesamtablauf (Gruppen -> Aufsteiger -> K.-o.)
gko_evaluation.py        Sweeps (Kollusionsrate, Rang-Erhaltung)
gko_presets.py           Permalink-Muster
gko_visualization.py     Plotly-Grafiken
tests/                   pytest-Suite
```

## Lokal starten

```bash
python -m venv venv
venv\Scripts\activate  # Windows; unter Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Turnierplanung: 7 Wege zum Turnierplan](https://sebastianhanisch.net/konzepte-turnierplanung.html).
