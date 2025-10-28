import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

// Add Roboto font for Material-UI
const link = document.createElement('link');
link.rel = 'stylesheet';
link.href = 'https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap';
document.head.appendChild(link);

// Add Material-UI icons
const iconsLink = document.createElement('link');
iconsLink.rel = 'stylesheet';
iconsLink.href = 'https://fonts.googleapis.com/icon?family=Material+Icons';
document.head.appendChild(iconsLink);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)