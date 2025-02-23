from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QPushButton, QLabel, QLineEdit, QDoubleSpinBox,
                            QTextEdit, QListWidget, QAbstractItemView)
from simulation import market_state, market_simulation  # Fix import path

class NewsEventPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # News Event Creation Form
        form_group = QGroupBox("Create News Event")
        form_layout = QVBoxLayout()

        # Title
        title_layout = QHBoxLayout()
        self.event_title = QLineEdit()
        self.event_title.setPlaceholderText("Event Title")
        title_layout.addWidget(QLabel("Title:"))
        title_layout.addWidget(self.event_title)
        form_layout.addLayout(title_layout)

        # Target Stocks
        stocks_layout = QVBoxLayout()
        self.stock_list = QListWidget()
        self.stock_list.setSelectionMode(QAbstractItemView.MultiSelection)
        stocks_layout.addWidget(QLabel("Target Stocks:"))
        stocks_layout.addWidget(self.stock_list)
        form_layout.addLayout(stocks_layout)

        # Impact Magnitude
        impact_layout = QHBoxLayout()
        self.impact_spinner = QDoubleSpinBox()
        self.impact_spinner.setRange(-100, 100)
        self.impact_spinner.setValue(0)
        self.impact_spinner.setSuffix("%")
        impact_layout.addWidget(QLabel("Impact Magnitude:"))
        impact_layout.addWidget(self.impact_spinner)
        form_layout.addLayout(impact_layout)

        # Description
        self.description = QTextEdit()
        self.description.setPlaceholderText("Event Description")
        form_layout.addWidget(QLabel("Description:"))
        form_layout.addWidget(self.description)

        # Submit Button
        self.submit_button = QPushButton("Inject News Event")
        self.submit_button.clicked.connect(self.inject_event)
        form_layout.addWidget(self.submit_button)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Event Log
        log_group = QGroupBox("Event Log")
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
