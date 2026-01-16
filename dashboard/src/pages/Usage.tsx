import { useState, useEffect } from 'react'
import { MessageSquare, Zap, FileText, Calendar } from 'lucide-react'

interface UsageProps {
  apiKey: string
}

interface DailyUsage {
  date: string
  message_count: number
  token_count: number
  rag_query_count: number
}

interface UsageData {
  total_messages: number
  total_tokens: number
  total_rag_queries: number
  daily_usage: DailyUsage[]
}

function Usage({ apiKey }: UsageProps) {
  const [usage, setUsage] = useState<UsageData | null>(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)
  
  useEffect(() => {
    const fetchUsage = async () => {
      setLoading(true)
      try {
        const res = await fetch(`/api/usage?days=${days}`, {
          headers: { 'X-API-Key': apiKey }
        })
        if (res.ok) {
          setUsage(await res.json())
        }
      } catch (error) {
        console.error('Failed to fetch usage:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchUsage()
  }, [apiKey, days])
  
  const getMaxValue = (data: DailyUsage[], key: keyof DailyUsage) => {
    return Math.max(...data.map(d => d[key] as number), 1)
  }
  
  if (loading) {
    return <div>Loading...</div>
  }
  
  return (
    <div>
      <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            Usage Analytics
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Monitor your chatbot's performance and usage.
          </p>
        </div>
        
        <select
          className="form-input"
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          style={{ width: 'auto' }}
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>
      
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
          <div className="stat-label">Total Messages</div>
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
              <Calendar size={24} color="var(--warning)" />
            </div>
          </div>
          <div className="stat-value">
            {usage && usage.total_messages > 0 
              ? Math.round(usage.total_messages / days) 
              : 0}
          </div>
          <div className="stat-label">Avg. Daily Messages</div>
        </div>
      </div>
      
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 24 }}>Messages Over Time</h2>
        
        {usage && usage.daily_usage.length > 0 ? (
          <div>
            <div style={{ 
              display: 'flex', 
              alignItems: 'flex-end', 
              gap: 4, 
              height: 200,
              padding: '0 16px'
            }}>
              {usage.daily_usage.slice().reverse().map((day, i) => {
                const maxMessages = getMaxValue(usage.daily_usage, 'message_count')
                const height = (day.message_count / maxMessages) * 100
                
                return (
                  <div
                    key={day.date}
                    style={{
                      flex: 1,
                      minWidth: 8,
                      height: `${Math.max(height, 2)}%`,
                      background: `linear-gradient(180deg, var(--primary) 0%, var(--primary) 100%)`,
                      borderRadius: '4px 4px 0 0',
                      transition: 'height 0.3s ease',
                      position: 'relative',
                    }}
                    title={`${day.date}: ${day.message_count} messages`}
                  />
                )
              })}
            </div>
            
            <div style={{ 
              display: 'flex', 
              justifyContent: 'space-between',
              marginTop: 8,
              padding: '0 16px',
              color: 'var(--text-muted)',
              fontSize: 12
            }}>
              <span>{usage.daily_usage[usage.daily_usage.length - 1]?.date || ''}</span>
              <span>{usage.daily_usage[0]?.date || ''}</span>
            </div>
          </div>
        ) : (
          <div style={{ 
            textAlign: 'center', 
            padding: 48, 
            background: 'var(--bg-input)', 
            borderRadius: 12 
          }}>
            <p style={{ color: 'var(--text-muted)' }}>
              No usage data yet. Start using your chatbot to see analytics.
            </p>
          </div>
        )}
      </div>
      
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 16 }}>Daily Breakdown</h2>
        
        {usage && usage.daily_usage.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ textAlign: 'left', padding: '12px 16px', color: 'var(--text-muted)', fontWeight: 500, fontSize: 14 }}>Date</th>
                  <th style={{ textAlign: 'right', padding: '12px 16px', color: 'var(--text-muted)', fontWeight: 500, fontSize: 14 }}>Messages</th>
                  <th style={{ textAlign: 'right', padding: '12px 16px', color: 'var(--text-muted)', fontWeight: 500, fontSize: 14 }}>Tokens</th>
                  <th style={{ textAlign: 'right', padding: '12px 16px', color: 'var(--text-muted)', fontWeight: 500, fontSize: 14 }}>RAG Queries</th>
                </tr>
              </thead>
              <tbody>
                {usage.daily_usage.map(day => (
                  <tr key={day.date} style={{ borderBottom: '1px solid var(--border)' }}>
                    <td style={{ padding: '12px 16px' }}>{day.date}</td>
                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>{day.message_count.toLocaleString()}</td>
                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>{day.token_count.toLocaleString()}</td>
                    <td style={{ padding: '12px 16px', textAlign: 'right' }}>{day.rag_query_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>No data available</p>
        )}
      </div>
    </div>
  )
}

export default Usage
