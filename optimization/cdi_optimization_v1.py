

"""

CDI-TRADER

Module d'optimisation V1.

Analyse les performances et propose des améliorations.

Ne modifie jamais les règles de sécurité.

Ne passe aucun ordre.

"""

from dataclasses import dataclass

from decimal import Decimal

from typing import List

@dataclass(frozen=True)

class PerformanceReport:

    total_trades: int

    winning_trades: int

    losing_trades: int

    total_profit: Decimal

    total_loss: Decimal

    max_drawdown_pct: Decimal

@dataclass(frozen=True)

class OptimizationResult:

    win_rate_pct: Decimal

    profit_factor: Decimal

    average_profit: Decimal

    average_loss: Decimal

    recommendation: str

    execution_allowed: bool = False

def analyze_performance(

    report: PerformanceReport,

) -> OptimizationResult:

    if report.total_trades < 0:

        raise ValueError("Nombre de transactions invalide.")

    if report.winning_trades < 0 or report.losing_trades < 0:

        raise ValueError("Statistiques invalides.")

    if report.winning_trades + report.losing_trades != report.total_trades:

        raise ValueError("Les statistiques ne correspondent pas.")

    if report.total_profit < 0 or report.total_loss < 0:

        raise ValueError("Les montants doivent être positifs.")

    if report.max_drawdown_pct < 0:

        raise ValueError("Drawdown invalide.")

    if report.total_trades == 0:

        return OptimizationResult(

            win_rate_pct=Decimal("0"),

            profit_factor=Decimal("0"),

            average_profit=Decimal("0"),

            average_loss=Decimal("0"),

            recommendation="Collecter davantage de données.",

        )

    win_rate = (

        Decimal(report.winning_trades)

        / Decimal(report.total_trades)

        * Decimal("100")

    )

    profit_factor = (

        report.total_profit / report.total_loss

        if report.total_loss > 0

        else Decimal("0")

    )

    average_profit = (

        report.total_profit / report.winning_trades

        if report.winning_trades > 0

        else Decimal("0")

    )

    average_loss = (

        report.total_loss / report.losing_trades

        if report.losing_trades > 0

        else Decimal("0")

    )

    if report.max_drawdown_pct >= Decimal("10"):

        recommendation = "Réduire le risque et réexaminer la stratégie."

    elif profit_factor < Decimal("1"):

        recommendation = "Revoir les entrées et les sorties."

    elif win_rate < Decimal("40"):

        recommendation = "Analyser les signaux et les faux départs."

    else:

        recommendation = "Continuer les simulations et surveiller les résultats."

    return OptimizationResult(

        win_rate_pct=win_rate,

        profit_factor=profit_factor,

        average_profit=average_profit,

        average_loss=average_loss,

        recommendation=recommendation,

    )

def compare_strategies(

    baseline: PerformanceReport,

    candidate: PerformanceReport,

) -> str:

    baseline_result = analyze_performance(baseline)

    candidate_result = analyze_performance(candidate)

    if candidate_result.profit_factor > baseline_result.profit_factor:

        return "Stratégie candidate à tester en simulation."

    return "Conserver la stratégie de référence."

def optimization_safety_check(

    proposed_change: str,

) -> bool:

    protected_rules = [

        "risk_limit",

        "stop_loss",

        "daily_loss_limit",

        "decision_authority",

        "capital_protection",

    ]

    if proposed_change in protected_rules:

        return False

    return True