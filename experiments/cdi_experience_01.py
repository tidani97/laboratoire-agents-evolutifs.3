

"""

CDI EXPERIENCE 01

Comparaison de trois stratégies de trading.

A : Analyste technique

B : Analyste économique

C : Equipe collective CDI-TRADER

Capital virtuel : 50 USD par stratégie.

Simulation uniquement.

"""

import csv

import random

from pathlib import Path

INITIAL_CAPITAL = 50.0

RISK = 0.01

COST = 0.0001

SIMULATIONS = 20

ROUNDS = 500

ENVIRONMENTS = [

    "haussier",

    "baissier",

    "lateral",

    "volatile",

]

def generate_market(rng, environment):

    settings = {

        "haussier": (0.002, 0.008),

        "baissier": (-0.002, 0.008),

        "lateral": (0.0, 0.004),

        "volatile": (0.0, 0.025),

    }

    drift, volatility = settings[environment]

    return rng.gauss(drift, volatility)

def technical_strategy(change):

    if change > 0.001:

        return "achat"

    if change < -0.001:

        return "vente"

    return "abstention"

def economic_strategy(environment):

    if environment == "haussier":

        return "achat"

    if environment == "baissier":

        return "vente"

    return "abstention"

def collective_strategy(change, environment):

    technical = technical_strategy(change)

    economic = economic_strategy(environment)

    risk_approved = abs(change) < 0.035

    if not risk_approved:

        return "abstention"

    proposals = [technical, economic]

    if proposals.count("achat") >= 2:

        return "achat"

    if proposals.count("vente") >= 2:

        return "vente"

    return "abstention"

def create_portfolio():

    return {

        "capital": INITIAL_CAPITAL,

        "peak": INITIAL_CAPITAL,

        "max_drawdown": 0.0,

        "trades": 0,

        "wins": 0,

        "losses": 0,

    }

def execute(portfolio, action, change):

    if action == "abstention":

        return 0.0

    if portfolio["capital"] <= 0:

        return 0.0

    direction = 1 if action == "achat" else -1

    # Modèle pédagogique simplifié.

    result = direction * change

    result = max(-RISK, min(0.03, result))

    result -= COST

    pnl = portfolio["capital"] * result

    portfolio["capital"] += pnl

    portfolio["trades"] += 1

    if pnl > 0:

        portfolio["wins"] += 1

    else:

        portfolio["losses"] += 1

    portfolio["peak"] = max(

        portfolio["peak"],

        portfolio["capital"],

    )

    if portfolio["peak"] > 0:

        drawdown = (

            portfolio["peak"] - portfolio["capital"]

        ) / portfolio["peak"]

        portfolio["max_drawdown"] = max(

            portfolio["max_drawdown"],

            drawdown,

        )

    return round(pnl, 5)

def run_experiment(seed):

    rng = random.Random(seed)

    portfolios = {

        "Technique": create_portfolio(),

        "Economique": create_portfolio(),

        "Collectif": create_portfolio(),

    }

    history = []

    for period in range(ROUNDS):

        environment = rng.choice(ENVIRONMENTS)

        change = generate_market(

            rng,

            environment,

        )

        actions = {

            "Technique": technical_strategy(change),

            "Economique": economic_strategy(environment),

            "Collectif": collective_strategy(

                change,

                environment,

            ),

        }

        for name, action in actions.items():

            pnl = execute(

                portfolios[name],

                action,

                change,

            )

            history.append({

                "simulation": seed + 1,

                "period": period + 1,

                "environment": environment,

                "market_change": round(change, 6),

                "strategy": name,

                "action": action,

                "pnl": pnl,

                "capital": round(

                    portfolios[name]["capital"], 5

                ),

            })

    return portfolios, history

def save_csv(filename, rows):

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

        portfolios, history = run_experiment(seed)

        all_history.extend(history)

        for name, portfolio in portfolios.items():

            summaries.append({

                "simulation": seed + 1,

                "strategy": name,

                "initial_capital": INITIAL_CAPITAL,

                "final_capital": round(

                    portfolio["capital"], 2

                ),

                "trades": portfolio["trades"],

                "wins": portfolio["wins"],

                "losses": portfolio["losses"],

                "max_drawdown_percent": round(

                    portfolio["max_drawdown"] * 100, 2

                ),

            })

    save_csv(

        "results/cdi_experience_01_history.csv",

        all_history,

    )

    save_csv(

        "results/cdi_experience_01_summary.csv",

        summaries,

    )

    print("\n=== CDI EXPERIENCE 01 ===")

    for name in ("Technique", "Economique", "Collectif"):

        values = [

            row["final_capital"]

            for row in summaries

            if row["strategy"] == name

        ]

        average = sum(values) / len(values)

        print(

            name,

            ": capital final moyen =",

            round(average, 2),

            "USD",

        )

    print("\nRésultats exportés dans results/")

if __name__ == "__main__":

    main()