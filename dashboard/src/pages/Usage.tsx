import { useState, useEffect } from 'react'
import { MessageSquare, Zap, FileText, Calendar, TrendingUp } from 'lucide-react'

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
  const [conversations, setConversations] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)
  
  useEffect(() => {
    const fetchUsage = async () => {
      setLoading(true)
      try {
        const [usageRes, conversationsRes] = await Promise.all([
          fetch(`/api/usage?days=${days}`, {
            headers: { 'X-API-Key': apiKey }
          }),
          fetch(`/api/conversations?limit=100`, {
            headers: { 'X-API-Key': apiKey }
          })
        ])
        if (usageRes.ok) {
          setUsage(await usageRes.json())
        }
        if (conversationsRes.ok) {
          const convData = await conversationsRes.json()
          setConversations(convData.conversations || [])
        }
      } catch (error) {
        console.error('Failed to fetch usage:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchUsage()
  }, [apiKey, days])

  // Calculate popular questions
  const getPopularQuestions = () => {
    const questionMap = new Map<string, number>()
    conversations.forEach(conv => {
      conv.messages?.forEach((msg: any) => {
        if (msg.role === 'user' && msg.content) {
          const question = msg.content.trim()
          if (question.length > 0 && question.length < 200) {
            questionMap.set(question, (questionMap.get(question) || 0) + 1)
          }
        }
      })
    })
    
    return Array.from(questionMap.entries())
      .map(([question, count]) => ({ question, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
  }
  
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
              {usage.daily_usage.slice().reverse().map((day) => {
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
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 24 }}>
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
                  </tr>
                </thead>
                <tbody>
                  {usage.daily_usage.slice().reverse().slice(0, 10).map(day => (
                    <tr key={day.date} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '12px 16px', fontSize: 13 }}>{day.date}</td>
                      <td style={{ padding: '12px 16px', textAlign: 'right', fontSize: 13 }}>{day.message_count.toLocaleString()}</td>
                      <td style={{ padding: '12px 16px', textAlign: 'right', fontSize: 13 }}>{day.token_count.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)' }}>No data available</p>
          )}
        </div>

        <div className="card">
          <h2 className="card-title" style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <TrendingUp size={20} />
            Popular Questions
          </h2>
          
          {getPopularQuestions().length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {getPopularQuestions().map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: 12,
                    background: 'var(--bg-input)',
                    borderRadius: 8,
                    border: '1px solid var(--border)'
                  }}
                >
                  <div style={{ fontSize: 13, marginBottom: 4, fontWeight: 500, color: 'var(--text)' }}>
                    {item.question}
                  </div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    Asked {item.count} {item.count === 1 ? 'time' : 'times'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
              No conversation data yet. Questions will appear here as visitors chat with your bot.
            </p>
          )}
        </div>
      </div>

      {usage && usage.daily_usage.length > 0 && (
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: 16 }}>Trends</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
            <div style={{ padding: 16, background: 'var(--bg-input)', borderRadius: 8 }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Growth Rate</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--primary)' }}>
                {usage.daily_usage.length > 1 ? (
                  (() => {
                    const firstHalf = usage.daily_usage.slice(0, Math.floor(usage.daily_usage.length / 2))
                    const secondHalf = usage.daily_usage.slice(Math.floor(usage.daily_usage.length / 2))
                    const firstAvg = firstHalf.reduce((sum, d) => sum + d.message_count, 0) / firstHalf.length
                    const secondAvg = secondHalf.reduce((sum, d) => sum + d.message_count, 0) / secondHalf.length
                    const growth = firstAvg > 0 ? ((secondAvg - firstAvg) / firstAvg * 100) : 0
                    return `${growth >= 0 ? '+' : ''}${Math.round(growth)}%`
                  })()
                ) : '0%'}
              </div>
            </div>
            <div style={{ padding: 16, background: 'var(--bg-input)', borderRadius: 8 }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Peak Day</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--text)' }}>
                {(() => {
                  const peak = usage.daily_usage.reduce((max, d) => d.message_count > max.message_count ? d : max, usage.daily_usage[0])
                  return peak ? peak.message_count.toLocaleString() : '0'
                })()}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
                {(() => {
                  const peak = usage.daily_usage.reduce((max, d) => d.message_count > max.message_count ? d : max, usage.daily_usage[0])
                  return peak ? peak.date : ''
                })()}
              </div>
            </div>
            <div style={{ padding: 16, background: 'var(--bg-input)', borderRadius: 8 }}>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>Avg per Day</div>
              <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--text)' }}>
                {usage.total_messages > 0 && usage.daily_usage.length > 0
                  ? Math.round(usage.total_messages / usage.daily_usage.length).toLocaleString()
                  : '0'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Usage
