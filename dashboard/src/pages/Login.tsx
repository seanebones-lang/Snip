import { useState } from 'react'
import { KeyRound, ArrowRight } from 'lucide-react'

interface LoginProps {
  onLogin: (apiKey: string) => void
}

function Login({ onLogin }: LoginProps) {
  const [apiKey, setApiKey] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)
    
    try {
      const response = await fetch('/api/clients/me', {
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
        <h1 className="login-logo">Snip</h1>
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
          Don't have an account? Contact us to get started.
        </p>
      </div>
    </div>
  )
}

export default Login
