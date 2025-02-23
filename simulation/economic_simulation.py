# Simulation Modules (simulation/economic_simulation.py)

import random

def simulate_periodic_adjustments(base_price, volatility):
    """Apply background adjustments to mimic real-world market fluctuations.

    Args:
        base_price (float): The initial price of the commodity.
        volatility (float): The percentage by which the price can fluctuate.

    Returns:
        float: The adjusted price after simulating market fluctuations.
    """
    price_change = random.uniform(-volatility, volatility)
    adjusted_price = base_price * (1 + price_change)
    return adjusted_price
