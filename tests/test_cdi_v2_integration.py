

"""

CDI-TRADER V2

Tests d'intégration : gouvernance et optimisation.

Objectif :

- Vérifier l'autorité du décideur.

- Vérifier les blocages du contrôle de risque.

- Vérifier les autorisations finales.

- Vérifier l'isolation du module d'optimisation.

Exécution : python -m unittest discover -s tests -v

"""

import unittest

from decimal import Decimal

from corrections.cdi_governance_v2 import (

    Direction,

    DecisionStatus,

    TradeProposal,

    RiskAssessment,

    RiskPolicy,

    evaluate_risk,

    make_final_decision,

    authorize_execution,

)

from optimization.cdi_optimization_v1 import (

    PerformanceReport,

    analyze_performance,

    optimization_safety_check,

)

class TestCDIV2Integration(unittest.TestCase):

    def setUp(self):

        self.capital = Decimal("50")

        self.proposal = TradeProposal(

            proposal_id="CDI-001",

            agent_id="AGENT-TECH-01",

            symbol="BTCUSD",

            direction=Direction.BUY,

            quantity=Decimal("0.01"),

            entry_price=Decimal("90000"),

            stop_loss=Decimal("89000"),

            risk_amount=Decimal("0.50"),

        )

        self.assessment = evaluate_risk(

            proposal=self.proposal,

            capital=self.capital,

            daily_loss_pct=Decimal("0"),

            drawdown_pct=Decimal("0"),

            volatility_pct=Decimal("1"),

            reviewer_id="RISK-01",

        )

    def test_01_unauthorized_decider_is_rejected(self):

        with self.assertRaises(PermissionError):

            make_final_decision(

                proposal=self.proposal,

                assessment=self.assessment,

                decision_maker_id="AGENT-TECH-01",

                authorized_decider_id="CDI-DECIDER",

                approve=True,

                reason="Test unauthorized",

            )

    def test_02_risk_rejection_blocks_trade(self):

        rejected_assessment = evaluate_risk(

            proposal=self.proposal,

            capital=self.capital,

            daily_loss_pct=Decimal("3"),

            drawdown_pct=Decimal("0"),

            volatility_pct=Decimal("1"),

            reviewer_id="RISK-01",

        )

        self.assertFalse(rejected_assessment.approved)

        with self.assertRaises(PermissionError):

            make_final_decision(

                proposal=self.proposal,

                assessment=rejected_assessment,

                decision_maker_id="CDI-DECIDER",

                authorized_decider_id="CDI-DECIDER",

                approve=True,

                reason="Test risk rejection",

            )

    def test_03_rejected_final_decision_blocks_execution(self):

        decision = make_final_decision(

            proposal=self.proposal,

            assessment=self.assessment,

            decision_maker_id="CDI-DECIDER",

            authorized_decider_id="CDI-DECIDER",

            approve=False,

            reason="Conditions not satisfactory",

        )

        self.assertEqual(decision.status, DecisionStatus.REJECTED)

        with self.assertRaises(PermissionError):

            authorize_execution(

                proposal=self.proposal,

                assessment=self.assessment,

                decision=decision,

                authorized_decider_id="CDI-DECIDER",

            )

    def test_04_approved_trade_requires_all_validations(self):

        decision = make_final_decision(

            proposal=self.proposal,

            assessment=self.assessment,

            decision_maker_id="CDI-DECIDER",

            authorized_decider_id="CDI-DECIDER",

            approve=True,

            reason="Simulation approval",

        )

        authorization = authorize_execution(

            proposal=self.proposal,

            assessment=self.assessment,

            decision=decision,

            authorized_decider_id="CDI-DECIDER",

        )

        self.assertEqual(

            authorization.proposal_id,

            self.proposal.proposal_id,

        )

        self.assertEqual(

            authorization.direction,

            Direction.BUY,

        )

    def test_05_mismatched_proposal_is_rejected(self):

        other_proposal = TradeProposal(

            proposal_id="CDI-002",

            agent_id="AGENT-TECH-02",

            symbol="ETHUSD",

            direction=Direction.BUY,

            quantity=Decimal("0.01"),

            entry_price=Decimal("3000"),

            stop_loss=Decimal("2900"),

            risk_amount=Decimal("0.50"),

        )

        with self.assertRaises(PermissionError):

            make_final_decision(

                proposal=other_proposal,

                assessment=self.assessment,

                decision_maker_id="CDI-DECIDER",

                authorized_decider_id="CDI-DECIDER",

                approve=True,

                reason="Mismatch test",

            )

    def test_06_optimization_cannot_execute_trades(self):

        report = PerformanceReport(

            total_trades=10,

            winning_trades=7,

            losing_trades=3,

            total_profit=Decimal("15"),

            total_loss=Decimal("5"),

            max_drawdown_pct=Decimal("2"),

        )

        result = analyze_performance(report)

        self.assertFalse(result.execution_allowed)

    def test_07_protected_rules_cannot_be_modified(self):

        protected_rules = [

            "risk_limit",

            "stop_loss",

            "daily_loss_limit",

            "decision_authority",

            "capital_protection",

        ]

        for rule in protected_rules:

            with self.subTest(rule=rule):

                self.assertFalse(

                    optimization_safety_check(rule)

                )

    def test_08_optimization_can_analyze_performance(self):

        report = PerformanceReport(

            total_trades=10,

            winning_trades=6,

            losing_trades=4,

            total_profit=Decimal("12"),

            total_loss=Decimal("6"),

            max_drawdown_pct=Decimal("2"),

        )

        result = analyze_performance(report)

        self.assertEqual(

            result.win_rate_pct,

            Decimal("60"),

        )

        self.assertEqual(

            result.profit_factor,

            Decimal("2"),

        )

if __name__ == "__main__":

    unittest.main()