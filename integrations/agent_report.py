

"""Formatage des rapports multi-agents CDI-TRADER.

Ce module prépare des rapports pour Telegram.

Il ne communique pas avec MetaTrader et ne passe aucun ordre.

"""

RISK_STATUSES = {"PROTECTED", "WARNING", "BLOCKED"}

DECISION_STATUSES = {"SIMULATION_APPROVED", "REJECTED", "WAITING"}

def format_agent_report(

    *,

    market: str,

    timeframe: str,

    analyst_summary: str,

    analyst_bias: str,

    critic_summary: str,

    risk_status: str,

    risk_summary: str,

    decision_status: str,

    decision_reason: str,

    confidence: int,

) -> str:

    if not isinstance(confidence, int) or not 0 <= confidence <= 100:

        raise ValueError("confidence must be between 0 and 100")

    if risk_status not in RISK_STATUSES:

        raise ValueError("Invalid risk status")

    if decision_status not in DECISION_STATUSES:

        raise ValueError("Invalid decision status")

    fields = {

        "market": market,

        "timeframe": timeframe,

        "analyst_summary": analyst_summary,

        "analyst_bias": analyst_bias,

        "critic_summary": critic_summary,

        "risk_summary": risk_summary,

        "decision_reason": decision_reason,

        "analyst_bias": analyst_bias,

    }

    for name, value in fields.items():

        if not isinstance(value, str) or not value.strip():

            raise ValueError(f"{name} must be a non-empty string")

    return (

        "🧪 CDI-TRADER — RAPPORT MULTI-AGENTS\n"

        "MODE : SIMULATION / NOTIFICATIONS UNIQUEMENT\n\n"

        f"Marché : {market}\n"

        f"Unité de temps : {timeframe}\n\n"

        "1) ANALYSTE\n"

        f"Biais : {analyst_bias}\n"

        f"Analyse : {analyst_summary}\n\n"

        "2) AGENT CRITIQUE\n"

        f"Contre-analyse : {critic_summary}\n\n"

        "3) GESTION DU RISQUE\n"

        f"Statut : {risk_status}\n"

        f"Contrôle : {risk_summary}\n\n"

        "4) AGENT DÉCIDEUR UNIQUE\n"

        f"Décision : {decision_status}\n"

        f"Motif : {decision_reason}\n"

        f"Confiance déclarée : {confidence}%\n\n"

        "SÉCURITÉ : rapport informatif limité à la simulation. "

        "Aucun ordre n'est transmis à un courtier."

    )