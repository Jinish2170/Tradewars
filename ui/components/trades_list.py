from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from ..styles import COLORS

class RecentTradesList(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()
        
    def setupUI(self):
        layout = QVBoxLayout(self)
        
        self.trades_list = QListWidget()
        self.trades_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['card_background']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS['border']};
            }}
        """)
        
        layout.addWidget(self.trades_list)
        
    def add_trade(self, trade_info):
        item = QListWidgetItem(trade_info)
        self.trades_list.insertItem(0, item)  # Add at top
        if self.trades_list.count() > 100:  # Keep last 100 trades
            self.trades_list.takeItem(self.trades_list.count() - 1)
