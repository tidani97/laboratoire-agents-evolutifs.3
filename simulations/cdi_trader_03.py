

import csv

import random

import sys

import uuid

from pathlib import Path

from decimal import Decimal

ROOT_DIR = Path(__file__).resolve().parents[1]

if str(ROOT_DIR) not in sys.path:

    sys.path.insert(0, str(ROOT_DIR))

from corrections.cdi_governance_v3 import (

    CDITradingGovernance,

    TradeProposal,

    Direction,

    verify_authorization,

)

from agents.cdi_memory_bridge_v2 import (

    record_round,

    flush_memory,

    reset_memory_buffer,

)

# ==================================================

# CDI-TRADER V3 — SIMULATION UNIQUEMENT

# ==================================================

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

AUTHORIZED_DECIDER = "CDI_MASTER"

RISK_REVIEWER = "CDI_RISK"

# Clé réservée aux simulations.

# Ne jamais réutiliser cette clé pour un compte réel.

SIMULATION_ONLY_SECRET = b"CDI_SIMULATION_ONLY_SECRET_KEY_2026"

governance = CDITradingGovernance(

    authorized_decider_id=AUTHORIZED_DECIDER,

    secret_key=SIMULATION_ONLY_SECRET,

)

def create_system():

    return {

        "capital": INITIAL_CAPITAL,

        "peak": INITIAL_CAPITAL,

        "daily_start": INITIAL_CAPITAL,

        "max_drawdown": 0.0,

        "trades": 0,

        "wins": 0,

        "losses": 0,

        "risk_vetoes": 0,

        "blocked_proposals": 0,

        "signed_authorizations": 0,

        "agents": {

            "CDI_TECHNICAL": {"skill": 0.60},

            "CDI_ECONOMIC": {"skill": 0.60},

            "CDI_RISK": {"skill": 0.90},

            "CDI_MASTER": {"skill": 0.75},

        },

    }

def generate_market(environment):

    conditions = {

        "haussier": (0.0008, 0.008),

        "baissier": (-0.0008, 0.008),

        "lateral": (0.0, 0.004),

        "volatile": (0.0, 0.020),

    }

    drift, volatility = conditions[environment]

    return random.gauss(drift, volatility), volatility

def technical_agent(market_return):

    if market_return > 0.001:

        return "BUY"

    if market_return < -0.001:

        return "SELL"

    return "HOLD"

def economic_agent(environment, market_return):

    if environment == "haussier" and market_return > 0:

        return "BUY"

    if environment == "baissier" and market_return < 0:

        return "SELL"

    if environment == "volatile":

        return "HOLD"

    return "HOLD"
    

def risk_agent(system, volatility):

    capital = system["capital"]

    daily_start = system["daily_start"]

    peak = system["peak"]

    if capital <= 0 or daily_start <= 0 or peak <= 0:

        return False, "Capital invalide."

    daily_loss_pct = max(

        0.0,

        (daily_start - capital) / daily_start * 100

    )

    drawdown_pct = max(

        0.0,

        (peak - capital) / peak * 100

    )

    volatility_pct = volatility * 100

    if daily_loss_pct >= MAX_DAILY_LOSS * 100:

        return False, "Limite de perte journalière."

    if drawdown_pct >= MAX_DRAWDOWN * 100:

        return False, "Limite de drawdown."

    if volatility_pct >= MAX_VOLATILITY * 100:

        return False, "Volatilité excessive."

    return True, "Contrôle préliminaire validé."

def decisionnaire_proposal(technical, economic):

    if technical == economic and technical in ("BUY", "SELL"):

        return technical

    return "HOLD"

def create_signed_authorization(

    system,

    decision,

    asset,

    volatility,

):

    """

    Demande une évaluation indépendante du risque,

    puis une décision signée du décideur unique.

    """

    if decision not in ("BUY", "SELL"):

        system["blocked_proposals"] += 1

        return None

    risk_approved, risk_reason = risk_agent(

        system,

        volatility

    )

    if not risk_approved:

        system["risk_vetoes"] += 1

        system["blocked_proposals"] += 1

        return None

    capital = Decimal(str(system["capital"]))

    daily_loss_pct = Decimal(str(max(

        0.0,

        (system["daily_start"] - system["capital"])

        / system["daily_start"] * 100

    )))

    drawdown_pct = Decimal(str(max(

        0.0,

        (system["peak"] - system["capital"])

        / system["peak"] * 100

    )))

    volatility_pct = Decimal(str(volatility * 100))

    direction = (

        Direction.BUY if decision == "BUY"

        else Direction.SELL

    )

    entry_price = Decimal("100")

    stop_loss = (

        Decimal("99") if direction == Direction.BUY

        else Decimal("101")

    )

    proposal = TradeProposal(

        proposal_id=str(uuid.uuid4()),

        agent_id=AUTHORIZED_DECIDER,

        symbol=asset,

        direction=direction,

        quantity=Decimal("0.01"),

        entry_price=entry_price,

        stop_loss=stop_loss,

        contract_size=Decimal("1"),

        estimated_costs=Decimal("0.001"),

    )

    assessment = governance.evaluate_risk(

        proposal=proposal,

        capital=capital,

        daily_loss_pct=daily_loss_pct,

        drawdown_pct=drawdown_pct,

        volatility_pct=volatility_pct,

        reviewer_id=RISK_REVIEWER,

    )

    if not assessment.approved:

        system["risk_vetoes"] += 1

        system["blocked_proposals"] += 1

        return None

    final_decision = governance.make_final_decision(

        proposal=proposal,

        assessment=assessment,

        decision_maker_id=AUTHORIZED_DECIDER,

        approve=True,

        reason="Consensus technique et économique validé.",

    )

    authorization = governance.authorize_execution(

        proposal,

        assessment,

        final_decision,

    )

    if not verify_authorization(

        authorization,

        SIMULATION_ONLY_SECRET,

    ):

        system["blocked_proposals"] += 1

        return None

    system["signed_authorizations"] += 1

    return authorization

def execute_virtual_order(system, authorization, market_return):

    """

    Exécute uniquement une transaction virtuelle

    après vérification de son autorisation signée.

    """

    if authorization is None:

        return 0.0

    if not verify_authorization(

        authorization,

        SIMULATION_ONLY_SECRET,

    ):

        system["blocked_proposals"] += 1

        return 0.0

    direction = authorization.direction

    signed_return = (

        market_return if direction == Direction.BUY

        else -market_return

    )

    risk_budget = system["capital"] * RISK_PER_TRADE

    pnl = risk_budget * signed_return / 0.01

    # Protection contre les résultats extrêmes.

    pnl = max(

        -risk_budget,

        min(pnl, risk_budget * 3)

    )

    pnl -= system["capital"] * TRADING_COST

    system["capital"] += pnl

    system["trades"] += 1

    if pnl > 0:

        system["wins"] += 1

    elif pnl < 0:

        system["losses"] += 1

    system["peak"] = max(

        system["peak"],

        system["capital"]

    )

    if system["peak"] > 0:

        drawdown = (

            (system["peak"] - system["capital"])

            / system["peak"]

        )

        system["max_drawdown"] = max(

            system["max_drawdown"],

            drawdown

        )

    return pnl
    
    

def run_simulation(seed, simulation_number):

    random.seed(seed)

    system = create_system()

    history = []

    for round_number in range(1, ROUNDS + 1):

        if (round_number - 1) % ROUNDS_PER_DAY == 0:

            system["daily_start"] = system["capital"]

        asset = random.choice(ASSETS)

        environment = random.choice(ENVIRONMENTS)

        market_return, volatility = generate_market(

            environment

        )

        # Analyse indépendante des agents.

        technical = technical_agent(market_return)

        economic = economic_agent(

            environment,

            market_return

        )

        # Le décideur unique exige un accord des deux analyses.

        decision = decisionnaire_proposal(

            technical,

            economic

        )

        # Contrôle du risque et autorisation cryptographique.

        authorization = create_signed_authorization(

            system,

            decision,

            asset,

            volatility,

        )

        # Aucun ordre n'est exécuté sans autorisation valide.

        pnl = execute_virtual_order(

            system,

            authorization,

            market_return,

        )

        # Conversion pour le pont mémoire existant.

        memory_signals = {

            "BUY": "achat",

            "SELL": "vente",

            "HOLD": "attente",

        }

        technical_memory = memory_signals[technical]

        economic_memory = memory_signals[economic]

        decision_memory = memory_signals[decision]

        risk_proposal = (

            "autorise" if authorization is not None

            else "bloque"

        )

        risk_approved = authorization is not None

        record_round(

            environment=environment,

            market_change=market_return,

            technical=technical_memory,

            economic=economic_memory,

            risk_proposal=risk_proposal,

            risk_approved=risk_approved,

            decision=decision_memory,

            pnl=pnl,

        )

        history.append({

            "simulation": simulation_number,

            "round": round_number,

            "asset": asset,

            "environment": environment,

            "market_return": market_return,

            "technical": technical,

            "economic": economic,

            "decision": decision,

            "authorized": authorization is not None,

            "pnl": pnl,

            "capital": system["capital"],

            "risk_vetoes": system["risk_vetoes"],

        })

    return system, history

def export_results(all_history, summaries):

    results_dir = ROOT_DIR / "results"

    results_dir.mkdir(parents=True, exist_ok=True)

    history_file = results_dir / "cdi_trader_v3_history.csv"

    summary_file = results_dir / "cdi_trader_v3_summary.csv"

    if all_history:

        with history_file.open(

            "w",

            newline="",

            encoding="utf-8"

        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=list(all_history[0].keys())

            )

            writer.writeheader()

            writer.writerows(all_history)

    if summaries:

        with summary_file.open(

            "w",

            newline="",

            encoding="utf-8"

        ) as file:

            writer = csv.DictWriter(

                file,

                fieldnames=list(summaries[0].keys())

            )

            writer.writeheader()

            writer.writerows(summaries)

    return history_file, summary_file

def main():

    reset_memory_buffer()

    all_history = []

    summaries = []

    print("===================================")

    print(" CDI-TRADER V3 — SIMULATION")

    print(" Capital virtuel :", INITIAL_CAPITAL, "USD")

    print(" Simulations :", SIMULATIONS)

    print(" Tours par simulation :", ROUNDS)

    print(" MT5 : NON CONNECTE")

    print(" Ordres reels : DESACTIVES")

    print("===================================")

    for simulation_number in range(1, SIMULATIONS + 1):

        seed = 2026 + simulation_number

        system, history = run_simulation(

            seed,

            simulation_number

        )

        all_history.extend(history)

        summaries.append({

            "simulation": simulation_number,

            "initial_capital": INITIAL_CAPITAL,

            "final_capital": round(system["capital"], 4),

            "trades": system["trades"],

            "wins": system["wins"],

            "losses": system["losses"],

            "risk_vetoes": system["risk_vetoes"],

            "blocked_proposals": system["blocked_proposals"],

            "signed_authorizations": system["signed_authorizations"],

            "max_drawdown_pct": round(

                system["max_drawdown"] * 100,

                4

            ),

        })

        print(

            f"Simulation {simulation_number}/{SIMULATIONS} | "

            f"Capital : {system['capital']:.2f} USD | "

            f"Transactions : {system['trades']} | "

            f"Refus risque : {system['risk_vetoes']}"

        )

    saved = flush_memory()

    history_file, summary_file = export_results(

        all_history,

        summaries

    )

    print("===================================")

    print(" SIMULATION TERMINEE")

    print(" Tours executes :", len(all_history))

    print(" Experiences memorisees :", saved)

    print(" Historique :", history_file)

    print(" Resume :", summary_file)

    print("===================================")

if __name__ == "__main__":

    main()