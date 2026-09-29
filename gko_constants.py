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
    "Normalfall, keine Kollusion moeglich (4 Gruppen)": {**_BASE},
    "Echte Gijon-Situation (Informationsvorteil existiert)": {**_BASE, "seed": 27, "focus_group": 3},
    "Gleichzeitigkeit waere wirkungslos gewesen": {**_BASE, "seed": 506, "focus_group": 2},
    "Grosses Turnier (8 Gruppen, WM-Groesse)": {**_BASE, "n_groups": 8, "seed": 1},
}
PRESET_HELP = {
    "Normalfall, keine Kollusion moeglich (4 Gruppen)": "Der haeufigste Fall: die Tabellenlage vor der letzten Runde laesst keine Kollusion zu, unabhaengig vom Ergebnis des zuerst ausgetragenen Spiels.",
    "Echte Gijon-Situation (Informationsvorteil existiert)": "Gruppe 3: genau EIN Ergebnis des zweiten Spiels rettet beide Teams - wer das erste Spiel kennt, kann gezielt darauf hinspielen. Genau das Muster von 1982.",
    "Gleichzeitigkeit waere wirkungslos gewesen": "Gruppe 2: JEDES Ergebnis des zweiten Spiels rettet ohnehin beide Teams - hier haette Wissen ueber das erste Spiel gar nichts gebracht, die Verabredungsmoeglichkeit war strukturell da, unabhaengig vom Zeitplan.",
    "Grosses Turnier (8 Gruppen, WM-Groesse)": "32 Teams, 8 Gruppen, 16 K.-o.-Plaetze - Turniergroesse einer echten Fussball-Weltmeisterschaft.",
}
