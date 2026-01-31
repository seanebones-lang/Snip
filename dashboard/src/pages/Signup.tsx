import { useState } from 'react'
import { ArrowRight, CreditCard } from 'lucide-react'

function Signup() {
  const [tier, setTier] = useState('standard')
  const [email, setEmail] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tier,
          email,
          company_name: companyName
        })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create checkout session')
      }

      const data = await response.json()
      window.location.href = data.url
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const tiers = [
    {
      id: 'basic',
      name: 'Basic',
      price: '$25/mo',
      features: ['Custom branding', 'Voice selection', 'FAQ management']
    },
    {
      id: 'standard',
      name: 'Standard',
      price: '$40/mo',
      features: ['Everything in Basic', 'Document upload (RAG)', 'Hide branding']
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: '$60/mo',
      features: ['Everything in Standard', 'Fine tuning', 'Advanced analytics']
    }
  ]

  return (
    <div className="signup-container">
      <div className="signup-card">
        <h1 style={{ fontSize: 36, fontWeight: 700, marginBottom: 16 }}>Custom AI Chatbots<br/><span style={{ fontWeight: 400, fontSize: 24, color: 'var(--text-muted)' }}>$25/month</span></h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
          Choose your plan and get your chatbot live in minutes.
        </p>

        {error && (
          <div className="alert alert-warning" style={{ marginBottom: 24 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Your Email</label>
            <input
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="john@acme.com"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Company Name</label>
            <input
              type="text"
              className="form-input"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="Acme Corporation"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Plan</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16 }}>
              {tiers.map((plan) => (
                <label key={plan.id} className={`plan-card ${tier === plan.id ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="tier"
                    value={plan.id}
                    checked={tier === plan.id}
                    onChange={(e) => setTier(e.target.value)}
                    style={{ display: 'none' }}
                  />
                  <div>
                    <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>{plan.name}</div>
                    <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--primary)', marginBottom: 12 }}>{plan.price}</div>
                    <ul style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 16 }}>
                      {plan.features.map((feature) => (
                        <li key={feature} style={{ marginBottom: 4 }}>&bull; {feature}</li>
                      ))}
                    </ul>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: 24 }}
            disabled={loading || !email || !companyName}
          >
            <CreditCard size={20} style={{ marginRight: 8 }} />
            {loading ? 'Creating Checkout...' : 'Get Started Now'}
            <ArrowRight size={20} />
          </button>
        </form>

        <p style={{ marginTop: 32, textAlign: 'center', color: 'var(--text-muted)', fontSize: 14 }}>
          Already have an API key? <a href="/login">Login here</a> | Questions? <a href="mailto:support@mothership-ai.com">support@mothership-ai.com</a>
        </p>
      </div>
    </div>
  )
}

export default Signup