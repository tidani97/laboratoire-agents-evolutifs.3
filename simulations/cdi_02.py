#!/usr/bin/env python3
"""CDI-02 — Apprentissage individuel, communication et mémoire collective.

Simulation exploratoire uniquement : aucun accès marché, aucune connexion broker,
aucun ordre de trading. Les résultats décrivent ce modèle, pas le monde réel.
"""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

SEEDS = 20
MISSIONS = 30
ROUNDS = 30
LEARNING_RATE = 0.08
EXPLORATION_RATE = 0.12
COMMUNICATION_INTERVAL = 5
COMMUNICATION_DURATION = 2

ACTIONS = ("observation", "analysis", "construction")
CONDITIONS = ("isoles", "communication_temporaire", "memoire_partagee")

SKILLS = {
    "Explorateur": {"observation": 0.90, "analysis": 0.25, "construction": 0.20},
    "Analyste": {"observation": 0.25, "analysis": 0.90, "construction": 0.25},
    "Constructeur": {"observation": 0.20, "analysis": 0.25, "construction": 0.90},
}

ENVIRONMENTS = {
    "abondant": {"observation": 0.65, "analysis": 0.70, "construction": 1.00},
    "rare": {"observation": 1.00, "analysis": 0.95, "construction": 0.55},
    "disperse": {"observation": 1.00, "analysis": 0.80, "construction": 0.75},
    "instable": {"observation": 0.90, "analysis": 1.00, "construction": 0.65},
    "mixte": {"observation": 0.85, "analysis": 0.85, "construction": 0.85},
}


def environment_for(mission: int) -> str:
    """Répartit les missions entre un bloc mixte et quatre environnements."""
    if mission < MISSIONS // 2:
        return "mixte"
    names = tuple(ENVIRONMENTS)
    return names[(mission - MISSIONS // 2) % len(names)]


def create_agents() -> dict[str, dict[str, Any]]:
    """Crée un état neuf pour chaque agent et chaque mission."""
    agents: dict[str, dict[str, Any]] = {}
    for name, skills in SKILLS.items():
        agents[name] = {
            "skills": skills.copy(),
            "values": skills.copy(),
            "successes": 0,
            "failures": 0,
            "score": 0.0,
            "memory": [],
        }
    return agents


def create_shared_memory() -> dict[str, dict[str, float]]:
    """Initialise les estimations collectives et leur niveau de confiance."""
    return {
        action: {"value": 0.5, "observations": 0.0}
        for action in ACTIONS
    }


def choose_action(
    agent: dict[str, Any],
    rng: random.Random,
    shared_memory: dict[str, dict[str, float]] | None = None,
) -> str:
    """Choisit une action selon les valeurs propres et, si disponible, collectives."""
    scores = agent["values"].copy()

    if shared_memory is not None:
        for action in ACTIONS:
            confidence = min(1.0, shared_memory[action]["observations"] / 10.0)
            collective_value = shared_memory[action]["value"]
            weight = 0.30 * confidence
            scores[action] = (1.0 - weight) * scores[action] + weight * collective_value

    if rng.random() < EXPLORATION_RATE:
        return rng.choice(ACTIONS)

    return max(ACTIONS, key=lambda action: scores[action])


def expected_success_probability(
    agent: dict[str, Any],
    action: str,
    environment: dict[str, float],
) -> float:
    """Probabilité théorique du modèle utilisée pour générer l'issue."""
    skill = agent["skills"][action]
    learned_value = agent["values"][action]
    probability = 0.45 * skill + 0.35 * learned_value + 0.20 * environment[action]
    return max(0.05, min(0.95, probability))


def learn(agent: dict[str, Any], action: str, reward: float) -> None:
    """Met à jour la valeur locale après une expérience."""
    old_value = agent["values"][action]
    updated = old_value + LEARNING_RATE * (reward - old_value)
    agent["values"][action] = max(0.0, min(1.0, updated))
    agent["memory"].append({"action": action, "reward": reward})

    if reward >= 0.55:
        agent["successes"] += 1
    else:
        agent["failures"] += 1


def update_shared_memory(
    shared_memory: dict[str, dict[str, float]],
    observations: list[dict[str, float | str]],
    learning_rate: float,
) -> None:
    """Agrège les retours reçus sans remplacer brutalement la mémoire collective."""
    for observation in observations:
        action = str(observation["action"])
        reward = float(observation["reward"])
        entry = shared_memory[action]
        entry["value"] += learning_rate * (reward - entry["value"])
        entry["observations"] += 1.0


def run_mission(seed: int, condition: str, mission: int) -> dict[str, Any]:
    """Exécute une mission indépendante et retourne ses indicateurs."""
    if condition not in CONDITIONS:
        raise ValueError(f"Condition inconnue : {condition}")

    rng = random.Random(seed * 100003 + mission * 997 + CONDITIONS.index(condition) * 31)
    environment_name = environment_for(mission)
    environment = ENVIRONMENTS[environment_name]
    agents = create_agents()
    shared_memory = create_shared_memory()

    total_score = 0.0
    successful_rounds = 0
    collective_influence = 0
    negative_transfer_events = 0

    for round_number in range(ROUNDS):
        communication_active = (
            condition == "communication_temporaire"
            and round_number % COMMUNICATION_INTERVAL < COMMUNICATION_DURATION
        )

        shared_for_decisions = None
        if condition == "memoire_partagee" or communication_active:
            shared_for_decisions = shared_memory

        round_score = 0.0
        round_observations: list[dict[str, float | str]] = []

        for agent in agents.values():
            action = choose_action(agent, rng, shared_for_decisions)

            if shared_for_decisions is not None:
                collective_influence += 1
                local_best = max(ACTIONS, key=lambda item: agent["values"][item])
                if action != local_best:
                    local_probability = expected_success_probability(
                        agent, local_best, environment
                    )
                    chosen_probability = expected_success_probability(
                        agent, action, environment
                    )
                    if chosen_probability + 0.02 < local_probability:
                        negative_transfer_events += 1

            probability = expected_success_probability(agent, action, environment)
            success = rng.random() < probability
            reward = rng.uniform(0.65, 1.0) if success else rng.uniform(0.0, 0.40)

            learn(agent, action, reward)
            contribution = reward * environment[action]
            agent["score"] += contribution
            round_score += contribution
            round_observations.append({"action": action, "reward": reward})

        if condition == "memoire_partagee":
            update_shared_memory(shared_memory, round_observations, 0.15)
        elif communication_active:
            update_shared_memory(shared_memory, round_observations, 0.30)

        total_score += round_score
        if round_score >= 1.5:
            successful_rounds += 1

    return {
        "seed": seed,
        "condition": condition,
        "mission": mission + 1,
        "environment": environment_name,
        "score": round(total_score, 5),
        "successful_rounds": successful_rounds,
        "total_successes": sum(agent["successes"] for agent in agents.values()),
        "total_failures": sum(agent["failures"] for agent in agents.values()),
        "negative_transfer_events": negative_transfer_events,
        "collective_influence": collective_influence,
        "explorer_score": round(agents["Explorateur"]["score"], 5),
        "analyst_score": round(agents["Analyste"]["score"], 5),
        "builder_score": round(agents["Constructeur"]["score"], 5),
        "explorer_memory": len(agents["Explorateur"]["memory"]),
        "analyst_memory": len(agents["Analyste"]["memory"]),
        "builder_memory": len(agents["Constructeur"]["memory"]),
    }


def save_csv(filename: str, rows: list[dict[str, Any]]) -> None:
    """Écrit un CSV UTF-8, avec création automatique du dossier parent."""
    if not rows:
        raise ValueError(f"Aucune donnée à enregistrer dans {filename}")

    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_summary(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Calcule les moyennes par condition et environnement."""
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        groups[(result["condition"], result["environment"])].append(result)

    summary = []
    for (condition, environment), rows in sorted(groups.items()):
        count = len(rows)
        summary.append({
            "condition": condition,
            "environment": environment,
            "missions": count,
            "mean_score": round(sum(row["score"] for row in rows) / count, 5),
            "mean_successful_rounds": round(
                sum(row["successful_rounds"] for row in rows) / count, 3
            ),
            "mean_successes": round(
                sum(row["total_successes"] for row in rows) / count, 3
            ),
            "mean_failures": round(
                sum(row["total_failures"] for row in rows) / count, 3
            ),
            "mean_negative_transfer": round(
                sum(row["negative_transfer_events"] for row in rows) / count, 3
            ),
        })
    return summary


def main() -> None:
    """Lance les expériences et sauvegarde les résultats."""
    results = [
        run_mission(seed, condition, mission)
        for seed in range(SEEDS)
        for condition in CONDITIONS
        for mission in range(MISSIONS)
    ]

    summary = build_summary(results)
    save_csv("results/cdi_02_runs.csv", results)
    save_csv("results/cdi_02_summary.csv", summary)

    print(f"CDI-02 terminé : {len(results)} missions simulées.")
    print("Résultats détaillés : results/cdi_02_runs.csv")
    print("Synthèse : results/cdi_02_summary.csv")
    print("\nCondition | Environnement | Missions | Score moyen | Transfert négatif")
    for row in summary:
        print(
            f'{row["condition"]:24} | {row["environment"]:10} | '
            f'{row["missions"]:8} | {row["mean_score"]:11.5f} | '
            f'{row["mean_negative_transfer"]:17.3f}'
        )


if __name__ == "__main__":
    main()