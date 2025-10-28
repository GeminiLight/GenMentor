import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const Settings: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={0} sx={{ p: 4, borderRadius: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Settings
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Configure your application preferences and settings.
        </Typography>
        <Box sx={{ mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Settings interface will be implemented here
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Settings;