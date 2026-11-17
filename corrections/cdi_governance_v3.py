

"""

CDI-TRADER V3

Gouvernance, contrôle des risques et autorisation signée.

Aucun ordre réel n'est envoyé par ce module.

"""

from dataclasses import dataclass

from decimal import Decimal

from enum import Enum

from hashlib import sha256

import hashlib

import hmac

import json

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

    contract_size: Decimal = Decimal("1")

    estimated_costs: Decimal = Decimal("0")

@dataclass(frozen=True)

class RiskPolicy:

    max_trade_risk_pct: Decimal = Decimal("1.0")

    max_daily_loss_pct: Decimal = Decimal("3.0")

    max_drawdown_pct: Decimal = Decimal("10.0")

    max_volatility_pct: Decimal = Decimal("5.0")

@dataclass(frozen=True)

class RiskAssessment:

    proposal_digest: str

    reviewer_id: str

    approved: bool

    calculated_risk: Decimal

    reasons: tuple

    signature: str

@dataclass(frozen=True)

class FinalDecision:

    proposal_digest: str

    assessment_signature: str

    decision_maker_id: str

    status: DecisionStatus

    reason: str

    signature: str

@dataclass(frozen=True)

class TradeAuthorization:

    proposal_id: str

    proposal_digest: str

    assessment_signature: str

    decision_signature: str

    decision_maker_id: str

    symbol: str

    direction: Direction

    quantity: Decimal

    signature: str

def finite(value):

    return isinstance(value, Decimal) and value.is_finite()

def canonical(payload):

    return json.dumps(

        payload, sort_keys=True, separators=(",", ":")

    ).encode("utf-8")

def proposal_payload(p):

    return {

        "proposal_id": p.proposal_id,

        "agent_id": p.agent_id,

        "symbol": p.symbol,

        "direction": str(p.direction),

        "quantity": str(p.quantity),

        "entry_price": str(p.entry_price),

        "stop_loss": str(p.stop_loss),

        "contract_size": str(p.contract_size),

        "estimated_costs": str(p.estimated_costs),

    }

class CDITradingGovernance:

    def __init__(

        self,

        authorized_decider_id,

        secret_key,

        policy=RiskPolicy()

    ):

        if not authorized_decider_id:

            raise ValueError("Décideur obligatoire.")

        if not isinstance(secret_key, bytes) or len(secret_key) < 32:

            raise ValueError("Clé secrète de 32 octets minimum.")

        self.decider = authorized_decider_id

        self.secret = secret_key

        self.policy = policy

        for value in (

            policy.max_trade_risk_pct,

            policy.max_daily_loss_pct,

            policy.max_drawdown_pct,

            policy.max_volatility_pct,

        ):

            if not finite(value) or value <= 0:

                raise ValueError("Politique de risque invalide.")

    def sign(self, payload):

        return hmac.new(

            self.secret, canonical(payload), hashlib.sha256

        ).hexdigest()

    def verify(self, payload, signature):

        return (

            isinstance(signature, str)

            and hmac.compare_digest(self.sign(payload), signature)

        )

    def proposal_digest(self, proposal):

        return hashlib.sha256(

            canonical(proposal_payload(proposal))

        ).hexdigest()

    def assessment_payload(self, a):

        return {

            "proposal_digest": a.proposal_digest,

            "reviewer_id": a.reviewer_id,

            "approved": a.approved,

            "calculated_risk": str(a.calculated_risk),

            "reasons": list(a.reasons),

        }

    def decision_payload(self, d):

        return {

            "proposal_digest": d.proposal_digest,

            "assessment_signature": d.assessment_signature,

            "decision_maker_id": d.decision_maker_id,

            "status": d.status.value,

            "reason": d.reason,

        }

    def evaluate_risk(

        self,

        proposal,

        capital,

        daily_loss_pct,

        drawdown_pct,

        volatility_pct,

        reviewer_id

    ):

        if not isinstance(proposal, TradeProposal):

            raise TypeError("Proposition invalide.")

        reasons = []

        if not reviewer_id or not reviewer_id.strip():

            reasons.append("Contrôleur non identifié.")

        values = {

            "capital": capital,

            "daily_loss_pct": daily_loss_pct,

            "drawdown_pct": drawdown_pct,

            "volatility_pct": volatility_pct,

            "quantity": proposal.quantity,

            "entry_price": proposal.entry_price,

            "stop_loss": proposal.stop_loss,

            "contract_size": proposal.contract_size,

            "estimated_costs": proposal.estimated_costs,

        }

        for name, value in values.items():

            if not finite(value):

                reasons.append(f"Valeur invalide : {name}.")

        if not proposal.proposal_id or not proposal.agent_id:

            reasons.append("Identité de proposition ou agent manquante.")

        if not proposal.symbol or not proposal.symbol.strip():

            reasons.append("Symbole manquant.")

        if not isinstance(proposal.direction, Direction):

            reasons.append("Direction invalide.")

        positive = (

            ("capital", capital),

            ("quantité", proposal.quantity),

            ("prix d'entrée", proposal.entry_price),

            ("taille du contrat", proposal.contract_size),

        )

        for name, value in positive:

            if finite(value) and value <= 0:

                reasons.append(f"{name} invalide.")

        if finite(proposal.estimated_costs):

            if proposal.estimated_costs < 0:

                reasons.append("Frais négatifs.")

        if isinstance(proposal.direction, Direction):

            if finite(proposal.entry_price) and finite(proposal.stop_loss):

                if proposal.direction == Direction.BUY:

                    if proposal.stop_loss >= proposal.entry_price:

                        reasons.append("Stop-loss invalide pour un achat.")

                else:

                    if proposal.stop_loss <= proposal.entry_price:

                        reasons.append("Stop-loss invalide pour une vente.")

        limits = (

            ("perte journalière", daily_loss_pct,

             self.policy.max_daily_loss_pct),

            ("drawdown", drawdown_pct,

             self.policy.max_drawdown_pct),

            ("volatilité", volatility_pct,

             self.policy.max_volatility_pct),

        )

        for name, value, limit in limits:

            if finite(value):

                if value < 0:

                    reasons.append(f"{name} négatif.")

                elif value >= limit:

                    reasons.append(f"Limite de {name} atteinte.")

        risk = Decimal("0")

        risk_inputs = (

            proposal.quantity,

            proposal.contract_size,

            proposal.entry_price,

            proposal.stop_loss,

            proposal.estimated_costs,

        )

        if all(finite(v) for v in risk_inputs):

            if (

                proposal.quantity > 0

                and proposal.contract_size > 0

                and proposal.estimated_costs >= 0

            ):

                risk = (

                    proposal.quantity

                    * proposal.contract_size

                    * abs(proposal.entry_price - proposal.stop_loss)

                    + proposal.estimated_costs

                )

        if finite(capital) and capital > 0:

            maximum = (

                capital * self.policy.max_trade_risk_pct

                / Decimal("100")

            )

            if risk > maximum:

                reasons.append("Risque par transaction dépassé.")

        unsigned = RiskAssessment(

            proposal_digest=self.proposal_digest(proposal),

            reviewer_id=reviewer_id,

            approved=len(reasons) == 0,

            calculated_risk=risk,

            reasons=tuple(reasons),

            signature=""

        )

        return RiskAssessment(

            proposal_digest=unsigned.proposal_digest,

            reviewer_id=unsigned.reviewer_id,

            approved=unsigned.approved,

            calculated_risk=unsigned.calculated_risk,

            reasons=unsigned.reasons,

            signature=self.sign(self.assessment_payload(unsigned))

        )

    def make_final_decision(

        self,

        proposal,

        assessment,

        decision_maker_id,

        approve,

        reason

    ):

        if decision_maker_id != self.decider:

            raise PermissionError("Décideur non autorisé.")

        if not isinstance(assessment, RiskAssessment):

            raise TypeError("Évaluation de risque obligatoire.")

        digest = self.proposal_digest(proposal)

        if assessment.proposal_digest != digest:

            raise PermissionError("Évaluation non correspondante.")

        if not self.verify(

            self.assessment_payload(assessment),

            assessment.signature

        ):

            raise PermissionError("Signature du risque invalide.")

        if approve and not assessment.approved:

            raise PermissionError("Transaction refusée par le risque.")

        if not isinstance(reason, str) or not reason.strip():

            raise ValueError("Justification obligatoire.")

        unsigned = FinalDecision(

            proposal_digest=digest,

            assessment_signature=assessment.signature,

            decision_maker_id=decision_maker_id,

            status=(

                DecisionStatus.APPROVED if approve

                else DecisionStatus.REJECTED

            ),

            reason=reason.strip(),

            signature=""

        )

        return FinalDecision(

            proposal_digest=unsigned.proposal_digest,

            assessment_signature=unsigned.assessment_signature,

            decision_maker_id=unsigned.decision_maker_id,

            status=unsigned.status,

            reason=unsigned.reason,

            signature=self.sign(self.decision_payload(unsigned))

        )

    def authorize_execution(self, proposal, assessment, decision):

        digest = self.proposal_digest(proposal)

        if not isinstance(assessment, RiskAssessment):

            raise PermissionError("Évaluation officielle obligatoire.")

        if not isinstance(decision, FinalDecision):

            raise PermissionError("Décision officielle obligatoire.")

        if not assessment.approved:

            raise PermissionError("Transaction bloquée par le risque.")

        if assessment.proposal_digest != digest:

            raise PermissionError("Évaluation non correspondante.")

        if decision.proposal_digest != digest:

            raise PermissionError("Décision non correspondante.")

        if not self.verify(

            self.assessment_payload(assessment),

            assessment.signature

        ):

            raise PermissionError("Évaluation falsifiée.")

        if decision.assessment_signature != assessment.signature:

            raise PermissionError("Évaluation de référence différente.")

        if decision.decision_maker_id != self.decider:

            raise PermissionError("Décideur non autorisé.")

        if decision.status != DecisionStatus.APPROVED:

            raise PermissionError("Transaction non approuvée.")

        if not self.verify(

            self.decision_payload(decision),

            decision.signature

        ):

            raise PermissionError("Décision falsifiée.")

        payload = {

            "proposal_id": proposal.proposal_id,

            "proposal_digest": digest,

            "assessment_signature": assessment.signature,

            "decision_signature": decision.signature,

            "decision_maker_id": decision.decision_maker_id,

            "symbol": proposal.symbol,

            "direction": proposal.direction.value,

            "quantity": str(proposal.quantity),

        }

        return TradeAuthorization(

            proposal_id=proposal.proposal_id,

            proposal_digest=digest,

            assessment_signature=assessment.signature,

            decision_signature=decision.signature,

            decision_maker_id=decision.decision_maker_id,

            symbol=proposal.symbol,

            direction=proposal.direction,

            quantity=proposal.quantity,

            signature=self.sign(payload)

        )

def verify_authorization(authorization, secret_key):

    if not isinstance(authorization, TradeAuthorization):

        return False

    if not isinstance(secret_key, bytes) or len(secret_key) < 32:

        return False

    payload = {

        "proposal_id": authorization.proposal_id,

        "proposal_digest": authorization.proposal_digest,

        "assessment_signature": authorization.assessment_signature,

        "decision_signature": authorization.decision_signature,

        "decision_maker_id": authorization.decision_maker_id,

        "symbol": authorization.symbol,

        "direction": authorization.direction.value,

        "quantity": str(authorization.quantity),

    }

    expected = hmac.new(

        secret_key,

        canonical(payload),

        hashlib.sha256

    ).hexdigest()

    return hmac.compare_digest(expected, authorization.signature)