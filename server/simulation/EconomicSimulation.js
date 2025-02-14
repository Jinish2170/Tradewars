class EconomicSimulation {
  constructor(marketState) {
    this.marketState = marketState;
    this.parameters = {
      baseVolatility: 0.01,
      eventImpactMultiplier: 1.0,
      recoveryRate: 0.5
    };
  }

  async processEvent(eventData) {
    const { stockId, impact, description } = eventData;
    
    const stock = this.marketState.stocks.find(s => s.id === stockId);
    if (!stock) throw new Error('Invalid stock');

    const currentPrice = stock.currentPrice;
    const priceChange = currentPrice * (impact / 100);
    
    await this.marketState.overrideStockPrice(stockId, currentPrice + priceChange);
    
    return { success: true, message: 'Event processed' };
  }

  updateParameters(params) {
    this.parameters = { ...this.parameters, ...params };
  }
}

module.exports = { EconomicSimulation };
