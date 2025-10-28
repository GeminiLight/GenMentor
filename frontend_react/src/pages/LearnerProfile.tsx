import React from 'react';
import { Container, Typography, Paper, Box } from '@mui/material';

const LearnerProfile: React.FC = () => {
  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Paper elevation={0} sx={{ p: 4, borderRadius: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          My Profile
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          View and manage your learner profile, preferences, and learning history.
        </Typography>
        <Box sx={{ mt: 4 }}>
          <Typography variant="body2" color="text.secondary">
            Learner profile management interface will be implemented here
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default LearnerProfile;