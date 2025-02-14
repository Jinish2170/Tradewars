import React, { useState } from 'react';
import AdminLayout from '../layouts/AdminLayout';
import { 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  Container 
} from '@mui/material';
import MarketControlPanel from '../components/admin/MarketControlPanel/MarketControlPanel';
import NewsEventPanel from '../components/admin/NewsEventPanel/NewsEventPanel';
import Settings from '../components/admin/Settings/Settings';
import TeamManagement from '../components/admin/TeamManagement/TeamManagement';

function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AdminDashboard = () => {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  return (
    <AdminLayout>
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Admin Dashboard
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={currentTab} 
            onChange={handleTabChange}
            aria-label="admin dashboard tabs"
          >
            <Tab label="Market Control" />
            <Tab label="News/Event" />
            <Tab label="Settings" />
            <Tab label="Team Management" />
          </Tabs>
        </Box>

        <TabPanel value={currentTab} index={0}>
          <MarketControlPanel />
        </TabPanel>
        <TabPanel value={currentTab} index={1}>
          <NewsEventPanel />
        </TabPanel>
        <TabPanel value={currentTab} index={2}>
          <Settings />
        </TabPanel>
        <TabPanel value={currentTab} index={3}>
          <TeamManagement />
        </TabPanel>
      </Container>
    </AdminLayout>
  );
};

export default AdminDashboard;
