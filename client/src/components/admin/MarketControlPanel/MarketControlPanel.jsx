import React, { useState, useEffect } from 'react';
import { socket } from '../../../services/socket';
import {
  Box,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';

const MarketControlPanel = () => {
  const [stocks, setStocks] = useState([]);
  const [selectedStock, setSelectedStock] = useState('');
  const [newPrice, setNewPrice] = useState('');
  const [actionLog, setActionLog] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  useEffect(() => {
    // Initialize socket listeners
    socket.on('stockPriceUpdate', handleStockUpdate);
    socket.emit('getStocks');

    socket.on('stockList', (stockList) => {
      setStocks(stockList);
    });

    socket.on('error', (error) => {
      setError(error.message);
      setLoading(false);
    });

    return () => {
      socket.off('stockPriceUpdate');
      socket.off('stockList');
      socket.off('error');
    };
  }, []);

  const handleStockUpdate = (data) => {
    setStocks(prevStocks => 
      prevStocks.map(stock => 
        stock.id === data.stockId 
          ? { ...stock, currentPrice: data.price }
          : stock
      )
    );
  };

  const handlePriceOverride = (e) => {
    e.preventDefault();
    setShowConfirmDialog(true);
  };

  const confirmPriceOverride = () => {
    setLoading(true);
    setError(null);
    
    socket.emit('adminPriceOverride', {
      stockId: selectedStock,
      price: parseFloat(newPrice)
    });

    setShowConfirmDialog(false);
    
    // Add to action log
    setActionLog(prev => [{
      timestamp: new Date().toLocaleTimeString(),
      action: `Price override: ${selectedStock} to $${newPrice}`
    }, ...prev]);

    setNewPrice('');
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Market Control
      </Typography>

      {/* Stock Price Table */}
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Stock</TableCell>
              <TableCell align="right">Current Price</TableCell>
              <TableCell align="right">Change</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {stocks.map((stock) => (
              <TableRow key={stock.id}>
                <TableCell>{stock.symbol}</TableCell>
                <TableCell align="right">${stock.currentPrice}</TableCell>
                <TableCell align="right" sx={{
                  color: stock.change >= 0 ? 'success.main' : 'error.main'
                }}>
                  {stock.change > 0 ? '+' : ''}{stock.change}%
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Price Override Form */}
      <Paper sx={{ p: 2, mb: 4 }}>
        <form onSubmit={handlePriceOverride}>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Select Stock</InputLabel>
              <Select
                value={selectedStock}
                label="Select Stock"
                onChange={(e) => setSelectedStock(e.target.value)}
              >
                {stocks.map((stock) => (
                  <MenuItem key={stock.id} value={stock.id}>
                    {stock.symbol}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <TextField
              label="New Price"
              type="number"
              value={newPrice}
              onChange={(e) => setNewPrice(e.target.value)}
              sx={{ width: 150 }}
            />
            <Button 
              type="submit" 
              variant="contained" 
              disabled={!selectedStock || !newPrice || loading}
              endIcon={loading && <CircularProgress size={20} />}
            >
              Override Price
            </Button>
          </Box>
        </form>
      </Paper>

      {/* Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onClose={() => setShowConfirmDialog(false)}>
        <DialogTitle>Confirm Price Override</DialogTitle>
        <DialogContent>
          Are you sure you want to override the price of {
            stocks.find(s => s.id === selectedStock)?.symbol
          } to ${newPrice}?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDialog(false)}>Cancel</Button>
          <Button onClick={confirmPriceOverride} variant="contained" color="primary">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Action Log */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Action Log
        </Typography>
        <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
          {actionLog.map((log, index) => (
            <Typography key={index} variant="body2" sx={{ mb: 1 }}>
              [{log.timestamp}] {log.action}
            </Typography>
          ))}
        </Box>
      </Paper>
    </Box>
  );
};

export default MarketControlPanel;
