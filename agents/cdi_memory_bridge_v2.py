

"""

CDI MEMORY BRIDGE V2

Relie CDI-TRADER au systeme CDI-MEMORY V2.

Les experiences sont accumulees pendant

la simulation puis sauvegardees en lot.

"""

from agents.cdi_memory_v2 import record_experiences_batch

PENDING_EXPERIENCES = []

def evaluate_proposal(proposal, market_change):

    if proposal not in ("achat", "vente"):

        return "non_evalue"

    direction = 1 if proposal == "achat" else -1

    result = direction * market_change

    if result > 0:

        return "positif"

    if result < 0:

        return "negatif"

    return "neutre"

def record_round(

    environment,

    market_change,

    technical,

    economic,

    risk_proposal,

    risk_approved,

    decision,

    pnl,

):

    """Ajoute les experiences des quatre agents au lot."""

    PENDING_EXPERIENCES.extend([

        {

            "agent": "technique",

            "environment": environment,

            "proposal": technical,

            "confidence": 0.50,

            "outcome": evaluate_proposal(

                technical, market_change

            ),

            "lesson": "Evaluation de la proposition technique.",

            "evidence": "Variation du marche simulee.",

        },

        {

            "agent": "economique",

            "environment": environment,

            "proposal": economic,

            "confidence": 0.50,

            "outcome": evaluate_proposal(

                economic, market_change

            ),

            "lesson": "Evaluation du contexte economique.",

            "evidence": "Environnement de marche simule.",

        },

        {

            "agent": "risque",

            "environment": environment,

            "proposal": risk_proposal,

            "confidence": 0.95,

            "outcome": "non_evalue",

            "lesson": (

                "Transaction autorisee."

                if risk_approved

                else "Transaction refusee par precaution."

            ),

            "evidence": "Controle des limites de risque.",

        },

        {

            "agent": "decisionnaire",

            "environment": environment,

            "proposal": decision,

            "confidence": 0.50,

            "outcome": (

                "positif" if pnl > 0

                else "negatif" if pnl < 0

                else "neutre" if decision in ("achat", "vente")

                else "non_evalue"

            ),

            "lesson": "Evaluation de la decision collective.",

            "evidence": "Resultat de la simulation.",

        },

    ])

def flush_memory():

    """Sauvegarde toutes les experiences accumulees."""

    global PENDING_EXPERIENCES

    if not PENDING_EXPERIENCES:

        return 0

    total = record_experiences_batch(PENDING_EXPERIENCES)

    PENDING_EXPERIENCES = []

    return total

def reset_memory_buffer():

    """Vide le lot sans sauvegarder."""

    global PENDING_EXPERIENCES

    PENDING_EXPERIENCES = []