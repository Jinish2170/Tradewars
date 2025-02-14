class MarketState {
  constructor() {
    this.stocks = [
      { id: '1', symbol: 'AAPL', currentPrice: 150.00, change: 0 },
      { id: '2', symbol: 'GOOGL', currentPrice: 2800.00, change: 0 },
      { id: '3', symbol: 'MSFT', currentPrice: 290.00, change: 0 },
      { id: '4', symbol: 'AMZN', currentPrice: 3300.00, change: 0 },
    ];
    this.orderLog = [];
    this.eventLog = [];
    this.actionLog = [];
    this.teams = [
      {
        id: '1',
        name: 'Team Alpha',
        cashBalance: 1000000,
        holdings: {}
      },
      {
        id: '2',
        name: 'Team Beta',
        cashBalance: 1000000,
        holdings: {}
      }
    ];
  }

  getStockList() {
    return this.stocks;
  }

  getTeamStates() {
    return this.teams;
  }

  getOrderLog() {
    return this.orderLog;
  }

  getEventLog() {
    return this.eventLog;
  }

  getActionLog() {
    return this.actionLog;
  }

  getStockPrice(stockId) {
    const stock = this.stocks.find(s => s.id === stockId);
    return stock ? stock.currentPrice : null;
  }

  async overrideStockPrice(stockId, newPrice) {
    const stockIndex = this.stocks.findIndex(s => s.id === stockId);
    if (stockIndex === -1) throw new Error('Stock not found');

    const oldPrice = this.stocks[stockIndex].currentPrice;
    this.stocks[stockIndex].currentPrice = newPrice;
    this.stocks[stockIndex].change = ((newPrice - oldPrice) / oldPrice) * 100;
    
    return this.stocks[stockIndex];
  }

  addToActionLog(action) {
    this.actionLog.unshift(action);
    if (this.actionLog.length > 100) this.actionLog.pop();
  }

  addToEventLog(event) {
    this.eventLog.unshift(event);
    if (this.eventLog.length > 100) this.eventLog.pop();
  }
}

module.exports = { MarketState };
