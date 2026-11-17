

"""

CDI MEMORY BRIDGE 01

Connecteur entre les moteurs CDI

et le systeme de memoire des agents.

Enregistre les propositions, decisions

et resultats des experiences.

"""

from agents.cdi_memory import record_experience

def evaluate_proposal(proposal, market_change):

    if proposal == "abstention":

        return "non_evalue"

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

    """

    Enregistre une experience pour chacun

    des quatre agents.

    """

    # 1. Analyste technique

    record_experience(

        agent="technique",

        environment=environment,

        proposal=technical,

        confidence=0.50,

        outcome=evaluate_proposal(

            technical,

            market_change,

        ),

        lesson="Evaluation de la proposition technique.",

        evidence="Variation du marche observee.",

    )

    # 2. Analyste economique

    record_experience(

        agent="economique",

        environment=environment,

        proposal=economic,

        confidence=0.50,

        outcome=evaluate_proposal(

            economic,

            market_change,

        ),

        lesson="Evaluation du contexte economique.",

        evidence="Environnement de marche simule.",

    )

    # 3. Gestionnaire du risque

    record_experience(

        agent="risque",

        environment=environment,

        proposal=risk_proposal,

        confidence=0.95,

        outcome="non_evalue",

        lesson=(

            "Transaction autorisee."

            if risk_approved

            else "Transaction refusee par precaution."

        ),

        evidence="Controle des limites de risque.",

    )

    # 4. Agent decisionnaire

    if decision in ("achat", "vente"):

        outcome = (

            "positif" if pnl > 0

            else "negatif" if pnl < 0

            else "neutre"

        )

    else:

        outcome = "non_evalue"

    record_experience(

        agent="decisionnaire",

        environment=environment,

        proposal=decision,

        confidence=0.50,

        outcome=outcome,

        lesson="Evaluation de la decision collective.",

        evidence="Resultat de la simulation.",

    )

    return {

        "technical": technical,

        "economic": economic,

        "risk": risk_approved,

        "decision": decision,

        "recorded": True,

    }