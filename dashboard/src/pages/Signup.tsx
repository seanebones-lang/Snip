import { useEffect, useState } from 'react'
import { ArrowRight, CreditCard } from 'lucide-react'
import { useSearchParams } from 'react-router-dom'
import { apiUrl } from '../api'

function Signup() {
  const [tier, setTier] = useState('standard')
  const [email, setEmail] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchParams] = useSearchParams()

  useEffect(() => {
    const selectedTier = searchParams.get('tier')?.toLowerCase()
    if (selectedTier && ['basic', 'standard', 'premium'].includes(selectedTier)) {
      setTier(selectedTier)
    }
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(apiUrl('/api/checkout'), {
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
      id: 'premium',
      name: 'Premium',
      price: '$60/mo',
      features: ['Everything in Standard', 'Fine tuning', 'Advanced analytics']
    }
  ]

  const selectedPlan = tiers.find((plan) => plan.id === tier) ?? tiers[1]

  return (
    <div className="signup-container">
      <div className="signup-card">
        <h1 className="signup-title">Custom AI Chatbots</h1>
        <p className="signup-price">{selectedPlan.name} • {selectedPlan.price}</p>
        <p className="signup-note">Billed monthly. Cancel anytime.</p>
        <p className="signup-subtitle">Choose your plan and get your chatbot live in minutes.</p>

        {error && (
          <div className="alert alert-warning signup-alert">
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
            <div className="plan-grid">
              {tiers.map((plan) => (
                <label key={plan.id} className={`plan-card ${tier === plan.id ? 'selected' : ''}`}>
                  <input
                    type="radio"
                    name="tier"
                    value={plan.id}
                    checked={tier === plan.id}
                    onChange={(e) => setTier(e.target.value)}
                    className="plan-card-input"
                  />
                  <div className="plan-card-content">
                    <div className="plan-card-title">{plan.name}</div>
                    <div className="plan-card-price">{plan.price}</div>
                    <ul className="plan-card-features">
                      {plan.features.map((feature) => (
                        <li key={feature}>&bull; {feature}</li>
                      ))}
                    </ul>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary signup-submit"
            disabled={loading || !email || !companyName}
          >
            <CreditCard size={20} />
            {loading ? 'Creating Checkout...' : 'Get Started Now'}
            <ArrowRight size={20} />
          </button>
        </form>

        <p className="signup-footer">
          Already have an API key? <a href="/login">Login here</a> | Questions? <a href="mailto:support@mothership-ai.com">support@mothership-ai.com</a>
        </p>
      </div>
    </div>
  )
}

export default Signup