

#!/usr/bin/env python3

"""

CDI-TRADER 01

Laboratoire expérimental de trading multi-agents.

Capital virtuel : 50 USD par agent.

Aucune exécution d'ordres réels.

"""

import csv

import random

from pathlib import Path

from collections import defaultdict

INITIAL_CAPITAL = 50.0

RISK_PER_TRADE = 0.01

MAX_POSITIONS = 1

AGENTS = [

    "Analyste_technique",

    "Analyste_economique",

    "Gestionnaire_risque",

    "Trader_decisionnaire",

]

ASSETS = ["BTCUSD", "ETHUSD", "XAUUSD"]

ENVIRONMENTS = [

    "haussier",

    "baissier",

    "lateral",

    "forte_volatilite",

    "faible_volatilite",

]

TRADING_COST = 0.001

def create_agent(name):

    return {

        "name": name,

        "capital": INITIAL_CAPITAL,

        "peak": INITIAL_CAPITAL,

        "max_drawdown": 0.0,

        "wins": 0,

        "losses": 0,

        "trades": 0,

        "memory": [],

        "skill": 0.50,

    }

def generate_market(rng, environment):

    if environment == "haussier":

        drift = 0.002

        volatility = 0.008

    elif environment == "baissier":

        drift = -0.002

        volatility = 0.008

    elif environment == "lateral":

        drift = 0.0

        volatility = 0.004

    elif environment == "forte_volatilite":

        drift = 0.0

        volatility = 0.025

    else:

        drift = 0.0

        volatility = 0.002

    return rng.gauss(drift, volatility)

def calculate_drawdown(agent):

    capital = agent["capital"]

    agent["peak"] = max(agent["peak"], capital)

    if agent["peak"] > 0:

        drawdown = (

            agent["peak"] - capital

        ) / agent["peak"]

        agent["max_drawdown"] = max(

            agent["max_drawdown"],

            drawdown,

        )

def choose_signal(rng, market_change, skill):

    confidence = rng.random()

    if confidence < skill:

        return "achat" if market_change > 0 else "vente"

    return "vente" if market_change > 0 else "achat"

def update_learning(agent, profitable):

    reward = 1.0 if profitable else 0.0

    agent["skill"] += 0.05 * (

        reward - agent["skill"]

    )

    agent["skill"] = max(

        0.10,

        min(0.90, agent["skill"])

    )

    agent["memory"].append({

        "profitable": profitable,

        "skill": round(agent["skill"], 4),

    })

def execute_simulated_trade(agent, signal, market_change):

    if agent["capital"] <= 0:

        return 0.0

    risk_amount = agent["capital"] * RISK_PER_TRADE

    if risk_amount <= 0:

        return 0.0

    # Risque plafonné à 1 % du capital courant.

    direction = 1 if signal == "achat" else -1

    # Modèle pédagogique : perte maximale théorique

    # de 1 % du capital sur un trade.

    gross_return = direction * market_change

    # Limitation des pertes par stop-loss simulé.

    gross_return = max(

        -RISK_PER_TRADE,

        min(0.03, gross_return)

    )

    cost = abs(gross_return) * TRADING_COST + 0.0001

    net_return = gross_return - cost

    pnl = agent["capital"] * net_return

    agent["capital"] += pnl

    agent["trades"] += 1

    if pnl > 0:

        agent["wins"] += 1

    else:

        agent["losses"] += 1

    update_learning(agent, pnl > 0)

    calculate_drawdown(agent)

    return round(pnl, 5)

def run_simulation(seed, rounds=500):

    rng = random.Random(seed)

    agents = {

        name: create_agent(name)

        for name in AGENTS

    }

    history = []

    for round_number in range(rounds):

        asset = rng.choice(ASSETS)

        environment = rng.choice(ENVIRONMENTS)

        market_change = generate_market(

            rng,

            environment,

        )

        # Analyse technique : observe la variation.

        technical = (

            "achat" if market_change > 0 else "vente"

        )

        # Analyse économique : observe le régime.

        economic = (

            "achat"

            if environment == "haussier"

            else "vente"

            if environment == "baissier"

            else "neutre"

        )

        # Gestionnaire du risque : contrôle le contexte.

        risk_agent = agents["Gestionnaire_risque"]

        risk_approved = (

            abs(market_change) < 0.04

            and risk_agent["capital"] > 0

        )

        # Le trader confronte les analyses.

        trader = agents["Trader_decisionnaire"]

        if not risk_approved or economic == "neutre":

            decision = "abstention"

        elif technical == economic:

            decision = technical

        else:

            decision = "abstention"

        signals = {

            "Analyste_technique": technical,

            "Analyste_economique": economic,

            "Gestionnaire_risque": (

                "autorise" if risk_approved else "refuse"

            ),

            "Trader_decisionnaire": decision,

        }

        for name, agent in agents.items():

            signal = signals[name]

            if name == "Gestionnaire_risque":

                continue

            if signal == "neutre":

                continue

            if signal == "abstention":

                continue

            if name == "Trader_decisionnaire":

                signal = choose_signal(

                    rng,

                    market_change,

                    agent["skill"],

                )

            pnl = execute_simulated_trade(

                agent,

                signal,

                market_change,

            )

            history.append({

                "seed": seed,

                "round": round_number + 1,

                "asset": asset,

                "environment": environment,

                "agent": name,

                "signal": signal,

                "market_change": round(

                    market_change, 6

                ),

                "pnl": pnl,

                "capital": round(

                    agent["capital"], 5

                ),

                "skill": round(agent["skill"], 4),

            })

    return agents, history

def save_csv(filename, rows):

    path = Path(filename)

    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:

        return

    with path.open(

        "w",

        newline="",

        encoding="utf-8",

    ) as file:

        writer = csv.DictWriter(

            file,

            fieldnames=list(rows[0].keys()),

        )

        writer.writeheader()

        writer.writerows(rows)

def main():

    all_history = []

    summaries = []

    for seed in range(20):

        agents, history = run_simulation(seed)

        all_history.extend(history)

        for name, agent in agents.items():

            summaries.append({

                "seed": seed,

                "agent": name,

                "initial_capital": INITIAL_CAPITAL,

                "final_capital": round(

                    agent["capital"], 5

                ),

                "trades": agent["trades"],

                "wins": agent["wins"],

                "losses": agent["losses"],

                "max_drawdown": round(

                    agent["max_drawdown"], 5

                ),

                "final_skill": round(

                    agent["skill"], 4

                ),

            })

    save_csv(

        "results/cdi_trader_01_runs.csv",

        all_history,

    )

    save_csv(

        "results/cdi_trader_01_summary.csv",

        summaries,

    )

    print("CDI-TRADER 01 terminé.")

    print("Capital initial : 50 USD par agent.")

    print("Nombre de graines : 20.")

    print("Résultats enregistrés dans results/.")

    print("\nRésumé des simulations :")

    grouped = defaultdict(list)

    for row in summaries:

        grouped[row["agent"]].append(row)

    for name, rows in grouped.items():

        average = sum(

            row["final_capital"] for row in rows

        ) / len(rows)

        print(

            name,

            "| Capital final moyen :",

            round(average, 2),

            "USD",

        )

if __name__ == "__main__":

    main()