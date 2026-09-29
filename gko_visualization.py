"""Plotly-Visualisierungen: Gruppentabelle, K.-o.-Baum (Konstruktion identisch zu bracket-seeding-demo,
hier ohne Cross-Repo-Import portiert), Kollusions- und Rang-Sweep-Diagramme. Alle Figuren per lock_axes
gesperrt (Touch-Scrolling-Konvention des Portfolios)."""

from __future__ import annotations

import plotly.graph_objects as go

from gko_bracket import KnockoutResult
from gko_evaluation import RankPreservationStats
from gko_group import GroupResult, standings_after

BLUE = "#1f77b4"
ORANGE = "#d68a2e"
GOLD = "#e8b923"
GRAY = "#8a8f98"
NAVY = "#14233B"
GREEN = "#2ca02c"
RED = "#c0392b"


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_group_table_chart(group: GroupResult, upto_round: int, team_labels: dict) -> go.Figure:
    points = standings_after(group, upto_round)
    order = sorted(group.team_ids, key=lambda t: (-points[t], t))
    labels = [team_labels.get(t, str(t)) for t in order]
    values = [points[t] for t in order]
    colors = [GREEN if i < 2 else GRAY for i in range(len(order))]

    fig = go.Figure(
        data=go.Bar(x=labels, y=values, marker_color=colors, text=values, textposition="outside")
    )
    fig.update_xaxes(title="Team", fixedrange=True)
    fig.update_yaxes(title="Punkte", fixedrange=True, rangemode="tozero", dtick=1)
    fig.update_layout(template="plotly_white", height=320, margin=dict(l=10, r=10, t=20, b=10))
    return lock_axes(fig)


def build_bracket_tree(knockout: KnockoutResult, seed_to_team: dict, team_labels: dict) -> go.Figure:
    rounds = knockout.rounds
    positions: list[list[float]] = [list(range(len(rounds[0])))]
    for r in range(1, len(rounds)):
        prev = positions[r - 1]
        positions.append([(prev[2 * i] + prev[2 * i + 1]) / 2 for i in range(len(rounds[r]))])

    fig = go.Figure()

    for r in range(len(rounds) - 1):
        for i, winner in enumerate(rounds[r + 1]):
            y_next = positions[r + 1][i]
            children = [j for j in (2 * i, 2 * i + 1) if j < len(rounds[r])]
            real_child_seeds = [rounds[r][j] for j in children if rounds[r][j] is not None]
            is_real_match = len(real_child_seeds) == 2
            is_upset = False
            if is_real_match and winner is not None:
                loser = real_child_seeds[0] if real_child_seeds[1] == winner else real_child_seeds[1]
                is_upset = winner > loser
            for j in children:
                if rounds[r][j] is None:
                    continue
                line_color = ORANGE if is_upset else GRAY
                fig.add_trace(
                    go.Scatter(
                        x=[r, r + 1], y=[positions[r][j], y_next], mode="lines",
                        line=dict(color=line_color, width=2), hoverinfo="skip", showlegend=False,
                    )
                )

    for r in range(len(rounds)):
        for i, s in enumerate(rounds[r]):
            if s is None:
                continue
            is_champion = r == len(rounds) - 1
            is_top2 = s in (1, 2)
            color = GOLD if is_champion else (ORANGE if is_top2 else BLUE)
            label = team_labels.get(seed_to_team.get(s), str(s))
            fig.add_trace(
                go.Scatter(
                    x=[r], y=[positions[r][i]], mode="markers+text", text=[str(s)],
                    textposition="middle center", textfont=dict(color="white", size=11),
                    marker=dict(size=26, color=color, line=dict(width=2, color="white")),
                    hovertext=f"Setzplatz {s} ({label})" + (" - Sieger" if is_champion else ""),
                    hoverinfo="text", showlegend=False,
                )
            )

    n_rounds = len(rounds) - 1
    round_labels = [f"R{r + 1}" for r in range(n_rounds)] + ["Sieger"]
    fig.update_xaxes(tickmode="array", tickvals=list(range(len(rounds))), ticktext=round_labels)
    fig.update_yaxes(visible=False, autorange="reversed")
    fig.update_layout(
        template="plotly_white", height=max(360, 24 * len(rounds[0])), margin=dict(l=10, r=10, t=10, b=30),
    )
    return lock_axes(fig)


def build_collusion_rate_chart(theoretical_rate: float, simulated_genuine: float, simulated_always: float) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=["Theoretisch\n(alle Kombinationen gleich wahrscheinlich)", "Simuliert\n(Elo-gewichtet, echter Lauf)"],
            y=[theoretical_rate, simulated_genuine + simulated_always],
            marker_color=[GRAY, RED],
            text=[f"{theoretical_rate:.1%}", f"{simulated_genuine + simulated_always:.1%}"],
            textposition="outside",
        )
    )
    fig.update_yaxes(title="Anteil Gruppen mit Kollusionsmöglichkeit", fixedrange=True, rangemode="tozero", tickformat=".0%")
    fig.update_xaxes(fixedrange=True)
    fig.update_layout(template="plotly_white", height=340, margin=dict(l=10, r=10, t=20, b=10))
    return lock_axes(fig)


def build_rank_preservation_chart(stats: list[RankPreservationStats]) -> go.Figure:
    ns = [s.n_group_sizes for s in stats]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[s.p_strongest_reaches_knockout for s in stats], mode="lines+markers",
                              line=dict(color=BLUE, width=3), name="erreicht K.-o.-Runde"))
    fig.add_trace(go.Scatter(x=ns, y=[s.p_strongest_tops_group for s in stats], mode="lines+markers",
                              line=dict(color=ORANGE, width=3), name="gewinnt eigene Gruppe"))
    fig.update_xaxes(title="Anzahl Gruppen", fixedrange=True, dtick=1)
    fig.update_yaxes(title="Anteil der Turniere", fixedrange=True, range=[0, 1.05], tickformat=".0%")
    fig.update_layout(template="plotly_white", height=340, margin=dict(l=10, r=10, t=20, b=10),
                       legend=dict(orientation="h", y=-0.25))
    return lock_axes(fig)
