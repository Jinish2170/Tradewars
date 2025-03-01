from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                          QFrame, QLabel, QPushButton, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon
from .market_control_panel import MarketControlPanel
from .news_event_panel import NewsEventPanel
from .settings_panel import SettingsPanel
from simulation import market_simulation
from ..styles import COLORS

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.trading_window = None
        self.init_ui()
        self.setup_timers()

    def init_ui(self):
        self.setWindowTitle("TradeWars Admin Dashboard")
        self.setMinimumSize(1280, 800)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Create main content area
        content_area = self.create_content_area()
        main_layout.addWidget(content_area, 1)
        
        self.setCentralWidget(main_widget)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(f"""
            QFrame#sidebar {{
                background-color: {COLORS['card']};
                border-right: 1px solid {COLORS['border']};
                min-width: 250px;
                max-width: 250px;
            }}
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add logo/header section
        header = QFrame()
        header.setStyleSheet(f"""
            background-color: {COLORS['primary']};
            padding: 20px;
        """)
        header_layout = QVBoxLayout(header)
        
        title = QLabel("TradeWars")
        title.setStyleSheet(f"""
            color: {COLORS['white']};
            font-size: 24px;
            font-weight: bold;
        """)
        subtitle = QLabel("Admin Dashboard")
        subtitle.setStyleSheet(f"""
            color: {COLORS['text_secondary']};
            font-size: 14px;
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        layout.addWidget(header)
        
        # Navigation buttons
        nav_items = [
            ("Market Control", "🏦", 0),
            ("News & Events", "📰", 1),
            ("Settings", "⚙️", 2)
        ]
        
        for text, icon, index in nav_items:
            btn = self.create_nav_button(text, icon, index)
            layout.addWidget(btn)
        
        # Add trading view launch button at bottom
        layout.addStretch()
        self.launch_btn = self.create_action_button(
            "Launch Trading View", 
            "🚀",
            self.launch_trading_view
        )
        layout.addWidget(self.launch_btn)
        
        return sidebar

    def create_nav_button(self, text, icon, index):
        btn = QPushButton(f" {icon}  {text}")
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setFixedHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_secondary']};
                border: none;
                text-align: left;
                padding: 0 20px;
                font-size: 15px;
                font-weight: 500;
            }}
            QPushButton:checked {{
                background-color: {COLORS['primary']};
                color: {COLORS['white']};
                border-left: 4px solid {COLORS['accent']};
                font-weight: bold;
            }}
            QPushButton:hover:!checked {{
                background-color: {COLORS['hover']};
                color: {COLORS['white']};
            }}
        """)
        btn.clicked.connect(lambda: self.content_stack.setCurrentIndex(index))
        if index == 0:
            btn.setChecked(True)
        return btn

    def create_action_button(self, text, icon, callback):
        btn = QPushButton(f" {icon}  {text}")
        btn.setFixedHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                color: {COLORS['white']};
                border: none;
                padding: 0 20px;
                font-size: 15px;
                font-weight: bold;
                margin: 10px 15px;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_light']};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def create_content_area(self):
        container = QFrame()
        container.setStyleSheet(f"""
            background-color: {COLORS['background']};
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Status bar at top
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
        
        # Stacked widget for content
        self.content_stack = QStackedWidget()
        
        # Add panels
        self.market_panel = MarketControlPanel()
        self.news_panel = NewsEventPanel()
        self.settings_panel = SettingsPanel()
        
        self.content_stack.addWidget(self.market_panel)
        self.content_stack.addWidget(self.news_panel)
        self.content_stack.addWidget(self.settings_panel)
        
        layout.addWidget(self.content_stack)
        return container

    def create_status_bar(self):
        status_bar = QFrame()
        status_bar.setStyleSheet(f"""
            background-color: {COLORS['card']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        status_bar.setFixedHeight(50)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        self.status_label = QLabel("Market Status: Active")
        self.status_label.setStyleSheet(f"color: {COLORS['text']};")
        layout.addWidget(self.status_label)
        
        return status_bar

    def setup_timers(self):
        """Setup refresh timers"""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_all)
        self.update_timer.start(1000)  # Update every second

    def update_all(self):
        """Update all panels"""
        current_panel = self.content_stack.currentWidget()
        if hasattr(current_panel, 'update_display'):
            current_panel.update_display()

    def launch_trading_view(self):
        """Launch trading view in a separate window"""
        from ..main_window import launch_trading_view
        
        # Close existing trading window if it exists
        if self.trading_window is not None:
            self.trading_window.close()
            
        # Create new trading window
        self.trading_window = launch_trading_view()
        
        # Update button text
        self.launch_btn.setText("Trading View Launched")
        self.statusBar().showMessage("Trading view launched in separate window")

    def launch_ipo(self):
        ipo_data = {
            'stock': self.ipo_stock_name.text(),
            'initial_price': self.ipo_price.value(),
            'available_quantity': self.ipo_quantity.value()
        }
        market_simulation.inject_IPO(ipo_data)

    def publish_news(self):
        event_data = {
            'content': self.news_text.toPlainText(),
            'impact': self.impact_spin.value() / 100.0
        }
        market_simulation.inject_news_event(event_data)
