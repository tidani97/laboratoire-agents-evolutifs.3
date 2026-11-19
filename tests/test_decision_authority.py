import unittest

from integrations.decision_authority import validate_decision

class TestDecisionAuthority(unittest.TestCase):

    def test_authorized_decider_can_approve_simulation(self):

        self.assertTrue(

            validate_decision(

                agent_id="CDI_DECIDER",

                decision="SIMULATION_APPROVED",

            )

        )

    def test_analyst_cannot_decide(self):

        with self.assertRaises(PermissionError):

            validate_decision(

                agent_id="CDI_ANALYST",

                decision="SIMULATION_APPROVED",

            )

    def test_critic_cannot_decide(self):

        with self.assertRaises(PermissionError):

            validate_decision(

                agent_id="CDI_CRITIC",

                decision="REJECTED",

            )

    def test_real_execution_is_rejected(self):

        with self.assertRaises(ValueError):

            validate_decision(

                agent_id="CDI_DECIDER",

                decision="EXECUTE",

            )

if __name__ == "__main__":

    unittest.main()