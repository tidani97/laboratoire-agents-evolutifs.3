

import unittest

from dataclasses import replace

from decimal import Decimal

from corrections.cdi_governance_v3 import (

    CDITradingGovernance,

    TradeProposal,

    Direction,

    verify_authorization,

)

class TestCDIGovernanceV3(unittest.TestCase):

    def setUp(self):

        self.secret = b"CDI_TEST_SECRET_KEY_2026_32_BYTES!!"

        self.gov = CDITradingGovernance(

            authorized_decider_id="CDI_MASTER",

            secret_key=self.secret,

        )

        self.proposal = TradeProposal(

            proposal_id="TEST-001",

            agent_id="AGENT-01",

            symbol="BTCUSD",

            direction=Direction.BUY,

            quantity=Decimal("0.01"),

            entry_price=Decimal("100"),

            stop_loss=Decimal("99"),

        )

    def assessment(self, proposal=None):

        return self.gov.evaluate_risk(

            proposal or self.proposal,

            capital=Decimal("50"),

            daily_loss_pct=Decimal("0"),

            drawdown_pct=Decimal("0"),

            volatility_pct=Decimal("1"),

            reviewer_id="RISK-01",

        )

    def test_valid_transaction(self):

        assessment = self.assessment()

        decision = self.gov.make_final_decision(

            self.proposal,

            assessment,

            "CDI_MASTER",

            True,

            "Risk acceptable.",

        )

        authorization = self.gov.authorize_execution(

            self.proposal,

            assessment,

            decision,

        )

        self.assertTrue(

            verify_authorization(authorization, self.secret)

        )

    def test_excessive_risk_rejected(self):

        risky = replace(

            self.proposal,

            quantity=Decimal("1"),

        )

        assessment = self.assessment(risky)

        self.assertFalse(assessment.approved)

        with self.assertRaises(PermissionError):

            self.gov.make_final_decision(

                risky,

                assessment,

                "CDI_MASTER",

                True,

                "Should be blocked.",

            )

    def test_unauthorized_decider_rejected(self):

        assessment = self.assessment()

        with self.assertRaises(PermissionError):

            self.gov.make_final_decision(

                self.proposal,

                assessment,

                "FAKE_MASTER",

                True,

                "Unauthorized.",

            )

    def test_forged_decision_rejected(self):

        assessment = self.assessment()

        decision = self.gov.make_final_decision(

            self.proposal,

            assessment,

            "CDI_MASTER",

            True,

            "Original decision.",

        )

        forged = replace(

            decision,

            reason="Forged decision.",

        )

        with self.assertRaises(PermissionError):

            self.gov.authorize_execution(

                self.proposal,

                assessment,

                forged,

            )

    def test_modified_proposal_rejected(self):

        assessment = self.assessment()

        modified = replace(

            self.proposal,

            quantity=Decimal("0.5"),

        )

        decision = self.gov.make_final_decision(

            self.proposal,

            assessment,

            "CDI_MASTER",

            True,

            "Approved.",

        )

        with self.assertRaises(PermissionError):

            self.gov.authorize_execution(

                modified,

                assessment,

                decision,

            )

if __name__ == "__main__":

    unittest.main()