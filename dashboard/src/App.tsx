import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { apiUrl } from './api'
import Layout from './components/Layout'
import Login from './pages/Login'
import Landing from './pages/Landing'
import Signup from './pages/Signup'
import Success from './pages/Success'
import Help from './pages/Help'
import Dashboard from './pages/Dashboard'
import Branding from './pages/Branding'
import Snippet from './pages/Snippet'
import Documents from './pages/Documents'
import Usage from './pages/Usage'
import TestChat from './pages/TestChat'
import FAQs from './pages/FAQs'
import Conversations from './pages/Conversations'
import OnboardingWizard from './components/OnboardingWizard'

function App() {
  const [apiKey, setApiKey] = useState<string | null>(() => {
    return localStorage.getItem('snip_api_key')
  })
  
  const [showWizard, setShowWizard] = useState(false)
  
  const handleLogin = (key: string) => {
    localStorage.setItem('snip_api_key', key)
    setApiKey(key)
  }
  
  const handleLogout = () => {
    localStorage.removeItem('snip_api_key')
    setApiKey(null)
  }
  
  const handleWizardComplete = () => {
    setShowWizard(false)
  }
  
  useEffect(() => {
    if (apiKey) {
      // Check if onboarding completed
      fetch(apiUrl('/api/config'), {
        headers: { 'X-API-Key': apiKey }
      }).then(res => res.json()).then(data => {
        setShowWizard(!data.has_completed_onboarding)
      }).catch(() => {
        setShowWizard(false)
      })
    }
  }, [apiKey])
  
  if (!apiKey) {
    return (
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/success" element={<Success />} />
        <Route path="/help" element={<Help />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    )
  }
  
  return (
    <>
      <Layout apiKey={apiKey} onLogout={handleLogout}>
        <Routes>
          <Route path="/" element={<Dashboard apiKey={apiKey} />} />
          <Route path="/branding" element={<Branding apiKey={apiKey} />} />
          <Route path="/snippet" element={<Snippet apiKey={apiKey} />} />
          <Route path="/test" element={<TestChat apiKey={apiKey} />} />
          <Route path="/conversations" element={<Conversations apiKey={apiKey} />} />
          <Route path="/faqs" element={<FAQs apiKey={apiKey} />} />
          <Route path="/documents" element={<Documents apiKey={apiKey} />} />
          <Route path="/usage" element={<Usage apiKey={apiKey} />} />
          <Route path="/help" element={<Help />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
      {showWizard && (
        <OnboardingWizard 
          apiKey={apiKey!} 
          onComplete={handleWizardComplete} 
          isOpen={true} 
          onClose={() => setShowWizard(false)}
        />
      )}
    </>
  )
}

export default App
