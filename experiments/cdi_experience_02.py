

"""

CDI EXPERIENCE 02

Analyse, justification et confiance des agents.

Simulation artificielle uniquement.

Capital virtuel : 50 USD.

Aucun ordre réel.

"""

import csv

import random

from pathlib import Path

INITIAL_CAPITAL = 50.0

RISK_PER_TRADE = 0.005

MAX_DAILY_LOSS = 0.02

MAX_DRAWDOWN = 0.05

COST = 0.0001

ROUNDS = 500

SIMULATIONS = 20

ENVIRONMENTS = [

    "haussier",

    "baissier",

    "lateral",

    "volatile",

]

def create_system():

    return {

        "capital": INITIAL_CAPITAL,

        "peak": INITIAL_CAPITAL,

        "daily_start": INITIAL_CAPITAL,

        "max_drawdown": 0.0,

        "trades": 0,

        "wins": 0,

        "losses": 0,

        "agents": {

            "technique": {"skill": 0.50},

            "economique": {"skill": 0.50},

            "risque": {"skill": 0.50},

            "decisionnaire": {"skill": 0.50},

        },

    }

def generate_market(rng, environment):

    settings = {

        "haussier": (0.002, 0.008),

        "baissier": (-0.002, 0.008),

        "lateral": (0.0, 0.004),

        "volatile": (0.0, 0.025),

    }

    drift, volatility = settings[environment]

    return rng.gauss(drift, volatility)

def technical_agent(change):

    if change > 0.001:

        return {

            "proposal": "achat",

            "confidence": min(0.95, 0.55 + abs(change) * 20),

            "evidence": "Variation positive observée",

        }

    if change < -0.001:

        return {

            "proposal": "vente",

            "confidence": min(0.95, 0.55 + abs(change) * 20),

            "evidence": "Variation négative observée",

        }

    return {

        "proposal": "abstention",

        "confidence": 0.50,

        "evidence": "Variation trop faible",

    }

def economic_agent(environment):

    if environment == "haussier":

        return {

            "proposal": "achat",

            "confidence": 0.70,

            "evidence": "Régime haussier simulé",

        }

    if environment == "baissier":

        return {

            "proposal": "vente",

            "confidence": 0.70,

            "evidence": "Régime baissier simulé",

        }

    return {

        "proposal": "abstention",

        "confidence": 0.65,

        "evidence": "Contexte sans direction claire",

    }

def risk_agent(system, change):

    capital = system["capital"]

    drawdown = (

        system["peak"] - capital

    ) / system["peak"] if system["peak"] else 1

    daily_loss = (

        system["daily_start"] - capital

    ) / system["daily_start"] if system["daily_start"] else 1

    reasons = []

    if capital <= 0:

        reasons.append("Capital épuisé")

    if drawdown >= MAX_DRAWDOWN:

        reasons.append("Limite de drawdown atteinte")

    if daily_loss >= MAX_DAILY_LOSS:

        reasons.append("Limite de perte journalière atteinte")

    if abs(change) >= 0.035:

        reasons.append("Volatilité excessive")

    approved = len(reasons) == 0

    return {

        "approved": approved,

        "confidence": 0.95 if approved else 1.0,

        "evidence": (

            "Limites respectées"

            if approved else "; ".join(reasons)

        ),

    }

def decision_agent(technical, economic, risk):

    if not risk["approved"]:

        return {

            "proposal": "refus",

            "confidence": 1.0,

            "reason": "Veto du gestionnaire de risque",

        }

    t = technical["proposal"]

    e = economic["proposal"]

    if t == e and t in ("achat", "vente"):

        confidence = (

            technical["confidence"] +

            economic["confidence"]

        ) / 2

        if confidence >= 0.65:

            return {

                "proposal": t,

                "confidence": round(confidence, 3),

                "reason": "Convergence des analyses",

            }

    return {

        "proposal": "abstention",

        "confidence": 0.90,

        "reason": "Arguments insuffisants ou contradictoires",

    }

def execute_virtual_trade(system, action, change):

    if action not in ("achat", "vente"):

        return 0.0

    capital = system["capital"]

    if capital <= 0:

        return 0.0

    direction = 1 if action == "achat" else -1

    # Modèle simplifié : ce rendement est plafonné.

    # Ce n'est pas une vraie simulation de lots MT5.

    market_return = direction * change

    market_return = max(

        -RISK_PER_TRADE,

        min(0.015, market_return),

    )

    net_return = market_return - COST

    pnl = capital * net_return

    system["capital"] += pnl

    system["trades"] += 1

    if pnl > 0:

        system["wins"] += 1

    else:

        system["losses"] += 1

    system["peak"] = max(

        system["peak"],

        system["capital"],

    )

    if system["peak"] > 0:

        drawdown = (

            system["peak"] - system["capital"]

        ) / system["peak"]

        system["max_drawdown"] = max(

            system["max_drawdown"],

            drawdown,

        )

    return round(pnl, 5)

def run_simulation(seed):

    rng = random.Random(seed)

    system = create_system()

    history = []

    for period in range(ROUNDS):

        # Une journée simulée = 20 périodes.

        if period % 20 == 0:

            system["daily_start"] = system["capital"]

        environment = rng.choice(ENVIRONMENTS)

        change = generate_market(rng, environment)

        technical = technical_agent(change)

        economic = economic_agent(environment)

        risk = risk_agent(system, change)

        decision = decision_agent(

            technical,

            economic,

            risk,

        )

        pnl = 0.0

        if decision["proposal"] in ("achat", "vente"):

            pnl = execute_virtual_trade(

                system,

                decision["proposal"],

                change,

            )

        profitable = pnl > 0

        for agent in system["agents"].values():

            reward = 1.0 if profitable else 0.0

            agent["skill"] += 0.02 * (

                reward - agent["skill"]

            )

            agent["skill"] = max(

                0.10,

                min(0.90, agent["skill"]),

            )

        history.append({

            "simulation": seed + 1,

            "period": period + 1,

            "environment": environment,

            "market_change": round(change, 6),

            "technical_proposal": technical["proposal"],

            "technical_evidence": technical["evidence"],

            "technical_confidence": technical["confidence"],

            "economic_proposal": economic["proposal"],

            "economic_evidence": economic["evidence"],

            "economic_confidence": economic["confidence"],

            "risk_approved": risk["approved"],

            "risk_evidence": risk["evidence"],

            "final_decision": decision["proposal"],

            "decision_reason": decision["reason"],

            "decision_confidence": decision["confidence"],

            "pnl": pnl,

            "capital": round(system["capital"], 5),

        })

    return system, history

def export_csv(filename, rows):

    if not rows:

        return

    path = Path(filename)

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(

        "w",

        newline="",

        encoding="utf-8",

    ) as file:

        writer = csv.DictWriter(

            file,

            fieldnames=rows[0].keys(),

        )

        writer.writeheader()

        writer.writerows(rows)

def main():

    all_history = []

    summaries = []

    for seed in range(SIMULATIONS):

        system, history = run_simulation(seed)

        all_history.extend(history)

        summaries.append({

            "simulation": seed + 1,

            "initial_capital": INITIAL_CAPITAL,

            "final_capital": round(system["capital"], 2),

            "trades": system["trades"],

            "wins": system["wins"],

            "losses": system["losses"],

            "max_drawdown_percent": round(

                system["max_drawdown"] * 100, 2

            ),

        })

    export_csv(

        "results/cdi_experience_02_history.csv",

        all_history,

    )

    export_csv(

        "results/cdi_experience_02_summary.csv",

        summaries,

    )

    average = sum(

        row["final_capital"] for row in summaries

    ) / len(summaries)

    print("=== CDI EXPERIENCE 02 ===")

    print("Simulations :", SIMULATIONS)

    print("Capital initial :", INITIAL_CAPITAL, "USD")

    print("Capital final moyen :", round(average, 2), "USD")

    print("Transactions :", sum(

        row["trades"] for row in summaries

    ))

    print("Résultats enregistrés dans results/")

if __name__ == "__main__":

    main()