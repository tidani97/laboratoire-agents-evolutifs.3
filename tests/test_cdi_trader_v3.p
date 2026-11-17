

import unittest

from simulations import cdi_trader_03 as trader

from agents.cdi_memory_bridge_v2 import (

    reset_memory_buffer,

    flush_memory,

)

class TestCDITraderV3(unittest.TestCase):

    def setUp(self):

        reset_memory_buffer()

        self.original_rounds = trader.ROUNDS

        trader.ROUNDS = 20

    def tearDown(self):

        trader.ROUNDS = self.original_rounds

        reset_memory_buffer()

    def test_simulation_runs_with_signed_authorizations(self):

        system, history = trader.run_simulation(2026, 1)

        self.assertEqual(len(history), 20)

        self.assertGreater(system["capital"], 0)

        self.assertEqual(

            system["trades"],

            sum(1 for item in history if item["authorized"])

        )

        self.assertEqual(

            system["signed_authorizations"],

            system["trades"]

        )

        self.assertTrue(

            all(

                item["authorized"] or item["pnl"] == 0.0

                for item in history

            )

        )

        saved = flush_memory()

        self.assertEqual(saved, 80)

if __name__ == "__main__":

    unittest.main()