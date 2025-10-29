import { Outlet } from 'react-router-dom';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import MainLayout from './components/Layout/MainLayout';

// Pages
import Dashboard from './pages/Dashboard';
import Onboarding from './pages/Onboarding';
import LearningPath from './pages/LearningPath';
import SkillGap from './pages/SkillGap';
import KnowledgeDocument from './pages/KnowledgeDocument';
import LearnerProfile from './pages/LearnerProfile';
import GoalManagement from './pages/GoalManagement';
import Chatbot from './pages/Chatbot';
import Settings from './pages/Settings';

// Context providers
import { AuthProvider } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';

// Components
import ErrorBoundary from './components/Common/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AuthProvider>
          <NotificationProvider>
            <Router>
              <Routes>
                {/* Onboarding flow - no layout */}
                <Route path="/onboarding" element={<Onboarding />} />
                
                {/* Main app with layout */}
                <Route path="/" element={<MainLayout><Outlet /></MainLayout>}>
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  <Route path="dashboard" element={<Dashboard />} />
                  <Route path="learning-path" element={<LearningPath />} />
                  <Route path="skill-gap" element={<SkillGap />} />
                  <Route path="knowledge-document" element={<KnowledgeDocument />} />
                  <Route path="learner-profile" element={<LearnerProfile />} />
                  <Route path="goal-management" element={<GoalManagement />} />
                  <Route path="chatbot" element={<Chatbot />} />
                  <Route path="settings" element={<Settings />} />
                </Route>
                
                {/* Catch all - redirect to dashboard */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </Router>
          </NotificationProvider>
        </AuthProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;