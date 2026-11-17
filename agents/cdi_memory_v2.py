

"""

CDI-MEMORY 02

Memoire individuelle et collective des agents.

Enregistrement optimise par lots.

Stockage local en JSON.

Aucune execution de transaction.

"""

import json

from pathlib import Path

from datetime import datetime, timezone

MEMORY_DIR = Path(__file__).resolve().parents[1] / "data" / "cdi_memory"

AGENTS = [

    "technique",

    "economique",

    "risque",

    "decisionnaire",

]

VALID_OUTCOMES = (

    "positif",

    "negatif",

    "neutre",

    "non_evalue",

)

def create_memory_directory():

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

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

        return data if isinstance(data, list) else []

    except (json.JSONDecodeError, OSError):

        print("Attention : memoire illisible :", path)

        return []

def save_memory(path, records):

    create_memory_directory()

    temporary_path = path.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:

        json.dump(

            records,

            file,

            indent=4,

            ensure_ascii=False,

        )

    temporary_path.replace(path)

def validate_experience(item):

    agent = item.get("agent")

    confidence = item.get("confidence")

    outcome = item.get("outcome")

    if agent not in AGENTS:

        raise ValueError("Agent inconnu")

    if not isinstance(confidence, (int, float)):

        raise ValueError("Confiance numerique requise")

    if not 0 <= confidence <= 1:

        raise ValueError("Confiance entre 0 et 1 requise")

    if outcome not in VALID_OUTCOMES:

        raise ValueError("Resultat inconnu")

def record_experiences_batch(experiences):

    """

    Enregistre plusieurs experiences en une seule operation.

    Chaque memoire individuelle et collective est sauvegardee

    une seule fois par lot.

    """

    experiences = list(experiences)

    if not experiences:

        return 0

    # Valider toutes les experiences avant toute ecriture.

    for item in experiences:

        validate_experience(item)

    create_memory_directory()

    individual_memories = {

        agent: load_memory(memory_path(agent))

        for agent in AGENTS

    }

    collective = load_memory(collective_path())

    for item in experiences:

        experience = {

            **item,

            "date": datetime.now(timezone.utc).isoformat(),

        }

        agent = experience["agent"]

        individual_memories[agent].append(experience)

        collective.append(experience)

    # Une sauvegarde par fichier, au lieu d'une sauvegarde

    # a chaque experience.

    for agent in AGENTS:

        save_memory(

            memory_path(agent),

            individual_memories[agent],

        )

    save_memory(collective_path(), collective)

    return len(experiences)

def record_experience(

    agent,

    environment,

    proposal,

    confidence,

    outcome,

    lesson,

    evidence,

):

    """Enregistre une experience individuelle et collective."""

    item = {

        "agent": agent,

        "environment": environment,

        "proposal": proposal,

        "confidence": confidence,

        "outcome": outcome,

        "lesson": lesson,

        "evidence": evidence,

    }

    record_experiences_batch([item])

    return item

def recall_experiences(

    agent=None,

    environment=None,

    limit=10,

):

    """Recherche les experiences recentes."""

    if agent is None:

        records = load_memory(collective_path())

    else:

        records = load_memory(memory_path(agent))

    matches = []

    for record in reversed(records):

        if environment is not None:

            if record.get("environment") != environment:

                continue

        matches.append(record)

        if len(matches) >= limit:

            break

    return matches

def calculate_performance(agent=None):

    """Analyse les resultats memorises."""

    if agent is None:

        records = load_memory(collective_path())

    else:

        records = load_memory(memory_path(agent))

    evaluated = [

        item for item in records

        if item.get("outcome") in ("positif", "negatif")

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

        "success_rate": round(positive / total * 100, 2),

    }

def compare_agents():

    """Compare les resultats memorises des quatre agents."""

    return {

        agent: calculate_performance(agent)

        for agent in AGENTS

    }

def main():

    create_memory_directory()

    print("=== CDI-MEMORY 02 ===")

    print("Memoire individuelle et collective")

    print("Dossier :", MEMORY_DIR)

    for agent in AGENTS:

        records = load_memory(memory_path(agent))

        print(agent, ":", len(records), "experiences")

    collective = load_memory(collective_path())

    print("Memoire collective :", len(collective), "experiences")

    print("\nPerformances memorisees :")

    for agent, results in compare_agents().items():

        print(agent, ":", results)

if __name__ == "__main__":

    main()