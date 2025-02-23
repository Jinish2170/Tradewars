import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QGroupBox, QFrame, QSplitter, QSizePolicy, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea)
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
        layout.setSpacing(4)
        layout.setContentsMargins(15, 12, 15, 12)
        
        # Symbol and price container
        header_layout = QHBoxLayout()
        
        # Symbol with stock icon
        symbol_container = QHBoxLayout()
        symbol_container.setSpacing(6)
        
        # Add stock icon (▲ or ▼)
        self.trend_label = QLabel("▲")
        self.trend_label.setObjectName("trend")
        symbol_container.addWidget(self.trend_label)
        
        self.symbol_label = QLabel(self.symbol)
        self.symbol_label.setObjectName("symbol")
        symbol_container.addWidget(self.symbol_label)
        
        header_layout.addLayout(symbol_container)
        header_layout.addStretch()
        
        # Price with large font
        self.price_label = QLabel("$0.00")
        self.price_label.setObjectName("price")
        header_layout.addWidget(self.price_label)
        
        # Add main price section
        layout.addLayout(header_layout)
        
        # Change and volume in a horizontal layout
        stats_layout = QHBoxLayout()
        
        self.change_label = QLabel("0.00%")
        self.change_label.setObjectName("change")
        stats_layout.addWidget(self.change_label)
        
        stats_layout.addStretch()
        
        self.volume_label = QLabel("Vol: 0")
        self.volume_label.setObjectName("volume")
        stats_layout.addWidget(self.volume_label)
        
        layout.addLayout(stats_layout)
        
        self.setStyleSheet(PRICE_TICKER_STYLE)
    
    def update_price(self, new_price, price_change, volume=0):
        # Update trend arrow
        self.trend_label.setText("▲" if new_price >= self.last_price else "▼")
        self.trend_label.setObjectName("trend_up" if new_price >= self.last_price else "trend_down")
        
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
        # Create main layout with padding and spacing
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(1)
        main_layout.setContentsMargins(1, 1, 1, 1)

        # Top bar with market overview
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # Main content area
        content_area = QHBoxLayout()
        
        # Left side: Chart container
        chart_container = self.create_chart_container()
        content_area.addWidget(chart_container, stretch=2)
        
        # Right side: Leaderboard
        leaderboard = self.create_leaderboard_container()
        content_area.addWidget(leaderboard, stretch=1)
        
        main_layout.addLayout(content_area)

    def create_top_bar(self):
        container = QFrame()
        container.setFixedHeight(80)
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_background']};
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Add price tickers in a horizontal scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        ticker_widget = QWidget()
        ticker_layout = QHBoxLayout(ticker_widget)
        ticker_layout.setSpacing(5)
        ticker_layout.setContentsMargins(0, 0, 0, 0)
        
        self.price_tickers = {}
        for symbol in ['TECH', 'BANK', 'AUTO']:
            ticker = self.create_enhanced_ticker(symbol)
            self.price_tickers[symbol] = ticker
            ticker_layout.addWidget(ticker)
        
        scroll.setWidget(ticker_widget)
        layout.addWidget(scroll)
        
        return container

    def create_market_depth(self):
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_background']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Market Depth")
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            border-bottom: 1px solid {COLORS['border']};
        """)
        layout.addWidget(header)
        
        # Add depth view here
        
        return container

    def create_leaderboard_container(self):
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_background']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Market Leaders")
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            border-bottom: 1px solid {COLORS['border']};
        """)
        layout.addWidget(header)
        
        # Leaderboard table
        self.leaderboard = self.create_leaderboard()
        layout.addWidget(self.leaderboard)
        
        return container

    def create_market_overview(self):
        market_overview = QGroupBox("Market Overview")
        market_overview.setStyleSheet(GROUP_BOX_STYLE)
        
        layout = QVBoxLayout(market_overview)
        layout.setSpacing(20)
        
        # Price tickers in a horizontal layout
        ticker_container = QWidget()
        ticker_layout = QHBoxLayout(ticker_container)
        ticker_layout.setSpacing(15)
        ticker_layout.setContentsMargins(0, 0, 0, 0)
        
        self.price_tickers = {}
        for symbol in ['TECH', 'BANK', 'AUTO']:
            ticker = self.create_enhanced_ticker(symbol)
            self.price_tickers[symbol] = ticker
            ticker_layout.addWidget(ticker)
        
        layout.addWidget(ticker_container)
        
        # Market health indicators
        health_container = self.create_health_indicators()
        layout.addWidget(health_container)
        
        return market_overview

    def create_enhanced_ticker(self, symbol):
        ticker = PriceTickerWidget(symbol)
        return ticker

    def create_health_indicators(self):
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        layout = QGridLayout(container)
        layout.setSpacing(20)
        
        indicators = [
            ("Volume", "volume"),
            ("Change", "change"),
            ("Volatility", "volatility"),
            ("Trend", "trend")
        ]
        
        for i, (label, id_name) in enumerate(indicators):
            indicator = self.create_indicator(label, id_name)
            row, col = divmod(i, 2)
            layout.addWidget(indicator, row, col)
        
        return container

    def create_indicator(self, label, id_name):
        widget = QFrame()
        widget.setObjectName(f"indicator_{id_name}")
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_background']};
                border-radius: 6px;
                padding: 10px;
            }}
            QLabel#label {{
                color: {COLORS['text_secondary']};
                font-size: 12px;
            }}
            QLabel#value {{
                color: {COLORS['text']};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        label_widget = QLabel(label)
        label_widget.setObjectName("label")
        
        value_widget = QLabel("0")
        value_widget.setObjectName("value")
        
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        
        return widget

    def create_chart_container(self):
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_background']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        return container

    def create_order_book(self):
        """Create order book display widget"""
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card_background']};
                border: 1px solid {COLORS['border']};
                border-radius: 4px;
            }}
        """)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Order Book")
        header.setStyleSheet(f"""
            color: {COLORS['text']};
            font-size: 14px;
            font-weight: bold;
            padding: 10px;
            border-bottom: 1px solid {COLORS['border']};
        """)
        layout.addWidget(header)
        
        # Create order book table
        self.order_book_table = QTableWidget()
        self.order_book_table.setColumnCount(3)
        self.order_book_table.setHorizontalHeaderLabels(['Price', 'Quantity', 'Total'])
        self.order_book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.order_book_table.setStyleSheet(MARKET_TABLE_STYLE)
        
        # Disable editing and selection
        self.order_book_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.order_book_table.setSelectionMode(QTableWidget.NoSelection)
        
        layout.addWidget(self.order_book_table)
        return container

    def create_leaderboard(self):
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(['Rank', 'Team', 'Portfolio Value', 'Change'])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Set fixed height and style
        table.setMinimumHeight(300)
        table.setMaximumHeight(400)
        
        # Apply enhanced table styling
        table.setStyleSheet(MARKET_TABLE_STYLE + """
            QTableWidget {
                background-color: transparent;
            }
            QTableWidget::item {
                color: """ + COLORS['text'] + """;
            }
            QTableWidget::item:selected {
                background-color: """ + COLORS['accent'] + "40" + """;
            }
        """)
        
        # Disable editing
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Enable sorting
        table.setSortingEnabled(True)
        
        # Set alternating row colors
        table.setAlternatingRowColors(True)
        
        # Set selection behavior
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.SingleSelection)
        
        return table

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
