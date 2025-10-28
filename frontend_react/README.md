# GenMentor React Frontend

A modern, high-performance React-based frontend for GenMentor - an AI-powered learning platform that provides personalized learning experiences.

## 🚀 Features

- **Modern UI/UX**: Built with Material-UI (MUI) for a polished, professional interface
- **Light/Dark Mode**: Full theme support with automatic system preference detection
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Advanced Analytics**: Interactive charts and visualizations using Recharts
- **Smooth Animations**: Enhanced user experience with Framer Motion
- **Type Safety**: Full TypeScript support for better development experience
- **High Performance**: Built with Vite for fast development and optimized builds

## 🛠️ Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI (MUI) v5
- **Charts**: Recharts
- **Animations**: Framer Motion
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Form Handling**: React Hook Form with Yup validation
- **Date Utilities**: date-fns

## 📦 Installation

1. Navigate to the frontend directory:
```bash
cd /home/ubuntu/tfwang/code/GenMentor/frontend_react
```

2. Install dependencies:
```bash
npm install
```

## 🚀 Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🔧 Build

Build for production:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## 📁 Project Structure

```
frontend_react/
├── public/                 # Static assets
│   └── assets/            # Images, icons, etc.
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── Layout/       # Layout components (Header, Navigation, MainLayout)
│   │   └── Common/       # Common components (LoadingSpinner, ErrorBoundary)
│   ├── contexts/         # React contexts (Theme, Auth, Notification)
│   ├── pages/            # Page components
│   ├── theme/            # Theme configuration
│   ├── types/            # TypeScript type definitions
│   ├── config/           # Application configuration
│   └── utils/            # Utility functions
└── dist/                 # Production build output
```

## 🎨 Features Implemented

### ✅ Completed
- **Project Setup**: Modern React + TypeScript + Vite configuration
- **Theme System**: Light/dark mode with Material-UI theming
- **Layout Components**: Responsive navigation, header, and main layout
- **Dashboard**: Comprehensive analytics with interactive charts
- **Routing**: Complete routing setup with all main pages
- **Error Handling**: Error boundary for better error management
- **Notifications**: Toast notification system
- **Authentication**: Basic auth context setup

### 🚧 In Progress
- **Onboarding Flow**: User onboarding and goal setting
- **Learning Path Management**: Session tracking and progress visualization
- **Skill Gap Analysis**: Interactive skill gap identification
- **Knowledge Document Management**: Document upload and organization
- **Learner Profile**: User profile management
- **Goal Management**: Learning goal setting and tracking
- **AI Chatbot**: Interactive AI tutor interface
- **Settings**: Application preferences and configuration

## 🎯 Key Improvements Over Streamlit Version

1. **Performance**: React + Vite provides much faster load times and interactions
2. **UI/UX**: Material-UI offers superior design consistency and modern aesthetics
3. **Responsiveness**: Fully responsive design that works on all devices
4. **Animations**: Smooth transitions and animations for better user experience
5. **Type Safety**: Full TypeScript support reduces runtime errors
6. **Scalability**: Component-based architecture for easier maintenance and extension
7. **Developer Experience**: Hot module replacement and better debugging tools

## 🔮 Future Enhancements

- **PWA Support**: Convert to Progressive Web App for offline functionality
- **Advanced Analytics**: More sophisticated learning analytics and insights
- **Collaborative Features**: Social learning and peer interaction
- **Mobile App**: React Native version for mobile platforms
- **AI Integration**: Enhanced AI-powered recommendations and personalization
- **Gamification**: Learning achievements, badges, and progress gamification

## 📝 API Integration

The frontend is designed to integrate with the GenMentor backend API. Configure the backend endpoint in `src/config/index.ts`:

```typescript
backendEndpoint: 'http://127.0.0.1:5006/', // Your backend URL
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the GenMentor system and follows the same licensing terms.