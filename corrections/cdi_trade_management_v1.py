

"""CDI-TRADER - Gestion hybride du TP avec protection stricte."""

from dataclasses import dataclass, replace

from decimal import Decimal

from enum import Enum

class Side(str, Enum):

    BUY = "BUY"

    SELL = "SELL"

class TradeStatus(str, Enum):

    OPEN = "OPEN"

    REVIEW_REQUIRED = "REVIEW_REQUIRED"

    CLOSED = "CLOSED"

@dataclass(frozen=True)

class TradeState:

    side: Side

    entry: Decimal

    stop_loss: Decimal

    take_profit: Decimal

    quantity: Decimal

    contract_size: Decimal

    session_id: str

    initial_risk: Decimal

    status: TradeStatus = TradeStatus.OPEN

    review_reason: str = ""

def positive(value, name):

    if not isinstance(value, Decimal):

        raise ValueError(f"{name} invalide.")

    if not value.is_finite() or value <= 0:

        raise ValueError(f"{name} doit être positif.")

def open_trade(side, entry, stop_loss, take_profit,

               quantity, contract_size=Decimal("1"),

               session_id="session_1"):

    if not isinstance(side, Side):

        raise ValueError("Sens invalide.")

    for value, name in [

        (entry, "entrée"),

        (stop_loss, "stop"),

        (take_profit, "TP"),

        (quantity, "quantité"),

        (contract_size, "contrat"),

    ]:

        positive(value, name)

    if not session_id:

        raise ValueError("Session obligatoire.")

    if side == Side.BUY:

        if not stop_loss < entry < take_profit:

            raise ValueError("Géométrie BUY invalide.")

    else:

        if not take_profit < entry < stop_loss:

            raise ValueError("Géométrie SELL invalide.")

    risk = abs(entry - stop_loss) * quantity * contract_size

    return TradeState(

        side, entry, stop_loss, take_profit,

        quantity, contract_size, session_id, risk

    )

def update_take_profit(state, proposed_tp):

    positive(proposed_tp, "TP")

    if state.status != TradeStatus.OPEN:

        raise PermissionError("Réévaluation obligatoire.")

    if state.side == Side.BUY:

        valid = state.entry < proposed_tp <= state.take_profit

    else:

        valid = state.take_profit <= proposed_tp < state.entry

    if not valid:

        raise PermissionError("Éloignement du TP interdit.")

    return replace(state, take_profit=proposed_tp)

def update_stop_loss(state, proposed_sl):

    positive(proposed_sl, "Stop")

    if state.status != TradeStatus.OPEN:

        raise PermissionError("Réévaluation obligatoire.")

    if state.side == Side.BUY:

        valid = state.stop_loss <= proposed_sl < state.entry

    else:

        valid = state.entry < proposed_sl <= state.stop_loss

    if not valid:

        raise PermissionError("Élargissement du stop interdit.")

    return replace(state, stop_loss=proposed_sl)

def reduce_quantity(state, new_quantity):

    positive(new_quantity, "Quantité")

    if state.status != TradeStatus.OPEN:

        raise PermissionError("Trade non modifiable.")

    if new_quantity > state.quantity:

        raise PermissionError("Augmentation interdite.")

    return replace(state, quantity=new_quantity)

def on_session_change(state, new_session_id):

    if not new_session_id:

        raise ValueError("Session obligatoire.")

    if state.status == TradeStatus.CLOSED:

        return state

    if new_session_id == state.session_id:

        return state

    return replace(

        state,

        status=TradeStatus.REVIEW_REQUIRED,

        review_reason="Changement de session : "

        + state.session_id + " -> " + new_session_id

    )

def resolve_session_review(state, decision, new_session_id=None):

    if state.status != TradeStatus.REVIEW_REQUIRED:

        raise PermissionError("Aucune revue en attente.")

    if decision == "close":

        return replace(state, status=TradeStatus.CLOSED)

    if decision == "continue":

        if not new_session_id:

            raise ValueError("Nouvelle session obligatoire.")

        return replace(

            state,

            session_id=new_session_id,

            status=TradeStatus.OPEN,

            review_reason=""

        )

    raise ValueError("Décision invalide.")

def simulate_policy_scenarios():

    trade = open_trade(

        Side.SELL,

        Decimal("100"),

        Decimal("102"),

        Decimal("96"),

        Decimal("1"),

        session_id="Europe"

    )

    tightened = update_take_profit(trade, Decimal("98"))

    waiting = on_session_change(tightened, "New_York")

    resumed = resolve_session_review(

        waiting, "continue", "New_York"

    )

    closed = resolve_session_review(

        on_session_change(resumed, "Asia"), "close"

    )

    return {

        "initial_risk": str(trade.initial_risk),

        "tp_initial": str(trade.take_profit),

        "tp_rapproche": str(tightened.take_profit),

        "session_bloquee": waiting.status == TradeStatus.REVIEW_REQUIRED,

        "reprise_apres_revue": resumed.status == TradeStatus.OPEN,

        "cloture_apres_revue": closed.status == TradeStatus.CLOSED,

        "stop_inchange": tightened.stop_loss == trade.stop_loss,

        "quantite_inchangee": tightened.quantity == trade.quantity

    }