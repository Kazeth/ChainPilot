import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { AgentProvider } from '@ic-reactor/react'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AgentProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </AgentProvider>
  </StrictMode>,
)
