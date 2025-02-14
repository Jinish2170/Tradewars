import React, { useState, useEffect } from 'react';
import { socket } from '../../../services/socket';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Collapse,
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';

const Row = ({ team, stocks }) => {
  const [open, setOpen] = useState(false);

  const calculateTotalValue = () => {
    const holdingsValue = Object.entries(team.holdings).reduce((total, [stockId, shares]) => {
      const stock = stocks.find(s => s.id === stockId);
      return total + (stock?.currentPrice || 0) * shares;
    }, 0);
    return holdingsValue + team.cashBalance;
  };

  return (
    <>
      <TableRow>
        <TableCell>
          <IconButton size="small" onClick={() => setOpen(!open)}>
            {open ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          </IconButton>
        </TableCell>
        <TableCell>{team.name}</TableCell>
        <TableCell align="right">${team.cashBalance.toLocaleString()}</TableCell>
        <TableCell align="right">
          {Object.keys(team.holdings).length} stocks
        </TableCell>
        <TableCell align="right">${calculateTotalValue().toLocaleString()}</TableCell>
      </TableRow>
      <TableRow>
        <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
          <Collapse in={open} timeout="auto" unmountOnExit>
            <Box sx={{ margin: 1 }}>
              <Typography variant="h6" gutterBottom component="div">
                Holdings Detail
              </Typography>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Stock</TableCell>
                    <TableCell align="right">Shares</TableCell>
                    <TableCell align="right">Current Price</TableCell>
                    <TableCell align="right">Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(team.holdings).map(([stockId, shares]) => {
                    const stock = stocks.find(s => s.id === stockId);
                    const value = (stock?.currentPrice || 0) * shares;
                    return (
                      <TableRow key={stockId}>
                        <TableCell>{stock?.symbol}</TableCell>
                        <TableCell align="right">{shares}</TableCell>
                        <TableCell align="right">
                          ${stock?.currentPrice.toLocaleString()}
                        </TableCell>
                        <TableCell align="right">
                          ${value.toLocaleString()}
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </Box>
          </Collapse>
        </TableCell>
      </TableRow>
    </>
  );
};

const TeamManagement = () => {
  const [teams, setTeams] = useState([]);
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    socket.emit('getTeams');
    socket.emit('getStocks');

    socket.on('teamUpdate', (updatedTeams) => {
      setTeams(updatedTeams);
      setLoading(false);
    });

    socket.on('stockList', (stockList) => {
      setStocks(stockList);
    });

    socket.on('error', (error) => {
      setError(error.message);
      setLoading(false);
    });

    return () => {
      socket.off('teamUpdate');
      socket.off('stockList');
      socket.off('error');
    };
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Team Management
      </Typography>
      
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell />
              <TableCell>Team Name</TableCell>
              <TableCell align="right">Cash Balance</TableCell>
              <TableCell align="right">Holdings</TableCell>
              <TableCell align="right">Total Value</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {teams.map((team) => (
              <Row key={team.id} team={team} stocks={stocks} />
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default TeamManagement;
