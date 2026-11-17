

"""

CDI-TRADER 02

Moteur collectif connecte a CDI-MEMORY V2.

4 agents proposent.

Le decisionnaire valide.

Le gestionnaire du risque possede un droit de veto.

Capital virtuel initial : 50 USD.

Simulation uniquement. Aucun ordre MT5.

"""

import csv

import random

import sys

from pathlib import Path

# Preparation des chemins du projet

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:

    sys.path.insert(0, str(ROOT_DIR))

from agents.cdi_memory_bridge_v2 import (

    record_round,

    flush_memory,

    reset_memory_buffer,

)

# PARAMETRES EXPERIMENTAUX

INITIAL_CAPITAL = 50.0

RISK_PER_TRADE = 0.005

MAX_DAILY_LOSS = 0.02

MAX_DRAWDOWN = 0.05

MAX_VOLATILITY = 0.025

TRADING_COST = 0.0001

SIMULATIONS = 20

ROUNDS = 500

ROUNDS_PER_DAY = 20

ASSETS = ["BTCUSD", "ETHUSD", "XAUUSD"]

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

    parameters = {

        "haussier": (0.002, 0.008),

        "baissier": (-0.002, 0.008),

        "lateral": (0.0, 0.004),

        "volatile": (0.0, 0.020),

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

    if capital <= 0:

        return "abstention", False

    drawdown = (

        (system["peak"] - capital) / system["peak"]

        if system["peak"] > 0 else 1

    )

    daily_loss = (

        (system["daily_start"] - capital)

        / system["daily_start"]

        if system["daily_start"] > 0 else 1

    )

    if drawdown >= MAX_DRAWDOWN:

        return "abstention", False

    if daily_loss >= MAX_DAILY_LOSS:

        return "abstention", False

    if abs(market_change) >= MAX_VOLATILITY:

        return "abstention", False

    if market_change > 0:

        return "achat", True

    if market_change < 0:

        return "vente", True

    return "abstention", True

# AGENT 4 : DECISIONNAIRE

def decisionnaire_proposal(technical, economic, risk):

    proposals = [technical, economic, risk]

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

# SEUL LE DECISIONNAIRE VALIDE

# LE GESTIONNAIRE DU RISQUE PEUT VETO.

def validate_transaction(proposal, risk_approved, capital):

    if not risk_approved:

        return False

    if proposal not in ("achat", "vente"):

        return False

    if capital <= 0:

        return False

    return True

def proposal_outcome(proposal, market_change):

    if proposal not in ("achat", "vente"):

        return "non_evalue"

    direction = 1 if proposal == "achat" else -1

    result = direction * market_change

    if result > 0:

        return "positif"

    if result < 0:

        return "negatif"

    return "neutre"

def update_learning(agent, outcome):

    # Un agent ne progresse que sur un resultat evaluable.

    if outcome not in ("positif", "negatif"):

        return

    reward = 1.0 if outcome == "positif" else 0.0

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

    market_return = direction * market_change

    # Modele pedagogique simplifie.

    # Ce plafond n'est PAS un calcul de risque MT5.

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

def run_simulation(seed, simulation_number):

    rng = random.Random(seed)

    system = create_system()

    history = []

    for round_number in range(ROUNDS):

        # Une journee simulee = 20 cycles.

        if round_number % ROUNDS_PER_DAY == 0:

            system["daily_start"] = system["capital"]

        asset = rng.choice(ASSETS)

        environment = rng.choice(ENVIRONMENTS)

        market_change = generate_market(

            rng,

            environment,

        )

        # Chaque agent formule sa proposition.

        technical = technical_agent(market_change)

        economic = economic_agent(environment)

        risk_proposal, risk_approved = risk_agent(

            system,

            market_change,

        )

        # Le decisionnaire prend la decision collective.

        decision_proposal = decisionnaire_proposal(

            technical,

            economic,

            risk_proposal,

        )

        # Validation finale.

        approved = validate_transaction(

            decision_proposal,

            risk_approved,

            system["capital"],

        )

        final_decision = (

            decision_proposal if approved else "refus"

        )

        pnl = 0.0

        if approved:

            pnl = execute_virtual_order(

                system,

                decision_proposal,

                market_change,

            )

        # Evaluation individuelle des propositions.

        technical_result = proposal_outcome(

            technical, market_change

        )

        economic_result = proposal_outcome(

            economic, market_change

        )

        decision_result = (

            "positif" if pnl > 0

            else "negatif" if pnl < 0

            else "non_evalue"

        ) if approved else "non_evalue"

        update_learning(

            system["agents"]["technique"],

            technical_result,

        )

        update_learning(

            system["agents"]["economique"],

            economic_result,

        )

        update_learning(

            system["agents"]["decisionnaire"],

            decision_result,

        )

        # Le gestionnaire du risque n'est pas note

        # simplement parce qu'une transaction gagne ou perd.

        # Transmission des experiences a CDI-MEMORY.

        record_round(

            environment=environment,

            market_change=market_change,

            technical=technical,

            economic=economic,

            risk_proposal=risk_proposal,

            risk_approved=risk_approved,

            decision=(

                decision_proposal if approved

                else "abstention"

            ),

            pnl=pnl,

        )

        history.append({

            "simulation": simulation_number,

            "round": round_number + 1,

            "asset": asset,

            "environment": environment,

            "market_change": round(market_change, 6),

            "technical": technical,

            "economic": economic,

            "risk": risk_proposal,

            "risk_approved": risk_approved,

            "decisionnaire": decision_proposal,

            "final_decision": final_decision,

            "pnl": pnl,

            "capital": round(system["capital"], 5),

        })

    return system, history

def export_csv(filename, rows):

    if not rows:

        return

    path = ROOT_DIR / filename

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

    reset_memory_buffer()

    try:

        for seed in range(SIMULATIONS):

            simulation_number = seed + 1

            system, history = run_simulation(

                seed,

                simulation_number,

            )

            all_history.extend(history)

            summaries.append({

                "simulation": simulation_number,

                "initial_capital": INITIAL_CAPITAL,

                "final_capital": round(

                    system["capital"], 2

                ),

                "trades": system["trades"],

                "wins": system["wins"],

                "losses": system["losses"],

                "max_drawdown_percent": round(

                    system["max_drawdown"] * 100, 2

                ),

                "technical_skill": round(

                    system["agents"]["technique"]["skill"],

                    4,

                ),

                "economic_skill": round(

                    system["agents"]["economique"]["skill"],

                    4,

                ),

                "decision_skill": round(

                    system["agents"]["decisionnaire"]["skill"],

                    4,

                ),

            })

    finally:

        # Sauvegarde groupee des experiences.

        saved = flush_memory()

    export_csv(

        "results/cdi_trader_02_history.csv",

        all_history,

    )

    export_csv(

        "results/cdi_trader_02_summary.csv",

        summaries,

    )

    average = sum(

        row["final_capital"] for row in summaries

    ) / len(summaries)

    print("\n=== CDI-TRADER 02 ===")

    print("Simulations :", SIMULATIONS)

    print("Capital initial :", INITIAL_CAPITAL, "USD")

    print("Capital final moyen :", round(average, 2), "USD")

    print("Ordres executes :", sum(

        row["trades"] for row in summaries

    ))

    print("Experiences transmises a CDI-MEMORY :", saved)

    print("Resultats enregistres dans results/")

if __name__ == "__main__":

    main()