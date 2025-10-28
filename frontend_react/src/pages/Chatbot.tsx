import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const Chatbot: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={0} sx={{ p: 4, borderRadius: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          AI Chatbot Tutor
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Get personalized assistance and answers to your learning questions.
        </Typography>
        <Box sx={{ mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            AI chatbot tutor interface will be implemented here
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default Chatbot;