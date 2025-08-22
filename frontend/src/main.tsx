import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { AgentProvider } from '@ic-reactor/react'
import AnimatedCursor from 'react-animated-cursor'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AgentProvider>
      <AuthProvider>
        <AnimatedCursor color='200, 255, 255'/>
        <App />
      </AuthProvider>
    </AgentProvider>
  </StrictMode>,
)
