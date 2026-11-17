

"""

CDI-TRADER V2

Module de gouvernance et de contrôle des transactions.

Aucun ordre réel n'est envoyé par ce module.

Il produit uniquement une autorisation vérifiable.

"""

from dataclasses import dataclass

from decimal import Decimal

from enum import Enum

from typing import Tuple

class Direction(str, Enum):

    BUY = "BUY"

    SELL = "SELL"

class DecisionStatus(str, Enum):

    APPROVED = "APPROVED"

    REJECTED = "REJECTED"

@dataclass(frozen=True)

class TradeProposal:

    proposal_id: str

    agent_id: str

    symbol: str

    direction: Direction

    quantity: Decimal

    entry_price: Decimal

    stop_loss: Decimal

    risk_amount: Decimal

@dataclass(frozen=True)

class RiskPolicy:

    max_trade_risk_pct: Decimal = Decimal("1.0")

    max_daily_loss_pct: Decimal = Decimal("3.0")

    max_drawdown_pct: Decimal = Decimal("10.0")

    max_volatility_pct: Decimal = Decimal("5.0")

@dataclass(frozen=True)

class RiskAssessment:

    proposal_id: str

    reviewer_id: str

    approved: bool

    reasons: Tuple[str, ...]

@dataclass(frozen=True)

class FinalDecision:

    proposal_id: str

    decision_maker_id: str

    status: DecisionStatus

    reason: str

@dataclass(frozen=True)

class TradeAuthorization:

    proposal_id: str

    decision_maker_id: str

    symbol: str

    direction: Direction

    quantity: Decimal

def evaluate_risk(

    proposal: TradeProposal,

    capital: Decimal,

    daily_loss_pct: Decimal,

    drawdown_pct: Decimal,

    volatility_pct: Decimal,

    reviewer_id: str,

    policy: RiskPolicy = RiskPolicy(),

) -> RiskAssessment:

    reasons = []

    if not reviewer_id:

        reasons.append("Identifiant du contrôleur de risque manquant.")

    if capital <= 0:

        reasons.append("Capital invalide.")

    if proposal.quantity <= 0:

        reasons.append("Quantité invalide.")

    if proposal.entry_price <= 0:

        reasons.append("Prix d'entrée invalide.")

    if proposal.risk_amount <= 0:

        reasons.append("Montant du risque invalide.")

    if proposal.direction == Direction.BUY:

        if proposal.stop_loss >= proposal.entry_price:

            reasons.append("Stop-loss invalide pour un achat.")

    elif proposal.direction == Direction.SELL:

        if proposal.stop_loss <= proposal.entry_price:

            reasons.append("Stop-loss invalide pour une vente.")

    else:

        reasons.append("Direction non reconnue.")

    if capital > 0:

        max_risk = capital * policy.max_trade_risk_pct / Decimal("100")

        if proposal.risk_amount > max_risk:

            reasons.append("Risque par transaction dépassé.")

    if daily_loss_pct < 0 or daily_loss_pct >= policy.max_daily_loss_pct:

        reasons.append("Limite de perte journalière atteinte.")

    if drawdown_pct < 0 or drawdown_pct >= policy.max_drawdown_pct:

        reasons.append("Drawdown maximal atteint.")

    if volatility_pct < 0 or volatility_pct >= policy.max_volatility_pct:

        reasons.append("Volatilité excessive.")

    if not proposal.proposal_id or not proposal.agent_id:

        reasons.append("Identité de proposition ou agent manquante.")

    if not proposal.symbol:

        reasons.append("Symbole de transaction manquant.")

    return RiskAssessment(

        proposal_id=proposal.proposal_id,

        reviewer_id=reviewer_id,

        approved=len(reasons) == 0,

        reasons=tuple(reasons),

    )

def make_final_decision(

    proposal: TradeProposal,

    assessment: RiskAssessment,

    decision_maker_id: str,

    authorized_decider_id: str,

    approve: bool,

    reason: str,

) -> FinalDecision:

    if not decision_maker_id:

        raise PermissionError("Identité du décideur manquante.")

    if decision_maker_id != authorized_decider_id:

        raise PermissionError("Décideur non autorisé.")

    if assessment.proposal_id != proposal.proposal_id:

        raise PermissionError("Évaluation de risque non correspondante.")

    if not assessment.reviewer_id:

        raise PermissionError("Contrôle de risque non identifié.")

    if approve and not assessment.approved:

        raise PermissionError("Le risque a refusé cette transaction.")

    if not reason.strip():

        raise ValueError("Une justification est obligatoire.")

    return FinalDecision(

        proposal_id=proposal.proposal_id,

        decision_maker_id=decision_maker_id,

        status=(

            DecisionStatus.APPROVED

            if approve

            else DecisionStatus.REJECTED

        ),

        reason=reason,

    )

def authorize_execution(

    proposal: TradeProposal,

    assessment: RiskAssessment,

    decision: FinalDecision,

    authorized_decider_id: str,

) -> TradeAuthorization:

    if not assessment.approved:

        raise PermissionError("Transaction bloquée par le risque.")

    if assessment.proposal_id != proposal.proposal_id:

        raise PermissionError("Évaluation de risque non correspondante.")

    if decision.proposal_id != proposal.proposal_id:

        raise PermissionError("Décision non correspondante.")

    if decision.decision_maker_id != authorized_decider_id:

        raise PermissionError("Signature du décideur invalide.")

    if decision.status != DecisionStatus.APPROVED:

        raise PermissionError("Transaction non approuvée.")

    return TradeAuthorization(

        proposal_id=proposal.proposal_id,

        decision_maker_id=decision.decision_maker_id,

        symbol=proposal.symbol,

        direction=proposal.direction,

        quantity=proposal.quantity,

    )