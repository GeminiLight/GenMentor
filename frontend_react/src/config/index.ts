import { AppConfig } from '../types';

export const config: AppConfig = {
  backendEndpoint: 'http://127.0.0.1:5006/',
  // backendEndpoint: 'http://57.152.82.155:8000/',
  useMockData: false,
  llmType: 'gpt4o',
  features: {
    darkMode: true,
    notifications: true,
    analytics: true,
    chatbot: true,
  },
};

export const llmLabelMap = {
  gpt4o: 'GPT-4o',
  llama: 'Llama3.2',
  deepseek: 'DeepSeek',
  together: 'Llama3.3-Turbo',
};

export const API_ENDPOINTS = {
  // Skill gap endpoints
  IDENTIFY_SKILL_GAP: '/api/skill-gap/identify',
  GET_SKILL_GAPS: '/api/skill-gap/list',
  UPDATE_SKILL_GAP: '/api/skill-gap/update',
  
  // Learner profile endpoints
  CREATE_LEARNER_PROFILE: '/api/learner-profile/create',
  GET_LEARNER_PROFILE: '/api/learner-profile/get',
  UPDATE_LEARNER_PROFILE: '/api/learner-profile/update',
  
  // Learning path endpoints
  CREATE_LEARNING_PATH: '/api/learning-path/create',
  GET_LEARNING_PATH: '/api/learning-path/get',
  UPDATE_LEARNING_PATH: '/api/learning-path/update',
  COMPLETE_SESSION: '/api/learning-path/session/complete',
  
  // Knowledge document endpoints
  UPLOAD_DOCUMENT: '/api/document/upload',
  GET_DOCUMENTS: '/api/document/list',
  GET_DOCUMENT: '/api/document/get',
  UPDATE_DOCUMENT: '/api/document/update',
  DELETE_DOCUMENT: '/api/document/delete',
  
  // Analytics endpoints
  GET_ANALYTICS: '/api/analytics/dashboard',
  GET_LEARNING_PROGRESS: '/api/analytics/progress',
  GET_SESSION_HISTORY: '/api/analytics/sessions',
  
  // Chat endpoints
  SEND_MESSAGE: '/api/chat/send',
  GET_CHAT_HISTORY: '/api/chat/history',
  CLEAR_CHAT: '/api/chat/clear',
};

export const ROUTES = {
  HOME: '/',
  ONBOARDING: '/onboarding',
  DASHBOARD: '/dashboard',
  LEARNING_PATH: '/learning-path',
  SKILL_GAP: '/skill-gap',
  KNOWLEDGE_DOCUMENT: '/knowledge-document',
  LEARNER_PROFILE: '/learner-profile',
  GOAL_MANAGEMENT: '/goal-management',
  CHATBOT: '/chatbot',
  SETTINGS: '/settings',
};

export const NAVIGATION_ITEMS = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: ROUTES.DASHBOARD,
    icon: 'dashboard',
    description: 'View your learning analytics and progress',
  },
  {
    id: 'learning-path',
    label: 'Learning Path',
    path: ROUTES.LEARNING_PATH,
    icon: 'route',
    description: 'Manage your learning sessions and track progress',
  },
  {
    id: 'skill-gap',
    label: 'Skill Gap',
    path: ROUTES.SKILL_GAP,
    icon: 'insights',
    description: 'Identify and analyze your skill gaps',
  },
  {
    id: 'knowledge-document',
    label: 'Knowledge Documents',
    path: ROUTES.KNOWLEDGE_DOCUMENT,
    icon: 'menu_book',
    description: 'Access and manage learning materials',
  },
  {
    id: 'learner-profile',
    label: 'My Profile',
    path: ROUTES.LEARNER_PROFILE,
    icon: 'person',
    description: 'View and update your learner profile',
  },
  {
    id: 'goal-management',
    label: 'Goal Management',
    path: ROUTES.GOAL_MANAGEMENT,
    icon: 'flag',
    description: 'Set and manage your learning goals',
  },
];

export const CHART_COLORS = {
  primary: '#1976d2',
  secondary: '#dc004e',
  success: '#4caf50',
  warning: '#ff9800',
  error: '#f44336',
  info: '#2196f3',
  gradient: [
    '#1976d2',
    '#dc004e',
    '#4caf50',
    '#ff9800',
    '#9c27b0',
    '#00bcd4',
    '#ff5722',
    '#673ab7',
  ],
};

export const SKILL_LEVELS = {
  unlearned: 0,
  beginner: 1,
  intermediate: 2,
  advanced: 3,
};

export const SKILL_LEVEL_LABELS = {
  0: 'Unlearned',
  1: 'Beginner',
  2: 'Intermediate',
  3: 'Advanced',
};