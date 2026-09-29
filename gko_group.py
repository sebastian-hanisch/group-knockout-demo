"""Gruppenphase: Zirkelmethode-Rundenplan fuer 4 Teams (3 Runden, je 2 Spiele - identisch zur
Konstruktion aus round-robin-demo, hier fest fuer Gruppengroesse 4), Elo-Ergebnissimulation mit
Remis-Wahrscheinlichkeit, Tabelle (Punkte 3/1/0), und die "Schande von Gijon"-Kollusionsanalyse.

Punkte-only-Tabelle (KEINE Tordifferenz) ist eine bewusste Vereinfachung - siehe README "Wo die
Annahmen enden": echte Tabellen brechen manche Gleichstaende ueber Tordifferenz eindeutig auf, dieses
Modell behandelt jeden Punktegleichstand an der Aufstiegsgrenze konservativ als unsicher.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from gko_elo import expected_score

DRAW_PROBABILITY = 0.25  # grobe, literaturuebliche Naeherung fuer Fussball - siehe README

# Zirkelmethode fuer 4 Teams (Team an Index 3 der Gruppe ist "fix"): identische Konstruktion wie
# round-robin-demo (Schrittweite (m+1)//2 mit m=3 -> 2). Rollen 0..3 sind GRUPPENINTERNE Positionen,
# nicht Team-IDs.
GROUP_ROUNDS: tuple[tuple[tuple[int, int], ...], ...] = (
    ((0, 3), (1, 2)),
    ((0, 2), (3, 1)),
    ((0, 1), (3, 2)),
)

OUTCOMES = ("home_win", "draw", "away_win")


@dataclass(frozen=True)
class MatchResult:
    home: int
    away: int
    outcome: str  # "home_win" | "draw" | "away_win"


@dataclass(frozen=True)
class GroupResult:
    team_ids: tuple[int, ...]  # Positionen 0..3 -> Team-ID
    rounds: tuple[tuple[MatchResult, ...], ...]  # 3 Runden, je 2 Ergebnisse
    points: dict  # Team-ID -> Punkte nach allen 3 Runden


def outcome_probabilities(rating_home: float, rating_away: float) -> tuple[float, float, float]:
    """(P(Heimsieg), P(Remis), P(Auswaertssieg)) - Elo-Erwartungswert abzueglich einer festen
    Remis-Wahrscheinlichkeit, Rest proportional auf Sieg/Niederlage verteilt."""
    e_home = expected_score(rating_home, rating_away)
    p_draw = DRAW_PROBABILITY
    p_home = e_home * (1 - p_draw)
    p_away = (1 - e_home) * (1 - p_draw)
    return p_home, p_draw, p_away


def simulate_match(rating_home: float, rating_away: float, rng: random.Random) -> str:
    p_home, p_draw, _p_away = outcome_probabilities(rating_home, rating_away)
    u = rng.random()
    if u < p_home:
        return "home_win"
    if u < p_home + p_draw:
        return "draw"
    return "away_win"


def points_delta(outcome: str) -> tuple[int, int]:
    if outcome == "home_win":
        return 3, 0
    if outcome == "draw":
        return 1, 1
    return 0, 3


def simulate_group(team_ids: tuple[int, ...], ratings: tuple[float, ...], rng: random.Random) -> GroupResult:
    assert len(team_ids) == 4
    points = {t: 0 for t in team_ids}
    all_rounds = []
    for round_pairs in GROUP_ROUNDS:
        round_results = []
        for (pos_a, pos_b) in round_pairs:
            a, b = team_ids[pos_a], team_ids[pos_b]
            outcome = simulate_match(ratings[a], ratings[b], rng)
            da, db = points_delta(outcome)
            points[a] += da
            points[b] += db
            round_results.append(MatchResult(home=a, away=b, outcome=outcome))
        all_rounds.append(tuple(round_results))
    return GroupResult(team_ids=team_ids, rounds=tuple(all_rounds), points=points)


def standings_after(group: GroupResult, upto_round: int) -> dict:
    """Punktestand nach den ersten `upto_round` Runden (0..3)."""
    points = {t: 0 for t in group.team_ids}
    for round_results in group.rounds[:upto_round]:
        for m in round_results:
            da, db = points_delta(m.outcome)
            points[m.home] += da
            points[m.away] += db
    return points


def safe_advancers(points: dict, top_k: int = 2) -> set:
    """Teams, die STRIKT genug Punkte haben, um unabhaengig von einer Gleichstand-Regel sicher
    aufzusteigen (siehe Modul-Docstring: konservative, tordifferenz-freie Tabelle)."""
    sorted_pts = sorted(points.values(), reverse=True)
    threshold_high = sorted_pts[top_k - 1]
    threshold_low = sorted_pts[top_k] if len(sorted_pts) > top_k else -1
    return {t for t, p in points.items() if p > threshold_low and p >= threshold_high}


def final_standings(group: GroupResult) -> list[int]:
    """Team-IDs sortiert nach Endpunktzahl (Rang 0 = Gruppensieger). Bei Punktegleichstand:
    Team-ID als Tiebreak (deterministisch, keine Tordifferenz modelliert - siehe Modul-Docstring)."""
    return sorted(group.team_ids, key=lambda t: (-group.points[t], t))


@dataclass(frozen=True)
class CollusionAnalysis:
    game_a: tuple[int, int]
    game_b: tuple[int, int]
    outcome_a: str
    good_outcomes_for_b: tuple[str, ...]  # welche B-Ergebnisse beide B-Teams retten
    genuine_information_advantage: bool  # 0 < len(good_outcomes_for_b) < 3
    always_saved: bool  # alle 3 B-Ergebnisse retten beide (Gleichzeitigkeit waere wirkungslos)


def analyse_final_round_collusion(group: GroupResult) -> CollusionAnalysis:
    """Prueft die 'Schande von Gijon'-Situation: in der letzten Runde wird Spiel A vor Spiel B
    ausgetragen (sequenziell, wie 1982) - haetten die B-Teams einen ECHTEN Informationsvorteil, wenn
    sie A's Ergebnis kennen, bevor sie spielen?"""
    points_before = standings_after(group, 2)
    game_a_pair = GROUP_ROUNDS[2][0]
    game_b_pair = GROUP_ROUNDS[2][1]
    team_a = (group.team_ids[game_a_pair[0]], group.team_ids[game_a_pair[1]])
    team_b = (group.team_ids[game_b_pair[0]], group.team_ids[game_b_pair[1]])

    actual_outcome_a = group.rounds[2][0].outcome
    points_after_a = dict(points_before)
    da, db = points_delta(actual_outcome_a)
    points_after_a[team_a[0]] += da
    points_after_a[team_a[1]] += db

    good_outcomes = []
    for outcome_b in OUTCOMES:
        final_pts = dict(points_after_a)
        da2, db2 = points_delta(outcome_b)
        final_pts[team_b[0]] += da2
        final_pts[team_b[1]] += db2
        safe = safe_advancers(final_pts, top_k=2)
        if team_b[0] in safe and team_b[1] in safe:
            good_outcomes.append(outcome_b)

    n_good = len(good_outcomes)
    return CollusionAnalysis(
        game_a=team_a,
        game_b=team_b,
        outcome_a=actual_outcome_a,
        good_outcomes_for_b=tuple(good_outcomes),
        genuine_information_advantage=0 < n_good < 3,
        always_saved=n_good == 3,
    )


def theoretical_collusion_rates() -> tuple[float, float, float]:
    """Kombinatorische Referenzlinie: Anteil (genuine, always_saved, none) ueber ALLE 3^4 * 3 = 243
    moeglichen (Runde-1, Runde-2, Ergebnis-Spiel-A)-Kombinationen fuer eine 4er-Gruppe, wenn jedes
    Ergebnis gleich wahrscheinlich waere (NICHT Elo-gewichtet - siehe collusion_stats() in
    gko_evaluation.py fuer die realistische, simulierte Rate). Reine Kombinatorik, unabhaengig von
    Team-IDs oder Ratings."""
    import itertools

    team_ids = (0, 1, 2, 3)
    genuine = always_saved = none = 0
    for o0 in itertools.product(OUTCOMES, repeat=2):
        pts = {t: 0 for t in team_ids}
        for (pos_a, pos_b), o in zip(GROUP_ROUNDS[0], o0):
            da, db = points_delta(o)
            pts[team_ids[pos_a]] += da
            pts[team_ids[pos_b]] += db
        for o1 in itertools.product(OUTCOMES, repeat=2):
            pts2 = dict(pts)
            for (pos_a, pos_b), o in zip(GROUP_ROUNDS[1], o1):
                da, db = points_delta(o)
                pts2[team_ids[pos_a]] += da
                pts2[team_ids[pos_b]] += db
            game_a_pos, game_b_pos = GROUP_ROUNDS[2]
            team_a = (team_ids[game_a_pos[0]], team_ids[game_a_pos[1]])
            team_b = (team_ids[game_b_pos[0]], team_ids[game_b_pos[1]])
            for outcome_a in OUTCOMES:
                pts_after_a = dict(pts2)
                da, db = points_delta(outcome_a)
                pts_after_a[team_a[0]] += da
                pts_after_a[team_a[1]] += db

                n_good = 0
                for outcome_b in OUTCOMES:
                    final_pts = dict(pts_after_a)
                    da2, db2 = points_delta(outcome_b)
                    final_pts[team_b[0]] += da2
                    final_pts[team_b[1]] += db2
                    safe = safe_advancers(final_pts, top_k=2)
                    if team_b[0] in safe and team_b[1] in safe:
                        n_good += 1

                if 0 < n_good < 3:
                    genuine += 1
                elif n_good == 3:
                    always_saved += 1
                else:
                    none += 1

    total = genuine + always_saved + none
    return genuine / total, always_saved / total, none / total
