

import unittest

from decimal import Decimal

from corrections.cdi_trade_management_v1 import (

    Side,

    TradeStatus,

    open_trade,

    update_take_profit,

    update_stop_loss,

    reduce_quantity,

    on_session_change,

    resolve_session_review,

    simulate_policy_scenarios,

)

class TestCDITradeManagementV1(unittest.TestCase):

    def setUp(self):

        self.sell = open_trade(

            Side.SELL,

            Decimal("100"),

            Decimal("102"),

            Decimal("96"),

            Decimal("1"),

            session_id="Europe",

        )

        self.buy = open_trade(

            Side.BUY,

            Decimal("100"),

            Decimal("98"),

            Decimal("104"),

            Decimal("1"),

            session_id="Europe",

        )

    def test_sell_tp_can_only_be_tightened(self):

        updated = update_take_profit(

            self.sell, Decimal("98")

        )

        self.assertEqual(updated.take_profit, Decimal("98"))

        with self.assertRaises(PermissionError):

            update_take_profit(

                self.sell, Decimal("94")

            )

    def test_buy_tp_can_only_be_tightened(self):

        updated = update_take_profit(

            self.buy, Decimal("102")

        )

        self.assertEqual(updated.take_profit, Decimal("102"))

        with self.assertRaises(PermissionError):

            update_take_profit(

                self.buy, Decimal("106")

            )

    def test_stop_loss_cannot_be_widened(self):

        updated = update_stop_loss(

            self.sell, Decimal("101")

        )

        self.assertEqual(updated.stop_loss, Decimal("101"))

        with self.assertRaises(PermissionError):

            update_stop_loss(

                self.sell, Decimal("103")

            )

        with self.assertRaises(PermissionError):

            update_stop_loss(

                self.buy, Decimal("97")

            )

    def test_quantity_can_only_decrease(self):

        updated = reduce_quantity(

            self.sell, Decimal("0.5")

        )

        self.assertEqual(updated.quantity, Decimal("0.5"))

        with self.assertRaises(PermissionError):

            reduce_quantity(

                self.sell, Decimal("1.1")

            )

    def test_session_change_requires_review(self):

        waiting = on_session_change(

            self.sell, "New_York"

        )

        self.assertEqual(

            waiting.status,

            TradeStatus.REVIEW_REQUIRED

        )

        with self.assertRaises(PermissionError):

            update_take_profit(

                waiting, Decimal("99")

            )

        resumed = resolve_session_review(

            waiting, "continue", "New_York"

        )

        self.assertEqual(

            resumed.status, TradeStatus.OPEN

        )

    def test_session_can_be_closed_after_review(self):

        waiting = on_session_change(

            self.sell, "New_York"

        )

        closed = resolve_session_review(

            waiting, "close"

        )

        self.assertEqual(

            closed.status, TradeStatus.CLOSED

        )

        with self.assertRaises(PermissionError):

            update_stop_loss(

                closed, Decimal("101")

            )

    def test_initial_risk_is_preserved(self):

        updated = update_take_profit(

            self.sell, Decimal("98")

        )

        self.assertEqual(

            self.sell.initial_risk, Decimal("2")

        )

        self.assertEqual(

            updated.initial_risk,

            self.sell.initial_risk

        )

    def test_invalid_order_geometry_rejected(self):

        with self.assertRaises(ValueError):

            open_trade(

                Side.SELL,

                Decimal("100"),

                Decimal("99"),

                Decimal("96"),

                Decimal("1"),

            )

    def test_deterministic_simulation(self):

        result = simulate_policy_scenarios()

        self.assertTrue(result["session_bloquee"])

        self.assertTrue(result["reprise_apres_revue"])

        self.assertTrue(result["cloture_apres_revue"])

        self.assertTrue(result["stop_inchange"])

        self.assertTrue(result["quantite_inchangee"])

if __name__ == "__main__":

    unittest.main()