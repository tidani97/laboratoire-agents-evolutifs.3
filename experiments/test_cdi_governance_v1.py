

import unittest

from agents.cdi_governance_v1 import (

    risk_agent,

    decisionnaire_proposal,

    validate_transaction,

)

class TestCDIGovernanceV1(unittest.TestCase):

    def test_risk_agent_can_authorize(self):

        approved, reason = risk_agent(

            capital=50,

            drawdown=0.01,

            daily_loss=0.005,

            volatility=0.01,

        )

        self.assertTrue(approved)

        self.assertEqual(reason, "risque_autorise")

    def test_risk_agent_vetoes_excessive_drawdown(self):

        approved, reason = risk_agent(

            capital=50,

            drawdown=0.05,

            daily_loss=0,

            volatility=0.01,

        )

        self.assertFalse(approved)

        self.assertEqual(reason, "limite_drawdown")

    def test_risk_agent_vetoes_daily_loss(self):

        approved, reason = risk_agent(

            capital=50,

            drawdown=0,

            daily_loss=0.02,

            volatility=0.01,

        )

        self.assertFalse(approved)

        self.assertEqual(reason, "limite_perte_journaliere")

    def test_risk_agent_vetoes_excessive_volatility(self):

        approved, reason = risk_agent(

            capital=50,

            drawdown=0,

            daily_loss=0,

            volatility=0.025,

        )

        self.assertFalse(approved)

        self.assertEqual(reason, "volatilite_excessive")

    def test_risk_agent_never_proposes_direction(self):

        result = risk_agent(50, 0, 0, 0.01)

        self.assertIsInstance(result[0], bool)

        self.assertNotIn(result[1], ("achat", "vente"))

    def test_decisionnaire_accepts_matching_proposals(self):

        self.assertEqual(

            decisionnaire_proposal("achat", "achat"),

            "achat",

        )

    def test_decisionnaire_abstains_on_conflict(self):

        self.assertEqual(

            decisionnaire_proposal("achat", "vente"),

            "abstention",

        )

    def test_decisionnaire_abstains_on_invalid_proposal(self):

        self.assertEqual(

            decisionnaire_proposal("achat", "incertain"),

            "abstention",

        )

    def test_risk_veto_blocks_transaction(self):

        self.assertFalse(

            validate_transaction("achat", False, 50)

        )

    def test_abstention_cannot_be_validated(self):

        self.assertFalse(

            validate_transaction("abstention", True, 50)

        )

    def test_valid_transaction_can_be_approved(self):

        self.assertTrue(

            validate_transaction("achat", True, 50)

        )

    def test_zero_capital_blocks_transaction(self):

        self.assertFalse(

            validate_transaction("vente", True, 0)

        )

if __name__ == "__main__":

    unittest.main()