import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QFrame, QSplitter, QSizePolicy, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea,
                            QGraphicsDropShadowEffect, QProgressBar, QPushButton,
                            QTabWidget, QStackedWidget, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot, QSize
from PyQt5.QtGui import QColor, QPainter, QFont, QIcon, QPixmap

from simulation import market_state
from simulation.market_simulation import market_session
from utils.decorators import safe_operation
from utils.logger import logger
from .styles import (COLORS, GROUP_BOX_STYLE, MARKET_TABLE_STYLE, PRICE_TICKER_STYLE)

# Modern dark theme colors
THEME = {
    'background': '#121212',
    'card': '#1E1E1E',
    'border': '#333333',
    'text': '#FFFFFF',
    'text_secondary': '#AAAAAA',
    'accent': '#4A8FE7',
    'positive': '#4CAF50',
    'negative': '#F44336',
    'neutral': '#9E9E9E',
    'header': '#252525',
    'chart_grid': '#333333',
    'selection': '#2C5282'
}

# Modern card style with border radius and subtle shadows
CARD_STYLE = f"""
QFrame.Card {{
    background-color: {THEME['card']};
    border: 1px solid {THEME['border']};
    border-radius: 8px;
}}
"""

# Modern table style with clean lines and better spacing
MODERN_TABLE_STYLE = f"""
QTableWidget {{
    background-color: {THEME['card']};
    alternate-background-color: {THEME['header']};
    color: {THEME['text']};
    gridline-color: {THEME['border']};
    border: none;
    border-radius: 4px;
    selection-background-color: {THEME['selection']};
    selection-color: {THEME['text']};
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {THEME['border']};
}}

QHeaderView::section {{
    background-color: {THEME['header']};
    color: {THEME['text_secondary']};
    font-weight: bold;
    padding: 8px;
    border: none;
    border-bottom: 1px solid {THEME['border']};
}}

QTableCornerButton::section {{
    background-color: {THEME['header']};
    border: none;
}}
"""

# Price display widget with animation effects
class ModernPriceWidget(QFrame):
    def __init__(self, symbol, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.last_price = 0
        self.setupUI()
        
    def setupUI(self):
        self.setObjectName("PriceCard")
        self.setStyleSheet(CARD_STYLE)
        self.setFixedHeight(90)
        self.setMinimumWidth(200)
        
        # Add shadow effect for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        
        # Symbol row with icon
        symbol_row = QHBoxLayout()
        self.symbol_label = QLabel(self.symbol)
        self.symbol_label.setStyleSheet(f"color: {THEME['text']}; font-weight: bold; font-size: 14px;")
        
        self.trend_icon = QLabel()
        self.trend_icon.setFixedSize(16, 16)
        self.trend_icon.setStyleSheet(f"color: {THEME['positive']};")
        
        symbol_row.addWidget(self.symbol_label)
        symbol_row.addStretch()
        symbol_row.addWidget(self.trend_icon)
        
        # Price row with large font
        price_row = QHBoxLayout()
        self.price_label = QLabel("$0.00")
        self.price_label.setStyleSheet(f"color: {THEME['text']}; font-weight: bold; font-size: 24px;")
        
        self.change_label = QLabel("0.00%")
        self.change_label.setStyleSheet(f"color: {THEME['positive']}; font-size: 14px;")
        self.change_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        price_row.addWidget(self.price_label)
        price_row.addStretch()
        price_row.addWidget(self.change_label)
        
        # Volume row
        volume_row = QHBoxLayout()
        self.volume_label = QLabel("Volume: 0")
        self.volume_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 12px;")
        volume_row.addWidget(self.volume_label)
        
        layout.addLayout(symbol_row)
        layout.addLayout(price_row)
        layout.addLayout(volume_row)
        
    def update_price(self, new_price, price_change, volume=0):
        # Format price
        price_str = f"${new_price:,.2f}"
        self.price_label.setText(price_str)
        
        # Format change with sign
        change_str = f"{price_change:+.2f}%"
        self.change_label.setText(change_str)
        
        # Format volume
        volume_str = f"Volume: {volume:,}"
        self.volume_label.setText(volume_str)
        
        # Update trend icon
        if new_price > self.last_price:
            self.trend_icon.setText("▲")
            self.trend_icon.setStyleSheet(f"color: {THEME['positive']}; font-size: 14px;")
            self.change_label.setStyleSheet(f"color: {THEME['positive']}; font-size: 14px;")
        elif new_price < self.last_price:
            self.trend_icon.setText("▼")
            self.trend_icon.setStyleSheet(f"color: {THEME['negative']}; font-size: 14px;")
            self.change_label.setStyleSheet(f"color: {THEME['negative']}; font-size: 14px;")
        else:
            self.trend_icon.setText("■")
            self.trend_icon.setStyleSheet(f"color: {THEME['neutral']}; font-size: 14px;")
            self.change_label.setStyleSheet(f"color: {THEME['neutral']}; font-size: 14px;")
        
        # Add animation effect for price changes
        if self.last_price != 0 and new_price != self.last_price:
            glow = QGraphicsDropShadowEffect(self.price_label)
            if new_price > self.last_price:
                glow.setColor(QColor(THEME['positive']))
            else:
                glow.setColor(QColor(THEME['negative']))
                
            glow.setBlurRadius(10)
            glow.setOffset(0, 0)
            self.price_label.setGraphicsEffect(glow)
            
            # Clear effect after animation
            QTimer.singleShot(1000, lambda: self.price_label.setGraphicsEffect(None))
        
        self.last_price = new_price

# Market status bar showing market state and current session
class MarketStatusBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUI()
        
    def setupUI(self):
        self.setFixedHeight(40)
        self.setStyleSheet(f"background-color: {THEME['header']}; border-radius: 4px;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        # Status indicator
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"color: {THEME['positive']}; font-size: 16px;")
        
        self.status_text = QLabel("Market Open")
        self.status_text.setStyleSheet(f"color: {THEME['text']}; font-weight: bold;")
        
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addSpacing(20)
        
        # Session info
        self.session_label = QLabel("Session 1 of 5")
        self.session_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        
        # Market time
        self.time_label = QLabel(time.strftime("%H:%M:%S"))
        self.time_label.setStyleSheet(f"color: {THEME['text_secondary']};")
        
        # Add all components to main layout
        layout.addLayout(status_layout)
        layout.addWidget(self.session_label)
        layout.addStretch()
        layout.addWidget(self.time_label)
        
        # Setup timer for clock updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def update_time(self):
        self.time_label.setText(time.strftime("%H:%M:%S"))
        
    def set_status(self, is_open, session_info="Session 1 of 5"):
        if is_open:
            self.status_indicator.setStyleSheet(f"color: {THEME['positive']}; font-size: 16px;")
            self.status_text.setText("Market Open")
        else:
            self.status_indicator.setStyleSheet(f"color: {THEME['negative']}; font-size: 16px;")
            self.status_text.setText("Market Closed")
            
        self.session_label.setText(session_info)

# Summary card for portfolio metrics
class SummaryCard(QFrame):
    def __init__(self, title, value="$0.00", color=THEME['text'], parent=None):
        super().__init__(parent)
        self.setupUI(title, value, color)
        
    def setupUI(self, title, value, color):
        self.setObjectName("SummaryCard")
        self.setStyleSheet(CARD_STYLE)
        self.setMinimumHeight(100)
        self.setMaximumHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(5)
        
        # Title label
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 12px;")
        
        # Value with large font
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        
    def update_value(self, new_value, color=None):
        self.value_label.setText(new_value)
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")

class ParticipantView(QWidget):
    def __init__(self):
        super().__init__()
        if not hasattr(market_state, 'stock_prices') or not market_state.stock_prices:
            market_state.initialize_market()
        self.price_widgets = {}
        self.setupUI()
        self.setupTimers()
        
    def setupUI(self):
        # Set main layout
        self.setStyleSheet(f"background-color: {THEME['background']};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Market status bar
        self.status_bar = MarketStatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Price tickers
        price_section = QFrame()
        price_section.setStyleSheet(CARD_STYLE)
        price_section.setObjectName("Card")
        price_section.setMinimumHeight(120)
        
        price_layout = QVBoxLayout(price_section)
        price_layout.setContentsMargins(15, 10, 15, 10)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Market Prices")
        header_label.setStyleSheet(f"color: {THEME['text']}; font-size: 16px; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        price_layout.addLayout(header_layout)
        price_layout.addSpacing(5)
        
        # Price ticker scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        scroll_area.setFixedHeight(100)
        
        scroll_widget = QWidget()
        self.ticker_layout = QHBoxLayout(scroll_widget)
        self.ticker_layout.setContentsMargins(0, 0, 0, 0)
        self.ticker_layout.setSpacing(12)
        self.ticker_layout.setAlignment(Qt.AlignLeft)
        
        scroll_area.setWidget(scroll_widget)
        price_layout.addWidget(scroll_area)
        
        main_layout.addWidget(price_section)
        
        # Main content area with tabs
        content_tabs = QTabWidget()
        content_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                background-color: {THEME['card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {THEME['header']};
                color: {THEME['text_secondary']};
                border: none;
                padding: 10px 20px;
                font-size: 14px;
            }}
            QTabBar::tab:selected {{
                background-color: {THEME['card']};
                color: {THEME['text']};
                font-weight: bold;
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {THEME['border']};
                color: {THEME['text']};
            }}
        """)
        
        # Market data tab
        market_tab = QWidget()
        market_tab_layout = QVBoxLayout(market_tab)
        market_tab_layout.setContentsMargins(15, 15, 15, 15)
        market_tab_layout.setSpacing(15)
        
        # Create market data table
        self.market_table = QTableWidget()
        self.market_table.setColumnCount(6)
        self.market_table.setHorizontalHeaderLabels(["Symbol", "Price", "Change", "Trend", "Volume", "Available"])
        self.market_table.setStyleSheet(MODERN_TABLE_STYLE)
        self.market_table.setAlternatingRowColors(True)
        self.market_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.market_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.market_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        market_tab_layout.addWidget(self.market_table)
        
        # Portfolio tab
        portfolio_tab = QWidget()
        portfolio_layout = QVBoxLayout(portfolio_tab)
        portfolio_layout.setContentsMargins(15, 15, 15, 15)
        portfolio_layout.setSpacing(15)
        
        # Portfolio summary cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)
        
        self.cash_card = SummaryCard("Available Cash", "$100,000", THEME['accent'])
        self.portfolio_value_card = SummaryCard("Portfolio Value", "$100,000", THEME['text'])
        self.profit_loss_card = SummaryCard("Profit/Loss", "$0.00", THEME['positive'])
        
        cards_layout.addWidget(self.cash_card)
        cards_layout.addWidget(self.portfolio_value_card)
        cards_layout.addWidget(self.profit_loss_card)
        
        portfolio_layout.addLayout(cards_layout)
        
        # Holdings table
        holdings_frame = QFrame()
        holdings_frame.setObjectName("Card")
        holdings_frame.setStyleSheet(CARD_STYLE)
        
        holdings_layout = QVBoxLayout(holdings_frame)
        holdings_layout.setContentsMargins(15, 12, 15, 12)
        
        # Holdings header
        holdings_header = QHBoxLayout()
        holdings_title = QLabel("Current Holdings")
        holdings_title.setStyleSheet(f"color: {THEME['text']}; font-size: 16px; font-weight: bold;")
        holdings_header.addWidget(holdings_title)
        holdings_layout.addLayout(holdings_header)
        
        # Holdings table
        self.holdings_table = QTableWidget()
        self.holdings_table.setColumnCount(5)
        self.holdings_table.setHorizontalHeaderLabels(["Symbol", "Quantity", "Avg Cost", "Current", "P/L"])
        self.holdings_table.setStyleSheet(MODERN_TABLE_STYLE)
        self.holdings_table.setAlternatingRowColors(True)
        self.holdings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.holdings_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        holdings_layout.addWidget(self.holdings_table)
        
        # Action log
        log_layout = QVBoxLayout()
        log_title = QLabel("Activity Log")
        log_title.setStyleSheet(f"color: {THEME['text']}; font-size: 16px; font-weight: bold;")
        log_layout.addWidget(log_title)
        
        self.action_log = QTextEdit()
        self.action_log.setReadOnly(True)
        self.action_log.setFixedHeight(120)
        self.action_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['header']};
                color: {THEME['text']};
                border: none;
                border-radius: 4px;
                font-family: monospace;
                padding: 8px;
            }}
        """)
        log_layout.addWidget(self.action_log)
        
        holdings_layout.addLayout(log_layout)
        
        portfolio_layout.addWidget(holdings_frame)
        
        # Add tabs to tab widget
        content_tabs.addTab(market_tab, "Market Data")
        content_tabs.addTab(portfolio_tab, "My Portfolio")
        
        main_layout.addWidget(content_tabs, 1)  # Give it stretch factor for responsive sizing
        
        # News ticker at bottom
        news_ticker = QFrame()
        news_ticker.setFixedHeight(30)
        news_ticker.setStyleSheet(f"background-color: {THEME['header']}; border-radius: 4px;")
        
        news_layout = QHBoxLayout(news_ticker)
        news_layout.setContentsMargins(15, 0, 15, 0)
        
        news_icon = QLabel("📢")
        news_icon.setStyleSheet(f"color: {THEME['accent']}; font-size: 16px;")
        
        self.news_label = QLabel("Welcome to the Trading Simulation!")
        self.news_label.setStyleSheet(f"color: {THEME['text']}; font-weight: bold;")
        
        news_layout.addWidget(news_icon)
        news_layout.addWidget(self.news_label)
        
        main_layout.addWidget(news_ticker)
        
        # Initialize price tickers
        for symbol in market_state.stock_prices.keys():
            price_widget = ModernPriceWidget(symbol)
            self.ticker_layout.addWidget(price_widget)
            self.price_widgets[symbol] = price_widget

    def setupTimers(self):
        """Setup timers for data refresh"""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
    
    def update_display(self):
        """Update all display components with current market data"""
        try:
            # Get latest market data
            market_data = market_state.get_market_state()
            
            # Update price widgets
            for symbol, widget in self.price_widgets.items():
                price = market_data['prices'].get(symbol, 0)
                change = market_data['price_changes'].get(symbol, 0)
                volume = market_data['volumes'].get(symbol, 0)
                widget.update_price(price, change, volume)
            
            # Update market table
            self.update_market_table(market_data)
            
            # Update portfolio information (team 0 for example)
            self.update_portfolio_view()
            
            # Update market status
            status = market_session.get_session_status()
            is_open = status['is_active'] and not market_session.pause_lock
            session_info = f"Session {status['current_session']} of {status['max_sessions']}"
            self.status_bar.set_status(is_open, session_info)
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def update_market_table(self, market_data):
        """Update market data table with current prices and volumes"""
        symbols = market_state.stock_prices.keys()
        self.market_table.setRowCount(len(symbols))
        
        for row, symbol in enumerate(symbols):
            # Symbol
            symbol_item = QTableWidgetItem(symbol)
            
            # Price with formatting
            price = market_data['prices'].get(symbol, 0)
            price_item = QTableWidgetItem(f"${price:,.2f}")
            price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Change percentage
            change = market_data['price_changes'].get(symbol, 0)
            change_item = QTableWidgetItem(f"{change:+.2f}%")
            change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Set color based on change
            if change > 0:
                change_item.setForeground(QColor(THEME['positive']))
            elif change < 0:
                change_item.setForeground(QColor(THEME['negative']))
            
            # Trend indicator
            trend_item = QTableWidgetItem("▲" if change >= 0 else "▼")
            trend_item.setTextAlignment(Qt.AlignCenter)
            if change > 0:
                trend_item.setForeground(QColor(THEME['positive']))
            elif change < 0:
                trend_item.setForeground(QColor(THEME['negative']))
            else:
                trend_item.setForeground(QColor(THEME['neutral']))
            
            # Volume
            volume = market_data['volumes'].get(symbol, 0)
            volume_item = QTableWidgetItem(f"{volume:,}")
            volume_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Available quantity
            available = market_data['quantities'].get(symbol, 0)
            available_item = QTableWidgetItem(f"{available:,}")
            available_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Add items to table
            self.market_table.setItem(row, 0, symbol_item)
            self.market_table.setItem(row, 1, price_item)
            self.market_table.setItem(row, 2, change_item)
            self.market_table.setItem(row, 3, trend_item)
            self.market_table.setItem(row, 4, volume_item)
            self.market_table.setItem(row, 5, available_item)
    
    def update_portfolio_view(self):
        """Update portfolio view with current holdings data"""
        try:
            # Get portfolio data for team 0
            portfolio = market_state.get_team_portfolio(0)
            
            # Update summary cards
            self.cash_card.update_value(f"${portfolio['cash']:,.2f}")
            self.portfolio_value_card.update_value(f"${portfolio['total_value']:,.2f}")
            
            # Calculate profit/loss
            initial_value = market_state.STARTING_BUDGET
            profit_loss = portfolio['total_value'] - initial_value
            profit_percent = (profit_loss / initial_value) * 100 if initial_value > 0 else 0
            
            profit_text = f"${profit_loss:,.2f} ({profit_percent:+.2f}%)"
            profit_color = THEME['positive'] if profit_loss >= 0 else THEME['negative']
            self.profit_loss_card.update_value(profit_text, profit_color)
            
            # Update holdings table
            holdings = portfolio['holdings']
            self.holdings_table.setRowCount(len(holdings))
            
            for row, (symbol, quantity) in enumerate(holdings.items()):
                # Symbol
                symbol_item = QTableWidgetItem(symbol)
                
                # Quantity
                quantity_item = QTableWidgetItem(f"{quantity:,}")
                quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Average cost - using 0 as placeholder since it's not tracked
                avg_cost = 0
                avg_cost_item = QTableWidgetItem("$0.00")
                avg_cost_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Current price
                current_price = market_state.stock_prices.get(symbol, 0)
                current_price_item = QTableWidgetItem(f"${current_price:,.2f}")
                current_price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Profit/Loss
                position_pl = (current_price - avg_cost) * quantity
                pl_item = QTableWidgetItem(f"${position_pl:,.2f}")
                pl_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                if position_pl > 0:
                    pl_item.setForeground(QColor(THEME['positive']))
                elif position_pl < 0:
                    pl_item.setForeground(QColor(THEME['negative']))
                
                # Add items to table
                self.holdings_table.setItem(row, 0, symbol_item)
                self.holdings_table.setItem(row, 1, quantity_item)
                self.holdings_table.setItem(row, 2, avg_cost_item)
                self.holdings_table.setItem(row, 3, current_price_item)
                self.holdings_table.setItem(row, 4, pl_item)
            
            # Update action log with recent transactions
            if 'transactions' in portfolio and portfolio['transactions']:
                recent = portfolio['transactions'][0]  # Most recent transaction
                
                # Format message based on transaction type
                if recent['type'] == 'buy':
                    msg = f"Bought {recent['quantity']} shares of {recent['stock']} at ${recent['price']:.2f}"
                elif recent['type'] == 'sell':
                    msg = f"Sold {recent['quantity']} shares of {recent['stock']} at ${recent['price']:.2f}"
                else:
                    msg = f"Transaction: {recent['type']} {recent['quantity']} {recent['stock']}"
                
                # Add timestamp
                timestamp = time.strftime("%H:%M:%S", time.localtime(recent['timestamp']))
                log_entry = f"[{timestamp}] {msg}"
                
                # Add to log if this is a new entry (avoid duplicates)
                if not self.action_log.toPlainText().endswith(log_entry):
                    self.action_log.append(log_entry)
            
        except Exception as e:
            logger.error(f"Error updating portfolio view: {e}")
            self.action_log.append(f"Error updating portfolio: {str(e)}")
