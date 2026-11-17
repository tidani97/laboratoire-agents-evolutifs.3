

#!/usr/bin/env python3

"""CDI-01 — modèle exploratoire de coopération entre agents spécialisés."""

from __future__ import annotations

import csv

import random

from collections import defaultdict

from pathlib import Path

SEEDS = 20

MISSIONS_PER_CONDITION = 30

ROUNDS_PER_MISSION = 30

AGENTS = {

    "Explorateur": {"observation": 90, "analysis": 25, "construction": 20},

    "Analyste": {"observation": 25, "analysis": 90, "construction": 25},

    "Constructeur": {"observation": 20, "analysis": 25, "construction": 90},

}

CONDITIONS = (

    "isoles",

    "communication_temporaire",

    "memoire_partagee",

)

ENVIRONMENTS = (

    "abondant",

    "rare",

    "disperse",

    "instable",

    "mixte",

)

def environment_for(mission_index: int) -> str:

    if mission_index < MISSIONS_PER_CONDITION // 2:

        return "mixte"

    return ENVIRONMENTS[

        (mission_index - MISSIONS_PER_CONDITION // 2)

        % len(ENVIRONMENTS)

    ]

def environment_parameters(name: str) -> dict[str, float]:

    return {

        "abondant": {

            "resource": 1.35,

            "uncertainty": 0.10,

            "travel": 0.80,

        },

        "rare": {

            "resource": 0.62,

            "uncertainty": 0.25,

            "travel": 1.00,

        },

        "disperse": {

            "resource": 0.95,

            "uncertainty": 0.20,

            "travel": 1.35,

        },

        "instable": {

            "resource": 0.90,

            "uncertainty": 0.55,

            "travel": 1.05,

        },

        "mixte": {

            "resource": 1.00,

            "uncertainty": 0.30,

            "travel": 1.00,

        },

    }[name]

def run_mission(seed: int, condition: str, mission_index: int) -> dict:

    rng = random.Random(

        seed * 100_003

        + mission_index * 997

        + CONDITIONS.index(condition) * 31

    )

    env_name = environment_for(mission_index)

    env = environment_parameters(env_name)

    agents = {

        name: {

            "skills": skills.copy(),

            "energy": 1.0,

            "knowledge": 0.0,

            "contribution": 0.0,

        }

        for name, skills in AGENTS.items()

    }

    shared_knowledge = 0.0

    team_score = 0.0

    successful_actions = 0

    for round_no in range(ROUNDS_PER_MISSION):

        if env_name == "instable" and rng.random() < env["uncertainty"]:

            shared_knowledge *= 0.88

            for agent in agents.values():

                agent["knowledge"] *= 0.92

        observations = {}

        for name, agent in agents.items():

            obs = agent["skills"]["observation"] / 100

            observations[name] = max(

                0.05,

                obs + agent["knowledge"] * 0.12,

            )

        round_gain = 0.0

        for name, agent in agents.items():

            skills = agent["skills"]

            role = max(skills, key=skills.get)

            base = skills[role] / 100

            insight = observations[name]

            memory_bonus = (

                shared_knowledge * 0.18

                if condition == "memoire_partagee"

                else 0.0

            )

            communication_bonus = (

                0.10

                if condition == "communication_temporaire"

                and round_no % 5 in (0, 1)

                else 0.0

            )

            if role == "observation":

                gain = (

                    0.10

                    + base * 0.22

                    + env["uncertainty"] * insight * 0.12

                )

                agent["knowledge"] += 0.025 * base

            elif role == "analysis":

                gain = 0.08 + base * 0.20 + insight * 0.10

                agent["knowledge"] += 0.035 * base

            else:

                gain = 0.12 + base * 0.25

            gain *= env["resource"] / env["travel"]

            gain *= 1.0 + memory_bonus + communication_bonus

            gain *= max(0.35, agent["energy"])

            gain *= rng.uniform(0.88, 1.12)

            agent["contribution"] += gain

            round_gain += gain

            agent["energy"] = min(

                1.0,

                agent["energy"] + 0.035 - 0.012 * env["travel"],

            )

            agent["energy"] = max(0.25, agent["energy"])

        if condition == "communication_temporaire" and round_no % 5 in (0, 1):

            transfer = sum(

                a["knowledge"] for a in agents.values()

            ) * 0.025

            for agent in agents.values():

                agent["knowledge"] += transfer

        elif condition == "memoire_partagee":

            shared_knowledge += (

                sum(a["knowledge"] for a in agents.values()) * 0.012

            )

            shared_knowledge = min(shared_knowledge, 2.5)

            for agent in agents.values():

                agent["knowledge"] = max(

                    agent["knowledge"],

                    shared_knowledge * 0.35,

                )

        team_score += round_gain

        if round_gain > 0.65:

            successful_actions += 1

    return {

        "seed": seed,

        "condition": condition,

        "mission": mission_index + 1,

        "environment": env_name,

        "score": round(team_score, 5),

        "successful_rounds": successful_actions,

        "knowledge_final": round(

            shared_knowledge

            + sum(a["knowledge"] for a in agents.values()),

            5,

        ),

        "explorer_contribution": round(

            agents["Explorateur"]["contribution"], 5

        ),

        "analyst_contribution": round(

            agents["Analyste"]["contribution"], 5

        ),

        "builder_contribution": round(

            agents["Constructeur"]["contribution"], 5

        ),

    }

def write_csv(path: Path, rows: list[dict]) -> None:

    path.parent.mkdir(parents=True, exist_ok=True)

    if rows:

        with path.open("w", newline="", encoding="utf-8") as handle:

            writer = csv.DictWriter(

                handle,

                fieldnames=list(rows[0].keys()),

            )

            writer.writeheader()

            writer.writerows(rows)

def main() -> None:

    runs = [

        run_mission(seed, condition, mission)

        for seed in range(SEEDS)

        for condition in CONDITIONS

        for mission in range(MISSIONS_PER_CONDITION)

    ]

    grouped = defaultdict(list)

    for row in runs:

        grouped[(row["condition"], row["environment"])].append(row)

    summary = []

    for (condition, environment), rows in sorted(grouped.items()):

        summary.append({

            "condition": condition,

            "environment": environment,

            "missions": len(rows),

            "mean_score": round(

                sum(r["score"] for r in rows) / len(rows), 5

            ),

            "mean_successful_rounds": round(

                sum(r["successful_rounds"] for r in rows) / len(rows),

                3,

            ),

            "mean_knowledge_final": round(

                sum(r["knowledge_final"] for r in rows) / len(rows),

                5,

            ),

        })

    write_csv(Path("results/cdi_01_runs.csv"), runs)

    write_csv(Path("results/cdi_01_summary.csv"), summary)

    print(f"CDI-01 terminé : {len(runs)} missions simulées.")

    print("Résultats : results/cdi_01_runs.csv")

    print("Synthèse : results/cdi_01_summary.csv")

    print("\nCondition | Environnement | Missions | Score moyen")

    for row in summary:

        print(

            f'{row["condition"]:24} | '

            f'{row["environment"]:10} | '

            f'{row["missions"]:8} | '

            f'{row["mean_score"]:.5f}'

        )

if __name__ == "__main__":

    main()