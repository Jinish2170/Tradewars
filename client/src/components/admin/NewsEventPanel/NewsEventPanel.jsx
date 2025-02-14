import React, { useState, useEffect } from 'react';
import { socket } from '../../../services/socket';
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemText,
  Chip,
  OutlinedInput,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const NewsEventPanel = () => {
  const [stocks, setStocks] = useState([]);
  const [eventLog, setEventLog] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    targetStocks: [],
    impact: '',
    description: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  useEffect(() => {
    socket.emit('getStocks');
    socket.on('stockList', (stockList) => setStocks(stockList));
    socket.on('eventLog', (events) => setEventLog(events));

    return () => {
      socket.off('stockList');
      socket.off('eventLog');
    };
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowConfirmDialog(true);
  };

  const confirmSubmit = () => {
    setLoading(true);
    setError(null);

    socket.emit('newEvent', {
      ...formData,
      impact: parseFloat(formData.impact),
      timestamp: new Date().toISOString()
    });

    setShowConfirmDialog(false);

    // Reset form after server acknowledges
    socket.once('eventSuccess', () => {
      setFormData({
        title: '',
        targetStocks: [],
        impact: '',
        description: ''
      });
      setLoading(false);
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        News/Event Injection
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Event Creation Form */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <form onSubmit={handleSubmit}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              name="title"
              label="Event Title"
              value={formData.title}
              onChange={handleChange}
              fullWidth
              required
            />

            <FormControl fullWidth required>
              <InputLabel>Target Stock(s)</InputLabel>
              <Select
                multiple
                name="targetStocks"
                value={formData.targetStocks}
                onChange={handleChange}
                input={<OutlinedInput label="Target Stock(s)" />}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip 
                        key={value} 
                        label={stocks.find(s => s.id === value)?.symbol} 
                      />
                    ))}
                  </Box>
                )}
                MenuProps={MenuProps}
              >
                {stocks.map((stock) => (
                  <MenuItem key={stock.id} value={stock.id}>
                    {stock.symbol}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              name="impact"
              label="Impact Magnitude (%)"
              type="number"
              value={formData.impact}
              onChange={handleChange}
              inputProps={{ step: '0.1' }}
              required
            />

            <TextField
              name="description"
              label="Description"
              multiline
              rows={4}
              value={formData.description}
              onChange={handleChange}
              required
            />

            <Button 
              type="submit" 
              variant="contained" 
              color="primary"
              size="large"
              disabled={loading}
              endIcon={loading && <CircularProgress size={20} />}
            >
              Submit Event
            </Button>
          </Box>
        </form>
      </Paper>

      {/* Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onClose={() => setShowConfirmDialog(false)}>
        <DialogTitle>Confirm Event Injection</DialogTitle>
        <DialogContent>
          Are you sure you want to inject this event affecting {formData.targetStocks.length} stocks with {formData.impact}% impact?
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowConfirmDialog(false)}>Cancel</Button>
          <Button onClick={confirmSubmit} variant="contained" color="primary">
            Confirm
          </Button>
        </DialogActions>
      </Dialog>

      {/* Event Log */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recent Events
        </Typography>
        <List sx={{ maxHeight: 300, overflow: 'auto' }}>
          {eventLog.map((event, index) => (
            <ListItem key={index} divider>
              <ListItemText
                primary={event.title}
                secondary={
                  <React.Fragment>
                    <Typography component="span" variant="body2" color="text.primary">
                      Impact: {event.impact}% | 
                      Stocks: {event.targetStocks.map(id => 
                        stocks.find(s => s.id === id)?.symbol
                      ).join(', ')}
                    </Typography>
                    <Typography variant="body2">
                      {new Date(event.timestamp).toLocaleString()}
                    </Typography>
                    {event.description}
                  </React.Fragment>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default NewsEventPanel;
