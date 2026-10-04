"""Gruppenphase + K.-o.-Hybrid - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Sechstes Stück der "Turnierplanung"-Linie der "Konzepte"-Reihe: kombiniert Stück 1 (Rundenturnier/
Zirkelmethode, hier in 4er-Gruppen) und Stück 2 (K.-o.-System mit Setzliste) - wie bei einer
Fußball-Weltmeisterschaft. Zeigt zusätzlich ein echtes Entwurfsproblem: die "Schande von Gijón" (WM
1982) - wie oft verschafft das WISSEN um das zeitversetzt ausgetragene Parallelspiel zwei Teams einen
echten taktischen Vorteil?

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import gko_constants as C
from gko_evaluation import collusion_stats, rank_preservation_sweep
from gko_group import standings_after, theoretical_collusion_rates
from gko_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sync_query_params,
)
from gko_scenario import generate_scenario
from gko_tournament import run_tournament
from gko_visualization import build_bracket_tree, build_collusion_rate_chart, build_group_table_chart, build_rank_preservation_chart

st.set_page_config(page_title="Gruppenphase + K.-o. – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _tournament(n_groups, seed):
    scenario = generate_scenario(n_groups, seed)
    return run_tournament(scenario, seed)


@st.cache_data(show_spinner=False)
def _collusion_stats():
    return collusion_stats(C.COLLUSION_STATS_REPS, n_groups=4)


@st.cache_data(show_spinner=False)
def _theoretical_collusion_rate():
    genuine, _always, _none = theoretical_collusion_rates()
    return genuine


@st.cache_data(show_spinner=False)
def _rank_sweep():
    return rank_preservation_sweep(C.SWEEP_N_GROUPS_VALUES, n_reps=C.SWEEP_REPS)


st.title("🏆 Gruppenphase + K.-o.: die Fußball-WM-Struktur")
st.markdown(
    """
Bei einem großen Turnier spielt man nicht gleich K.-o. - erst eine **Gruppenphase** (Stück 1: Zirkelmethode
in kleinen Gruppen), dann ziehen die Besten in eine **geseedete K.-o.-Runde** ein (Stück 2). Diese Demo
zeigt, wie beide Formate zusammenspielen - und ein echtes Entwurfsproblem, das dabei entsteht: bei der
WM 1982 in Gijón kannten Deutschland und Österreich das Ergebnis des zeitversetzt ausgetragenen
Parallelspiels, bevor sie selbst spielten - und konnten gezielt auf das für beide passende Ergebnis
hinspielen. Seither schreibt die FIFA gleichzeitigen Anstoß der letzten Gruppenspiele vor.
"""
)
st.caption(
    "Baut auf Stück 1 (round-robin-demo) und Stück 2 (bracket-seeding-demo) auf: dieselbe Zirkelmethode "
    "für die Gruppenphase, dieselbe Setzliste für die K.-o.-Runde - neu ist hier, wie Gruppenplatzierung "
    "zur K.-o.-Setzliste wird, und die Kollusions-Analyse der letzten Gruppenrunde."
)

with st.expander("Wie entsteht ein Informationsvorteil?", expanded=True):
    st.markdown(
        """
In der letzten Gruppenrunde gibt es zwei Spiele. Wird **Spiel A zuerst** ausgetragen (wie 1982), kennen
die Teams aus **Spiel B** dessen Ergebnis, bevor sie selbst antreten. Diese Demo prüft für jede Gruppe:
gibt es ein Ergebnis von Spiel B, das BEIDE B-Teams aufsteigen lässt? Und falls ja - hätte es dafür
gereicht, irgendein gutes Ergebnis zu erzielen (Gleichzeitigkeit wäre wirkungslos gewesen), oder musste
es GENAU auf das bekannte Ergebnis von Spiel A abgestimmt sein (echter Informationsvorteil, das
1982er-Muster)?
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_groups = st.slider("Anzahl Gruppen", *bounds("n_groups_slider"), key="n_groups_slider",
                          help="4 Teams je Gruppe, wie bei einer Fußball-WM.")
    seed = st.slider("Saatwert", *bounds("seed_slider"), key="seed_slider",
                      help="Bestimmt Ratings, Gruppenauslosung und alle Spielergebnisse.")

sync_query_params(n_groups, seed, st.session_state.get("focus_group_select", 0))

n_groups = int(n_groups)
seed = int(seed)
result = _tournament(n_groups, seed)
team_labels = {t: f"T{t}" for t in range(len(result.scenario.ratings))}

st.markdown("---")
st.markdown("## 🎯 Gruppenphase")

focus_group = st.selectbox("Gruppe im Fokus", list(range(n_groups)), key="focus_group_select")
group = result.groups[focus_group]
collusion = result.collusion[focus_group]

round_key = (n_groups, seed, focus_group)
if "gko_round_slider" not in st.session_state or st.session_state.get("gko_round_owner") != round_key:
    st.session_state["gko_round_slider"] = 3
    st.session_state["gko_round_owner"] = round_key

upto_round = st.slider("Nach Runde", 1, 3, key="gko_round_slider")
st.plotly_chart(build_group_table_chart(group, upto_round, team_labels), width="stretch",
                 key=f"table_{n_groups}_{seed}_{focus_group}_{upto_round}")

standings = standings_after(group, upto_round)
st.caption(
    "Tabelle: " + " · ".join(f"{team_labels[t]} {p}" for t, p in sorted(standings.items(), key=lambda kv: -kv[1]))
    + " - grün = würde aktuell aufsteigen."
)

if upto_round == 3:
    if collusion.genuine_information_advantage:
        st.error(
            f"🚨 Echter Informationsvorteil in dieser Gruppe: Spiel A ({team_labels[collusion.game_a[0]]} "
            f"vs. {team_labels[collusion.game_a[1]]}, Ergebnis: {collusion.outcome_a}) endete zuerst - "
            f"danach rettete GENAU {len(collusion.good_outcomes_for_b)} von 3 möglichen Ergebnissen in "
            f"Spiel B ({team_labels[collusion.game_b[0]]} vs. {team_labels[collusion.game_b[1]]}) beide "
            "B-Teams. Das ist exakt das Gijón-1982-Muster - gleichzeitiger Anstoß hätte diesen gezielten "
            "Vorteil verhindert."
        )
    elif collusion.always_saved:
        st.warning(
            "⚠️ In dieser Gruppe hätte JEDES Ergebnis von Spiel B beide B-Teams gerettet - "
            "Gleichzeitigkeit hätte hier nichts gebracht, die Absprachemöglichkeit war strukturell da, "
            "unabhängig vom Zeitplan der Spiele."
        )
    else:
        st.success("✅ Keine Kollusion möglich: kein Ergebnis von Spiel B hätte beide B-Teams gerettet.")

st.markdown("---")
st.markdown("## 🎯 K.-o.-Runde")
st.caption(
    f"{len(result.seed_to_team)} Teams (Gruppensieger + -Zweite, nach Rating geseedet) - "
    f"Sieger: {team_labels[result.seed_to_team[result.knockout.champion]]}."
)
st.plotly_chart(build_bracket_tree(result.knockout, result.seed_to_team, team_labels), width="stretch",
                 key=f"bracket_{n_groups}_{seed}")

st.markdown("---")
st.subheader("📐 Wie oft ist eine echte Gijón-Situation möglich?")
stats = _collusion_stats()
theoretical = _theoretical_collusion_rate()
st.plotly_chart(build_collusion_rate_chart(theoretical, stats.genuine_rate, stats.always_saved_rate),
                 width="stretch", key="collusion_chart")
st.caption(
    f"Theoretisch (alle 243 möglichen Ergebnis-Vorgeschichten einer Gruppe gleich wahrscheinlich "
    f"angenommen): {theoretical:.1%} hätten einen echten Informationsvorteil. Simuliert über "
    f"{stats.n_groups:,} Elo-gewichtete Gruppen: nur {stats.genuine_rate:.1%} echter Vorteil "
    f"(plus {stats.always_saved_rate:.1%}, wo es ohnehin egal gewesen wäre) - unter realistischen "
    "Stärkeunterschieden sind knappe, mehrdeutige Tabellenlagen seltener als bei rein zufälligen Ergebnissen."
)

st.markdown("---")
st.subheader("🔬 Experiment: erreicht das stärkste Team immer die K.-o.-Runde?")
rank_sweep = _rank_sweep()
st.plotly_chart(build_rank_preservation_chart(rank_sweep), width="stretch", key="rank_chart")
st.caption(
    f"Über {C.SWEEP_REPS:,} simulierte Turniere je Gruppenzahl: das laut Rating stärkste Team der "
    "gesamten Teilnehmerliste erreicht in rund 90-94% der Fälle die K.-o.-Runde, gewinnt aber nur in "
    "etwa zwei Dritteln der Fälle überhaupt seine eigene Gruppe - eine schwache Gruppenphase (kleine "
    "Fallzahl, nur 3 Spiele) filtert also spürbar, aber keineswegs perfekt."
)

st.markdown("---")

with st.expander("🚧 Wo die Annahmen enden"):
    st.markdown(
        """
- **Nur Punkte, keine Tordifferenz.** Echte Tabellen brechen manche Gleichstände über Tordifferenz
  eindeutig auf; dieses Modell behandelt jeden Punktegleichstand an der Aufstiegsgrenze konservativ als
  unsicher (siehe `gko_group.py`) - das kann die gemessene Kollusions-Häufigkeit leicht überschätzen.
- **Feste Gruppengröße 4.** Größere Gruppen (z. B. 5 oder 6 Teams) haben eine andere letzte-Runde-
  Struktur (mehr als 2 Spiele gleichzeitig) - hier nicht behandelt.
- **Vereinfachte K.-o.-Setzliste.** Gruppensieger nach Rating sortiert, dann Gruppenzweite - reale
  Turniere (z. B. FIFA-WM) ziehen komplexer (Kontinentalverband-Beschränkungen, Lostöpfe).
- **Remis-Wahrscheinlichkeit fest (25 %).** Eine grobe, literaturübliche Näherung, kein aus echten Ligen
  gemessener Wert.
        """
    )

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gruppenphase**: identische Zirkelmethode-Konstruktion wie Stück 1, fest für $k{=}4$ Teams (3 Runden).
Punkte 3/1/0. **Kollusionsanalyse** (`gko_group.analyse_final_round_collusion`): sei $\text{Spiel A}$ das
zuerst ausgetragene, $\text{Spiel B}$ das zweite Spiel der letzten Runde. Für jedes der drei möglichen
Ergebnisse von B wird geprüft, ob beide B-Teams danach echt (nicht nur durch eine Gleichstand-Regel)
unter den besten zwei der Gruppe liegen. Ist das für **mindestens ein, aber nicht alle drei** Ergebnisse
der Fall, besteht ein echter Informationsvorteil - für **alle drei** wäre Gleichzeitigkeit wirkungslos
gewesen.

**K.-o.-Runde**: identische Setzlisten-Rekursion wie Stück 2 (`gko_bracket.standard_seed_order`),
Setzplätze aus Gruppensiegern (nach Rating sortiert) gefolgt von Gruppenzweiten. Matches per
Elo-Erwartungswert simuliert, kein Remis (Verlängerung/Elfmeter erzwingen einen Sieger).

Implementiert in `gko_group.py` (Gruppenphase + Kollusionsanalyse), `gko_bracket.py`
(K.-o.-Setzliste + Simulation), `gko_tournament.py` (Gesamtablauf) und `gko_evaluation.py` (Sweeps).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Turnierplanung: 7 Wege zum Turnierplan](https://sebastianhanisch.net/konzepte-turnierplanung.html)."
)
