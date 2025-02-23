from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, 
                            QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import QTimer
from simulation import market_state  # Fix the import path
from config import STARTING_BUDGET  # Add this import
import logging  # Import the logging module
from PyQt5.QtGui import QColor  # Import QColor for color coding

logger = logging.getLogger(__name__)  # Set up logger

class TeamManagementPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_timer()
        self.update_team_data()  # Load initial data

    def init_ui(self):
        layout = QVBoxLayout()

        # Team Overview Table
        overview_group = QGroupBox("Team Overview")
        overview_layout = QVBoxLayout()
        
        self.team_table = QTableWidget()
        self.team_table.setColumnCount(5)
        self.team_table.setHorizontalHeaderLabels([
            "Team ID", "Cash Balance", "Holdings Value", "Total Value", "P&L (%)"
        ])
        
        overview_layout.addWidget(self.team_table)
        overview_group.setLayout(overview_layout)
        layout.addWidget(overview_group)

        self.setLayout(layout)

    def setup_timer(self):
        """Set up timer for periodic updates"""
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_team_data)
        self.update_timer.start(1000)  # Update every second

    def update_team_data(self):
        """Update the team overview table with enhanced information"""
        try:
            self.team_table.setRowCount(0)  # Clear existing rows
            
            for team_id in range(market_state.TEAM_COUNT):
                portfolio = market_state.get_team_portfolio(team_id)
                if not portfolio:
                    continue
                
                row = self.team_table.rowCount()
                self.team_table.insertRow(row)
                
                # Calculate P&L
                pl_amount = portfolio['total_value'] - STARTING_BUDGET
                pl_percent = (pl_amount / STARTING_BUDGET) * 100
                
                # Create and format items
                team_item = QTableWidgetItem(f"Team {team_id}")
                cash_item = QTableWidgetItem(f"${portfolio['cash']:,.2f}")
                holdings_item = QTableWidgetItem(f"${portfolio['holdings_value']:,.2f}")
                total_item = QTableWidgetItem(f"${portfolio['total_value']:,.2f}")
                pl_item = QTableWidgetItem(f"{pl_percent:+.2f}%")
                
                # Color code P&L
                if pl_amount > 0:
                    pl_item.setForeground(QColor('green'))
                elif pl_amount < 0:
                    pl_item.setForeground(QColor('red'))
                
                # Set items in table
                self.team_table.setItem(row, 0, team_item)
                self.team_table.setItem(row, 1, cash_item)
                self.team_table.setItem(row, 2, holdings_item)
                self.team_table.setItem(row, 3, total_item)
                self.team_table.setItem(row, 4, pl_item)
            
            self.team_table.resizeColumnsToContents()
            
        except Exception as e:
            logger.error(f"Error updating team data: {str(e)}", exc_info=True)
