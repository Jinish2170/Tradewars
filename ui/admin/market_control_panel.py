from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QPushButton, QLabel, QComboBox, QDoubleSpinBox,
                            QTextEdit, QTableWidget, QTableWidgetItem, QSpinBox)
from PyQt5.QtCore import QTimer
from simulation import market_state
from simulation.market_simulation import market_session
import time

GROUP_BOX_STYLE = """
QGroupBox {
    font-weight: bold;
    border: 2px solid gray;
    border-radius: 5px;
    margin-top: 1ex;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
}
"""

BUTTON_STYLE = """
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    font-size: 16px;
    margin: 4px 2px;
    border-radius: 8px;
}
QPushButton:hover {
    background-color: #45a049;
}
QPushButton:disabled {
    background-color: #cccccc;
    color: #666666;
}
"""

STATUS_LABEL_STYLE = """
QLabel[status="info"] {
    color: blue;
    font-weight: bold;
}
"""

INPUT_STYLE = """
QComboBox, QDoubleSpinBox {
    padding: 5px;
    border: 1px solid gray;
    border-radius: 5px;
}
"""

TABLE_STYLE = """
QTableWidget {
    border: 1px solid gray;
    border-radius: 5px;
}
QHeaderView::section {
    background-color: lightgray;
    padding: 4px;
    border: 1px solid gray;
}
"""

COLORS = {
    'background': '#f0f0f0',
    'text': '#333333',
    'border': '#cccccc'
}

class MarketControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        # Create member variables first
        self.create_controls()
        self.init_ui()
        self.setup_timer()
        # Initialize button states
        self.update_button_states(False)
        
        # Ensure stock selector has an initial selection if available
        self.update_stock_list()

    def create_controls(self):
        """Create all control widgets as class members"""
        # Session control buttons
        self.start_session_btn = QPushButton("Start Session")
        self.end_session_btn = QPushButton("End Session")
        self.pause_btn = QPushButton("Pause")
        self.resume_btn = QPushButton("Resume")
        self.session_status_label = QLabel("Session: Not Started")

        # Override controls
        self.stock_selector = QComboBox()
        self.price_spinner = QDoubleSpinBox()
        self.override_btn = QPushButton("Override Price")  # Changed name to override_btn
        
        # Price display
        self.price_table = QTableWidget()
        self.log_text = QTextEdit()

        # Configure controls
        self.price_spinner.setRange(0.01, 10000.00)
        self.price_spinner.setDecimals(2)
        self.price_spinner.setValue(100.00)
        self.log_text.setReadOnly(True)

        # Connect signals
        self.start_session_btn.clicked.connect(self.start_session)
        self.end_session_btn.clicked.connect(self.end_session)
        self.pause_btn.clicked.connect(self.pause_session)
        self.resume_btn.clicked.connect(self.resume_session)
        self.override_btn.clicked.connect(self.override_price)  # Connect override button

        # Add trade order controls with separate stock selector
        self.team_selector = QComboBox()
        self.team_selector.addItems([f"Team {i}" for i in range(market_state.TEAM_COUNT)])
        
        self.order_type = QComboBox()
        self.order_type.addItems(["buy", "sell"])
        
        # Create separate stock selector for team orders
        self.team_order_stock_selector = QComboBox()
        
        self.quantity_spinner = QSpinBox()
        self.quantity_spinner.setRange(1, 10000)
        self.quantity_spinner.setValue(100)
        
        self.place_order_btn = QPushButton("Place Order")
        self.place_order_btn.clicked.connect(self.place_team_order)

        # Add price manipulation controls
        self.price_change_spinner = QDoubleSpinBox()
        self.price_change_spinner.setRange(-20.0, 20.0)  # Wider range: ±20%
        self.price_change_spinner.setDecimals(2)
        self.price_change_spinner.setValue(0.0)
        self.price_change_spinner.setSingleStep(0.5)  # Finer step control
        self.price_change_spinner.setSuffix("%")
        
        self.apply_change_btn = QPushButton("Apply Price Change")
        self.apply_change_btn.clicked.connect(self.apply_price_change)
        self.apply_change_btn.setStyleSheet(BUTTON_STYLE)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Session Controls with enhanced styling
        session_group = QGroupBox("Session Controls")
        session_group.setStyleSheet(GROUP_BOX_STYLE)
        session_layout = QHBoxLayout()
        session_layout.setSpacing(15)
        session_layout.setContentsMargins(15, 20, 15, 20)

        # Style the status label
        self.session_status_label.setProperty('status', 'info')
        self.session_status_label.setStyleSheet(STATUS_LABEL_STYLE)
        
        # Style the control buttons
        control_buttons = [self.start_session_btn, self.end_session_btn,
                          self.pause_btn, self.resume_btn]
        
        for btn in control_buttons:
            btn.setStyleSheet(BUTTON_STYLE)
            btn.setMinimumWidth(120)

        session_layout.addWidget(self.start_session_btn)
        session_layout.addWidget(self.end_session_btn)
        session_layout.addWidget(self.pause_btn)
        session_layout.addWidget(self.resume_btn)
        session_layout.addWidget(self.session_status_label)

        session_group.setLayout(session_layout)
        layout.addWidget(session_group)

        # Update button initial states
        self.update_button_states(False)

        # Override Controls with enhanced styling
        override_group = QGroupBox("Manual Price Override")
        override_group.setStyleSheet(GROUP_BOX_STYLE)
        override_layout = QHBoxLayout()
        override_layout.setSpacing(15)
        override_layout.setContentsMargins(15, 20, 15, 20)

        self.stock_selector.setStyleSheet(INPUT_STYLE)
        self.price_spinner.setStyleSheet(INPUT_STYLE)
        self.override_btn.setStyleSheet(BUTTON_STYLE)

        override_layout.addWidget(QLabel("Stock:"))
        override_layout.addWidget(self.stock_selector)
        override_layout.addWidget(QLabel("New Price:"))
        override_layout.addWidget(self.price_spinner)
        override_layout.addWidget(self.override_btn)  # Use the correct button name

        override_group.setLayout(override_layout)
        layout.addWidget(override_group)

        # Update Trade Order section with separate stock selector
        trade_group = QGroupBox("Place Team Orders")
        trade_group.setStyleSheet(GROUP_BOX_STYLE)
        trade_layout = QHBoxLayout()
        
        # Apply style to new stock selector
        self.team_order_stock_selector.setStyleSheet(INPUT_STYLE)
        
        trade_layout.addWidget(QLabel("Team:"))
        trade_layout.addWidget(self.team_selector)
        trade_layout.addWidget(QLabel("Action:"))
        trade_layout.addWidget(self.order_type)
        trade_layout.addWidget(QLabel("Stock:"))
        trade_layout.addWidget(self.team_order_stock_selector)  # Use separate selector
        trade_layout.addWidget(QLabel("Quantity:"))
        trade_layout.addWidget(self.quantity_spinner)
        trade_layout.addWidget(self.place_order_btn)
        
        trade_group.setLayout(trade_layout)
        layout.addWidget(trade_group)

        # Add Price Manipulation section after Override Controls
        manipulation_group = QGroupBox("Price Manipulation")
        manipulation_group.setStyleSheet(GROUP_BOX_STYLE)
        manipulation_layout = QHBoxLayout()
        manipulation_layout.setSpacing(15)
        manipulation_layout.setContentsMargins(15, 20, 15, 20)

        self.price_change_spinner.setStyleSheet(INPUT_STYLE)
        
        manipulation_layout.addWidget(QLabel("Stock:"))
        manipulation_layout.addWidget(self.stock_selector)
        manipulation_layout.addWidget(QLabel("Price Change:"))
        manipulation_layout.addWidget(self.price_change_spinner)
        manipulation_layout.addWidget(self.apply_change_btn)

        manipulation_group.setLayout(manipulation_layout)
        layout.addWidget(manipulation_group)

        # Stock Price Display
        price_group = QGroupBox("Current Stock Prices")
        price_layout = QVBoxLayout()
        self.price_table = QTableWidget()
        self.price_table.setColumnCount(3)
        self.price_table.setHorizontalHeaderLabels(["Stock", "Price", "Available Quantity"])
        price_layout.addWidget(self.price_table)
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)

        # Enhanced table styling
        self.price_table.setStyleSheet(TABLE_STYLE)
        self.price_table.horizontalHeader().setStretchLastSection(True)
        self.price_table.verticalHeader().setVisible(False)
        self.price_table.setShowGrid(False)

        # Action Log
        log_group = QGroupBox("Action Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Enhanced log text styling
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                border: 2px solid {COLORS['border']};
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
            }}
        """)

        # Add Transaction Log section
        transaction_group = QGroupBox("Market Transactions")
        transaction_group.setStyleSheet(GROUP_BOX_STYLE)
        transaction_layout = QVBoxLayout()
        
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels(["Time", "Team", "Type", "Stock", "Quantity", "Price"])
        self.transaction_table.setStyleSheet(TABLE_STYLE)
        self.transaction_table.horizontalHeader().setStretchLastSection(True)
        self.transaction_table.verticalHeader().setVisible(False)
        
        transaction_layout.addWidget(self.transaction_table)
        transaction_group.setLayout(transaction_layout)
        layout.addWidget(transaction_group)

        self.setLayout(layout)
        self.update_stock_list()
        self.update_session_status()

    def setup_timer(self):
        """Setup timers for updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_price_display)
        self.update_timer.start(1000)  # Update every second

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_session_status)
        self.status_timer.start(500)  # Update status more frequently

        # Add transaction update timer
        self.transaction_timer = QTimer()
        self.transaction_timer.timeout.connect(self.update_transaction_log)
        self.transaction_timer.start(2000)  # Update every 2 seconds

    # Fix the update_stock_list method to handle empty market state and ensure selection
    def update_stock_list(self):
        """Properly update stock selectors with available stocks"""
        try:
            # First ensure market is initialized
            if not market_state.stock_prices:
                self.log_text.append("Initializing market state...")
                market_state.initialize_market()
                
            # Get current stock symbols from market_state
            current_stocks = list(market_state.stock_prices.keys())
            
            if not current_stocks:
                self.log_text.append("ERROR: No stocks available after initialization!")
                return
                
            # Save the currently selected items if they exist
            current_stock = self.stock_selector.currentText()
            current_team_stock = self.team_order_stock_selector.currentText()
            
            # Block signals during update to prevent handlers from firing incorrectly
            self.stock_selector.blockSignals(True)
            self.team_order_stock_selector.blockSignals(True)
            
            # Clear and repopulate both selectors
            self.stock_selector.clear()
            self.team_order_stock_selector.clear()
            
            # Add stocks to both selectors
            self.stock_selector.addItems(current_stocks)
            self.team_order_stock_selector.addItems(current_stocks)
            
            # Always select first item by default, then try to restore previous selection
            self.stock_selector.setCurrentIndex(0)
            self.team_order_stock_selector.setCurrentIndex(0)
            
            # Try to restore previous selections if they existed
            if current_stock:
                index = self.stock_selector.findText(current_stock)
                if index >= 0:
                    self.stock_selector.setCurrentIndex(index)
                    
            if current_team_stock:
                index = self.team_order_stock_selector.findText(current_team_stock)
                if index >= 0:
                    self.team_order_stock_selector.setCurrentIndex(index)
            
            # Re-enable signals
            self.stock_selector.blockSignals(False)
            self.team_order_stock_selector.blockSignals(False)
            
            # Log current selection for debugging
            self.log_text.append(f"Stock list updated. Selected: {self.stock_selector.currentText()}")
            
        except Exception as e:
            self.log_text.append(f"Error updating stock list: {str(e)}")

    def update_price_display(self):
        prices = market_state.get_stock_prices()
        quantities = market_state.available_quantities
        
        self.price_table.setRowCount(len(prices))
        for row, (stock, price) in enumerate(prices.items()):
            self.price_table.setItem(row, 0, QTableWidgetItem(stock))
            self.price_table.setItem(row, 1, QTableWidgetItem(f"${price:.2f}"))
            self.price_table.setItem(row, 2, QTableWidgetItem(str(quantities.get(stock, 0))))
        
        # Make sure the table updates visually
        self.price_table.viewport().update()

    # Fix override price function to properly get selected stock
    def override_price(self):
        """Handle price override with proper error checks and stock selection"""
        if not market_session.session_active:
            self.log_text.append("Cannot override price: No active session")
            return
        
        # Verify stock selector has items
        if self.stock_selector.count() == 0:
            self.log_text.append("Stock selector is empty - refreshing selector")
            self.update_stock_list()
            if self.stock_selector.count() == 0:
                self.log_text.append("ERROR: Failed to populate stock list!")
                return
        
        # Get selected stock, force selection if needed
        stock = self.stock_selector.currentText()
        if not stock:
            # Force a selection if none exists
            if self.stock_selector.count() > 0:
                self.stock_selector.setCurrentIndex(0)
                stock = self.stock_selector.currentText()
                self.log_text.append(f"Auto-selected stock: {stock}")
            else:
                self.log_text.append("Error: No stock available to select")
                return
        
        # Continue with price override
        new_price = self.price_spinner.value()
        self.log_text.append(f"Attempting price override for stock: {stock} to ${new_price:.2f}")
        
        # Use the admin override function
        if market_state.admin_override_price(stock, new_price):
            log_entry = f"Manual override: {stock} price set to ${new_price:.2f}"
            self.log_text.append(log_entry)
            # Force immediate update of price display
            self.update_price_display()
        else:
            self.log_text.append(f"Failed to override price for {stock}")

    # Ensure selectors are properly initialized when the market session starts
    def start_session(self):
        """Start the market session and initialize stock selectors"""
        if market_session.start_session():
            self.log_text.append("New trading session started")
            # Make sure we refresh stock list after session starts
            self.update_stock_list()
            self.update_button_states(True)
            self.update_session_status()
        else:
            self.log_text.append("Failed to start session")

    def end_session(self):
        if market_session.end_session():
            self.log_text.append("Trading session ended")
            self.update_button_states(False)
            self.update_session_status()
        else:
            self.log_text.append("Failed to end session")

    def pause_session(self):
        if market_session.pause():
            self.log_text.append("Trading session paused")
            self.update_button_states(True, True)
            self.update_session_status()
        else:
            self.log_text.append("Failed to pause session")

    def resume_session(self):
        if market_session.resume():
            self.log_text.append("Trading session resumed")
            self.update_button_states(True, False)
            self.update_session_status()
        else:
            self.log_text.append("Failed to resume session")

    def update_session_status(self):
        status = market_session.get_session_status()
        status_text = f"Session: {status['current_session']}/{status['max_sessions']}"
        
        if status['is_active']:
            if market_session.pause_lock:
                status_text += " (Paused)"
            else:
                status_text += " (Active)"
        else:
            status_text += " (Inactive)"
            
        self.session_status_label.setText(status_text)
        self.update_button_states(status['is_active'], market_session.pause_lock)

    def update_button_states(self, is_session_active, is_paused=False):
        """Update button states based on session status"""
        self.start_session_btn.setEnabled(not is_session_active)
        self.end_session_btn.setEnabled(is_session_active)
        self.pause_btn.setEnabled(is_session_active and not is_paused)
        self.resume_btn.setEnabled(is_session_active and is_paused)
        self.override_btn.setEnabled(is_session_active and not is_paused)
        self.place_order_btn.setEnabled(is_session_active and not is_paused)
        self.apply_change_btn.setEnabled(is_session_active and not is_paused)

    # Fix place team order function to properly get selected stock
    def place_team_order(self):
        """Admin-placed order for teams with proper stock selection"""
        if not market_session.session_active:
            self.log_text.append("Cannot place order: No active session")
            return
        
        # Verify stock selector has items
        if self.team_order_stock_selector.count() == 0:
            self.log_text.append("Team order stock selector is empty - refreshing selectors")
            self.update_stock_list()
            if self.team_order_stock_selector.count() == 0:
                self.log_text.append("ERROR: Failed to populate stock list!")
                return
        
        # Get team selection
        team_id = int(self.team_selector.currentText().split()[-1])
        
        # Get selected stock, force selection if needed
        stock = self.team_order_stock_selector.currentText()
        if not stock:
            # Force a selection if none exists
            if self.team_order_stock_selector.count() > 0:
                self.team_order_stock_selector.setCurrentIndex(0)
                stock = self.team_order_stock_selector.currentText()
                self.log_text.append(f"Auto-selected stock: {stock}")
            else:
                self.log_text.append("Error: No stock available to select")
                return
        
        # Continue with order placement
        quantity = self.quantity_spinner.value()
        order_type = self.order_type.currentText()
        
        # Rest of the function remains the same
        # Validate quantity
        if quantity <= 0:
            self.log_text.append("Error: Quantity must be positive")
            return
        
        # Check for available quantity only for buys
        if order_type.lower() == "buy":
            available = market_state.available_quantities.get(stock, 0)
            if quantity > available:
                self.log_text.append(f"Error: Only {available} shares of {stock} available")
                return
        
        # Log attempt
        current_price = market_state.stock_prices.get(stock, 0)
        order_value = current_price * quantity
        self.log_text.append(f"Attempting {order_type} order: {quantity} {stock} at ${current_price:.2f}")
        
        # Debug information
        self.log_text.append(f"DEBUG - Selected stock: '{stock}', Team: {team_id}, Type: {order_type}")
        
        # Use admin_place_order function for direct order placement
        if market_state.admin_place_order(team_id, stock, quantity, order_type):
            self.log_text.append(f"Order executed: Team {team_id}, {order_type} {quantity} {stock}")
            
            # Show updated portfolio value
            portfolio = market_state.get_team_portfolio(team_id)
            self.log_text.append(f"Team {team_id} new portfolio value: ${portfolio['total_value']:,.2f}")
            
            # Reset quantity spinner
            self.quantity_spinner.setValue(100)
            
            # Update display
            self.update_price_display()
        else:
            self.log_text.append(f"Order failed: Team {team_id}, {order_type} {quantity} {stock}")

    # Fix price change function to properly get selected stock
    def apply_price_change(self):
        """Apply percentage price change with proper stock selection"""
        if not market_session.session_active:
            self.log_text.append("Cannot manipulate price: No active session")
            return
        
        # Ensure a stock is selected    
        stock = self.stock_selector.currentText()
        if not stock:
            self.log_text.append("Error: No stock selected")
            return
            
        percent_change = self.price_change_spinner.value() / 100.0  # Convert to decimal
        
        current_price = market_state.stock_prices.get(stock, 0)
        new_price = current_price * (1 + percent_change)
        
        # Ensure minimum price
        if new_price < 0.01:
            self.log_text.append("Error: Price cannot go below $0.01")
            return
        
        # Debug information
        self.log_text.append(f"DEBUG - Changing price for: '{stock}' by {percent_change*100:+.2f}%")
        
        # Use the price manipulation function with percentage flag
        if market_state.update_stock_price(stock, percent_change, is_percent_change=True):
            log_entry = f"Price change: {stock} adjusted by {percent_change*100:+.2f}% to ${new_price:.2f}"
            self.log_text.append(log_entry)
            
            # Reset spinner and update display
            self.price_change_spinner.setValue(0.0)
            self.update_price_display()
        else:
            self.log_text.append(f"Failed to change price for {stock}")

    # Add a method to update transaction log
    def update_transaction_log(self):
        """Update transaction log with recent transactions from all teams"""
        try:
            all_transactions = []
            
            # Collect transactions from all teams
            for team_id in range(market_state.TEAM_COUNT):
                portfolio = market_state.get_team_portfolio(team_id)
                if 'transactions' in portfolio:
                    for tx in portfolio['transactions']:
                        tx['team_id'] = team_id  # Add team ID to transaction data
                        all_transactions.append(tx)
            
            # Sort by timestamp (most recent first)
            all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Limit to last 20 transactions
            recent_transactions = all_transactions[:20]
            
            # Update table
            self.transaction_table.setRowCount(len(recent_transactions))
            
            for row, tx in enumerate(recent_transactions):
                # Format timestamp
                time_item = QTableWidgetItem(time.strftime("%H:%M:%S", time.localtime(tx['timestamp'])))
                
                # Team ID
                team_item = QTableWidgetItem(f"Team {tx['team_id']}")
                
                # Type with color
                type_text = tx['type'].upper()
                type_item = QTableWidgetItem(type_text)
                if type_text == "BUY":
                    type_item.setForeground(QBrush(QColor("#4BB543")))
                elif type_text == "SELL":
                    type_item.setForeground(QBrush(QColor("#FF3333")))
                
                # Stock symbol
                stock_item = QTableWidgetItem(tx['stock'])
                
                # Quantity
                quantity_item = QTableWidgetItem(f"{tx['quantity']:,}")
                
                # Price
                price_item = QTableWidgetItem(f"${tx['price']:,.2f}")
                
                # Add items to table
                self.transaction_table.setItem(row, 0, time_item)
                self.transaction_table.setItem(row, 1, team_item)
                self.transaction_table.setItem(row, 2, type_item)
                self.transaction_table.setItem(row, 3, stock_item)
                self.transaction_table.setItem(row, 4, quantity_item)
                self.transaction_table.setItem(row, 5, price_item)
            
        except Exception as e:
            self.log_text.append(f"Error updating transaction log: {str(e)}")
