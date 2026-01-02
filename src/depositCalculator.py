# depositCalculator.py

import math
import json


def calculate_v3_deposit(
    amount_base: float,
    price_lower: float,
    price_upper: float,
    current_price: float
) -> dict:
    """
    Calculates the liquidity (L) minted and token amounts when depositing a fixed amount
    of base_token (cbBTC), swapping some of it to quote_token (WETH) at the current price
    (no fees/slippage assumed) to exactly match the ratio required for the specified price range
    in the Uniswap v3 cbBTC/WETH pool on Base.

    The price inputs are in "quote per base" terms (WETH per cbBTC), matching the
    "base_token_price_quote_token" field in common pool data APIs.

    Parameters:
    - amount_base: amount of cbBTC to fully use for the position
    - price_lower: lower bound of the price range (WETH per cbBTC)
    - price_upper: upper bound of the price range (WETH per cbBTC, must be > price_lower)
    - current_price: current price (WETH per cbBTC)

    Returns a dict with liquidity minted, amounts provided to the pool, etc.

    Note: Uses float for simplicity — in production use fixed-point to match contracts.
          Ignores fees (fees are earned separately in v3).
    """
    if price_lower >= price_upper:
        raise ValueError("price_lower must be less than price_upper")

    # Convert displayed prices (WETH per cbBTC) to Uniswap sqrt prices
    sqrt_price_lower = 1 / math.sqrt(price_upper)
    sqrt_price_upper = 1 / math.sqrt(price_lower)
    sqrt_price_current = 1 / math.sqrt(current_price)

    if sqrt_price_current <= sqrt_price_lower:
        # Current price >= price_upper → position is "below" current price
        # Provide only base_token (cbBTC)
        liquidity = amount_base / (sqrt_price_upper - sqrt_price_lower)
        base_to_pool = amount_base
        quote_to_pool = 0.0
        base_swapped = 0.0
        situation = "current price ≥ upper bound -> provide only cbBTC"

    elif sqrt_price_current >= sqrt_price_upper:
        # Current price <= price_lower → position is "above" current price
        # Provide only quote_token (WETH) → swap all cbBTC to WETH
        quote_to_pool = amount_base * current_price
        liquidity = quote_to_pool / (1 / sqrt_price_lower - 1 / sqrt_price_upper)
        base_to_pool = 0.0
        base_swapped = amount_base
        situation = "current price ≤ lower bound -> provide only WETH"

    else:
        # Current price inside range → provide both tokens
        term_base = sqrt_price_current - sqrt_price_lower
        term_quote = (1 / sqrt_price_current - 1 / sqrt_price_upper) / current_price
        liquidity = amount_base / (term_base + term_quote)

        base_to_pool = liquidity * term_base
        quote_to_pool = liquidity * (1 / sqrt_price_current - 1 / sqrt_price_upper)
        base_swapped = quote_to_pool / current_price
        situation = "current price inside range -> provide both tokens"

    return {
        "liquidity": liquidity,
        "cbBTC_to_pool": base_to_pool,
        "WETH_to_pool": quote_to_pool,
        "cbBTC_swapped_to_WETH": base_swapped,
        "total_cbBTC_used": base_to_pool + base_swapped,
        "situation": situation
    }


if __name__ == '__main__':
    # Example using values similar to your JSON data
    result = calculate_v3_deposit(
        amount_base=1.0,                  # e.g., deposit 1 cbBTC
        price_lower=25.0,                 # range: 25–35 WETH per cbBTC
        price_upper=35.0,
        current_price=29.428922053        # from your JSON
    )
    print(json.dumps(result, indent=4))
