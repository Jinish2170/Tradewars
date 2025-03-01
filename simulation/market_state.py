import time
from utils.logger import logger
from utils.decorators import safe_operation
from config import INITIAL_PRICE, AVAILABLE_QUANTITY, TEAM_COUNT, STARTING_BUDGET
from data.db import db

# Initialize empty containers without data
stock_prices = {}
available_quantities = {}
order_logs = []
team_portfolios = {}
last_prices = {}
trading_volume = {}
price_history = {}

def initialize_market():
    """Set up initial market data."""
    global stock_prices, available_quantities, trading_volume, last_prices, team_portfolios, price_history
    
    # Clear any existing data
    stock_prices.clear()
    available_quantities.clear()
    trading_volume.clear()
    last_prices.clear()
    team_portfolios.clear()
    price_history.clear()
    
    # Initialize example stocks with their initial data
    initial_stocks = {
        'TECH': {'price': 100, 'quantity': 1000},
        'BANK': {'price': 50, 'quantity': 2000},
        'AUTO': {'price': 75, 'quantity': 1500},
    }
    
    for symbol, data in initial_stocks.items():
        stock_prices[symbol] = data['price']
        available_quantities[symbol] = data['quantity']
        last_prices[symbol] = data['price']
        trading_volume[symbol] = 0
    
    # Initialize team portfolios with starting budget
    for i in range(TEAM_COUNT):
        team_portfolios[i] = {
            'cash': STARTING_BUDGET,
            'holdings': {},
            'transactions': [],
            'holdings_value': 0,
            'total_value': STARTING_BUDGET
        }
    
    price_history = {stock: [] for stock in stock_prices.keys()}
    
    logger.info(f"Market initialized with {len(initial_stocks)} stocks and {TEAM_COUNT} teams")
    logger.info(f"Each team starting with ${STARTING_BUDGET:,.2f}")

def get_stock_prices():
    """Return current stock price data."""
    return stock_prices

def get_market_state():
    """Get complete market state."""
    return {
        'prices': stock_prices.copy(),
        'quantities': available_quantities.copy(),
        'volumes': trading_volume.copy(),
        'price_changes': {
            symbol: ((stock_prices[symbol] - last_prices[symbol]) / last_prices[symbol] * 100)
            for symbol in stock_prices
        }
    }

def get_market_health():
    """Calculate market health indicators"""
    global stock_prices, last_prices, trading_volume
    
    total_volume = sum(trading_volume.values())
    average_change = sum(
        ((stock_prices[s] - last_prices[s]) / last_prices[s])
        for s in stock_prices
    ) / len(stock_prices)
    
    volatility = sum(
        abs((stock_prices[s] - last_prices[s]) / last_prices[s])
        for s in stock_prices
    ) / len(stock_prices)
    
    return {
        'total_volume': total_volume,
        'average_change': average_change * 100,  # as percentage
        'volatility': volatility * 100,  # as percentage
        'active_stocks': len(stock_prices)
    }

def update_stock_price(stock, new_price, is_percent_change=False):
    """Update stock price and record the change"""
    global stock_prices, last_prices
    
    try:
        if stock not in stock_prices:
            logger.error(f"Invalid stock symbol: {stock}")
            return False
            
        current_price = stock_prices[stock]
        
        # Handle percentage change calculation
        if is_percent_change:
            new_price = current_price * (1 + new_price)
            
        if new_price <= 0:
            logger.error(f"Invalid price value: {new_price}")
            return False
        
        # Store the last price before updating
        last_prices[stock] = current_price
        
        # Update the price
        stock_prices[stock] = new_price
        
        # Calculate and log the price change
        price_change = ((new_price - current_price) / current_price) * 100
        logger.info(f"Price change: {stock} changed by {price_change:+.2f}% to ${new_price:.2f}")
        
        # Save the updated state
        save_market_state()
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating stock price: {str(e)}")
        return False

def save_market_state():
    """Save current market state to database"""
    try:
        db.save_market_state(stock_prices, available_quantities)
        # Add price history to saved state
        if len(price_history.get(stock, [])) > 100:
            price_history[stock] = price_history[stock][-100:]
        return True
    except Exception as e:
        logger.error(f"Error saving market state: {str(e)}")
        return False

@safe_operation
def process_market_order(team_id, order):
    """Process a market order with enhanced validation and feedback"""
    from simulation.market_simulation import market_session
    
    try:
        # Validate session state
        if not market_session.session_active:
            logger.error("Cannot process order: No active trading session")
            return False
        
        if market_session.pause_lock:
            logger.error("Cannot process order: Session is paused")
            return False
        
        # Validate order basics
        if not validate_order(order):
            logger.error(f"Invalid order format: {order}")
            return False
        
        stock = order['stock']
        quantity = order['quantity']
        order_type = order['type']
        current_price = stock_prices[stock]
        
        # Enhanced validation
        if quantity > available_quantities[stock] and order_type == 'buy':
            logger.error(f"Insufficient {stock} available: {available_quantities[stock]}")
            return False
            
        # Calculate execution details
        slippage = calculate_slippage(stock, quantity, order_type)
        price_impact = calculate_price_impact(stock, quantity, order_type)
        execution_price = current_price * (1 + price_impact) * (1 + slippage)
        
        # Validate final price
        if not is_price_acceptable(current_price, execution_price):
            logger.error(f"Price movement too large: {((execution_price/current_price)-1)*100:.1f}%")
            return False
        
        # Update the order
        order['price'] = execution_price
        order['slippage'] = slippage
        order['impact'] = price_impact
        
        # Execute the order
        if update_portfolio(team_id, order):
            # Update market state
            stock_prices[stock] = execution_price
            trading_volume[stock] = trading_volume.get(stock, 0) + quantity
            last_prices[stock] = current_price
            
            # Log success
            logger.info(f"Order executed: {order_type} {quantity} {stock} @ ${execution_price:.2f}")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Order processing error: {str(e)}")
        return False

def validate_order(order):
    """Validate order structure and parameters."""
    required_fields = ['stock', 'quantity', 'type']
    if not all(field in order for field in required_fields):
        return False
    
    if order['quantity'] <= 0:
        return False
    
    if order['type'] not in ['buy', 'sell']:
        return False
        
    if order['stock'] not in stock_prices:
        return False
    
    return True

def validate_team_order(team_id, order):
    """Validate if team can execute the order."""
    portfolio = team_portfolios[team_id]
    stock = order['stock']
    quantity = order['quantity']
    order_type = order['type']
    
    if order_type == 'buy':
        # Check if team has enough cash
        estimated_cost = stock_prices[stock] * quantity
        if portfolio['cash'] < estimated_cost:
            logger.warning(f"Team {team_id} has insufficient funds for order. Required: ${estimated_cost:,.2f}, Available: ${portfolio['cash']:,.2f}")
            return False
    
    elif order_type == 'sell':
        # Check if team has enough stocks to sell
        if stock not in portfolio['holdings'] or portfolio['holdings'][stock] < quantity:
            logger.warning(f"Team {team_id} has insufficient {stock} holdings for sell order")
            return False
    
    return True

def calculate_slippage(stock, quantity, order_type):
    """Calculate order slippage based on volume and liquidity."""
    daily_volume = trading_volume.get(stock, 1)
    order_ratio = quantity / daily_volume if daily_volume > 0 else 1
    
    # Base slippage increases with order size
    base_slippage = min(order_ratio * 0.01, 0.05)  # Max 5% slippage
    
    # Add market volatility factor
    volatility = abs(stock_prices[stock] - last_prices.get(stock, stock_prices[stock])) / stock_prices[stock]
    volatility_impact = volatility * 0.5
    
    total_slippage = base_slippage + volatility_impact
    
    # Slippage direction based on order type
    return total_slippage if order_type == 'buy' else -total_slippage

def is_price_acceptable(current_price, execution_price):
    """Check if execution price is within acceptable bounds."""
    price_change = abs(execution_price - current_price) / current_price
    MAX_PRICE_CHANGE = 0.25  # Increased from 0.1 to 0.25 (25% maximum allowed price change)
    
    return price_change <= MAX_PRICE_CHANGE

def calculate_price_impact(stock, quantity, order_type):
    """Calculate price impact based on order size relative to available quantity."""
    available = available_quantities[stock]
    impact_factor = quantity / available
    
    # Limit impact and adjust direction based on order type
    max_impact = 0.1  # Maximum 10% price impact
    impact = min(impact_factor, max_impact)
    
    return impact if order_type == 'buy' else -impact

def update_portfolio(team_id, order):
    """Process an order and update portfolio."""
    global stock_prices, available_quantities, trading_volume
    
    stock = order['stock']
    quantity = order['quantity']
    order_type = order['type']
    price = order['price']
    timestamp = time.time()
    
    if team_id not in team_portfolios:
        logger.error(f"Invalid team ID: {team_id}")
        return False
    
    portfolio = team_portfolios[team_id]
    order_value = price * quantity
    
    try:
        if order_type == 'buy':
            if portfolio['cash'] < order_value:
                logger.error(f"Team {team_id}: Insufficient funds for purchase")
                return False
            if available_quantities[stock] < quantity:
                logger.error(f"Insufficient {stock} quantity available in market")
                return False
            
            # Execute buy
            portfolio['cash'] -= order_value
            portfolio['holdings'][stock] = portfolio['holdings'].get(stock, 0) + quantity
            available_quantities[stock] -= quantity
        
        elif order_type == 'sell':
            if portfolio['holdings'].get(stock, 0) < quantity:
                logger.error(f"Team {team_id}: Insufficient {stock} holdings")
                return False
            
            # Execute sell
            portfolio['cash'] += order_value
            portfolio['holdings'][stock] -= quantity
            if portfolio['holdings'][stock] == 0:
                del portfolio['holdings'][stock]
            available_quantities[stock] += quantity
        
        # Record transaction with team details
        transaction = {
            'timestamp': timestamp,
            'team_id': team_id,
            'type': order_type,
            'stock': stock,
            'quantity': quantity,
            'price': price,
            'total_value': order_value
        }
        
        portfolio['transactions'].append(transaction)
        
        # Update trading volume and last price
        trading_volume[stock] = trading_volume.get(stock, 0) + quantity
        last_prices[stock] = stock_prices[stock]
        
        # Log to database with team information
        db.log_order(team_id, order, "executed")
        
        # Save portfolio snapshot
        portfolio_value = calculate_portfolio_value(team_id)
        db.save_portfolio_snapshot(
            team_id,
            portfolio['cash'],
            portfolio['holdings'],
            portfolio_value
        )
                
        logger.info(f"Team {team_id} portfolio updated successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error processing order for Team {team_id}: {str(e)}")
        db.log_order(team_id, order, f"failed: {str(e)}")
        return False

def calculate_portfolio_value(team_id):
    """Calculate total portfolio value for a team."""
    portfolio = team_portfolios[team_id]
    holdings_value = sum(
        stock_prices[stock] * quantity
        for stock, quantity in portfolio['holdings'].items()
    )
    return portfolio['cash'] + holdings_value

def get_team_portfolio(team_id):
    """Get detailed portfolio information for a team."""
    if team_id not in team_portfolios:
        raise ValueError(f"Invalid team ID: {team_id}")
    
    portfolio = team_portfolios[team_id]
    holdings_value = sum(
        stock_prices[stock] * quantity
        for stock, quantity in portfolio['holdings'].items()
    )
    
    return {
        'cash': portfolio['cash'],
        'holdings': portfolio['holdings'].copy(),
        'holdings_value': holdings_value,
        'total_value': portfolio['cash'] + holdings_value,
        'transactions': portfolio['transactions'][-10:]  # Last 10 transactions
    }

def transfer_stock(from_team, to_team, stock, quantity):
    """Transfer stock between teams."""
    if from_team not in team_portfolios or to_team not in team_portfolios:
        raise ValueError("Invalid team ID")
    
    from_portfolio = team_portfolios[from_team]
    to_portfolio = team_portfolios[to_team]
    
    if stock not in from_portfolio['holdings'] or from_portfolio['holdings'][stock] < quantity:
        raise ValueError("Insufficient stock holdings")
    
    # Execute transfer
    from_portfolio['holdings'][stock] -= quantity
    to_portfolio['holdings'][stock] = to_portfolio['holdings'].get(stock, 0) + quantity
    
    # Clean up empty holdings
    if from_portfolio['holdings'][stock] == 0:
        del from_portfolio['holdings'][stock]
    
    # Record transaction for both teams
    timestamp = time.time()
    price = stock_prices[stock]
    
    from_portfolio['transactions'].append({
        'timestamp': timestamp,
        'type': 'transfer_out',
        'stock': stock,
        'quantity': quantity,
        'price': price,
        'counterparty': to_team
    })
    
    to_portfolio['transactions'].append({
        'timestamp': timestamp,
        'type': 'transfer_in',
        'stock': stock,
        'quantity': quantity,
        'price': price,
        'counterparty': from_team
    })
    
    return True

def reset_team_portfolio(team_id):
    """Reset a team's portfolio to initial state."""
    if team_id in team_portfolios:
        team_portfolios[team_id] = {
            'cash': STARTING_BUDGET,
            'holdings': {},
            'transactions': []
        }
        return True
    return False

def admin_place_order(team_id, stock, quantity, order_type, admin_key=None):
    """Process admin-placed orders for teams with validation"""
    # Validate admin privileges
    if admin_key != "admin123":  # Simple validation - should be more secure in production
        logger.error("Unauthorized admin order attempt")
        return False

    # Remove direct session check
    # Instead, implement a function to check session status
    if not is_trading_active():
        logger.error("Cannot place order: No active trading session")
        return False

    # Ensure team exists and initialize if needed
    if team_id not in team_portfolios:
        logger.error(f"Invalid team ID: {team_id}")
        return False

    order = {
        'stock': stock,
        'quantity': quantity,
        'type': order_type,
        'timestamp': time.time(),
        'admin_placed': True
    }

    # Validate and process the order
    if validate_order(order):
        # For admin orders, skip team order validation
        return process_market_order(team_id, order)
    return False

def is_trading_active():
    """Check if trading is currently active"""
    # This can be enhanced with more sophisticated checks
    return True  # Default to True for now

def get_session_summary(team_id):
    """Get team's performance summary for current session"""
    portfolio = get_team_portfolio(team_id)
    initial_value = STARTING_BUDGET
    current_value = portfolio['total_value']
    profit_loss = current_value - initial_value
    
    return {
        'team_id': team_id,
        'initial_value': initial_value,
        'current_value': current_value,
        'profit_loss': profit_loss,
        'profit_loss_percentage': (profit_loss / initial_value) * 100,
        'cash': portfolio['cash'],
        'holdings': portfolio['holdings'],
    }
