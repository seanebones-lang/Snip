import { useEffect, useState } from 'react'
import { CheckCircle } from 'lucide-react'

function Success() {
  const [sessionId, setSessionId] = useState('')
  
  useEffect(() => {
    // Extract session_id from URL
    const urlParams = new URLSearchParams(window.location.search)
    const id = urlParams.get('session_id')
    if (id) {
      setSessionId(id)
    }
  }, [])

  const handleLogin = () => {
    window.location.href = '/'
  }

  return (
    <div className="success-container">
      <div className="success-card">
        <CheckCircle size={64} color="var(--success)" style={{ marginBottom: 24 }} />
        
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 16, color: 'var(--success)' }}>
          Payment Successful!
        </h1>
        
        <p style={{ marginBottom: 32, color: 'var(--text-muted)' }}>
          Your subscription is active. Check your email for your API key.
        </p>
        
        <div style={{ 
          background: 'var(--bg-input)', 
          padding: 24, 
          borderRadius: 12, 
          marginBottom: 32,
          textAlign: 'center'
        }}>
          <h3 style={{ marginBottom: 16 }}>Next Steps</h3>
          <ol style={{ textAlign: 'left', maxWidth: 400, margin: '0 auto' }}>
            <li>Check your email (including spam) for your API key</li>
            <li>Go to <a href="https://snip.mothership-ai.com" style={{ color: 'var(--primary)' }}>snip.mothership-ai.com</a></li>
            <li>Enter your API key to log in</li>
            <li>Customize your chatbot and get your embed code</li>
          </ol>
        </div>
        
        <div style={{ display: 'flex', gap: 12 }}>
          <button className="btn btn-primary" onClick={handleLogin} style={{ flex: 1 }}>
            Go to Login
          </button>
          <a href="mailto:support@mothership-ai.com" className="btn btn-secondary" style={{ flex: 1 }}>
            Contact Support
          </a>
        </div>
        
        {sessionId && (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 24, textAlign: 'center' }}>
            Session ID: {sessionId} (for support)
          </p>
        )}
      </div>
    </div>
  )
}

export default Success