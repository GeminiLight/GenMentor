import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Avatar,
  IconButton,
  Button,
  Divider,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  School as SchoolIcon,
  Schedule as ScheduleIcon,
  EmojiEvents as EmojiEventsIcon,
  ArrowForward as ArrowForwardIcon,
  PlayArrow as PlayIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
} from 'recharts';
import { motion } from 'framer-motion';
import { useNotification } from '../contexts/NotificationContext';
import { LearningAnalytics, SkillProgression, DataPoint } from '../types';
import { CHART_COLORS } from '../config';

const Dashboard: React.FC = () => {
  const { showNotification } = useNotification();
  const [analytics, setAnalytics] = useState<LearningAnalytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate loading analytics data
    setTimeout(() => {
      setAnalytics(generateMockAnalytics());
      setLoading(false);
      showNotification({
        type: 'success',
        title: 'Dashboard Loaded',
        message: 'Your learning analytics are ready to view.',
      });
    }, 1000);
  }, [showNotification]);

  if (loading || !analytics) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Learning Analytics
        </Typography>
        <Grid container spacing={3}>
          {[1, 2, 3, 4].map((i) => (
            <Grid item xs={12} md={6} lg={3} key={i}>
              <Card sx={{ height: 200 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box
                      sx={{
                        width: 40,
                        height: 40,
                        borderRadius: '50%',
                        backgroundColor: 'action.hover',
                      }}
                    />
                    <Box sx={{ ml: 2, flexGrow: 1 }}>
                      <Box sx={{ height: 20, backgroundColor: 'action.hover', borderRadius: 1, mb: 1 }} />
                      <Box sx={{ height: 16, backgroundColor: 'action.hover', borderRadius: 1, width: '60%' }} />
                    </Box>
                  </Box>
                  <Box sx={{ height: 8, backgroundColor: 'action.hover', borderRadius: 1, mb: 1 }} />
                  <Box sx={{ height: 8, backgroundColor: 'action.hover', borderRadius: 1, width: '80%' }} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  }

  const skillProgressData = analytics.skillProgression.map(skill => ({
    name: skill.skillName,
    current: skill.currentLevel,
    target: skill.targetLevel,
    progress: skill.progress,
  }));

  const learningTrendData = analytics.learningTrend.map(point => ({
    name: new Date(point.timestamp).toLocaleDateString(),
    progress: point.value,
  }));

  const sessionData = analytics.sessionHistory.map(session => ({
    name: new Date(session.date).toLocaleDateString(),
    duration: session.duration,
    completion: session.completionRate,
  }));

  const skillDistribution = [
    { name: 'Mastered', value: 12, color: CHART_COLORS.success },
    { name: 'In Progress', value: 8, color: CHART_COLORS.warning },
    { name: 'Not Started', value: 5, color: CHART_COLORS.error },
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Learning Analytics
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track your learning progress and view personalized insights
        </Typography>
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <Card sx={{ height: '100%', borderRadius: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                    <ScheduleIcon />
                  </Avatar>
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      Total Learning Time
                    </Typography>
                    <Typography variant="h5" component="div" sx={{ fontWeight: 600 }}>
                      {Math.floor(analytics.totalTimeSpent / 60)}h {analytics.totalTimeSpent % 60}m
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  +15% from last week
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card sx={{ height: '100%', borderRadius: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                    <SchoolIcon />
                  </Avatar>
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      Skills Mastered
                    </Typography>
                    <Typography variant="h5" component="div" sx={{ fontWeight: 600 }}>
                      12 / 25
                    </Typography>
                  </Box>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={48}
                  sx={{ height: 6, borderRadius: 3, mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  48% completion rate
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card sx={{ height: '100%', borderRadius: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                    <TrendingUpIcon />
                  </Avatar>
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      Learning Streak
                    </Typography>
                    <Typography variant="h5" component="div" sx={{ fontWeight: 600 }}>
                      7 days
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  Keep it up! 🔥
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card sx={{ height: '100%', borderRadius: 3 }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                    <EmojiEventsIcon />
                  </Avatar>
                  <Box>
                    <Typography color="text.secondary" variant="body2">
                      Next Milestone
                    </Typography>
                    <Typography variant="h6" component="div" sx={{ fontWeight: 600 }}>
                      JavaScript Expert
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  3 skills remaining
                </Typography>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Learning Progress Over Time */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
          >
            <Card sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Learning Progress Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={learningTrendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Area
                      type="monotone"
                      dataKey="progress"
                      stroke={CHART_COLORS.primary}
                      fill={CHART_COLORS.primary}
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Skill Distribution */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
          >
            <Card sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Skill Distribution
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={skillDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {skillDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Skill Progress and Session History */}
      <Grid container spacing={3}>
        {/* Current Skills Progress */}
        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.7 }}
          >
            <Card sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Current Skills Progress
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={skillProgressData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="current" fill={CHART_COLORS.primary} name="Current Level" />
                    <Bar dataKey="target" fill={CHART_COLORS.secondary} name="Target Level" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recent Sessions */}
        <Grid item xs={12} lg={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.8 }}
          >
            <Card sx={{ borderRadius: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Recent Learning Sessions
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={sessionData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="duration"
                      stroke={CHART_COLORS.success}
                      strokeWidth={2}
                      name="Duration (min)"
                    />
                    <Line
                      type="monotone"
                      dataKey="completion"
                      stroke={CHART_COLORS.info}
                      strokeWidth={2}
                      name="Completion %"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>

      {/* Quick Actions */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
          Quick Actions
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            size="large"
            sx={{ borderRadius: 3 }}
          >
            Continue Learning
          </Button>
          <Button
            variant="outlined"
            startIcon={<ArrowForwardIcon />}
            size="large"
            sx={{ borderRadius: 3 }}
          >
            View Learning Path
          </Button>
          <Button
            variant="outlined"
            startIcon={<TrendingUpIcon />}
            size="large"
            sx={{ borderRadius: 3 }}
          >
            View Detailed Analytics
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

// Mock data generator
function generateMockAnalytics(): LearningAnalytics {
  return {
    totalTimeSpent: 1245, // minutes
    averageSessionDuration: 45,
    completionRate: 78,
    skillProgression: [
      {
        skillId: '1',
        skillName: 'JavaScript',
        startLevel: 1,
        currentLevel: 3,
        targetLevel: 3,
        progress: 100,
        timestamps: [],
      },
      {
        skillId: '2',
        skillName: 'React',
        startLevel: 0,
        currentLevel: 2,
        targetLevel: 3,
        progress: 67,
        timestamps: [],
      },
      {
        skillId: '3',
        skillName: 'TypeScript',
        startLevel: 0,
        currentLevel: 1,
        targetLevel: 2,
        progress: 50,
        timestamps: [],
      },
      {
        skillId: '4',
        skillName: 'Node.js',
        startLevel: 0,
        currentLevel: 0,
        targetLevel: 2,
        progress: 0,
        timestamps: [],
      },
    ],
    learningTrend: [
      { timestamp: '2024-01-01', value: 10 },
      { timestamp: '2024-01-08', value: 25 },
      { timestamp: '2024-01-15', value: 35 },
      { timestamp: '2024-01-22', value: 48 },
      { timestamp: '2024-01-29', value: 52 },
      { timestamp: '2024-02-05', value: 65 },
      { timestamp: '2024-02-12', value: 78 },
    ],
    sessionHistory: [
      { sessionId: '1', date: '2024-02-10', duration: 45, skillsCovered: ['JavaScript'], completionRate: 100, engagementScore: 8.5 },
      { sessionId: '2', date: '2024-02-11', duration: 60, skillsCovered: ['React'], completionRate: 85, engagementScore: 9.0 },
      { sessionId: '3', date: '2024-02-12', duration: 30, skillsCovered: ['TypeScript'], completionRate: 70, engagementScore: 7.5 },
      { sessionId: '4', date: '2024-02-13', duration: 50, skillsCovered: ['React'], completionRate: 90, engagementScore: 8.8 },
      { sessionId: '5', date: '2024-02-14', duration: 40, skillsCovered: ['JavaScript'], completionRate: 95, engagementScore: 9.2 },
    ],
  };
}

export default Dashboard;