import { useState, useEffect } from 'react'
import { MessageSquare, Zap, FileText, TrendingUp } from 'lucide-react'

interface DashboardProps {
  apiKey: string
}

interface ClientInfo {
  id: string
  email: string
  company_name: string
  tier: 'basic' | 'standard' | 'enterprise'
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
        <h2 className="card-title" style={{ marginBottom: 16 }}>Quick Actions</h2>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <a href="/branding" className="btn btn-primary">
            Customize Branding
          </a>
          <a href="/snippet" className="btn btn-secondary">
            Get Embed Code
          </a>
          {client?.tier === 'basic' && (
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-secondary" style={{ background: 'rgba(236, 72, 153, 0.2)', borderColor: '#ec4899', color: '#ec4899' }}>
                Upgrade to Standard ($40/mo)
              </button>
              <button className="btn btn-secondary" style={{ background: 'rgba(34, 197, 94, 0.2)', borderColor: 'var(--success)', color: 'var(--success)' }}>
                Enterprise ($60/mo)
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
