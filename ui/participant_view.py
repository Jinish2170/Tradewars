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
    'selection': '#2C5282',
    # Add font size definitions
    'font_small': '16px',    # Was ~8px
    'font_normal': '18px',   # Was ~9px
    'font_medium': '22px',   # Was ~11px
    'font_large': '28px',    # Was ~14px
    'font_xlarge': '36px',   # Was ~18px
    'font_xxlarge': '48px'   # Was ~24px
}

# Modern card style with border radius and subtle shadows
CARD_STYLE = f"""
QFrame.Card {{
    background-color: {THEME['card']};
    border: 1px solid {THEME['border']};
    border-radius: 8px;
    font-size: {THEME['font_normal']};  /* Added base font size */
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
    font-size: {THEME['font_normal']};  /* Increased font size */
}}

QTableWidget::item {{
    padding: 12px;  /* Increased padding for larger text */
    border-bottom: 1px solid {THEME['border']};
}}

QHeaderView::section {{
    background-color: {THEME['header']};
    color: {THEME['text_secondary']};
    font-weight: bold;
    font-size: {THEME['font_medium']};  /* Larger header font */
    padding: 12px;  /* More padding for headers */
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
        
        # Symbol row with icon - increase font sizes
        symbol_row = QHBoxLayout()
        self.symbol_label = QLabel(self.symbol)
        self.symbol_label.setStyleSheet(f"color: {THEME['text']}; font-weight: bold; font-size: {THEME['font_large']};")
        
        self.trend_icon = QLabel()
        self.trend_icon.setFixedSize(24, 24)  # Increased from 16,16
        self.trend_icon.setStyleSheet(f"color: {THEME['positive']}; font-size: {THEME['font_large']};")
        
        symbol_row.addWidget(self.symbol_label)
        symbol_row.addStretch()
        symbol_row.addWidget(self.trend_icon)
        
        # Price row with much larger font
        price_row = QHBoxLayout()
        self.price_label = QLabel("$0.00")
        self.price_label.setStyleSheet(f"color: {THEME['text']}; font-weight: bold; font-size: {THEME['font_xxlarge']};")
        
        self.change_label = QLabel("0.00%")
        self.change_label.setStyleSheet(f"color: {THEME['positive']}; font-size: {THEME['font_medium']};")
        self.change_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        price_row.addWidget(self.price_label)
        price_row.addStretch()
        price_row.addWidget(self.change_label)
        
        # Volume row - larger text
        volume_row = QHBoxLayout()
        self.volume_label = QLabel("Volume: 0")
        self.volume_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: {THEME['font_normal']};")
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
        
        # Update trend icon with larger font
        if new_price > self.last_price:
            self.trend_icon.setText("▲")
            self.trend_icon.setStyleSheet(f"color: {THEME['positive']}; font-size: {THEME['font_large']};")
            self.change_label.setStyleSheet(f"color: {THEME['positive']}; font-size: {THEME['font_medium']};")
        elif new_price < self.last_price:
            self.trend_icon.setText("▼")
            self.trend_icon.setStyleSheet(f"color: {THEME['negative']}; font-size: {THEME['font_large']};")
            self.change_label.setStyleSheet(f"color: {THEME['negative']}; font-size: {THEME['font_medium']};")
        else:
            self.trend_icon.setText("■")
            self.trend_icon.setStyleSheet(f"color: {THEME['neutral']}; font-size: {THEME['font_large']};")
            self.change_label.setStyleSheet(f"color: {THEME['neutral']}; font-size: {THEME['font_medium']};")
        
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
            
            # Create a safer way to clear the effect
            # Store a reference to the label in a local variable
            label = self.price_label
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(lambda: self._safe_clear_effect(label))
            timer.start(1000)
        
        self.last_price = new_price

    # Add a helper method to safely clear the graphics effect
    def _safe_clear_effect(self, widget):
        """Safely clear graphics effect if widget still exists"""
        try:
            if widget and widget.isVisible():
                widget.setGraphicsEffect(None)
        except RuntimeError:
            # Widget was already deleted, nothing to do
            pass

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
        
        # Status indicator with larger symbols and text
        status_layout = QHBoxLayout()
        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet(f"color: {THEME['positive']}; font-size: {THEME['font_large']};")
        
        self.status_text = QLabel("Market Open")
        self.status_text.setStyleSheet(f"color: {THEME['text']}; font-weight: bold; font-size: {THEME['font_medium']};")
        
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addSpacing(20)
        
        # Session info
        self.session_label = QLabel("Session 1 of 5")
        self.session_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: {THEME['font_medium']};")
        
        # Market time
        self.time_label = QLabel(time.strftime("%H:%M:%S"))
        self.time_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: {THEME['font_medium']};")
        
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
            self.status_indicator.setStyleSheet(f"color: {THEME['positive']}; font-size: {THEME['font_large']};")
            self.status_text.setText("Market Open")
        else:
            self.status_indicator.setStyleSheet(f"color: {THEME['negative']}; font-size: {THEME['font_large']};")
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
        
        # Title label with larger font
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: {THEME['font_normal']};")
        
        # Value with extra large font
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {color}; font-size: {THEME['font_xlarge']}; font-weight: bold;")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        
    def update_value(self, new_value, color=None):
        self.value_label.setText(new_value)
        if color:
            self.value_label.setStyleSheet(f"color: {color}; font-size: {THEME['font_xlarge']}; font-weight: bold;")

class ParticipantView(QWidget):
    def __init__(self):
        super().__init__()
        if not hasattr(market_state, 'stock_prices') or not market_state.stock_prices:
            market_state.initialize_market()
        self.price_widgets = {}
        self.setupUI()
        self.setupTimers()
        
    def setupUI(self):
        # Make the app use our larger fonts globally
        self.setStyleSheet(f"""
            * {{
                font-size: {THEME['font_normal']};
            }}
            QLabel {{
                font-size: {THEME['font_medium']};
            }}
            QPushButton {{
                font-size: {THEME['font_normal']};
                padding: 8px 16px;
            }}
        """)
        
        # Set main layout
        self.setStyleSheet(f"background-color: {THEME['background']};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Market status bar
        self.status_bar = MarketStatusBar()
        main_layout.addWidget(self.status_bar)
        
        # Price tickers - increase size
        price_section = QFrame()
        price_section.setStyleSheet(CARD_STYLE)
        price_section.setObjectName("Card")
        price_section.setMinimumHeight(120)
        
        price_layout = QVBoxLayout(price_section)
        price_layout.setContentsMargins(15, 10, 15, 10)
        
        # Header with larger text
        header_layout = QHBoxLayout()
        header_label = QLabel("Market Prices")
        header_label.setStyleSheet(f"color: {THEME['text']}; font-size: {THEME['font_large']}; font-weight: bold;")
        header_layout.addWidget(header_label)
        
        price_layout.addLayout(header_layout)
        price_layout.addSpacing(5)
        
        # Price ticker scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        scroll_area.setFixedHeight(150)  # Increased from 100
        
        scroll_widget = QWidget()
        self.ticker_layout = QHBoxLayout(scroll_widget)
        self.ticker_layout.setContentsMargins(0, 0, 0, 0)
        self.ticker_layout.setSpacing(12)
        self.ticker_layout.setAlignment(Qt.AlignLeft)
        
        scroll_area.setWidget(scroll_widget)
        price_layout.addWidget(scroll_area)
        
        main_layout.addWidget(price_section)
        
        # Main content area with larger tab text
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
                padding: 12px 24px;  /* Increased padding */
                font-size: {THEME['font_medium']};  /* Larger font */
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
        self.market_table.verticalHeader().setDefaultSectionSize(48)  # Increased from 30
        
        market_tab_layout.addWidget(self.market_table)
        
        # Replace Portfolio tab with Team Performance tab
        team_performance_tab = QWidget()
        team_layout = QVBoxLayout(team_performance_tab)
        team_layout.setContentsMargins(15, 15, 15, 15)
        team_layout.setSpacing(8)  # Reduced spacing between elements
        
        # Team performance table directly at the top
        teams_frame = QFrame()
        teams_frame.setObjectName("Card")
        teams_frame.setStyleSheet(CARD_STYLE)
        
        teams_layout = QVBoxLayout(teams_frame)
        teams_layout.setContentsMargins(15, 12, 15, 12)
        teams_layout.setSpacing(8)  # Reduced spacing inside frame
        
        # Teams header with larger text
        teams_header = QHBoxLayout()
        teams_title = QLabel("Team Rankings")
        teams_title.setStyleSheet(f"color: {THEME['text']}; font-size: {THEME['font_large']}; font-weight: bold;")
        teams_header.addWidget(teams_title)
        teams_layout.addLayout(teams_header)
        
        # Team rankings table with more vertical space
        self.teams_table = QTableWidget()
        self.teams_table.setColumnCount(5)
        self.teams_table.setHorizontalHeaderLabels(["Team", "Cash", "Holdings Value", "Total Value", "% Change"])
        self.teams_table.setStyleSheet(MODERN_TABLE_STYLE)
        self.teams_table.setAlternatingRowColors(True)
        self.teams_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teams_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.teams_table.verticalHeader().setDefaultSectionSize(48)   # Increased from 30
        self.teams_table.setMinimumHeight(400)  # Give enough space for all teams
        
        teams_layout.addWidget(self.teams_table)
        
        # Market transactions log with reduced height
        log_layout = QVBoxLayout()
        log_layout.setSpacing(4)  # Reduced spacing
        log_title = QLabel("Recent Market Activity")
        log_title.setStyleSheet(f"color: {THEME['text']}; font-size: {THEME['font_large']}; font-weight: bold;")
        log_layout.addWidget(log_title)
        
        self.market_log = QTextEdit()
        self.market_log.setReadOnly(True)
        self.market_log.setFixedHeight(120)  # Increased from 100
        self.market_log.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['header']};
                color: {THEME['text']};
                border: none;
                border-radius: 4px;
                font-family: monospace;
                font-size: {THEME['font_normal']};  /* Larger text */
                padding: 10px;
            }}
        """)
        log_layout.addWidget(self.market_log)
        
        teams_layout.addLayout(log_layout)
        team_layout.addWidget(teams_frame)
        
        # Add tabs to tab widget
        content_tabs.addTab(market_tab, "Market Data")
        content_tabs.addTab(team_performance_tab, "Team Rankings")  # Changed tab name
        
        main_layout.addWidget(content_tabs, 1)  # Give it stretch factor for responsive sizing
        
        # News ticker at bottom
        news_ticker = QFrame()
        news_ticker.setFixedHeight(42)  # Increased from 30
        news_ticker.setStyleSheet(f"background-color: {THEME['header']}; border-radius: 4px;")
        
        news_layout = QHBoxLayout(news_ticker)
        news_layout.setContentsMargins(15, 0, 15, 0)
        
        news_icon = QLabel("📢")
        news_icon.setStyleSheet(f"color: {THEME['accent']}; font-size: {THEME['font_large']};")
        
        self.news_label = QLabel("Welcome to the Trading Simulation!")
        self.news_label.setStyleSheet(f"color: {THEME['text']}; font-weight: bold; font-size: {THEME['font_medium']};")
        
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
            
            # Update team performance data
            self.update_team_performance()
            
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
        
        # Adjust table column width to fit larger text
        self.market_table.resizeColumnsToContents()
        self.market_table.resizeRowsToContents()
    
    def update_team_performance(self):
        """Update team performance data"""
        try:
            all_teams_data = []
            total_transactions = 0
            
            # Get data for all teams
            for team_id in range(market_state.TEAM_COUNT):
                try:
                    portfolio = market_state.get_team_portfolio(team_id)
                    
                    # Calculate performance metrics
                    initial_value = market_state.STARTING_BUDGET
                    profit_loss = portfolio['total_value'] - initial_value
                    profit_percent = (profit_loss / initial_value) * 100 if initial_value > 0 else 0
                    
                    # Add to totals for transactions count
                    if 'transactions' in portfolio:
                        total_transactions += len(portfolio['transactions'])
                    
                    # Add to team data collection
                    all_teams_data.append({
                        'team_id': team_id,
                        'cash': portfolio['cash'],
                        'holdings_value': portfolio['holdings_value'],
                        'total_value': portfolio['total_value'],
                        'profit_percent': profit_percent
                    })
                except Exception as e:
                    logger.error(f"Error getting portfolio for team {team_id}: {str(e)}")
            
            # Sort teams by total value (descending)
            all_teams_data.sort(key=lambda x: x['total_value'], reverse=True)
            
            # Update team table
            self.teams_table.setRowCount(len(all_teams_data))
            for row, team_data in enumerate(all_teams_data):
                # Team ID with rank
                team_item = QTableWidgetItem(f"Team {team_data['team_id']}")
                if row < 3:  # Top 3 teams get special formatting
                    team_item.setForeground(QColor(THEME['accent']))
                    font = team_item.font()
                    font.setBold(True)
                    team_item.setFont(font)
                
                # Cash
                cash_item = QTableWidgetItem(f"${team_data['cash']:,.2f}")
                cash_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Holdings value
                holdings_item = QTableWidgetItem(f"${team_data['holdings_value']:,.2f}")
                holdings_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Total value
                total_item = QTableWidgetItem(f"${team_data['total_value']:,.2f}")
                total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Percent change
                percent = team_data['profit_percent']
                percent_item = QTableWidgetItem(f"{percent:+.2f}%")
                percent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                if percent > 0:
                    percent_item.setForeground(QColor(THEME['positive']))
                elif percent < 0:
                    percent_item.setForeground(QColor(THEME['negative']))
                
                # Add items to table
                self.teams_table.setItem(row, 0, team_item)
                self.teams_table.setItem(row, 1, cash_item)
                self.teams_table.setItem(row, 2, holdings_item)
                self.teams_table.setItem(row, 3, total_item)
                self.teams_table.setItem(row, 4, percent_item)
            
            # Update market activity log with recent transactions
            self.update_market_activity_log()
            
            # Make sure the team rankings table adjusts to larger text
            self.teams_table.resizeColumnsToContents()
            self.teams_table.resizeRowsToContents()
            
        except Exception as e:
            logger.error(f"Error updating team performance: {str(e)}")
            self.market_log.append(f"Error updating performance data: {str(e)}")

    def update_market_activity_log(self):
        """Update the market activity log with recent transactions"""
        try:
            all_transactions = []
            
            # Collect recent transactions from all teams
            for team_id in range(market_state.TEAM_COUNT):
                try:
                    portfolio = market_state.get_team_portfolio(team_id)
                    if 'transactions' in portfolio and portfolio['transactions']:
                        for tx in portfolio['transactions']:
                            tx_copy = tx.copy()  # Create a copy to avoid modifying original
                            tx_copy['team_id'] = team_id
                            all_transactions.append(tx_copy)
                except Exception as e:
                    logger.error(f"Error getting transactions for team {team_id}: {str(e)}")
            
            # Sort by timestamp (most recent first)
            all_transactions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Take only the most recent 10 transactions
            recent_transactions = all_transactions[:10]
            
            # Get current log content to avoid duplicates
            current_log = self.market_log.toPlainText()
            
            # Add recent transactions to log
            for tx in recent_transactions:
                timestamp = time.strftime("%H:%M:%S", time.localtime(tx['timestamp']))
                
                # Format message based on transaction type
                if tx['type'] == 'buy':
                    msg = f"Team {tx['team_id']} bought {tx['quantity']} {tx['stock']} at ${tx['price']:.2f}"
                elif tx['type'] == 'sell':
                    msg = f"Team {tx['team_id']} sold {tx['quantity']} {tx['stock']} at ${tx['price']:.2f}"
                else:
                    msg = f"Team {tx['team_id']} {tx['type']} {tx['quantity']} {tx['stock']}"
                
                log_entry = f"[{timestamp}] {msg}"
                
                # Only add if not already in log
                if log_entry not in current_log:
                    self.market_log.append(log_entry)
                    
            # Add special handling for the log to ensure text is properly visible
            self.market_log.setFontPointSize(12)  # Set explicit point size for log text
                    
        except Exception as e:
            logger.error(f"Error updating market activity log: {str(e)}"
)
