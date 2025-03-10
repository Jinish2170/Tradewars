# Configuration Module (config.py)

# Team count
TEAM_COUNT = 11  # Changed from 5 to 11

# Starting budget
STARTING_BUDGET = 100000

# Stock parameters (abstract details)
INITIAL_PRICE = 100
AVAILABLE_QUANTITY = 1000
MARKET_CAP = 1000000

# Pricing coefficients
DEMAND_COEFFICIENT = 0.1
EVENT_COEFFICIENT = 0.2
RANDOM_NOISE = 0.05

# IPO stock parameters
IPO_INITIAL_PRICE = 50
IPO_AVAILABLE_QUANTITY = 500
IPO_MARKET_CAP = 500000

# Price Fluctuation Settings
PRICE_FLUCTUATION = {
    'DEFAULT': {
        'MIN_CHANGE': -0.03,  # -3%
        'MAX_CHANGE': 0.03,   # +3%
        'UPDATE_INTERVAL': 2,  # seconds
    },
    'TECH': {  # Example of stock-specific settings
        'MIN_CHANGE': -0.04,  # More volatile
        'MAX_CHANGE': 0.04,
    }
}

# Export configuration dictionary (if needed elsewhere)
CONFIG = {
    'TEAM_COUNT': TEAM_COUNT,
    'STARTING_BUDGET': STARTING_BUDGET,
    'INITIAL_PRICE': INITIAL_PRICE,
    'AVAILABLE_QUANTITY': AVAILABLE_QUANTITY,
    'MARKET_CAP': MARKET_CAP,
    'DEMAND_COEFFICIENT': DEMAND_COEFFICIENT,
    'EVENT_COEFFICIENT': EVENT_COEFFICIENT,
    'RANDOM_NOISE': RANDOM_NOISE,
    'IPO_INITIAL_PRICE': IPO_INITIAL_PRICE,
    'IPO_AVAILABLE_QUANTITY': IPO_AVAILABLE_QUANTITY,
    'IPO_MARKET_CAP': IPO_MARKET_CAP,
    'PRICE_FLUCTUATION': PRICE_FLUCTUATION,
}

# Make all variables available when importing
__all__ = [
    'TEAM_COUNT', 'STARTING_BUDGET', 'INITIAL_PRICE', 'AVAILABLE_QUANTITY',
    'MARKET_CAP', 'DEMAND_COEFFICIENT', 'EVENT_COEFFICIENT', 'RANDOM_NOISE',
    'IPO_INITIAL_PRICE', 'IPO_AVAILABLE_QUANTITY', 'IPO_MARKET_CAP', 'CONFIG'
]
