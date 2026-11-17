

"""

CDI GOVERNANCE V1

Separation stricte entre propositions, controle du risque

et validation finale par le decisionnaire.

"""

VALID_ACTIONS = ("achat", "vente")

def risk_agent(

    capital,

    drawdown,

    daily_loss,

    volatility,

    max_drawdown=0.05,

    max_daily_loss=0.02,

    max_volatility=0.025,

):

    """Le risque autorise ou oppose un veto. Il ne choisit pas la direction."""

    values = (

        capital, drawdown, daily_loss, volatility,

        max_drawdown, max_daily_loss, max_volatility,

    )

    if not all(isinstance(v, (int, float)) for v in values):

        return False, "donnees_invalides"

    if capital <= 0:

        return False, "capital_insuffisant"

    if drawdown >= max_drawdown:

        return False, "limite_drawdown"

    if daily_loss >= max_daily_loss:

        return False, "limite_perte_journaliere"

    if volatility >= max_volatility:

        return False, "volatilite_excessive"

    return True, "risque_autorise"

def decisionnaire_proposal(technical, economic):

    """Le decisionnaire confronte les propositions des deux analystes."""

    if technical not in VALID_ACTIONS:

        return "abstention"

    if economic not in VALID_ACTIONS:

        return "abstention"

    if technical == economic:

        return technical

    return "abstention"

def validate_transaction(decision, risk_approved, capital):

    """Seul le decisionnaire peut soumettre une decision a validation."""

    if not risk_approved:

        return False

    if decision not in VALID_ACTIONS:

        return False

    if not isinstance(capital, (int, float)) or capital <= 0:

        return False

    return True