

"""

CDI-MEMORY 01

Systeme de memoire individuelle et collective.

Chaque agent possede sa propre memoire.

Une memoire collective partage les experiences.

Les donnees sont conservees en JSON.

Aucune execution de transaction.

"""

import json

from pathlib import Path

from datetime import datetime, timezone

from collections import Counter

MEMORY_DIR = Path("data/cdi_memory")

AGENTS = [

    "technique",

    "economique",

    "risque",

    "decisionnaire",

]

def create_memory_directory():

    MEMORY_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )

def memory_path(agent):

    if agent not in AGENTS:

        raise ValueError("Agent inconnu")

    return MEMORY_DIR / f"{agent}.json"

def collective_path():

    return MEMORY_DIR / "collective.json"

def load_memory(path):

    if not path.exists():

        return []

    try:

        with path.open("r", encoding="utf-8") as file:

            data = json.load(file)

        if isinstance(data, list):

            return data

        return []

    except (json.JSONDecodeError, OSError):

        print("Attention : memoire illisible :", path)

        return []

def save_memory(path, records):

    create_memory_directory()

    temporary_path = path.with_suffix(".tmp")

    with temporary_path.open(

        "w",

        encoding="utf-8",

    ) as file:

        json.dump(

            records,

            file,

            indent=4,

            ensure_ascii=False,

        )

    temporary_path.replace(path)

def record_experience(

    agent,

    environment,

    proposal,

    confidence,

    outcome,

    lesson,

    evidence,

):

    """

    Enregistre une experience dans la memoire

    individuelle et dans la memoire collective.

    """

    if agent not in AGENTS:

        raise ValueError("Agent inconnu")

    if not 0 <= confidence <= 1:

        raise ValueError("Confiance entre 0 et 1 requise")

    if outcome not in (

        "positif",

        "negatif",

        "neutre",

        "non_evalue",

    ):

        raise ValueError("Resultat inconnu")

    experience = {

        "date": datetime.now(

            timezone.utc

        ).isoformat(),

        "agent": agent,

        "environment": environment,

        "proposal": proposal,

        "confidence": confidence,

        "outcome": outcome,

        "lesson": lesson,

        "evidence": evidence,

    }

    # Memoire individuelle.

    individual = load_memory(memory_path(agent))

    individual.append(experience)

    save_memory(

        memory_path(agent),

        individual,

    )

    # Memoire collective.

    collective = load_memory(collective_path())

    collective.append(experience)

    save_memory(

        collective_path(),

        collective,

    )

    return experience

def recall_experiences(

    agent=None,

    environment=None,

    limit=10,

):

    """

    Recherche les experiences similaires.

    Sans agent : consultation collective.

    """

    if agent is None:

        records = load_memory(collective_path())

    else:

        records = load_memory(memory_path(agent))

    matches = []

    for record in reversed(records):

        if environment is not None:

            if record["environment"] != environment:

                continue

        matches.append(record)

        if len(matches) >= limit:

            break

    return matches

def calculate_performance(agent=None):

    """

    Analyse les resultats memorises.

    Ne constitue pas une preuve de rentabilite.

    """

    if agent is None:

        records = load_memory(collective_path())

    else:

        records = load_memory(memory_path(agent))

    evaluated = [

        item for item in records

        if item["outcome"] in ("positif", "negatif")

    ]

    total = len(evaluated)

    if total == 0:

        return {

            "experiences": len(records),

            "evaluated": 0,

            "success_rate": None,

        }

    positive = sum(

        item["outcome"] == "positif"

        for item in evaluated

    )

    return {

        "experiences": len(records),

        "evaluated": total,

        "positive": positive,

        "negative": total - positive,

        "success_rate": round(

            positive / total * 100,

            2,

        ),

    }

def compare_agents():

    """

    Compare les experiences evaluees

    de chaque agent.

    """

    results = {}

    for agent in AGENTS:

        results[agent] = calculate_performance(agent)

    return results

def main():

    create_memory_directory()

    print("=== CDI-MEMORY 01 ===")

    print("Memoire individuelle et collective")

    print("Dossier :", MEMORY_DIR)

    for agent in AGENTS:

        path = memory_path(agent)

        records = load_memory(path)

        print(

            agent,

            ":",

            len(records),

            "experiences memorisees",

        )

    collective = load_memory(collective_path())

    print(

        "Memoire collective :",

        len(collective),

        "experiences",

    )

    print("\nPerformances memorisees :")

    for agent, results in compare_agents().items():

        print(agent, ":", results)

if __name__ == "__main__":

    main()