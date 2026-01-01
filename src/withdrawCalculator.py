# withdrawCalculator.py

import math
import json


def calculate_v3_withdrawal(
    delta_L: float,
    sqrt_price_current: float,
    sqrt_price_lower: float,
    sqrt_price_upper: float
) -> dict:
    """
    Calculates the principal token amounts returned when burning delta_L liquidity
    in a Uniswap v3 position.
    
    Parameters:
    - delta_L: amount of liquidity to burn (positive float)
    - sqrt_price_current: current sqrt(P) where P = price of token1 in token0
    - sqrt_price_lower: lower bound of position sqrt(P_l)
    - sqrt_price_upper: upper bound of position sqrt(P_u)
    
    Returns a dict with amounts and description of the situation.
    
    Note: This ignores accrued fees (fees are calculated separately in v3).
          Uses float for simplicity — in production you'd use fixed-point ints
          like the contracts do (Q64.96 format) to avoid precision errors.
    """
    if sqrt_price_current <= sqrt_price_lower:
        amount_token0 = 0.0
        amount_token1 = delta_L * (sqrt_price_upper - sqrt_price_lower)
        situation = "Current price <= lower bound -> receive only token1"
        
    elif sqrt_price_current >= sqrt_price_upper:
        amount_token0 = delta_L * (1 / sqrt_price_lower - 1 / sqrt_price_upper)
        amount_token1 = 0.0
        situation = "Current price >= upper bound -> receive only token0"
        
    else:
        amount_token0 = delta_L * (1 / sqrt_price_current - 1 / sqrt_price_upper)
        amount_token1 = delta_L * (sqrt_price_current - sqrt_price_lower)
        situation = "Current price inside range -> receive both tokens"
    
    return {
        "amount_token0": amount_token0,
        "amount_token1": amount_token1,
        "situation": situation
    }


if __name__ == '__main__':
    result = calculate_v3_withdrawal(
        delta_L=1_000_000,
        sqrt_price_current=20.0,
        sqrt_price_lower=31.62,
        sqrt_price_upper=63.25
    )

    print(json.dumps(result, indent=4))
