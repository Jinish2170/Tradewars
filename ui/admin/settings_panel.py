from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
                            QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                            QTextEdit, QComboBox, QFormLayout, QMessageBox)
import config
import time  # Add this import
from simulation import market_state
from utils.logger import logger

class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Market Parameters
        param_group = QGroupBox("Market Parameters")
        param_layout = QVBoxLayout()

        # Demand Coefficient
        demand_layout = QHBoxLayout()
        self.demand_spin = QDoubleSpinBox()
        self.demand_spin.setRange(0.01, 1.0)
        self.demand_spin.setSingleStep(0.01)
        self.demand_spin.setValue(config.DEMAND_COEFFICIENT)
        demand_layout.addWidget(QLabel("Demand Coefficient:"))
        demand_layout.addWidget(self.demand_spin)
        param_layout.addLayout(demand_layout)

        # Event Coefficient
        event_layout = QHBoxLayout()
        self.event_spin = QDoubleSpinBox()
        self.event_spin.setRange(0.01, 1.0)
        self.event_spin.setSingleStep(0.01)
        self.event_spin.setValue(config.EVENT_COEFFICIENT)
        event_layout.addWidget(QLabel("Event Coefficient:"))
        event_layout.addWidget(self.event_spin)
        param_layout.addLayout(event_layout)

        # Random Noise
        noise_layout = QHBoxLayout()
        self.noise_spin = QDoubleSpinBox()
        self.noise_spin.setRange(0.0, 0.5)
        self.noise_spin.setSingleStep(0.01)
        self.noise_spin.setValue(config.RANDOM_NOISE)
        noise_layout.addWidget(QLabel("Random Noise:"))
        noise_layout.addWidget(self.noise_spin)
        param_layout.addLayout(noise_layout)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # Cash Management Group
        cash_group = QGroupBox("Team Cash Management")
        cash_layout = QFormLayout()

        # Team selector
        self.team_selector = QComboBox()
        self.team_selector.addItems([f"Team {i+1}" for i in range(market_state.TEAM_COUNT)])
        cash_layout.addRow("Select Team:", self.team_selector)

        # Current cash display
        self.current_cash_label = QLabel("$0.00")
        cash_layout.addRow("Current Cash:", self.current_cash_label)

        # Amount to add/subtract
        self.cash_amount = QDoubleSpinBox()
        self.cash_amount.setRange(-1000000, 1000000)
        self.cash_amount.setDecimals(2)
        self.cash_amount.setSingleStep(1000)
        self.cash_amount.setPrefix("$")
        cash_layout.addRow("Amount:", self.cash_amount)

        # Add buttons
        button_layout = QHBoxLayout()
        self.add_cash_btn = QPushButton("Add Cash")
        self.subtract_cash_btn = QPushButton("Subtract Cash")
        button_layout.addWidget(self.add_cash_btn)
        button_layout.addWidget(self.subtract_cash_btn)
        cash_layout.addRow("Actions:", button_layout)

        # Transaction log
        self.cash_log = QTextEdit()
        self.cash_log.setReadOnly(True)
        cash_layout.addRow("Transaction Log:", self.cash_log)

        cash_group.setLayout(cash_layout)
        layout.addWidget(cash_group)

        # Save Button
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

        # Connect signals
        self.team_selector.currentIndexChanged.connect(self.update_cash_display)
        self.add_cash_btn.clicked.connect(self.add_cash)
        self.subtract_cash_btn.clicked.connect(self.subtract_cash)

        # Initialize display
        self.update_cash_display()

    def save_settings(self):
        """Save settings back to config"""
        config.DEMAND_COEFFICIENT = self.demand_spin.value()
        config.EVENT_COEFFICIENT = self.event_spin.value()
        config.RANDOM_NOISE = self.noise_spin.value()
        
        # Update the CONFIG dictionary
        config.CONFIG.update({
            'DEMAND_COEFFICIENT': config.DEMAND_COEFFICIENT,
            'EVENT_COEFFICIENT': config.EVENT_COEFFICIENT,
            'RANDOM_NOISE': config.RANDOM_NOISE
        })

    def update_cash_display(self):
        """Update the current cash display for selected team"""
        team_id = self.get_selected_team_id()
        try:
            portfolio = market_state.get_team_portfolio(team_id)
            if portfolio:
                self.current_cash_label.setText(f"${portfolio['cash']:,.2f}")
        except Exception as e:
            logger.error(f"Error updating cash display: {e}")

    def get_selected_team_id(self):
        """Get the currently selected team ID"""
        return int(self.team_selector.currentText().split()[-1]) - 1

    def add_cash(self):
        """Add cash to selected team"""
        self._modify_cash(self.cash_amount.value())

    def subtract_cash(self):
        """Subtract cash from selected team"""
        self._modify_cash(-self.cash_amount.value())

    def _modify_cash(self, amount):
        """Modify team's cash balance"""
        team_id = self.get_selected_team_id()
        try:
            portfolio = market_state.team_portfolios[team_id]
            old_cash = portfolio['cash']
            new_cash = old_cash + amount

            if new_cash < 0:
                QMessageBox.warning(self, "Invalid Operation", 
                    "Operation would result in negative cash balance!")
                return

            # Update the cash balance
            portfolio['cash'] = new_cash
            # Update total value
            portfolio['total_value'] = portfolio['holdings_value'] + new_cash

            # Log the transaction
            transaction = {
                'timestamp': time.time(),
                'type': 'cash_adjustment',
                'amount': amount,
                'old_balance': old_cash,
                'new_balance': new_cash
            }
            portfolio['transactions'].append(transaction)

            # Update display
            self.update_cash_display()
            
            # Log entry
            action = "added to" if amount > 0 else "subtracted from"
            self.cash_log.append(
                f"${abs(amount):,.2f} {action} Team {team_id + 1}\n"
                f"New balance: ${new_cash:,.2f}"
            )
            logger.info(f"Cash adjustment for Team {team_id}: {amount:+,.2f}")

        except Exception as e:
            logger.error(f"Error modifying cash: {e}")
            QMessageBox.critical(self, "Error", f"Failed to modify cash: {str(e)}")
