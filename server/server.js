const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const { MarketState } = require('./simulation/MarketState');
const { MarketSimulation } = require('./simulation/MarketSimulation');
const { EconomicSimulation } = require('./simulation/EconomicSimulation');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Initialize simulation instances
const marketState = new MarketState();
const marketSimulation = new MarketSimulation(marketState);
const economicSimulation = new EconomicSimulation(marketState);

io.on('connection', (socket) => {
  console.log('New client connected');

  // Handle new orders
  socket.on('newOrder', async (orderData) => {
    try {
      const { stockId, quantity, price, type, teamId } = orderData;
      const result = await marketSimulation.processOrder({
        stockId,
        quantity,
        price,
        type,
        teamId
      });

      // Broadcast updates
      io.emit('orderLogUpdate', marketState.getOrderLog());
      io.emit('priceUpdate', {
        stockId,
        price: marketState.getStockPrice(stockId),
        timestamp: Date.now()
      });
      io.emit('teamUpdate', marketState.getTeamStates());
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });

  // Handle admin price override
  socket.on('adminPriceOverride', async (data) => {
    try {
      const { stockId, price } = data;
      await marketState.overrideStockPrice(stockId, price);
      
      // Log the override
      marketState.addToActionLog({
        type: 'PRICE_OVERRIDE',
        stockId,
        price,
        timestamp: Date.now()
      });

      // Broadcast updates
      io.emit('priceUpdate', {
        stockId,
        price,
        timestamp: Date.now()
      });
      io.emit('actionLogUpdate', marketState.getActionLog());
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });

  // Handle news/event injection
  socket.on('newEvent', async (eventData) => {
    try {
      const { title, targetStocks, impact, description } = eventData;
      
      // Process event impact on each target stock
      for (const stockId of targetStocks) {
        await economicSimulation.processEvent({
          stockId,
          impact,
          description: title
        });
      }

      // Add to event log
      marketState.addToEventLog({
        ...eventData,
        timestamp: Date.now()
      });

      // Broadcast updates
      io.emit('eventLogUpdate', marketState.getEventLog());
      io.emit('stockList', marketState.getStockList());
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });

  // Handle simulation settings updates
  socket.on('updateSettings', async (settings) => {
    try {
      // Update simulation parameters
      marketSimulation.updateParameters(settings.market);
      economicSimulation.updateParameters(settings.economic);
      
      // Log the settings change
      marketState.addToActionLog({
        type: 'SETTINGS_UPDATE',
        settings,
        timestamp: Date.now()
      });

      // Broadcast updates
      io.emit('settingsUpdate', settings);
      io.emit('actionLogUpdate', marketState.getActionLog());
    } catch (error) {
      socket.emit('error', { message: error.message });
    }
  });

  // Handle requests for initial data
  socket.on('getStocks', () => {
    socket.emit('stockList', marketState.getStockList());
  });

  socket.on('getTeams', () => {
    socket.emit('teamUpdate', marketState.getTeamStates());
  });

  socket.on('getEventLog', () => {
    socket.emit('eventLogUpdate', marketState.getEventLog());
  });

  socket.on('getActionLog', () => {
    socket.emit('actionLogUpdate', marketState.getActionLog());
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

const port = process.env.PORT || 4001;
server.listen(port, () => console.log(`Listening on port ${port}`));
