import { useState, useEffect } from 'react'
import { MessageSquare, Search } from 'lucide-react'
import { apiUrl } from '../api'

interface ConversationsProps {
  apiKey: string
}

interface Message {
  id: string
  role: string
  content: string
  created_at: string
}

interface Conversation {
  id: string
  started_at: string
  last_message_at: string
  message_count: number
  messages: Message[]
}

function Conversations({ apiKey }: ConversationsProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [total, setTotal] = useState(0)

  useEffect(() => {
    fetchConversations()
  }, [apiKey])

  const fetchConversations = async () => {
    try {
      const res = await fetch(apiUrl('/api/conversations?limit=50'), {
        headers: { 'X-API-Key': apiKey }
      })
      if (res.ok) {
        const data = await res.json()
        setConversations(data.conversations || [])
        setTotal(data.total || 0)
      }
    } catch (error) {
      console.error('Failed to fetch conversations:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const filteredConversations = conversations.filter(conv => {
    if (!search) return true
    const searchLower = search.toLowerCase()
    return conv.messages.some(msg => 
      msg.content.toLowerCase().includes(searchLower)
    )
  })

  const selectedConversation = conversations.find(c => c.id === selectedId)

  if (loading) {
    return <div>Loading conversations...</div>
  }

  return (
    <div>
      <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            Conversation Logs
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            View all conversations between visitors and your chatbot. ({total} total)
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '400px 1fr', gap: 24, height: 'calc(100vh - 200px)', minHeight: 600 }}>
        <div className="card" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ marginBottom: 16 }}>
            <div style={{ position: 'relative' }}>
              <Search size={18} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input
                type="text"
                className="form-input"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search conversations..."
                style={{ paddingLeft: 40 }}
              />
            </div>
          </div>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 8 }}>
            {filteredConversations.length === 0 ? (
              <div style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)' }}>
                {search ? 'No conversations match your search' : 'No conversations yet'}
              </div>
            ) : (
              filteredConversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => setSelectedId(conv.id)}
                  style={{
                    padding: 12,
                    border: '1px solid var(--border)',
                    borderRadius: 8,
                    background: selectedId === conv.id ? 'var(--primary)' : 'var(--bg-card)',
                    color: selectedId === conv.id ? 'white' : 'var(--text)',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ fontSize: 12, marginBottom: 4, opacity: 0.8 }}>
                    {formatDate(conv.started_at)}
                  </div>
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
                    {conv.message_count} messages
                  </div>
                  <div style={{ fontSize: 12, opacity: 0.8, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {conv.messages[0]?.content || 'No messages'}...
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="card" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {selectedConversation ? (
            <>
              <div style={{ padding: 16, borderBottom: '1px solid var(--border)', marginBottom: 16 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
                  <MessageSquare size={20} color="var(--primary)" />
                  <h2 className="card-title" style={{ margin: 0 }}>
                    Conversation Details
                  </h2>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', gap: 16 }}>
                  <span>Started: {formatDate(selectedConversation.started_at)}</span>
                  <span>Last: {formatDate(selectedConversation.last_message_at)}</span>
                  <span>{selectedConversation.message_count} messages</span>
                </div>
              </div>

              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 12, padding: '0 16px 16px' }}>
                {selectedConversation.messages.map((msg, idx) => (
                  <div
                    key={msg.id || idx}
                    style={{
                      alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                      maxWidth: '80%',
                      padding: '12px 16px',
                      borderRadius: 16,
                      background: msg.role === 'user' 
                        ? 'var(--primary)' 
                        : 'rgba(0, 0, 0, 0.05)',
                      color: msg.role === 'user' ? 'white' : 'var(--text)',
                      borderBottomRightRadius: msg.role === 'user' ? 4 : 16,
                      borderBottomLeftRadius: msg.role === 'user' ? 16 : 4,
                      fontSize: 14,
                      lineHeight: 1.5
                    }}
                  >
                    {msg.content}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1, color: 'var(--text-muted)' }}>
              Select a conversation to view details
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Conversations
