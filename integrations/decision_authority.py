

"""Autorite de decision CDI-TRADER.

Un seul agent peut valider une decision.

Ce module autorise uniquement les decisions de simulation.

Aucun ordre n'est transmis a MetaTrader.

"""

AUTHORIZED_DECIDER = "CDI_DECIDER"

ALLOWED_DECISIONS = {

    "SIMULATION_APPROVED",

    "REJECTED",

    "WAITING",

}

def validate_decision(

    *,

    agent_id: str,

    decision: str,

) -> bool:

    """Verifie l'identite du decideur et la decision proposee."""

    if agent_id != AUTHORIZED_DECIDER:

        raise PermissionError("Agent non autorise a decider.")

    if decision not in ALLOWED_DECISIONS:

        raise ValueError("Decision non autorisee.")

    return True