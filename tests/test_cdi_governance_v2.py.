

"""Tests de gouvernance CDI-TRADER V2."""

import unittest

from decimal import Decimal

from corrections.cdi_governance_v2 import (

    DecisionStatus,

    Direction,

    TradeProposal,

    evaluate_risk,

    make_final_decision,

    authorize_execution,

)

AUTHORIZED = "decisionnaire_principal"

def proposal(**overrides):

    values = {

        "proposal_id": "TEST-001",

        "agent_id": "technique",

        "symbol": "BTCUSD",

        "direction": Direction.BUY,

        "quantity": Decimal("0.01"),

        "entry_price": Decimal("100"),

        "stop_loss": Decimal("99"),

        "risk_amount": Decimal("0.25"),

    }

    values.update(overrides)

    return TradeProposal(**values)

def assessment_for(item, **overrides):

    values = {

        "capital": Decimal("50"),

        "daily_loss_pct": Decimal("0"),

        "drawdown_pct": Decimal("0"),

        "volatility_pct": Decimal("1"),

        "reviewer_id": "controle_risque",

    }

    values.update(overrides)

    return evaluate_risk(item, **values)

class GovernanceTests(unittest.TestCase):

    def test_valid_proposal(self):

        item = proposal()

        risk = assessment_for(item)

        self.assertTrue(risk.approved)

        decision = make_final_decision(

            item, risk, AUTHORIZED, AUTHORIZED,

            True, "Validation de test"

        )

        authorization = authorize_execution(

            item, risk, decision, AUTHORIZED

        )

        self.assertEqual(

            authorization.decision_maker_id, AUTHORIZED

        )

    def test_unauthorized_agent(self):

        item = proposal()

        risk = assessment_for(item)

        with self.assertRaises(PermissionError):

            make_final_decision(

                item, risk, "agent_technique",

                AUTHORIZED, True, "Tentative"

            )

    def test_risk_veto(self):

        item = proposal(risk_amount=Decimal("1"))

        risk = assessment_for(item)

        self.assertFalse(risk.approved)

        with self.assertRaises(PermissionError):

            make_final_decision(

                item, risk, AUTHORIZED,

                AUTHORIZED, True, "Doit être bloqué"

            )

    def test_invalid_stop_loss(self):

        item = proposal(stop_loss=Decimal("100"))

        risk = assessment_for(item)

        self.assertFalse(risk.approved)

    def test_daily_loss_limit(self):

        item = proposal()

        risk = assessment_for(

            item, daily_loss_pct=Decimal("3.0")

        )

        self.assertFalse(risk.approved)

    def test_drawdown_limit(self):

        item = proposal()

        risk = assessment_for(

            item, drawdown_pct=Decimal("10.0")

        )

        self.assertFalse(risk.approved)

    def test_volatility_limit(self):

        item = proposal()

        risk = assessment_for(

            item, volatility_pct=Decimal("5.0")

        )

        self.assertFalse(risk.approved)

    def test_rejected_decision(self):

        item = proposal()

        risk = assessment_for(item)

        decision = make_final_decision(

            item, risk, AUTHORIZED,

            AUTHORIZED, False, "Refus volontaire"

        )

        self.assertEqual(

            decision.status, DecisionStatus.REJECTED

        )

        with self.assertRaises(PermissionError):

            authorize_execution(

                item, risk, decision, AUTHORIZED

            )

    def test_mismatched_assessment(self):

        item = proposal()

        other = proposal(proposal_id="TEST-002")

        risk = assessment_for(other)

        with self.assertRaises(PermissionError):

            make_final_decision(

                item, risk, AUTHORIZED,

                AUTHORIZED, True, "Mauvaise correspondance"

            )

if __name__ == "__main__":

    unittest.main()