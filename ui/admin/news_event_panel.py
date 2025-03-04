from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QPushButton, QLabel, QLineEdit, QDoubleSpinBox,
                            QTextEdit, QListWidget, QAbstractItemView, QFormLayout,
                            QCheckBox)  # Add QCheckBox
from simulation import market_state
from simulation.market_simulation import market_session, market_simulation  # Add market_simulation import

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
        self.selected_stocks = set()  # Track selected stocks
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
        
        # Modify stock selector to support better multi-selection
        stock_label = QLabel("Select Stocks to Manipulate:")
        stock_layout = QVBoxLayout()
        self.stock_list = QListWidget()
        self.stock_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.stock_list.itemSelectionChanged.connect(self.update_selected_stocks)
        
        # Add "Select All" checkbox
        self.select_all = QCheckBox("Select All Stocks")
        self.select_all.stateChanged.connect(self.toggle_all_stocks)
        stock_layout.addWidget(self.select_all)
        stock_layout.addWidget(stock_label)
        stock_layout.addWidget(self.stock_list)
        event_layout.addRow(stock_layout)

        # Add selected stocks display
        self.selected_label = QLabel("Selected: None")
        stock_layout.addWidget(self.selected_label)
        
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
        self.selected_stocks.clear()
        for stock in sorted(market_state.stock_prices.keys()):  # Sort alphabetically
            self.stock_list.addItem(stock)
        self.update_selected_label()

    def toggle_all_stocks(self, state):
        """Toggle selection of all stocks"""
        for i in range(self.stock_list.count()):
            item = self.stock_list.item(i)
            item.setSelected(state == 2)  # 2 is Checked state
        self.update_selected_stocks()

    def update_selected_stocks(self):
        """Update the set of selected stocks"""
        self.selected_stocks = {item.text() for item in self.stock_list.selectedItems()}
        self.update_selected_label()

    def update_selected_label(self):
        """Update the label showing selected stocks"""
        if not self.selected_stocks:
            text = "Selected: None"
        else:
            text = "Selected: " + ", ".join(sorted(self.selected_stocks))
        self.selected_label.setText(text)

    def inject_event(self):
        """Inject the news event into the market"""
        selected_stocks = list(self.selected_stocks)
        if not selected_stocks:
            self.log_event("Error: No stocks selected")
            return

        impact_percent = self.impact_spinner.value()
        
        # Add the news impact to market session
        market_session.add_news_impact(selected_stocks, impact_percent)
        
        event_data = {
            'title': self.event_title.text(),
            'description': self.description.toPlainText(),
            'stocks': selected_stocks,
            'impact': impact_percent / 100.0
        }

        # Now market_simulation will be defined
        market_simulation.inject_news_event(event_data)
        self.log_event(f"Event Injected: {event_data['title']} "
                      f"(Target Impact: {impact_percent:+.1f}% on {', '.join(selected_stocks)})")

        # Clear selections after injection
        self.stock_list.clearSelection()
        self.selected_stocks.clear()
        self.update_selected_label()

    def log_event(self, message):
        """Add an entry to the event log"""
        self.event_log.append(message)
