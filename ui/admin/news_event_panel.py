from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QPushButton, QLabel, QLineEdit, QDoubleSpinBox,
                            QTextEdit, QListWidget, QAbstractItemView, QFormLayout)
from simulation import market_state, market_simulation  # Fix import path

GROUP_BOX_STYLE = """
QGroupBox {
    font-weight: bold;
    border: 1px solid gray;
    border-radius: 5px;
    margin-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
}
"""

class NewsEventPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # News Event Creator
        event_group = QGroupBox("Create Market News Event")
        event_group.setStyleSheet(GROUP_BOX_STYLE)
        event_layout = QFormLayout()
        event_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Title field
        self.event_title = QLineEdit()
        self.event_title.setPlaceholderText("Event Title (e.g. 'Tech Sector Boom')")
        self.event_title.setMinimumWidth(300)
        event_layout.addRow("Title:", self.event_title)
        
        # Stock selector
        stock_label = QLabel("Affected Stocks:")
        stock_layout = QVBoxLayout()
        self.stock_list = QListWidget()
        self.stock_list.setSelectionMode(QAbstractItemView.MultiSelection)
        stock_layout.addWidget(stock_label)
        stock_layout.addWidget(self.stock_list)
        event_layout.addRow(stock_layout)
        
        # Impact magnitude
        self.impact_spinner = QDoubleSpinBox()
        self.impact_spinner.setRange(-100, 100)
        self.impact_spinner.setValue(0)
        self.impact_spinner.setSuffix("%")
        event_layout.addRow("Impact Magnitude:", self.impact_spinner)
        
        # Description field
        self.description = QTextEdit()
        self.description.setPlaceholderText("Event Description")
        event_layout.addRow("Description:", self.description)
        
        # Submit button
        self.submit_button = QPushButton("Inject News Event")
        self.submit_button.clicked.connect(self.inject_event)
        event_layout.addRow(self.submit_button)
        
        event_group.setLayout(event_layout)
        layout.addWidget(event_group)
        
        # Event log
        log_group = QGroupBox("Event Log")
        log_group.setStyleSheet(GROUP_BOX_STYLE)
        log_layout = QVBoxLayout()
        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        log_layout.addWidget(self.event_log)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        self.setLayout(layout)
        self.update_stock_list()

    def update_stock_list(self):
        """Update the list of available stocks"""
        self.stock_list.clear()
        for stock in market_state.stock_prices.keys():
            self.stock_list.addItem(stock)

    def inject_event(self):
        """Inject the news event into the market"""
        selected_stocks = [item.text() for item in self.stock_list.selectedItems()]
        if not selected_stocks:
            self.log_event("Error: No stocks selected")
            return

        event_data = {
            'title': self.event_title.text(),
            'description': self.description.toPlainText(),
            'stocks': selected_stocks,
            'impact': self.impact_spinner.value() / 100.0
        }

        market_simulation.inject_news_event(event_data)
        self.log_event(f"Event Injected: {event_data['title']} "
                      f"(Impact: {event_data['impact']*100:+.1f}% on {', '.join(selected_stocks)})")

    def log_event(self, message):
        """Add an entry to the event log"""
        self.event_log.append(message)
