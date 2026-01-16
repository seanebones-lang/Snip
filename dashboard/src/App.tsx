import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Branding from './pages/Branding'
import Snippet from './pages/Snippet'
import Documents from './pages/Documents'
import Usage from './pages/Usage'

function App() {
  const [apiKey, setApiKey] = useState<string | null>(() => {
    return localStorage.getItem('snip_api_key')
  })
  
  const handleLogin = (key: string) => {
    localStorage.setItem('snip_api_key', key)
    setApiKey(key)
  }
  
  const handleLogout = () => {
    localStorage.removeItem('snip_api_key')
    setApiKey(null)
  }
  
  if (!apiKey) {
    return <Login onLogin={handleLogin} />
  }
  
  return (
    <Layout apiKey={apiKey} onLogout={handleLogout}>
      <Routes>
        <Route path="/" element={<Dashboard apiKey={apiKey} />} />
        <Route path="/branding" element={<Branding apiKey={apiKey} />} />
        <Route path="/snippet" element={<Snippet apiKey={apiKey} />} />
        <Route path="/documents" element={<Documents apiKey={apiKey} />} />
        <Route path="/usage" element={<Usage apiKey={apiKey} />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  )
}

export default App
