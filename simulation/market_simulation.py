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
        self.state = {
            'trend_duration': 0,  # How long current trend has lasted
            'trend_strength': 1.0,  # Current trend strength (1.0 to 2.0)
            'market_momentum': 0.0,  # Market momentum (-1.0 to 1.0)
            'sector_performance': {},  # Track sector-specific trends
            'volatility_factors': {},  # Per-stock volatility
        }
        self.trend_change_probability = 0.05  # 5% chance to change trend
        self.max_trend_duration = 300  # Maximum trend duration in seconds

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
        """Process news events directly with exact percentage"""
        affected_stocks = event_data.get('stocks', [])
        impact = event_data.get('impact', 0)
        
        # Impact is already the exact percentage we want (e.g., 100 for 100%)
        # Do NOT convert it - pass it directly
        market_session.add_news_impact(affected_stocks, impact)
        logger.info(f"News impact queued: {impact}% for {affected_stocks}")
        
        # Log the event only
        db.log_event(
            event_type="news",
            description=event_data.get('description', ''),
            affected_stocks=affected_stocks,
            impact=impact
        )

    def update_market_dynamics(self):
        """Update market dynamics including trends, momentum, and sector performance"""
        global current_trend, volatility_factor, market_sentiment
        
        # Update trend duration and check for trend change
        self.state['trend_duration'] += 1
        trend_age_factor = min(self.state['trend_duration'] / self.max_trend_duration, 1.0)
        
        # Increased chance of trend reversal as trend ages
        trend_change_chance = self.trend_change_probability * (1 + trend_age_factor)
        
        if random.random() < trend_change_chance or self.state['trend_duration'] >= self.max_trend_duration:
            # Reverse trend
            current_trend = -current_trend
            self.state['trend_duration'] = 0
            self.state['trend_strength'] = 1.0 + random.uniform(0.2, 0.8)  # New trend strength
            logger.info(f"Market trend changed to {'Bullish' if current_trend == MarketTrend.BULLISH else 'Bearish'}")
        
        # Update market momentum
        momentum_change = random.uniform(-0.1, 0.1)
        self.state['market_momentum'] = max(-1.0, min(1.0, 
            self.state['market_momentum'] + momentum_change * self.state['trend_strength']))
        
        # Update sector performance
        self._update_sector_trends()
        
        # Update volatility
        self._update_volatility()

    def _update_sector_trends(self):
        """Update sector-specific market trends"""
        sectors = {stock['sector'] for stock in market_state.STOCK_DETAILS.values()}
        
        for sector in sectors:
            if sector not in self.state['sector_performance']:
                self.state['sector_performance'][sector] = 0.0
            
            # Update sector performance with trend influence
            sector_change = random.uniform(-0.05, 0.05) * self.state['trend_strength']
            current_perf = self.state['sector_performance'][sector]
            
            # Add trend bias - Fix the missing closing quote
            trend_bias = 0.02 * current_trend * self.state['trend_strength']
            
            # Calculate new performance with mean reversion
            new_perf = current_perf + sector_change + trend_bias
            new_perf *= 0.95  # Mean reversion factor
            
            self.state['sector_performance'][sector] = max(-0.2, min(0.2, new_perf))

    def _update_volatility(self):
        """Update stock-specific volatility factors"""
        global volatility_factor
        
        base_volatility = volatility_factor
        
        for stock in market_state.stock_prices.keys():
            if stock not in self.state['volatility_factors']:
                self.state['volatility_factors'][stock] = 1.0
            
            # Get stock's sector
            sector = market_state.STOCK_DETAILS[stock]['sector']
            sector_impact = abs(self.state['sector_performance'].get(sector, 0))
            
            # Calculate stock-specific volatility
            vol_change = random.uniform(-0.1, 0.1)
            stock_vol = self.state['volatility_factors'][stock]
            
            # Include sector and momentum effects
            new_vol = stock_vol + vol_change + (sector_impact * 0.5)
            new_vol *= 0.95  # Mean reversion
            
            # Apply limits
            self.state['volatility_factors'][stock] = max(0.5, min(2.0, new_vol))

    def get_stock_modifiers(self, stock):
        """Get all price modifiers for a specific stock"""
        sector = market_state.STOCK_DETAILS[stock]['sector']
        return {
            'trend': current_trend * self.state['trend_strength'],
            'momentum': self.state['market_momentum'],
            'sector': self.state['sector_performance'].get(sector, 0),
            'volatility': self.state['volatility_factors'].get(stock, 1.0)
        }

# Module-level instance for backward compatibility
market_simulation = MarketSimulation()

# Market simulation state
current_trend = MarketTrend.NEUTRAL
volatility_factor = 1.0
market_sentiment = 0  # Range: -1 to 1

def calculate_new_price(old_price, net_demand, news_impact, stock):  # Add stock parameter
    """Enhanced price calculation with improved market dynamics"""
    mods = market_simulation.get_stock_modifiers(stock)
    
    # Base calculations
    trend_impact = mods['trend'] * 0.001  # 0.1% base trend effect
    momentum_impact = mods['momentum'] * 0.002  # 0.2% momentum effect
    sector_impact = mods['sector'] * 0.003  # 0.3% sector effect
    
    # Apply volatility to all effects
    volatility = mods['volatility']
    
    # Calculate final impact
    total_impact = (
        (trend_impact + momentum_impact + sector_impact) * volatility +
        net_demand * DEMAND_COEFFICIENT +
        news_impact * EVENT_COEFFICIENT
    )
    
    # Add noise scaled by volatility
    noise = random.uniform(-0.001, 0.001) * volatility
    total_impact += noise
    
    # Calculate new price
    new_price = old_price * (1 + total_impact)
    
    # Ensure minimum price
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
    """Enhanced order processing with market impact - no session validation"""
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
        trend_impact,
        stock  # Add stock parameter here too
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
        """Enhanced random price fluctuation with more realistic behavior"""
        settings = self.stock_settings[stock]
        
        # More realistic, smaller base changes
        base_change = random.uniform(-0.004, 0.004)  # Reduced from (-0.015, 0.015)
        
        # Add rare market shock events (3% chance instead of 5%)
        if random.random() < 0.03:
            shock_multiplier = random.choice([-2.0, -1.5, 1.5, 2.0])
            base_change *= shock_multiplier
        
        # Add gradual trend component for smoother changes
        if not hasattr(self, 'stock_trends'):
            self.stock_trends = {}
        if stock not in self.stock_trends:
            self.stock_trends[stock] = random.uniform(-0.001, 0.001)
        
        # Gradually shift the trend direction
        if random.random() < 0.10:  # 10% chance to adjust trend
            self.stock_trends[stock] += random.uniform(-0.0005, 0.0005)
            # Keep trend within bounds
            self.stock_trends[stock] = max(-0.002, min(0.002, self.stock_trends[stock]))
        
        # Apply the trend
        base_change += self.stock_trends[stock]
        
        # Add smaller noise component
        noise = random.gauss(0, 0.002)  # Reduced from 0.005
        total_change = base_change + noise
        
        # Apply change to current price
        current_price = market_state.stock_prices[stock]
        new_price = current_price * (1 + total_change)
        
        # Ensure price doesn't change too dramatically
        max_change = 0.1  # Reduced from 0.2 (10% max change per update)
        if abs(total_change) > max_change:
            total_change = math.copysign(max_change, total_change)
            new_price = current_price * (1 + total_change)
        
        # Apply the new price
        market_state.stock_prices[stock] = max(0.01, new_price)
        
        # Safely update price history
        if not hasattr(market_state, 'price_history'):
            market_state.price_history = {}
        if stock not in market_state.price_history:
            market_state.price_history[stock] = []
        
        market_state.price_history[stock].append(new_price)
        if len(market_state.price_history[stock]) > 100:
            market_state.price_history[stock] = market_state.price_history[stock][-100:]
        
        # Log significant changes with higher threshold
        if abs(total_change) > 0.03:  # Changed from 0.02
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
        self.news_impacts = {}  # Add this to track active news impacts

    def initialize_session(self):
        """Initialize session without resetting market state"""
        # Remove market state initialization
        # Only store initial prices for reference
        self.initial_prices = market_state.stock_prices.copy()
        self.initialized = True
        logger.info("Market session initialized - preserving existing holdings")

    def start_session(self):
        """Enhanced session start that guarantees impacts are only processed AFTER session is fully active"""
        if self.session_active:
            logger.warning("A session is already active")
            return False
            
        try:
            # First fully initialize the session
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
            
            # Set session active flags BEFORE processing impacts
            self.session_active = True
            self.is_active = True
            
            # Log session start BEFORE processing impacts
            logger.info(f"Trading Session {self.current_session} started - Duration: 10 minutes")
            
            # ONLY NOW, after session is fully active, process impacts
            # Wait a short time to ensure session has truly started
            timer = QTimer(singleShot=True)
            timer.timeout.connect(self._process_pending_impacts)
            timer.start(1000)  # Process impacts 1 second after session start
            
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
        """Enhanced session end that GUARANTEES all news impacts reach exactly their target"""
        if not self.session_active:
            logger.warning("No active session to end")
            return False
            
        try:
            # First, process any unfinished news impacts to ensure targets are hit EXACTLY
            for stock, impact in list(self.news_impacts.items()):
                # Get the original target values stored when impact was registered
                start_price = impact['start_price']
                target_percent = impact['target_percent']
                target_price = impact['target_price']  # This is the exact price we want
                
                # Get the current price before forcing change
                current_price = market_state.stock_prices[stock]
                actual_percent = ((current_price - start_price) / start_price) * 100
                
                # FORCE the stock price to exactly match the target price
                market_state.stock_prices[stock] = target_price
                
                # Calculate the new actual percentage after forcing the exact price
                final_percent = ((target_price - start_price) / start_price) * 100
                
                # This is critical for debugging - log details about what happened
                logger.info(f"SESSION END - FORCING TARGET PRICE: {stock}")
                logger.info(f"  Start price: ${start_price:.2f}")
                logger.info(f"  Before force: ${current_price:.2f} ({actual_percent:.2f}%)")
                logger.info(f"  Target: ${target_price:.2f} ({target_percent:.2f}%)")
                logger.info(f"  After force: ${market_state.stock_prices[stock]:.2f} ({final_percent:.2f}%)")
                logger.info(f"  VERIFICATION: Target reached exactly: {market_state.stock_prices[stock] == target_price}")
            
            # Clear all impacts
            self.news_impacts.clear()
            
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
        """Simplified price updates for more predictable behavior"""
        if not self.session_active or self.pause_lock:
            return

        # Process news impacts first and exclusively
        if self.news_impacts:
            self._process_news_impacts()
            return  # Skip other market movements when we have active impacts

    def _process_news_impacts(self):
        """Process news impacts with steady progress toward target over 10 minutes"""
        for stock, impact in list(self.news_impacts.items()):
            current_price = market_state.stock_prices[stock]
            target_price = impact['target_price']
            start_price = impact['start_price']

            # Calculate total distance to move and progress per update
            total_price_change = target_price - start_price
            total_steps = 600  # 10 minutes = 600 seconds
            price_change_per_step = total_price_change / total_steps
            
            # Move price by one step
            new_price = current_price + price_change_per_step
            
            # Verify we're moving in the right direction
            if total_price_change > 0:  # Price should go up
                new_price = min(new_price, target_price)  # Don't overshoot upward
            else:  # Price should go down
                new_price = max(new_price, target_price)  # Don't overshoot downward
            
            # Update price
            market_state.stock_prices[stock] = new_price
            
            # Calculate and log progress percentage
            progress = ((new_price - start_price) / (target_price - start_price)) * 100
            logger.info(f"Stock: {stock} | Progress: {progress:.1f}% | " +
                       f"Current: ${new_price:.2f} | Target: ${target_price:.2f}")

    def log_market_status(self):
        """Log current market status."""
        from simulation import market_state
        state = market_state.get_market_state()
        logger.info(f"Market Status - Tick {self.tick_count}")
        logger.info(f"Prices: {state['prices']}")
        logger.info(f"Volumes: {state['volumes']}")

    def process_market_order(self, team_id, order):
        """Enhanced order processing with better portfolio management - no session validation"""
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

    def add_news_impact(self, stocks, target_percent, duration=None):
        """Queue news impacts ONLY, never apply them directly"""
        logger.info(f"News impact for {stocks} recorded: {target_percent}% target")
        
        # Always queue impacts, never apply them immediately
        if not hasattr(self, 'pending_impacts'):
            self.pending_impacts = []
        
        # Store the impact for later application when session starts/is active
        self.pending_impacts.append((stocks, target_percent, duration))
        
        # Show message indicating it's queued
        if not self.session_active:
            logger.info(f"Impact for {stocks} queued for when session starts")
        else:
            logger.info(f"Impact for {stocks} queued for immediate processing")
            
        # IMPORTANT: Do NOT call _apply_queued_impact here!

    def _apply_queued_impact(self, stocks, target_percent, duration=None):
        """Set up the impact with 10-minute duration"""
        if not self.session_active:
            return
        
        for stock in stocks:
            current_price = market_state.stock_prices[stock]
            # Calculate exact target price from percentage
            target_price = current_price * (1 + (target_percent / 100.0))
            
            self.news_impacts[stock] = {
                'target_percent': target_percent,
                'start_price': current_price,
                'target_price': target_price
            }
            
            logger.info(f"Impact registered for {stock}:")
            logger.info(f"  Start: ${current_price:.2f}")
            logger.info(f"  Target: ${target_price:.2f} ({target_percent:+.1f}%)")
            logger.info(f"  Duration: 10 minutes")

    def _process_pending_impacts(self):
        """Process pending impacts after session has fully started"""
        if not self.session_active:
            logger.warning("Cannot process impacts - session not active")
            return
            
        if hasattr(self, 'pending_impacts') and self.pending_impacts:
            pending_count = len(self.pending_impacts)
            logger.info(f"Processing {pending_count} queued news impacts now that session is active")
            
            # Make a copy of the queue to process
            impacts_to_process = self.pending_impacts.copy()
            # Clear the queue before processing
            self.pending_impacts = []
            
            # Process each impact
            for impact in impacts_to_process:
                stocks, target_percent, duration = impact
                self._apply_queued_impact(stocks, target_percent, duration)

def admin_place_order(team_id, stock, quantity, order_type, admin_key=None):
    """Process admin-placed orders for teams with admin validation"""
    # Remove session check
    if not validate_admin(admin_key):
        logger.error("Unauthorized admin order attempt")
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
