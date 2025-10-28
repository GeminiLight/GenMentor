import React, { useState } from 'react';
import { Box, Toolbar } from '@mui/material';
import Header from './Header';
import Navigation from './Navigation';

interface MainLayoutProps {
  children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [navOpen, setNavOpen] = useState(true);

  const handleNavToggle = () => {
    setNavOpen(!navOpen);
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Header onMenuClick={handleNavToggle} />
      <Navigation open={navOpen} onToggle={handleNavToggle} />
      
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: 'background.default',
          transition: 'margin-left 0.3s ease',
        }}
      >
        <Toolbar />
        <Box
          sx={{
            flexGrow: 1,
            p: 3,
            overflow: 'auto',
            backgroundColor: 'background.default',
          }}
        >
          {children}
        </Box>
      </Box>
    </Box>
  );
};

export default MainLayout;