import { useState, useEffect } from 'react'
import { MessageSquare, Zap, FileText, TrendingUp, Check } from 'lucide-react'

interface DashboardProps {
  apiKey: string
}

interface ClientInfo {
  id: string
  email: string
  company_name: string
  tier: 'basic' | 'premium'
  is_active: boolean
  created_at: string
}

interface UsageData {
  total_messages: number
  total_tokens: number
  total_rag_queries: number
}

function Dashboard({ apiKey }: DashboardProps) {
  const [client, setClient] = useState<ClientInfo | null>(null)
  const [usage, setUsage] = useState<UsageData | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clientRes, usageRes] = await Promise.all([
          fetch('/api/clients/me', {
            headers: { 'X-API-Key': apiKey }
          }),
          fetch('/api/usage?days=30', {
            headers: { 'X-API-Key': apiKey }
          })
        ])
        
        if (clientRes.ok) {
          setClient(await clientRes.json())
        }
        if (usageRes.ok) {
          setUsage(await usageRes.json())
        }
      } catch (error) {
        console.error('Failed to fetch data:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchData()
  }, [apiKey])
  
  if (loading) {
    return <div>Loading...</div>
  }
  
  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
          Welcome back{client ? `, ${client.company_name}` : ''}!
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Here's an overview of your chatbot performance.
        </p>
      </div>
      
      {client && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 4 }}>Account Status</p>
              <p style={{ fontSize: 18, fontWeight: 600 }}>{client.email}</p>
            </div>
            <span className={`badge badge-${client.tier}`}>
              {client.tier.toUpperCase()}
            </span>
          </div>
        </div>
      )}
      
      <div className="stats-grid">
        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <div style={{ 
              width: 48, 
              height: 48, 
              borderRadius: 12, 
              background: 'rgba(99, 102, 241, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <MessageSquare size={24} color="var(--primary)" />
            </div>
          </div>
          <div className="stat-value">{usage?.total_messages.toLocaleString() || 0}</div>
          <div className="stat-label">Messages (30 days)</div>
        </div>
        
        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <div style={{ 
              width: 48, 
              height: 48, 
              borderRadius: 12, 
              background: 'rgba(236, 72, 153, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Zap size={24} color="#ec4899" />
            </div>
          </div>
          <div className="stat-value">{usage?.total_tokens.toLocaleString() || 0}</div>
          <div className="stat-label">Tokens Used</div>
        </div>
        
        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <div style={{ 
              width: 48, 
              height: 48, 
              borderRadius: 12, 
              background: 'rgba(34, 197, 94, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <FileText size={24} color="var(--success)" />
            </div>
          </div>
          <div className="stat-value">{usage?.total_rag_queries || 0}</div>
          <div className="stat-label">RAG Queries</div>
        </div>
        
        <div className="stat-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
            <div style={{ 
              width: 48, 
              height: 48, 
              borderRadius: 12, 
              background: 'rgba(245, 158, 11, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <TrendingUp size={24} color="var(--warning)" />
            </div>
          </div>
          <div className="stat-value">
            {usage && usage.total_messages > 0 
              ? Math.round(usage.total_messages / 30) 
              : 0}
          </div>
          <div className="stat-label">Avg. Daily Messages</div>
        </div>
      </div>
      
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 24 }}>Pricing Plans</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 24, fontSize: 14 }}>
          Monthly hosting, service, and updates. Upgrade anytime to unlock more features.
        </p>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
          gap: 20,
          marginBottom: 16
        }}>
          {/* Basic Plan */}
          <div style={{
            background: 'var(--bg-input)',
            border: `2px solid ${client?.tier === 'basic' ? 'var(--primary)' : 'var(--border)'}`,
            borderRadius: '12px',
            padding: '24px',
            position: 'relative',
            transition: 'all 0.2s'
          }}>
            <div style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: 20, fontWeight: 600, marginBottom: 8 }}>Basic</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                <span style={{ fontSize: 36, fontWeight: 700 }}>$25</span>
                <span style={{ color: 'var(--text-muted)', fontSize: 14 }}>/month</span>
              </div>
            </div>
            <ul style={{ listStyle: 'none', marginBottom: 24 }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Chatbot widget included</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Custom branding</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Monthly updates</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Basic support</span>
              </li>
            </ul>
            {client?.tier === 'basic' ? (
              <button className="btn btn-primary" style={{ width: '100%', pointerEvents: 'none', opacity: 0.7 }}>
                Current Plan
              </button>
            ) : (
              <button className="btn btn-secondary" style={{ width: '100%' }}>
                Select Basic
              </button>
            )}
          </div>

          {/* Standard Plan */}
          <div style={{
            background: 'var(--bg-input)',
            border: `2px solid ${client?.tier === 'premium' ? '#ec4899' : 'var(--border)'}`,
            borderRadius: '12px',
            padding: '24px',
            position: 'relative',
            transition: 'all 0.2s'
          }}>
            <div style={{ 
              position: 'absolute', 
              top: -10, 
              right: 16, 
              background: '#ec4899', 
              color: 'white', 
              padding: '4px 12px', 
              borderRadius: '12px', 
              fontSize: 12, 
              fontWeight: 600 
            }}>
              POPULAR
            </div>
            <div style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: 20, fontWeight: 600, marginBottom: 8 }}>Standard</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                <span style={{ fontSize: 36, fontWeight: 700 }}>$50</span>
                <span style={{ color: 'var(--text-muted)', fontSize: 14 }}>/month</span>
              </div>
            </div>
            <ul style={{ listStyle: 'none', marginBottom: 24 }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Everything in Basic</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Document training (RAG)</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Advanced analytics</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Priority support</span>
              </li>
            </ul>
            {client?.tier === 'premium' ? (
              <button className="btn btn-primary" style={{ width: '100%', background: '#ec4899', pointerEvents: 'none', opacity: 0.7 }}>
                Current Plan
              </button>
            ) : (
              <button className="btn btn-primary" style={{ width: '100%', background: '#ec4899' }}>
                Select Standard
              </button>
            )}
          </div>

          {/* Advanced Plan */}
          <div style={{
            background: 'var(--bg-input)',
            border: '2px solid var(--border)',
            borderRadius: '12px',
            padding: '24px',
            position: 'relative',
            transition: 'all 0.2s'
          }}>
            <div style={{ marginBottom: 16 }}>
              <h3 style={{ fontSize: 20, fontWeight: 600, marginBottom: 8 }}>Advanced</h3>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                <span style={{ fontSize: 36, fontWeight: 700 }}>$100</span>
                <span style={{ color: 'var(--text-muted)', fontSize: 14 }}>/month</span>
              </div>
            </div>
            <ul style={{ listStyle: 'none', marginBottom: 24 }}>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Everything in Standard</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Remove branding</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Custom integrations</span>
              </li>
              <li style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, fontSize: 14 }}>
                <Check size={18} color="var(--success)" />
                <span>Dedicated support</span>
              </li>
            </ul>
            <button className="btn btn-secondary" style={{ width: '100%' }}>
              Select Advanced
            </button>
          </div>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: 12, textAlign: 'center', marginTop: 16 }}>
          All plans include hosting, service maintenance, and monthly updates. Billed monthly, cancel anytime.
        </p>
      </div>
      
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 16 }}>Quick Actions</h2>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <a href="/branding" className="btn btn-primary">
            Customize Branding
          </a>
          <a href="/snippet" className="btn btn-secondary">
            Get Embed Code
          </a>
          {client?.tier === 'basic' && (
            <button className="btn btn-secondary" style={{ background: 'rgba(236, 72, 153, 0.2)', borderColor: '#ec4899', color: '#ec4899' }}>
              Upgrade to Premium
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
