
import sqlite3
import json
from datetime import datetime
import os

class SimulationDB:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), 'simulation.db')
        self.init_database()

    def init_database(self):
        """Initialize the database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    team_id INTEGER,
                    stock TEXT,
                    order_type TEXT,
                    quantity INTEGER,
                    price REAL,
                    status TEXT
                )
            ''')
            
            # Events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    description TEXT,
                    affected_stocks TEXT,
                    impact REAL
                )
            ''')
            
            # Market states table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    stock_prices TEXT,
                    available_quantities TEXT
                )
            ''')
            
            # Portfolio snapshots table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    team_id INTEGER,
                    cash_balance REAL,
                    holdings TEXT,
                    total_value REAL
                )
            ''')
            
            conn.commit()

    def log_order(self, team_id, order, status="executed"):
        """Log an order to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (team_id, stock, order_type, quantity, price, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (team_id, order['stock'], order['type'], 
                 order['quantity'], order['price'], status))
            conn.commit()

    def log_event(self, event_type, description, affected_stocks, impact):
        """Log a market event to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO events (event_type, description, affected_stocks, impact)
                VALUES (?, ?, ?, ?)
            ''', (event_type, description, json.dumps(affected_stocks), impact))
            conn.commit()

    def save_market_state(self, stock_prices, available_quantities):
        """Save current market state."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO market_states (stock_prices, available_quantities)
                VALUES (?, ?)
            ''', (json.dumps(stock_prices), json.dumps(available_quantities)))
            conn.commit()

    def save_portfolio_snapshot(self, team_id, cash_balance, holdings, total_value):
        """Save a portfolio snapshot."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO portfolio_snapshots 
                (team_id, cash_balance, holdings, total_value)
                VALUES (?, ?, ?, ?)
            ''', (team_id, cash_balance, json.dumps(holdings), total_value))
            conn.commit()

    def get_order_history(self, team_id=None, start_date=None, end_date=None):
        """Query order history with optional filters."""
        query = "SELECT * FROM orders WHERE 1=1"
        params = []
        
        if team_id is not None:
            query += " AND team_id = ?"
            params.append(team_id)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
            
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def get_event_history(self, event_type=None, start_date=None, end_date=None):
        """Query event history with optional filters."""
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
            
        query += " ORDER BY timestamp DESC"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

# Create a global instance for easy import
db = SimulationDB()
