"""Regler-Grenzen, Presets und Konstanten fuer die Gruppenphase+K.-o.-Demo."""

DEFAULT_N_GROUPS = 4
N_GROUPS_MIN, N_GROUPS_MAX = 2, 8

DEFAULT_SEED = 1
SEED_MIN, SEED_MAX = 0, 999

DEFAULT_FOCUS_GROUP = 0

SWEEP_N_GROUPS_VALUES = [2, 3, 4, 5, 6, 7, 8]
SWEEP_REPS = 4000
COLLUSION_STATS_REPS = 6000

_BASE = {"n_groups": DEFAULT_N_GROUPS, "seed": DEFAULT_SEED, "focus_group": DEFAULT_FOCUS_GROUP}
PRESETS = {
    "Normalfall, keine Kollusion möglich (4 Gruppen)": {**_BASE},
    "Echte Gijón-Situation (Informationsvorteil existiert)": {**_BASE, "seed": 27, "focus_group": 3},
    "Gleichzeitigkeit wäre wirkungslos gewesen": {**_BASE, "seed": 506, "focus_group": 2},
    "Großes Turnier (8 Gruppen, WM-Größe)": {**_BASE, "n_groups": 8, "seed": 1},
}
PRESET_HELP = {
    "Normalfall, keine Kollusion möglich (4 Gruppen)": "Der häufigste Fall: die Tabellenlage vor der letzten Runde lässt keine Kollusion zu, unabhängig vom Ergebnis des zuerst ausgetragenen Spiels.",
    "Echte Gijón-Situation (Informationsvorteil existiert)": "Gruppe 3: genau EIN Ergebnis des zweiten Spiels rettet beide Teams - wer das erste Spiel kennt, kann gezielt darauf hinspielen. Genau das Muster von 1982.",
    "Gleichzeitigkeit wäre wirkungslos gewesen": "Gruppe 2: JEDES Ergebnis des zweiten Spiels rettet ohnehin beide Teams - hier hätte Wissen über das erste Spiel gar nichts gebracht, die Verabredungsmöglichkeit war strukturell da, unabhängig vom Zeitplan.",
    "Großes Turnier (8 Gruppen, WM-Größe)": "32 Teams, 8 Gruppen, 16 K.-o.-Plätze - Turniergröße einer echten Fußball-Weltmeisterschaft.",
}
