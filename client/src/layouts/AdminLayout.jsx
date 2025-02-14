import React from 'react';
import { Box, AppBar, Toolbar, Typography, Container } from '@mui/material';

const AdminLayout = ({ children }) => {
  return (
    <Box>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6">
            TradeWar 2 Admin
          </Typography>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        {children}
      </Container>
    </Box>
  );
};

export default AdminLayout;
