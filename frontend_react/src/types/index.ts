// User types
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  createdAt: string;
  updatedAt: string;
}

// Learning types
export interface LearningGoal {
  id: string;
  title: string;
  description: string;
  targetDate?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'active' | 'completed' | 'paused';
  progress: number;
  createdAt: string;
  updatedAt: string;
}

export interface Skill {
  id: string;
  name: string;
  description: string;
  category: string;
  proficiencyLevel: 'unlearned' | 'beginner' | 'intermediate' | 'advanced';
  requiredLevel: 'beginner' | 'intermediate' | 'advanced';
  isGap: boolean;
  priority: 'low' | 'medium' | 'high';
  estimatedTime: number; // in hours
}

export interface SkillGap {
  skill: Skill;
  gapAnalysis: string;
  recommendedActions: string[];
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  sessions: LearningSession[];
  totalDuration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

export interface LearningSession {
  id: string;
  title: string;
  description: string;
  duration: number; // in minutes
  order: number;
  type: 'video' | 'reading' | 'exercise' | 'quiz' | 'project';
  resources: Resource[];
  completed: boolean;
  completedAt?: string;
}

export interface Resource {
  id: string;
  title: string;
  type: 'video' | 'article' | 'pdf' | 'link' | 'exercise';
  url: string;
  duration?: number;
  description?: string;
}

export interface LearnerProfile {
  id: string;
  userId: string;
  background: string;
  experience: string;
  learningStyle: 'visual' | 'auditory' | 'kinesthetic' | 'mixed';
  preferences: {
    contentStyle: string[];
    activityType: string[];
    timeCommitment: number; // hours per week
    preferredTime: 'morning' | 'afternoon' | 'evening' | 'flexible';
  };
  cognitiveStatus: CognitiveStatus;
  behavioralPatterns: BehavioralPatterns;
  createdAt: string;
  updatedAt: string;
}

export interface CognitiveStatus {
  overallProgress: number; // percentage
  masteredSkills: Skill[];
  inProgressSkills: Skill[];
  unlearnedSkills: Skill[];
  learningVelocity: number; // skills per week
  retentionRate: number; // percentage
}

export interface BehavioralPatterns {
  systemUsageFrequency: string;
  sessionDurationEngagement: string;
  motivationalTriggers: string[];
  completionRate: number;
  averageSessionTime: number; // in minutes
  preferredLearningTime: string;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  content: string;
  summary: string;
  tags: string[];
  category: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedReadTime: number; // in minutes
  createdAt: string;
  updatedAt: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

// Analytics types
export interface LearningAnalytics {
  totalTimeSpent: number; // in minutes
  averageSessionDuration: number;
  completionRate: number;
  skillProgression: SkillProgression[];
  learningTrend: DataPoint[];
  sessionHistory: SessionHistory[];
}

export interface SkillProgression {
  skillId: string;
  skillName: string;
  startLevel: number;
  currentLevel: number;
  targetLevel: number;
  progress: number;
  timestamps: string[];
}

export interface DataPoint {
  timestamp: string;
  value: number;
  label?: string;
}

export interface SessionHistory {
  sessionId: string;
  date: string;
  duration: number;
  skillsCovered: string[];
  completionRate: number;
  engagementScore: number;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// Form types
export interface OnboardingFormData {
  learningGoal: string;
  background: string;
  experience: string;
  learningStyle: string;
  timeCommitment: number;
  preferredTime: string;
}

export interface SkillGapFormData {
  skills: Skill[];
  priorities: Record<string, 'low' | 'medium' | 'high'>;
}

// Navigation types
export interface NavigationItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  description?: string;
  children?: NavigationItem[];
}

// UI types
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
}

export interface ErrorState {
  hasError: boolean;
  message?: string;
  details?: any;
}

// Configuration types
export interface AppConfig {
  backendEndpoint: string;
  useMockData: boolean;
  llmType: 'gpt4o' | 'llama' | 'deepseek' | 'together';
  features: {
    darkMode: boolean;
    notifications: boolean;
    analytics: boolean;
    chatbot: boolean;
  };
}