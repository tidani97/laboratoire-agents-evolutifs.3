

"""

CDI-TRADER 01 - VERSION COLLECTIVE

4 agents proposent.

1 agent décide.

Le gestionnaire de risque possède un droit de veto.

Capital collectif virtuel : 50 USD.

Simulation uniquement.

Aucun ordre réel ni connexion MT5.

"""

import csv

import random

from pathlib import Path

INITIAL_CAPITAL = 50.0

RISK_PER_TRADE = 0.01

MAX_DRAWDOWN = 0.10

MAX_VOLATILITY = 0.035

TRADING_COST = 0.0001

SIMULATIONS = 20

ROUNDS = 500

ASSETS = ["BTCUSD", "ETHUSD", "XAUUSD"]

ENVIRONMENTS = [

    "haussier",

    "baissier",

    "lateral",

    "volatile",

]

ACTIONS = ["achat", "vente", "abstention"]

def create_system():

    return {

        "capital": INITIAL_CAPITAL,

        "peak": INITIAL_CAPITAL,

        "max_drawdown": 0.0,

        "trades": 0,

        "wins": 0,

        "losses": 0,

        "memory": [],

        "agents": {

            "technique": {"skill": 0.50},

            "economique": {"skill": 0.50},

            "risque": {"skill": 0.50},

            "decisionnaire": {"skill": 0.50},

        },

    }

def generate_market(rng, environment):

    parameters = {

        "haussier": (0.002, 0.008),

        "baissier": (-0.002, 0.008),

        "lateral": (0.0, 0.004),

        "volatile": (0.0, 0.025),

    }

    drift, volatility = parameters[environment]

    return rng.gauss(drift, volatility)

# AGENT 1 : ANALYSE TECHNIQUE

def technical_agent(market_change):

    if market_change > 0.001:

        return "achat"

    if market_change < -0.001:

        return "vente"

    return "abstention"

# AGENT 2 : ANALYSE ECONOMIQUE

def economic_agent(environment):

    if environment == "haussier":

        return "achat"

    if environment == "baissier":

        return "vente"

    return "abstention"

# AGENT 3 : GESTIONNAIRE DU RISQUE

def risk_agent(system, market_change):

    capital = system["capital"]

    drawdown = (

        system["peak"] - capital

    ) / system["peak"] if system["peak"] > 0 else 1

    if capital <= 0:

        return "abstention", False

    if drawdown >= MAX_DRAWDOWN:

        return "abstention", False

    if abs(market_change) >= MAX_VOLATILITY:

        return "abstention", False

    # Le gestionnaire peut proposer une direction,

    # mais son rôle principal reste la protection.

    if market_change > 0:

        return "achat", True

    if market_change < 0:

        return "vente", True

    return "abstention", True

# AGENT 4 : PROPOSITION DU DECISIONNAIRE

def decisionnaire_proposal(

    technical,

    economic,

    risk_proposal,

):

    proposals = [

        technical,

        economic,

        risk_proposal,

    ]

    valid = [

        action for action in proposals

        if action in ("achat", "vente")

    ]

    if len(valid) < 2:

        return "abstention"

    if valid.count("achat") >= 2:

        return "achat"

    if valid.count("vente") >= 2:

        return "vente"

    return "abstention"

# VALIDATION FINALE

# SEUL LE DECISIONNAIRE PEUT AUTORISER UN ORDRE.

def validate_transaction(

    proposal,

    risk_approved,

    capital,

):

    if not risk_approved:

        return False

    if proposal not in ("achat", "vente"):

        return False

    if capital <= 0:

        return False

    return True

def update_learning(agent, profitable):

    reward = 1.0 if profitable else 0.0

    agent["skill"] += 0.05 * (

        reward - agent["skill"]

    )

    agent["skill"] = max(

        0.10,

        min(0.90, agent["skill"]),

    )

def execute_virtual_order(system, action, market_change):

    capital = system["capital"]

    if capital <= 0:

        return 0.0

    direction = 1 if action == "achat" else -1

    # Modèle pédagogique simplifié :

    # perte plafonnée à 1 % du capital.

    # Ce n'est pas un calcul de lot MT5.

    market_return = direction * market_change

    market_return = max(

        -RISK_PER_TRADE,

        min(0.03, market_return),

    )

    net_return = market_return - TRADING_COST

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

    for round_number in range(ROUNDS):

        asset = rng.choice(ASSETS)

        environment = rng.choice(ENVIRONMENTS)

        market_change = generate_market(

            rng,

            environment,

        )

        # Chaque agent formule une proposition.

        technical = technical_agent(market_change)

        economic = economic_agent(environment)

        risk_proposal, risk_approved = risk_agent(

            system,

            market_change,

        )

        decision_proposal = decisionnaire_proposal(

            technical,

            economic,

            risk_proposal,

        )

        # Le décisionnaire valide ou refuse.

        approved = validate_transaction(

            decision_proposal,

            risk_approved,

            system["capital"],

        )

        final_decision = (

            decision_proposal if approved

            else "refus"

        )

        pnl = 0.0

        if approved:

            pnl = execute_virtual_order(

                system,

                decision_proposal,

                market_change,

            )

        # Apprentissage des agents à partir du résultat.

        profitable = pnl > 0

        for agent in system["agents"].values():

            update_learning(agent, profitable)

        system["memory"].append({

            "technical": technical,

            "economic": economic,

            "risk": risk_proposal,

            "decisionnaire": decision_proposal,

            "approved": approved,

            "profitable": profitable,

        })

        history.append({

            "simulation": seed + 1,

            "round": round_number + 1,

            "asset": asset,

            "environment": environment,

            "market_change": round(market_change, 6),

            "technical_proposal": technical,

            "economic_proposal": economic,

            "risk_proposal": risk_proposal,

            "risk_approved": risk_approved,

            "decisionnaire_proposal": decision_proposal,

            "final_decision": final_decision,

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

            "decision_skill": round(

                system["agents"]["decisionnaire"]["skill"],

                4,

            ),

        })

    export_csv(

        "results/cdi_trader_01_history.csv",

        all_history,

    )

    export_csv(

        "results/cdi_trader_01_summary.csv",

        summaries,

    )

    average = sum(

        row["final_capital"] for row in summaries

    ) / len(summaries)

    print("\n=== CDI-TRADER 01 ===")

    print("Simulations :", SIMULATIONS)

    print("Capital initial :", INITIAL_CAPITAL, "USD")

    print("Capital final moyen :", round(average, 2), "USD")

    print("Ordres exécutés :", sum(

        row["trades"] for row in summaries

    ))

    print("Résultats enregistrés dans results/")

if __name__ == "__main__":

    main()