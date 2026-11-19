

"""CDI-TRADER - Simulation du TP hybride V1."""

from corrections.cdi_trade_management_v1 import (

    simulate_policy_scenarios,

)

def run_simulation():

    results = simulate_policy_scenarios()

    print("=== CDI-TRADER TP HYBRIDE V1 ===")

    for name, value in results.items():

        print(f"{name}: {value}")

    assert results["initial_risk"] == "2"

    assert results["tp_initial"] == "96"

    assert results["tp_rapproche"] == "98"

    assert results["session_bloquee"] is True

    assert results["reprise_apres_revue"] is True

    assert results["cloture_apres_revue"] is True

    assert results["stop_inchange"] is True

    assert results["quantite_inchangee"] is True

    print("\nRESULTAT : SIMULATION VALIDEE")

if __name__ == "__main__":

    run_simulation()