# Tradewars - Advanced Stock Market Simulation

![Tradewars](https://shields.io/badge/Tradewars-Market_Simulation-blue)

A comprehensive, multi-team trading simulation platform designed for educational environments, competitions, and financial literacy training. This advanced system simulates a dynamic stock market with real-time price movements, team-based trading, administrative controls, and customizable market conditions.

## 🌟 Features

### Core Functionality
- **Real-time Market Simulation**: Dynamic price movements based on trading activity, market sentiment, and sector trends
- **Multi-team Support**: Competitive environment for multiple teams with real-time portfolio tracking
- **Session-based Trading**: Configurable trading sessions with timing controls
- **Realistic Market Dynamics**: Incorporates volatility, momentum, sector-based trends, and realistic price reactions

### Administrative Features
- **Market Control Panel**: Start, pause, and end trading sessions
- **Price Manipulation**: Direct price overrides and percentage-based adjustments
- **Team Order Management**: Place orders on behalf of teams
- **Cash Management**: Add or remove cash from team accounts
- **News Event System**: Inject news events to gradually influence specific stocks
- **Market Parameter Controls**: Adjust demand coefficients, event impact, and market volatility

### Trading Interface
- **Real-time Price Tickers**: Live-updating price cards with trend indicators
- **Market Data Table**: Comprehensive view of all stocks with prices, trends, volumes, and available quantities
- **Team Rankings**: Real-time performance tracking with portfolio valuations
- **Transaction Log**: Record of all market activity
- **Price Movement Visualization**: Clear visual indicators of price movements and trends

### Advanced Market Features
- **Sector-specific Trends**: Related stocks move together based on sector performance
- **Market Sentiment**: Overall market direction influences individual stocks
- **Volatility Modeling**: Dynamic volatility based on trading activity and market conditions
- **News Impact System**: Gradual price adjustments following news events
- **Market Depth Simulation**: Order size affects price impact and execution quality
- **IPO Support**: Ability to introduce new stocks to the market

## 📋 Technical Requirements

- Python 3.7+ 
- PyQt5 (5.15.9 or later)
- PyQt5-sip (12.12.1 or later)
- Windows/Linux/MacOS supported

## 🚀 Deployment Guide

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/tradewars.git
   cd tradewars
   ```

2. **Set up a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

### Configuration

Core simulation settings can be adjusted in `config.py`:

- `DEMAND_COEFFICIENT`: Controls how orders impact prices
- `EVENT_COEFFICIENT`: Controls how news events impact prices
- `RANDOM_NOISE`: Amount of random price movement
- `TEAM_COUNT`: Number of teams in the simulation
- `STARTING_BUDGET`: Initial cash for each team

## 📊 Usage Guide

### Administrator Interface

1. **Starting a Session**
   - Open the admin interface
   - Navigate to "Market Control"
   - Click "Start Session" to begin trading
   - Use Pause/Resume buttons to control trading flow

2. **Creating News Events**
   - Navigate to "News & Events" tab
   - Enter event title and description
   - Select affected stocks (use Ctrl+Click for multiple stocks)
   - Set impact percentage (-20% to +20%)
   - Click "Inject News Event"

3. **Managing Team Cash**
   - Navigate to "Settings" tab
   - Select a team from dropdown
   - Enter amount to add/subtract
   - Click "Add Cash" or "Subtract Cash"
   - Review transaction log

4. **Manipulating Stock Prices**
   - In "Market Control," select a stock
   - Use "Override Price" to set a specific price
   - Use "Apply Price Change" for percentage adjustments
   - Confirm changes in the Action Log

### Participant View

- **Market Data**: View current prices, trends, volumes, and available quantities
- **Team Rankings**: Track performance relative to other teams
- **Market Activity**: Follow recent transactions
- **Price Tickers**: Monitor price movements with trend indicators

## 🔍 Project Structure

```
Tradewars/
├── simulation/
│   ├── __init__.py
│   ├── market_simulation.py    # Core simulation engine
│   └── market_state.py         # Market data structures and state
├── ui/
│   ├── admin/
│   │   ├── admin_window.py     # Main admin interface
│   │   ├── market_control_panel.py
│   │   ├── news_event_panel.py
│   │   └── settings_panel.py
│   ├── participant_view.py     # Team view interface
│   └── main_window.py          # Application window management
├── utils/
│   ├── logger.py               # Logging utilities
│   └── decorators.py           # Operation safety wrappers
├── data/
│   └── db.py                   # Data persistence
├── config.py                   # Global configuration
└── run.py                      # Application entry point
```

## 💻 Skills & Technologies Demonstrated

### Programming & Development
- **Python**: Advanced object-oriented programming with inheritance and composition
- **Event-driven Programming**: Signal/slot implementation with PyQt5
- **Real-time Systems**: Live data updates and asynchronous processing
- **Multi-threading**: Background processing for simulation calculations
- **State Management**: Comprehensive market state tracking and updates

### Financial Modeling
- **Market Simulation**: Realistic price movements and dynamics
- **Portfolio Management**: Team holdings, transactions, and performance tracking
- **Financial Algorithms**: Price impact models, slippage calculations, and volatility modeling
- **Market Behaviors**: Trend simulation, sentiment analysis, and sector correlations

### UI Development
- **PyQt5 Framework**: Custom widgets, layouts, and styling
- **Responsive Design**: Adaptable layouts and organized component structure
- **Data Visualization**: Real-time updates and visual feedback systems
- **Event Handling**: User interaction management and validation

### System Architecture
- **Modular Design**: Clear separation of concerns with dedicated modules
- **Service Layer**: Clean interfaces between simulation and presentation layers
- **Configurable System**: Externalized settings and parameters
- **Extensible Framework**: Support for adding new features with minimal code changes

## 📝 Notes for Instructors/Facilitators

1. **Session Structure**
   - Each session lasts 10 minutes by default
   - Market prices stabilize within sessions but can be manually manipulated
   - Team portfolios persist between sessions for tournament-style play

2. **Recommended Setup**
   - One admin screen (teacher/facilitator)
   - One projection screen for participant view (team rankings)
   - Teams using own devices or paper trading based on projected data

3. **Competition Ideas**
   - Highest portfolio value after X sessions
   - Most consistent growth
   - Best performance under specific market conditions
   - Best recovery from market downturn

4. **Customizable Difficulty**
   - Control market volatility for different experience levels
   - Preset news events for guided scenarios
   - Manual interventions for teachable moments

## 📞 Contact & Support

For issues, feature requests, or contributions, please:
1. Open an issue in the GitHub repository
2. Contact the development team at [your-email@example.com]

## 📜 License

Tradewars is licensed under the MIT License - see the LICENSE file for details.

---

**Developed by jinish karthiriya - 2025**