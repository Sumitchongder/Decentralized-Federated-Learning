def encode_update_tx(client_id: str, round_number: int, cid: str):
    """
    Encode a model update as a transaction payload
    """
    return {
        "from": client_id,
        "round": round_number,
        "cid": cid
    }
