const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use('/socket.io', createProxyMiddleware({
    target: 'http://localhost:4001',
    changeOrigin: true,
    ws: true,
    logLevel: 'debug'
  }));

  app.use('/api', createProxyMiddleware({
    target: 'http://localhost:4001',
    changeOrigin: true,
  }));
};
