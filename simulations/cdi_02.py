

#!/usr/bin/env python3

"""

CDI-02 — Apprentissage individuel et mémoire collective.

Modèle exploratoire :

- Trois agents spécialisés.

- Apprentissage après réussite ou échec.

- Exploration de stratégies.

- Communication temporaire ou mémoire partagée.

- Comparaison reproductible sur plusieurs missions.

"""

import csv

import random

from pathlib import Path

from collections import defaultdict

SEEDS = 20

MISSIONS = 30

ROUNDS = 30

LEARNING_RATE = 0.08

EXPLORATION_RATE = 0.12

SKILLS = {

    "Explorateur": {

        "observation": 0.90,

        "analysis": 0.25,

        "construction": 0.20,

    },

    "Analyste": {

        "observation": 0.25,

        "analysis": 0.90,

        "construction": 0.25,

    },

    "Constructeur": {

        "observation": 0.20,

        "analysis": 0.25,

        "construction": 0.90,

    },

}

ACTIONS = ("observation", "analysis", "construction")

CONDITIONS = (

    "isoles",

    "communication_temporaire",

    "memoire_partagee",

)

ENVIRONMENTS = {

    "abondant": {

        "observation": 0.65,

        "analysis": 0.70,

        "construction": 1.00,

    },

    "rare": {

        "observation": 1.00,

        "analysis": 0.95,

        "construction": 0.55,

    },

    "disperse": {

        "observation": 1.00,

        "analysis": 0.80,

        "construction": 0.75,

    },

    "instable": {

        "observation": 0.90,

        "analysis": 1.00,

        "construction": 0.65,

    },

    "mixte": {

        "observation": 0.85,

        "analysis": 0.85,

        "construction": 0.85,

    },

}

def environment_for(mission):

    if mission < MISSIONS // 2:

        return "mixte"

    names = list(ENVIRONMENTS)

    return names[(mission - MISSIONS // 2) % len(names)]

def create_agents():

    agents = {}

    for name, skills in SKILLS.items():

        agents[name] = {

            "skills": skills.copy(),

            "memory": [],

            "values": skills.copy(),

            "successes": 0,

            "failures": 0,

            "score": 0.0,

        }

    return agents

def choose_action(agent, rng, shared_values=None):

    values = agent["values"].copy()
    
    shared = (

    shared_values

    if condition in (

        "communication_temporaire",

        "memoire_partagee"

    )

    else None

)
    

    if rng.random() < EXPLORATION_RATE:

        return rng.choice(ACTIONS)

    return max(values, key=values.get)

def learn(agent, action, reward):

    old_value = agent["values"][action]

    agent["values"][action] = (

        old_value

        + LEARNING_RATE * (reward - old_value)

    )

    agent["values"][action] = max(

        0.0,

        min(1.0, agent["values"][action])

    )

    agent["memory"].append({

        "action": action,

        "reward": round(reward, 4),

    })

    if reward >= 0.55:

        agent["successes"] += 1

    else:

        agent["failures"] += 1

def run_mission(seed, condition, mission):

    rng = random.Random(

        seed * 100003

        + mission * 997

        + CONDITIONS.index(condition) * 31

    )

    environment_name = environment_for(mission)

    environment = ENVIRONMENTS[environment_name]

    agents = create_agents()

    shared_values = {

        action: 0.50 for action in ACTIONS

    }

    total_score = 0.0

    successful_rounds = 0

    for round_number in range(ROUNDS):

        round_score = 0.0

        observations = []

        for name, agent in agents.items():

            shared = (

                shared_values

                if condition == "memoire_partagee"

                else None

            )

            action = choose_action(agent, rng, shared)

            skill = agent["skills"][action]

            environmental_factor = environment[action]

            # L'expérience passée améliore progressivement

            # la maîtrise de la stratégie choisie.

            learned_value = agent["values"][action]

            probability = (

                0.45 * skill

                + 0.35 * learned_value

                + 0.20 * environmental_factor

            )

            probability = max(

                0.05,

                min(0.95, probability)

            )

            success = rng.random() < probability

            reward = (

                rng.uniform(0.65, 1.0)

                if success

                else rng.uniform(0.0, 0.40)

            )

            learn(agent, action, reward)

            contribution = reward * environmental_factor

            agent["score"] += contribution

            round_score += contribution

            observations.append({

                "action": action,

                "reward": reward,

            })

        # Communication périodique.

        if (

            condition == "communication_temporaire"

            and round_number % 5 in (0, 1)

        ):

            for observation in observations:

                action = observation["action"]

                shared_values[action] = (

                    shared_values[action] * 0.7

                    + observation["reward"] * 0.3

                )

        # Mémoire collective persistante.

        elif condition == "memoire_partagee":

            for observation in observations:

                action = observation["action"]

                shared_values[action] = (

                    shared_values[action] * 0.85

                    + observation["reward"] * 0.15

                )

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

        "total_successes": sum(

            agent["successes"] for agent in agents.values()

        ),

        "total_failures": sum(

            agent["failures"] for agent in agents.values()

        ),

        "explorer_score": round(

            agents["Explorateur"]["score"], 5

        ),

        "analyst_score": round(

            agents["Analyste"]["score"], 5

        ),

        "builder_score": round(

            agents["Constructeur"]["score"], 5

        ),

        "explorer_memory": len(

            agents["Explorateur"]["memory"]

        ),

        "analyst_memory": len(

            agents["Analyste"]["memory"]

        ),

        "builder_memory": len(

            agents["Constructeur"]["memory"]

        ),

    }

def save_csv(filename, rows):

    path = Path(filename)

    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:

        return

    with path.open(

        "w",

        newline="",

        encoding="utf-8"

    ) as file:

        writer = csv.DictWriter(

            file,

            fieldnames=list(rows[0].keys())

        )

        writer.writeheader()

        writer.writerows(rows)

def main():

    results = []

    for seed in range(SEEDS):

        for condition in CONDITIONS:

            for mission in range(MISSIONS):

                results.append(

                    run_mission(seed, condition, mission)

                )

    groups = defaultdict(list)

    for result in results:

        key = (

            result["condition"],

            result["environment"]

        )

        groups[key].append(result)

    summary = []

    for (condition, environment), rows in sorted(

        groups.items()

    ):

        summary.append({

            "condition": condition,

            "environment": environment,

            "missions": len(rows),

            "mean_score": round(

                sum(r["score"] for r in rows) / len(rows),

                5

            ),

            "mean_successes": round(

                sum(r["total_successes"] for r in rows)

                / len(rows),

                3

            ),

            "mean_failures": round(

                sum(r["total_failures"] for r in rows)

                / len(rows),

                3

            ),

        })

    save_csv("results/cdi_02_runs.csv", results)

    save_csv("results/cdi_02_summary.csv", summary)

    print(f"CDI-02 terminé : {len(results)} missions.")

    print("Résultats détaillés : results/cdi_02_runs.csv")

    print("Synthèse : results/cdi_02_summary.csv")

    for row in summary:

        print(

            row["condition"],

            row["environment"],

            row["mean_score"]

        )

if __name__ == "__main__":

    main()