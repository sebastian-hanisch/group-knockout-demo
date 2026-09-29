"""Orchestriert die ganze Kette: Gruppenphase (alle Gruppen) -> Aufsteiger -> geseedete K.-o.-Runde.

Setzlisten-Regel fuer den Uebergang (bewusste Vereinfachung, siehe README "Wo die Annahmen enden"):
alle Gruppensieger zuerst, nach Rating absteigend sortiert (Setzplaetze 1..n_groups), dann alle
Gruppenzweiten ebenso (Setzplaetze n_groups+1..2*n_groups). Echte Turniere (z. B. FIFA-WM) ziehen die
K.-o.-Paarungen komplexer (Kontinentalverband-Beschraenkungen, Lostopf-Regeln) - hier bewusst auf die
Kernidee reduziert: Gruppenplatzierung bestimmt die Setzliste.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from gko_bracket import Bracket, KnockoutResult, build_bracket, simulate_knockout
from gko_group import CollusionAnalysis, GroupResult, analyse_final_round_collusion, final_standings, simulate_group
from gko_scenario import Scenario


@dataclass(frozen=True)
class TournamentResult:
    scenario: Scenario
    groups: tuple[GroupResult, ...]
    collusion: tuple[CollusionAnalysis, ...]  # je Gruppe eine Analyse
    seed_to_team: dict  # Setzplatz (1-indiziert) -> Team-ID
    bracket: Bracket
    knockout: KnockoutResult


def run_tournament(scenario: Scenario, seed: int) -> TournamentResult:
    rng = random.Random(seed)
    groups = tuple(simulate_group(g, scenario.ratings, rng) for g in scenario.groups)
    collusion = tuple(analyse_final_round_collusion(g) for g in groups)

    winners = []
    runners_up = []
    for g in groups:
        ranked = final_standings(g)
        winners.append(ranked[0])
        runners_up.append(ranked[1])
    winners.sort(key=lambda t: -scenario.ratings[t])
    runners_up.sort(key=lambda t: -scenario.ratings[t])
    advancers = winners + runners_up

    seed_to_team = {i + 1: t for i, t in enumerate(advancers)}
    ratings_by_seed = {s: scenario.ratings[t] for s, t in seed_to_team.items()}

    bracket = build_bracket(len(advancers))
    knockout = simulate_knockout(bracket, ratings_by_seed, rng)

    return TournamentResult(
        scenario=scenario,
        groups=groups,
        collusion=collusion,
        seed_to_team=seed_to_team,
        bracket=bracket,
        knockout=knockout,
    )


def strongest_team_reached_knockout(result: TournamentResult) -> bool:
    """Ist das Team mit dem hoechsten Rating ueberhaupt aufgestiegen (Gruppensieger oder -zweiter)?"""
    strongest = max(range(len(result.scenario.ratings)), key=lambda t: result.scenario.ratings[t])
    return strongest in result.seed_to_team.values()


def strongest_team_topped_its_group(result: TournamentResult) -> bool | None:
    """None, wenn das staerkste Team gar nicht in dieser Simulation die staerkste Gesamtmannschaft war
    (nicht anwendbar) - sonst: hat es seine eigene Gruppe gewonnen (Rang 1, nicht nur Rang 2)?"""
    strongest = max(range(len(result.scenario.ratings)), key=lambda t: result.scenario.ratings[t])
    for g in result.groups:
        if strongest in g.team_ids:
            return final_standings(g)[0] == strongest
    return None
