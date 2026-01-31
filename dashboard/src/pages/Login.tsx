import { useState } from 'react'
import { KeyRound, ArrowRight } from 'lucide-react'
import { apiUrl } from '../api'

interface LoginProps {
  onLogin: (apiKey: string) => void
}

function Login({ onLogin }: LoginProps) {
  const [apiKey, setApiKey] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showResend, setShowResend] = useState(false)
  const [resendEmail, setResendEmail] = useState('')
  const [resendStatus, setResendStatus] = useState<string | null>(null)
  const [resendLoading, setResendLoading] = useState(false)

  const handleResend = async (e: React.FormEvent) => {
    e.preventDefault()
    setResendStatus(null)
    setResendLoading(true)
    try {
      const res = await fetch(apiUrl('/api/resend-api-key'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: resendEmail.trim() })
      })
      const data = await res.json().catch(() => ({}))
      setResendStatus(data.message || 'If an account exists for this email, a new API key has been sent.')
    } catch {
      setResendStatus('Request failed. Try again or contact support.')
    } finally {
      setResendLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    
    try {
      const response = await fetch(apiUrl('/api/clients/me'), {
        headers: {
          'X-API-Key': apiKey
        }
      })
      
      if (!response.ok) {
        throw new Error('Invalid API key')
      }
      
      onLogin(apiKey)
    } catch (err) {
      setError('Invalid API key. Please check and try again.')
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="login-container">
      <div className="login-card">
        <h1 className="login-logo">Snip by NextEleven</h1>
        <p className="login-subtitle">Enter your API key to access the dashboard</p>
        
        {error && (
          <div className="alert alert-warning" style={{ marginBottom: 24 }}>
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">API Key</label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                className="form-input"
                placeholder="snip_xxxxxxxxxxxx"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                style={{ paddingLeft: 44 }}
              />
              <KeyRound 
                size={18} 
                style={{ 
                  position: 'absolute', 
                  left: 14, 
                  top: '50%', 
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)'
                }} 
              />
            </div>
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%' }}
            disabled={isLoading || !apiKey}
          >
            {isLoading ? 'Verifying...' : 'Access Dashboard'}
            <ArrowRight size={18} />
          </button>
        </form>
        
        <p style={{ marginTop: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
          New here? You've been sent an API key via email. Check spam if missing. Questions? <a href="mailto:support@mothership-ai.com">support@mothership-ai.com</a>.
        </p>
        <p style={{ marginTop: 12, textAlign: 'center', fontSize: 14 }}>
          <button type="button" className="btn-link" onClick={() => setShowResend(!showResend)}>
            Forgot your API key?
          </button>
        </p>
        {showResend && (
          <form onSubmit={handleResend} style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid var(--border)' }}>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input
                type="email"
                className="form-input"
                placeholder="you@example.com"
                value={resendEmail}
                onChange={(e) => setResendEmail(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-secondary" style={{ width: '100%' }} disabled={resendLoading || !resendEmail.trim()}>
              {resendLoading ? 'Sending...' : 'Send new API key'}
            </button>
            {resendStatus && <p style={{ marginTop: 12, fontSize: 13, color: 'var(--text-muted)' }}>{resendStatus}</p>}
          </form>
        )}
      </div>
    </div>
  )
}

export default Login
