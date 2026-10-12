"""
unit.py: builds the fingerprint: a unique, reproducible identifier for
one specific API call, based on everything that could affect its result.
"""

import hashlib


def build_fingerprint(
    item_id: str,
    model_name: str,
    mutation_type: str,
    severity: str,
    seed: int,
    strategy: str,
    prompt_hash: str,
) -> str:
    """
    Builds a unique fingerprint from all inputs that could affect the result.
    Same inputs -> same fingerprint -> same call, safe to skip if already done.
    """

    input_data = "|".join(
        [
            item_id,
            model_name,
            mutation_type,
            severity,
            str(seed),
            strategy,
            prompt_hash,
        ]
    )

    return hashlib.sha256(input_data.encode("utf-8")).hexdigest()
