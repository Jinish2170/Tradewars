from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QTabWidget, QPushButton, QWidget
# Use relative imports for files in same directory
from .market_control_panel import MarketControlPanel
from .news_event_panel import NewsEventPanel
from .settings_panel import SettingsPanel
# Use absolute import for simulation module
from simulation import market_simulation
from ..styles import BUTTON_STYLE, COLORS

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.trading_window = None  # Store reference to trading window
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Add Launch Trading View button at the top
        self.launch_btn = QPushButton("Launch Trading View")
        self.launch_btn.setStyleSheet(
            BUTTON_STYLE + f"""
            QPushButton {{
                background-color: {COLORS['accent']};
                margin: 10px;
                padding: 12px;
                font-size: 14px;
            }}
            """
        )
        self.launch_btn.clicked.connect(self.launch_trading_view)
        layout.addWidget(self.launch_btn)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Market Control Panel
        market_panel = MarketControlPanel()
        tabs.addTab(market_panel, "Market Control")
        
        # News/Event Panel
        news_panel = NewsEventPanel()
        tabs.addTab(news_panel, "News & Events")
        
        # Settings Panel
        settings_panel = SettingsPanel()
        tabs.addTab(settings_panel, "Settings")
        
        layout.addWidget(tabs)
        self.setCentralWidget(central_widget)
        self.statusBar().showMessage("Ready")

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
