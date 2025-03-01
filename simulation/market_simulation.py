from config import DEMAND_COEFFICIENT, EVENT_COEFFICIENT, RANDOM_NOISE, PRICE_FLUCTUATION
from . import market_state  # Changed this line
from data.db import db
from utils.logger import logger
from utils.decorators import safe_operation
import random
import math
import time
import threading
import logging
from PyQt5.QtCore import QTimer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MarketTrend:
    BULLISH = 1
    BEARISH = -1
    NEUTRAL = 0

class MarketSimulation:
    def __init__(self):
        self.state = {}  # example state container

    def inject_IPO(self, ipo_data):
        logging.info("Injecting IPO with data: %s", ipo_data)
        thread = threading.Thread(target=self._process_IPO, args=(ipo_data,))
        thread.start()

    def _process_IPO(self, ipo_data):
        logging.info("Processing IPO: %s", ipo_data)
        market_state.stock_prices[ipo_data['stock']] = ipo_data['initial_price']
        market_state.available_quantities[ipo_data['stock']] = ipo_data['available_quantity']
        db.log_event(
            event_type="ipo",
            description=f"IPO: {ipo_data['stock']}",
            affected_stocks=[ipo_data['stock']],
            impact=0
        )
        market_state.save_market_state()

    def inject_news_event(self, event_data):
        logging.info("Injecting news event with data: %s", event_data)
        thread = threading.Thread(target=self._process_news_event, args=(event_data,))
        thread.start()

    def _process_news_event(self, event_data):
        logging.info("Processing news event: %s", event_data)
        affected_stocks = event_data.get('stocks', [])
        impact = event_data.get('impact', 0)
        for stock in affected_stocks:
            if stock in market_state.stock_prices:
                current_price = market_state.stock_prices[stock]
                new_price = calculate_new_price(current_price, 0, impact)
                market_state.stock_prices[stock] = new_price
        db.log_event(
            event_type="news",
            description=event_data.get('description', ''),
            affected_stocks=affected_stocks,
            impact=impact
        )
        market_state.save_market_state()

# Module-level instance for backward compatibility
market_simulation = MarketSimulation()

# Market simulation state
current_trend = MarketTrend.NEUTRAL
volatility_factor = 1.0
market_sentiment = 0  # Range: -1 to 1

def calculate_new_price(old_price, net_demand, news_impact):
    """Enhanced price calculation with market depth and liquidity factors."""
    global volatility_factor, market_sentiment
    
    # Input validation and normalization
    old_price = max(0.01, old_price)
    net_demand = max(-1.0, min(1.0, net_demand))
    news_impact = max(-1.0, min(1.0, news_impact))
    
    # Enhanced market depth factor - exponential impact for larger orders
    depth_factor = math.exp(abs(net_demand)) - 1
    
    # Enhanced liquidity adjustment based on trading volume
    volume_factor = min(1.0, market_state.trading_volume.get(stock, 0) / 1000)
    liquidity_factor = 1.0 + (volatility_factor - 1.0) * 0.5 * (1 - volume_factor)
    
    # Calculate price pressure from order size
    price_pressure = net_demand * DEMAND_COEFFICIENT * depth_factor * liquidity_factor
    
    # Market momentum factor
    momentum = calculate_momentum(stock)
    
    # Enhanced market factors
    demand_impact = price_pressure * (1 + momentum)
    news_effect = news_impact * EVENT_COEFFICIENT * volatility_factor
    sentiment_impact = market_sentiment * 0.01 * volatility_factor
    
    # Dynamic volatility adjustment
    vol_modifier = 1.0 + (abs(net_demand) * volatility_factor * momentum)
    noise = (random.random() - 0.5) * RANDOM_NOISE * vol_modifier
    
    # Weighted impact calculation with dynamic weights
    weights = {
        'demand': 0.5 * liquidity_factor,  # Increased importance of demand
        'news': 0.2 * volatility_factor,
        'sentiment': 0.2,
        'noise': 0.1 * vol_modifier
    }
    
    # Normalize weights
    weight_sum = sum(weights.values())
    weights = {k: v/weight_sum for k, v in weights.items()}
    
    # Calculate total impact
    total_impact = (
        demand_impact * weights['demand'] +
        news_effect * weights['news'] +
        sentiment_impact * weights['sentiment'] +
        noise * weights['noise']
    )
    
    # Apply non-linear dampening for large movements
    if abs(total_impact) > 0.1:
        total_impact = math.copysign(math.log(1 + abs(total_impact)), total_impact)
    
    # Calculate new price with momentum consideration
    new_price = old_price * (1 + total_impact)
    
    # Apply circuit breakers
    max_change = 0.1 * (1 + volatility_factor)  # Dynamic circuit breaker
    if abs(new_price - old_price) / old_price > max_change:
        new_price = old_price * (1 + max_change * math.copysign(1, new_price - old_price))
    
    return max(0.01, new_price)

def calculate_momentum(stock):
    """Calculate price momentum for a stock"""
    if stock not in market_state.last_prices:
        return 0
    
    current_price = market_state.stock_prices[stock]
    last_price = market_state.last_prices[stock]
    
    # Calculate recent price trend
    price_change = (current_price - last_price) / last_price
    
    # Exponential smoothing of momentum
    momentum = math.copysign(math.sqrt(abs(price_change)), price_change)
    
    return momentum

def process_order(order):
    """Enhanced order processing with market impact"""
    stock = order['stock']
    quantity = order['quantity']
    order_type = order['type']
    
    # Get current market state
    current_price = market_state.stock_prices.get(stock, 0)
    available = market_state.available_quantities.get(stock, 0)
    
    # Calculate relative order size impact
    market_cap = current_price * available
    order_value = current_price * quantity
    size_impact = order_value / market_cap if market_cap > 0 else 0
    
    # Enhanced net demand calculation
    base_demand = (quantity / available) if available > 0 else 0
    net_demand = base_demand * (1 + size_impact)
    if order_type == 'sell':
        net_demand = -net_demand
    
    # Apply current market trend influence
    trend_impact = current_trend * 0.01 * (1 + abs(net_demand))
    
    # Calculate new price with market depth consideration
    new_price = calculate_new_price(
        current_price,
        net_demand,
        trend_impact
    )
    
    # Update market state
    market_state.stock_prices[stock] = new_price
    market_state.trading_volume[stock] = market_state.trading_volume.get(stock, 0) + quantity
    
    # Update volatility based on order impact
    global volatility_factor
    price_change = abs(new_price - current_price) / current_price
    volatility_factor = min(2.0, volatility_factor * (1 + price_change))
    
    # Save state changes
    market_state.save_market_state()
    
    return new_price

def update_market_conditions():
    """Periodically update market conditions."""
    global current_trend, volatility_factor, market_sentiment
    
    # Randomly shift market trend
    if random.random() < 0.1:  # 10% chance to change trend
        current_trend = random.choice([
            MarketTrend.BULLISH,
            MarketTrend.BEARISH,
            MarketTrend.NEUTRAL
        ])
    
    # Update volatility
    volatility_factor = max(0.5, min(2.0, volatility_factor + random.uniform(-0.1, 0.1)))
    
    # Update market sentiment
    market_sentiment = max(-1.0, min(1.0, market_sentiment + random.uniform(-0.1, 0.1)))

class PriceFluctuationManager:
    def __init__(self):
        self.last_update = {}
        self.stock_settings = {}
        self.initialize_settings()
    
    def initialize_settings(self):
        """Initialize settings for each stock"""
        default = PRICE_FLUCTUATION['DEFAULT']
        for stock in market_state.stock_prices.keys():
            self.last_update[stock] = time.time()
            # Use stock-specific settings if available, otherwise use default
            self.stock_settings[stock] = PRICE_FLUCTUATION.get(stock, default)
    
    @safe_operation
    def update_prices(self):
        """Update prices for all stocks based on their fluctuation settings"""
        current_time = time.time()
        
        for stock in market_state.stock_prices.keys():
            settings = self.stock_settings[stock]
            update_interval = settings.get('UPDATE_INTERVAL', 
                                        PRICE_FLUCTUATION['DEFAULT']['UPDATE_INTERVAL'])
            
            # Check if it's time to update this stock
            if current_time - self.last_update[stock] >= update_interval:
                self._fluctuate_stock_price(stock)
                self.last_update[stock] = current_time
    
    def _fluctuate_stock_price(self, stock):
        """Enhanced random price fluctuation with more unpredictable behavior"""
        settings = self.stock_settings[stock]
        
        # Increased randomness in price changes
        base_change = random.uniform(-0.015, 0.015)  # Wider range
        
        # Add random market shock events (5% chance)
        if random.random() < 0.05:
            shock_multiplier = random.choice([-2.5, -2.0, 2.0, 2.5])
            base_change *= shock_multiplier
        
        # Add occasional trend reversal
        if random.random() < 0.15:  # 15% chance of trend reversal
            base_change *= -1.5
        
        # Add some noise to prevent predictable patterns
        noise = random.gauss(0, 0.005)
        total_change = base_change + noise
        
        # Apply change to current price
        current_price = market_state.stock_prices[stock]
        new_price = current_price * (1 + total_change)
        
        # Ensure price doesn't change too dramatically
        max_change = 0.2  # 20% max change per update
        if abs(total_change) > max_change:
            total_change = math.copysign(max_change, total_change)
            new_price = current_price * (1 + total_change)
        
        market_state.stock_prices[stock] = max(0.01, new_price)
        
        # Safely update price history
        if not hasattr(market_state, 'price_history'):
            market_state.price_history = {}
        if stock not in market_state.price_history:
            market_state.price_history[stock] = []
        
        market_state.price_history[stock].append(new_price)
        if len(market_state.price_history[stock]) > 100:
            market_state.price_history[stock] = market_state.price_history[stock][-100:]
        
        # Log significant changes
        if abs(total_change) > 0.02:
            logger.info(f"Significant price change for {stock}: {total_change*100:.2f}%")

class MarketSession:
    def __init__(self):
        self.start_time = None
        self.is_active = False
        self.session_active = False
        self.tick_count = 0
        self.last_update = None
        self.price_manager = None
        self.pause_lock = False
        self.current_session = 0
        self.max_sessions = 6
        self.last_price_update = None
        self.price_update_interval = 1.0
        self.initial_prices = {}
        self.initialized = False  # Add flag to track if market is initialized
        self.session_duration = 600  # 10 minutes in seconds
        self.time_remaining = self.session_duration
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_session_time)
        self.timer.setInterval(1000)  # Update every second

    def initialize_session(self):
        """Always initialize market state properly"""
        from simulation import market_state
        
        # Initialize market state first
        market_state.initialize_market()
        logger.info("Market state initialized with stocks: " + ", ".join(market_state.stock_prices.keys()))
        
        # Store initial prices as reference
        self.initial_prices = market_state.stock_prices.copy()
        
        # Set initialized flag
        self.initialized = True
        
        logger.info("Market initialized - ready for session start")

    def start_session(self):
        """Enhanced session start with timer"""
        if self.session_active:
            logger.warning("A session is already active")
            return False
            
        try:
            # Reset session parameters
            self.current_session += 1
            self.start_time = time.time()
            self.last_update = self.start_time
            self.last_price_update = self.start_time
            self.tick_count = 0
            self.pause_lock = False
            
            # Reset and start timer
            self.time_remaining = self.session_duration
            self.timer.start()
            
            # Initialize price manager if needed
            if not self.price_manager:
                self.price_manager = PriceFluctuationManager()
            
            # Activate session
            self.session_active = True
            self.is_active = True
            
            logger.info(f"Trading Session {self.current_session} started - Duration: 10 minutes")
            return True
            
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            self.session_active = False
            self.is_active = False
            return False

    def update_session_time(self):
        """Update session countdown timer"""
        if not self.session_active or self.pause_lock:
            return

        self.time_remaining -= 1
        
        # Log time remaining at certain intervals
        if self.time_remaining in [300, 180, 60, 30, 10]:  # 5min, 3min, 1min, 30s, 10s
            mins = self.time_remaining // 60
            secs = self.time_remaining % 60
            logger.info(f"Session time remaining: {mins}:{secs:02d}")
            
        # End session when time runs out
        if self.time_remaining <= 0:
            logger.info("Session time expired")
            self.end_session()

    def end_session(self):
        """Enhanced session end with timer cleanup"""
        if not self.session_active:
            logger.warning("No active session to end")
            return False
            
        try:
            # Stop the timer
            self.timer.stop()
            self.time_remaining = self.session_duration
            
            # End session
            self.session_active = False
            self.is_active = False
            self.pause_lock = True
            
            # Save final state of current session
            for team_id in range(market_state.TEAM_COUNT):
                portfolio = market_state.get_team_portfolio(team_id)
                if portfolio:
                    db.save_portfolio_snapshot(
                        team_id,
                        portfolio['cash'],
                        portfolio['holdings'],
                        portfolio['total_value']
                    )
                    
            # Save final market state
            market_state.save_market_state()
            
            logger.info(f"Trading Session {self.current_session} ended successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return False

    def get_session_status(self):
        """Enhanced status with time remaining"""
        mins = self.time_remaining // 60
        secs = self.time_remaining % 60
        
        return {
            'current_session': self.current_session,
            'max_sessions': self.max_sessions,
            'is_active': self.session_active,
            'time_remaining': f"{mins}:{secs:02d}",
            'is_paused': self.pause_lock
        }

    @safe_operation
    def update(self):
        """Improved update logic with better session state checks"""
        # Don't update if session isn't properly started
        if not self.start_time or not self.session_active or not self.is_active or self.pause_lock:
            return
            
        current_time = time.time()
        
        # Only update if we're in an active session
        if self.session_active and not self.pause_lock:
            self.tick_count += 1
            
            # Update prices at regular intervals
            if current_time - self.last_price_update >= self.price_update_interval:
                self.update_market_conditions()
                self.price_manager.update_prices()
                self.last_price_update = current_time
                
                # Log market state periodically
                if self.tick_count % 60 == 0:
                    self.log_market_status()
    
    def pause(self):
        """Enhanced pause with timer pause"""
        if not self.session_active or self.pause_lock:
            return False
            
        self.pause_lock = True
        self.timer.stop()  # Pause the countdown
        logger.info("Session paused")
        return True
    
    def resume(self):
        """Enhanced resume with timer resume"""
        if not self.session_active or not self.pause_lock:
            return False
            
        self.pause_lock = False
        self.timer.start()  # Resume the countdown
        logger.info("Session resumed")
        return True
    
    def update_market_conditions(self):
        """Enhanced market conditions update with more dynamic factors"""
        from simulation import market_state
        
        for stock in market_state.stock_prices:
            # More dynamic base movement
            base_movement = random.gauss(0, 0.002)  # Normal distribution
            
            # Dynamic trend influence
            trend_strength = random.uniform(0.3, 1.0)
            trend_impact = current_trend * random.uniform(0.0003, 0.0008) * trend_strength
            
            # Enhanced volatility impact
            vol_impact = random.gauss(0, volatility_factor * 0.002)
            
            # Market sentiment influence
            sentiment_impact = market_sentiment * random.uniform(0.0002, 0.0005)
            
            # Combine all factors with random weights
            weights = [random.uniform(0.7, 1.3) for _ in range(4)]
            total_change = (
                base_movement * weights[0] +
                trend_impact * weights[1] +
                vol_impact * weights[2] +
                sentiment_impact * weights[3]
            )
            
            current_price = market_state.stock_prices[stock]
            new_price = current_price * (1 + total_change)
            market_state.stock_prices[stock] = max(0.01, new_price)
    
    def log_market_status(self):
        """Log current market status."""
        from simulation import market_state
        state = market_state.get_market_state()
        logger.info(f"Market Status - Tick {self.tick_count}")
        logger.info(f"Prices: {state['prices']}")
        logger.info(f"Volumes: {state['volumes']}")

    def process_market_order(self, team_id, order):
        """Enhanced order processing with better portfolio management"""
        portfolio = market_state.team_portfolios.get(team_id)
        if not portfolio:
            return False

        stock = order['stock']
        quantity = order['quantity']
        current_price = market_state.stock_prices.get(stock, 0)
        order_value = current_price * quantity

        if order['type'] == 'buy':
            if portfolio['cash'] < order_value:
                return False
                
            # Update portfolio with average purchase price
            if stock not in portfolio['holdings']:
                portfolio['holdings'][stock] = {
                    'quantity': 0,
                    'avg_price': 0,
                    'total_cost': 0
                }
            
            holdings = portfolio['holdings'][stock]
            total_value = holdings['total_cost'] + order_value
            new_quantity = holdings['quantity'] + quantity
            holdings['avg_price'] = total_value / new_quantity
            holdings['quantity'] = new_quantity
            holdings['total_cost'] = total_value
            portfolio['cash'] -= order_value

        elif order['type'] == 'sell':
            if stock not in portfolio['holdings'] or portfolio['holdings'][stock]['quantity'] < quantity:
                return False
                
            # Calculate profit/loss
            holdings = portfolio['holdings'][stock]
            avg_price = holdings['avg_price']
            profit_loss = (current_price - avg_price) * quantity
            
            # Update portfolio
            holdings['quantity'] -= quantity
            portfolio['cash'] += order_value
            
            # Remove stock if no shares left
            if holdings['quantity'] == 0:
                del portfolio['holdings'][stock]
            else:
                # Adjust total cost
                holdings['total_cost'] = holdings['avg_price'] * holdings['quantity']

        # Update portfolio value
        self._update_portfolio_value(team_id)
        return True

    def _update_portfolio_value(self, team_id):
        """Calculate current portfolio value"""
        portfolio = market_state.team_portfolios.get(team_id)
        if not portfolio:
            return

        total_value = portfolio['cash']
        for stock, holdings in portfolio['holdings'].items():
            current_price = market_state.stock_prices.get(stock, 0)
            stock_value = current_price * holdings['quantity']
            total_value += stock_value

        portfolio['total_value'] = total_value
        portfolio['holdings_value'] = total_value - portfolio['cash']

def admin_place_order(team_id, stock, quantity, order_type, admin_key=None):
    """Process admin-placed orders for teams with admin validation"""
    # Validate admin privileges
    if not validate_admin(admin_key):
        logger.error("Unauthorized admin order attempt")
        return False

    if not market_session.session_active:
        logger.error("Cannot place order: No active trading session")
        return False

    if team_id not in market_state.team_portfolios:
        logger.error(f"Invalid team ID: {team_id}")
        return False

    order = {
        'stock': stock,
        'quantity': quantity,
        'type': order_type,
        'timestamp': time.time(),
        'admin_placed': True,
        'team_id': team_id
    }

    if market_state.validate_order(order) and market_state.validate_team_order(team_id, order):
        success = market_state.process_market_order(team_id, order)
        if success:
            logger.info(f"Admin order placed for Team {team_id}: {order_type} {quantity} {stock}")
        return success
    return False

def validate_admin(admin_key):
    """Validate admin privileges"""
    # Simple validation - in a real system, use proper authentication
    ADMIN_KEY = "admin123"  # This should be stored securely in configuration
    return admin_key == ADMIN_KEY

# Create global market session without initialization
market_session = MarketSession()
# Remove any auto-initialization calls

def start_session(session_number=None):
    """Start a new trading session"""
    global session_active, current_session, session_start_time, pause_lock
    
    if session_active:
        logger.warning("Session already active")
        return False
    
    # Initialize or increment session number
    if session_number is not None:
        current_session = session_number
    else:
        current_session = (current_session or 0) + 1
    
    if current_session > MAX_SESSIONS:
        logger.warning(f"Maximum sessions ({MAX_SESSIONS}) reached")
        return False
    
    # Start new session
    session_active = True
    pause_lock = False
    session_start_time = time.time()
    logger.info(f"Trading Session {current_session} started")
    
    return True

def pause():
    """Pause the current trading session"""
    global pause_lock
    
    if not session_active:
        logger.warning("No active session to pause")
        return False
    
    if pause_lock:
        logger.warning("Session already paused")
        return False
    
    pause_lock = True
    logger.info("Trading session paused")
    return True

def resume():
    """Resume the current trading session"""
    global pause_lock
    
    if not session_active:
        logger.warning("No active session to resume")
        return False
    
    if not pause_lock:
        logger.warning("Session not paused")
        return False
    
    pause_lock = False
    logger.info("Trading session resumed")
    return True

def is_market_open():
    """Check if market is open for trading"""
    return session_active and not pause_lock
