import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QFrame, QSplitter, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from simulation import market_state
from utils.decorators import safe_operation
from utils.logger import logger
from .styles import *
from .components.price_chart import PriceChart
from .components.volume_chart import VolumeChart
from .components.trades_list import RecentTradesList

class PriceTickerWidget(QFrame):
    def __init__(self, symbol, parent=None):
        super().__init__(parent)
        self.symbol = symbol
        self.last_price = 0
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Symbol header with icon
        header_layout = QHBoxLayout()
        self.symbol_label = QLabel(self.symbol)
        self.symbol_label.setObjectName("symbol")
        self.symbol_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(self.symbol_label)
        header_layout.addStretch()
        
        # Price display with large font
        self.price_label = QLabel("$0.00")
        self.price_label.setObjectName("price")
        self.price_label.setAlignment(Qt.AlignCenter)
        
        # Change percentage with animation
        self.change_label = QLabel("0.00%")
        self.change_label.setObjectName("change")
        self.change_label.setAlignment(Qt.AlignCenter)
        
        # Volume indicator (new)
        self.volume_label = QLabel("Vol: 0")
        self.volume_label.setObjectName("volume")
        self.volume_label.setAlignment(Qt.AlignRight)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.price_label)
        layout.addWidget(self.change_label)
        layout.addWidget(self.volume_label)
        
        self.setStyleSheet(PRICE_TICKER_STYLE)
        
    def update_price(self, new_price, price_change, volume=0):
        # Animate price change
        if new_price != self.last_price:
            animation_class = "price_up" if new_price > self.last_price else "price_down"
            self.price_label.setProperty("animation", animation_class)
            self.style().unpolish(self.price_label)
            self.style().polish(self.price_label)
        
        self.price_label.setText(f"${new_price:,.2f}")
        self.change_label.setText(f"{price_change:+.2f}%")
        self.volume_label.setText(f"Vol: {volume:,}")
        self.last_price = new_price
        
        # Update color based on change
        self.change_label.setObjectName(
            "change_up" if price_change >= 0 else "change_down"
        )

class ParticipantView(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.setupTimers()

    def setupUI(self):
        # Create main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left side: Market overview
        left_panel = QVBoxLayout()
        self.market_overview = self.create_market_overview()
        left_panel.addWidget(self.market_overview)
        left_panel.addStretch()

        # Right side: Leaderboard
        right_panel = QVBoxLayout()
        leaderboard_label = self.create_section_label("Team Rankings")
        self.leaderboard = self.create_leaderboard()
        right_panel.addWidget(leaderboard_label)
        right_panel.addWidget(self.leaderboard)
        right_panel.addStretch()

        # Add panels to main layout with proper proportions
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)

    def create_market_overview(self):
        # Enhanced Market Overview Section
        market_overview = QGroupBox("Market Overview")
        market_overview.setStyleSheet(f"""
            {GROUP_BOX_STYLE}
            QGroupBox {{
                font-size: 14px;  /* Increased font size */
            }}
        """)
        overview_layout = QGridLayout()
        overview_layout.setSpacing(20)

        # Price Tickers with improved layout
        ticker_container = QFrame()
        ticker_layout = QHBoxLayout(ticker_container)
        ticker_layout.setSpacing(15)
        
        self.price_tickers = {}
        for i, symbol in enumerate(['TECH', 'BANK', 'AUTO']):
            ticker = PriceTickerWidget(symbol)
            self.price_tickers[symbol] = ticker
            ticker_layout.addWidget(ticker)

        overview_layout.addWidget(ticker_container, 0, 0, 1, 2)

        # Market Health Indicators with enhanced styling
        health_frame = QFrame()
        health_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        health_layout = QGridLayout(health_frame)
        
        # Create health indicator widgets
        indicators = [
            ("Volume", self.create_indicator_widget()),
            ("Average Change", self.create_indicator_widget()),
            ("Volatility", self.create_indicator_widget()),
            ("Market Trend", self.create_indicator_widget())
        ]
        
        for i, (label, widget) in enumerate(indicators):
            row = i // 2
            col = i % 2
            health_layout.addWidget(QLabel(label), row * 2, col)
            health_layout.addWidget(widget, row * 2 + 1, col)
            
        overview_layout.addWidget(health_frame, 1, 0, 1, 2)
        market_overview.setLayout(overview_layout)
        
        return market_overview

    def create_indicator_widget(self):
        label = QLabel("0.00")
        label.setStyleSheet("""
            QLabel {
                font-size: 20px;   /* Larger font */
                font-weight: bold;
                color: #61AFEF;
                padding: 5px;
                background: rgba(97, 175, 239, 0.1);
                border-radius: 5px;
            }
        """)
        return label

    def create_leaderboard(self):
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Rank', 'Team', 'Portfolio Value', 'Change'])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Style the table
        table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['card_background']};
                border: 1px solid {COLORS['chart_grid']};
                border-radius: 4px;
                gridline-color: {COLORS['chart_grid']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
                padding: 8px;
                border: none;
                border-bottom: 1px solid {COLORS['chart_grid']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}
        """)
        
        # Set fixed height to ensure visibility
        table.setMinimumHeight(300)
        table.setMaximumHeight(400)
        
        return table

    def create_section_label(self, text):
        label = QLabel(text)
        label.setStyleSheet(f"""
            font-size: 16px;
            color: {COLORS['text']};
            padding: 8px;
            font-weight: bold;
        """)
        return label

    def setupTimers(self):
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)

    @safe_operation
    def update_display(self):
        """Update display with enhanced market data."""
        try:
            # Get market state data
            market_state_data = market_state.get_market_state()
            health_data = market_state.get_market_health()
            
            # Update price tickers with animation effect
            for symbol, ticker in self.price_tickers.items():
                if symbol in market_state_data['prices']:
                    price = market_state_data['prices'][symbol]
                    change = market_state_data['price_changes'][symbol]
                    volume = market_state_data['volumes'][symbol]
                    ticker.update_price(price, change, volume)
            
            # Update health indicators with formatted values
            indicators = self.findChildren(QLabel)
            for indicator in indicators:
                if "Volume" in indicator.text():
                    indicator.setText(f"{health_data['total_volume']:,}")
                elif "Change" in indicator.text():
                    value = health_data['average_change']
                    indicator.setText(f"{value:+.2f}%")
                    indicator.setStyleSheet(self.get_change_color(value))
                elif "Volatility" in indicator.text():
                    indicator.setText(f"{health_data['volatility']:.2f}%")
                elif "Trend" in indicator.text():
                    trend = health_data.get('trend', 'NEUTRAL')
                    indicator.setText(trend)
                    indicator.setStyleSheet(self.get_trend_color(trend))
                    
            # Update leaderboard
            self.update_leaderboard()
                    
        except Exception as e:
            logger.error("Display update error", exc_info=True)

    def get_change_color(self, value):
        if value > 0:
            return "color: #98C379;"  # Green for positive
        elif value < 0:
            return "color: #E06C75;"  # Red for negative
        return "color: #61AFEF;"      # Blue for neutral

    def get_trend_color(self, trend):
        colors = {
            'BULLISH': "#98C379",
            'BEARISH': "#E06C75",
            'NEUTRAL': "#61AFEF"
        }
        return f"color: {colors.get(trend, '#61AFEF')};"

    def update_leaderboard(self):
        """Update leaderboard with current team rankings"""
        from simulation import market_state
        
        # Get all team portfolios and sort by total value
        portfolios = []
        for team_id in range(market_state.TEAM_COUNT):
            portfolio = market_state.get_team_portfolio(team_id)
            if portfolio:
                portfolios.append((team_id, portfolio))
        
        # Sort by total value
        portfolios.sort(key=lambda x: x[1]['total_value'], reverse=True)
        
        # Update table
        self.leaderboard.setRowCount(len(portfolios))
        for rank, (team_id, portfolio) in enumerate(portfolios):
            # Rank
            rank_item = QTableWidgetItem(str(rank + 1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            
            # Team name
            team_item = QTableWidgetItem(f"Team {team_id}")
            
            # Portfolio value
            value_item = QTableWidgetItem(f"${portfolio['total_value']:,.2f}")
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Change (calculate percentage change)
            initial_value = market_state.STARTING_BUDGET
            change = ((portfolio['total_value'] - initial_value) / initial_value) * 100
            change_item = QTableWidgetItem(f"{change:+.2f}%")
            change_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Set colors based on performance
            if change > 0:
                change_item.setForeground(Qt.green)
            elif change < 0:
                change_item.setForeground(Qt.red)
            
            # Add items to row
            self.leaderboard.setItem(rank, 0, rank_item)
            self.leaderboard.setItem(rank, 1, team_item)
            self.leaderboard.setItem(rank, 2, value_item)
            self.leaderboard.setItem(rank, 3, change_item)
