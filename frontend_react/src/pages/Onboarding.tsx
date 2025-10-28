import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const Onboarding: React.FC = () => {
  return (
    <Container maxWidth="md" sx={{ py: 8 }}>
      <Paper elevation={0} sx={{ p: 6, borderRadius: 4, textAlign: 'center' }}>
        <Typography variant="h3" gutterBottom sx={{ fontWeight: 600, color: 'primary.main' }}>
          Welcome to GenMentor
        </Typography>
        <Typography variant="h6" color="text.secondary" paragraph>
          Your AI-powered learning companion
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Let's get started by setting up your learning profile and goals.
        </Typography>
        <Box sx={{ mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Onboarding flow will be implemented here
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Onboarding;