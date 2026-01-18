import { useState, useEffect, useRef } from 'react'
import { Send, Volume2, VolumeX } from 'lucide-react'

interface TestChatProps {
  apiKey: string
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  audio_url?: string
}

interface Config {
  bot_name: string
  welcome_message: string
  placeholder_text: string
  client_id: string
}

function TestChat({ apiKey }: TestChatProps) {
  const [config, setConfig] = useState<Config | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [audioEnabled, setAudioEnabled] = useState(true)
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const configLoading = useState(true)[0]

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const [configRes, clientRes] = await Promise.all([
          fetch('/api/config', {
            headers: { 'X-API-Key': apiKey }
          }),
          fetch('/api/clients/me', {
            headers: { 'X-API-Key': apiKey }
          })
        ])
        
        if (configRes.ok && clientRes.ok) {
          const configData = await configRes.json()
          const clientData = await clientRes.json()
          
          setConfig({
            bot_name: configData.bot_name,
            welcome_message: configData.welcome_message,
            placeholder_text: configData.placeholder_text,
            client_id: clientData.id
          })
          
          // Add welcome message
          setMessages([{
            role: 'assistant',
            content: configData.welcome_message,
            timestamp: new Date()
          }])
        }
      } catch (error) {
        console.error('Failed to fetch config:', error)
        setError('Failed to load configuration')
      } finally {
        // configLoading would be set here if we had the state setter
      }
    }
    
    fetchConfig()
  }, [apiKey])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.currentTime = 0
      setCurrentAudio(null)
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }

  const playAudio = (audioUrl?: string, fallbackText?: string) => {
    if (!audioEnabled) return
    
    stopAudio()
    
    if (audioUrl) {
      try {
        const audio = new Audio(audioUrl)
        setCurrentAudio(audio)
        
        audio.addEventListener('ended', () => {
          setCurrentAudio(null)
        })
        
        audio.addEventListener('error', () => {
          if (fallbackText) {
            fallbackBrowserTTS(fallbackText)
          }
        })
        
        audio.play().catch(() => {
          if (fallbackText) {
            fallbackBrowserTTS(fallbackText)
          }
        })
      } catch (err) {
        if (fallbackText) {
          fallbackBrowserTTS(fallbackText)
        }
      }
    } else if (fallbackText) {
      fallbackBrowserTTS(fallbackText)
    }
  }

  const fallbackBrowserTTS = (text: string) => {
    if (!('speechSynthesis' in window)) return
    
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    
    const voices = window.speechSynthesis.getVoices()
    const englishVoice = voices.find(v => v.lang.startsWith('en'))
    if (englishVoice) {
      utterance.voice = englishVoice
    }
    
    utterance.rate = 0.95
    window.speechSynthesis.speak(utterance)
  }

  const sendMessage = async () => {
    if (!input.trim() || loading || !config) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          client_id: config.client_id,
          message: userMessage.content
        })
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        audio_url: data.audio_url
      }

      setMessages(prev => [...prev, assistantMessage])
      
      // Play audio if enabled
      if (data.audio_url) {
        playAudio(data.audio_url, data.response)
      } else {
        playAudio(undefined, data.response)
      }
    } catch (error) {
      setError('Failed to send message. Please try again.')
      console.error('Chat error:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    return () => {
      stopAudio()
    }
  }, [])

  if (!config) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div>Loading chat configuration...</div>
      </div>
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            Test Chat
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Test your chatbot before deploying. This chat interface matches what visitors will see.
          </p>
        </div>
        <button
          onClick={() => {
            setAudioEnabled(!audioEnabled)
            if (!audioEnabled) {
              stopAudio()
            }
          }}
          className="btn btn-secondary"
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}
        >
          {audioEnabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
          {audioEnabled ? 'Audio On' : 'Audio Off'}
        </button>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: 24 }}>
          {error}
        </div>
      )}

      <div className="card" style={{ height: 'calc(100vh - 300px)', minHeight: 600, display: 'flex', flexDirection: 'column' }}>
        <div style={{
          padding: 16,
          borderBottom: '1px solid var(--border)',
          display: 'flex',
          alignItems: 'center',
          gap: 12
        }}>
          <div style={{
            width: 36,
            height: 36,
            borderRadius: '50%',
            background: 'var(--primary)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontWeight: 'bold'
          }}>
            {config.bot_name.charAt(0)}
          </div>
          <span style={{ fontWeight: 600 }}>{config.bot_name}</span>
        </div>

        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: 16,
          display: 'flex',
          flexDirection: 'column',
          gap: 12
        }}>
          {messages.map((msg, idx) => (
            <div
              key={idx}
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
          
          {loading && (
            <div style={{
              alignSelf: 'flex-start',
              padding: '12px 16px',
              borderRadius: 16,
              background: 'rgba(0, 0, 0, 0.05)',
              display: 'flex',
              gap: 4
            }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary)', animation: 'bounce 1.4s infinite' }}></span>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary)', animation: 'bounce 1.4s infinite 0.2s' }}></span>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary)', animation: 'bounce 1.4s infinite 0.4s' }}></span>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div style={{
          padding: 16,
          borderTop: '1px solid var(--border)',
          display: 'flex',
          gap: 12
        }}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
            placeholder={config.placeholder_text}
            className="form-input"
            style={{ flex: 1 }}
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            className="btn btn-primary"
            disabled={loading || !input.trim()}
            style={{ display: 'flex', alignItems: 'center', gap: 8 }}
          >
            <Send size={18} />
            Send
          </button>
        </div>
      </div>

      <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
          40% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  )
}

export default TestChat
