import { useState, useEffect } from 'react'
import { Save } from 'lucide-react'

interface BrandingProps {
  apiKey: string
}

interface Config {
  bot_name: string
  logo_url: string | null
  primary_color: string
  secondary_color: string
  background_color: string
  text_color: string
  welcome_message: string
  placeholder_text: string
  system_prompt: string | null
  position: string
  auto_open: boolean
  show_branding: boolean
  allowed_domains: string[]
  ai_provider?: string | null
  ai_model?: string | null
  ai_api_key_set: boolean
  tts_voice?: string | null
  widget_width?: number | null
  widget_height?: number | null
  custom_css?: string | null
  theme?: string | null
}

function Branding({ apiKey }: BrandingProps) {
  const [config, setConfig] = useState<Config | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ttsVoice, setTtsVoice] = useState('Ara')
  
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await fetch('/api/config', {
          headers: { 'X-API-Key': apiKey }
        })
        if (res.ok) {
          const data = await res.json()
          setConfig(data)
          // Initialize form fields from config
          if (data.tts_voice) setTtsVoice(data.tts_voice)
          else setTtsVoice('Ara') // Default voice
          setError(null)
        } else {
          const errorData = await res.json().catch(() => ({}))
          setError(errorData.detail || `Failed to load config (${res.status})`)
          console.error('Failed to fetch config:', res.status, errorData)
        }
      } catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Network error'
        setError(errorMsg)
        console.error('Failed to fetch config:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchConfig()
  }, [apiKey])
  
  const handleSave = async () => {
    if (!config) return
    
    setSaving(true)
    try {
      const res = await fetch('/api/config', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify(config)
      })
      
      if (res.ok) {
        setSaved(true)
        setTimeout(() => setSaved(false), 3000)
      }
    } catch (error) {
      console.error('Failed to save config:', error)
    } finally {
      setSaving(false)
    }
  }
  
  const updateConfig = (field: keyof Config, value: any) => {
    if (!config) return
    setConfig({ ...config, [field]: value })
  }
  
  if (loading) {
    return (
      <div>
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            Branding
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Loading branding configuration...
          </p>
        </div>
        <div className="card">
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
            Loading...
          </div>
        </div>
      </div>
    )
  }
  
  if (!config && error) {
    return (
      <div>
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            Branding
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Customize how your chatbot looks and feels.
          </p>
        </div>
        <div className="alert alert-warning">
          <strong>Error loading configuration:</strong> {error}
          <br />
          <span style={{ fontSize: 12 }}>The backend may still be deploying. Please try again in a moment.</span>
        </div>
      </div>
    )
  }

  if (!config) {
    return (
      <div>
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            Branding
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Failed to load configuration
          </p>
        </div>
      </div>
    )
  }
  
  return (
    <div>
      <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            Branding
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Customize how your chatbot looks and feels.
          </p>
        </div>
        <button 
          className="btn btn-primary" 
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Changes'}
          <Save size={18} />
        </button>
      </div>
      
      {saved && (
        <div className="alert alert-success">
          Changes saved successfully!
        </div>
      )}
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 32 }}>
        <div>
          <div className="card">
            <h2 className="card-title">Basic Info</h2>
            
            <div className="form-group">
              <label className="form-label">Bot Name</label>
              <input
                type="text"
                className="form-input"
                value={config.bot_name}
                onChange={(e) => updateConfig('bot_name', e.target.value)}
                placeholder="My Assistant"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Logo URL</label>
              <input
                type="text"
                className="form-input"
                value={config.logo_url || ''}
                onChange={(e) => updateConfig('logo_url', e.target.value || null)}
                placeholder="https://example.com/logo.png"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Welcome Message</label>
              <textarea
                className="form-input"
                value={config.welcome_message}
                onChange={(e) => updateConfig('welcome_message', e.target.value)}
                placeholder="Hello! How can I help you today?"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Input Placeholder</label>
              <input
                type="text"
                className="form-input"
                value={config.placeholder_text}
                onChange={(e) => updateConfig('placeholder_text', e.target.value)}
                placeholder="Type your message..."
              />
            </div>
          </div>
          
          <div className="card">
            <h2 className="card-title">Colors</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Primary Color</label>
                <div className="color-picker-group">
                  <input
                    type="color"
                    className="color-picker"
                    value={config.primary_color}
                    onChange={(e) => updateConfig('primary_color', e.target.value)}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={config.primary_color}
                    onChange={(e) => updateConfig('primary_color', e.target.value)}
                    style={{ flex: 1 }}
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label className="form-label">Secondary Color</label>
                <div className="color-picker-group">
                  <input
                    type="color"
                    className="color-picker"
                    value={config.secondary_color}
                    onChange={(e) => updateConfig('secondary_color', e.target.value)}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={config.secondary_color}
                    onChange={(e) => updateConfig('secondary_color', e.target.value)}
                    style={{ flex: 1 }}
                  />
                </div>
              </div>
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Background Color</label>
                <div className="color-picker-group">
                  <input
                    type="color"
                    className="color-picker"
                    value={config.background_color}
                    onChange={(e) => updateConfig('background_color', e.target.value)}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={config.background_color}
                    onChange={(e) => updateConfig('background_color', e.target.value)}
                    style={{ flex: 1 }}
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label className="form-label">Text Color</label>
                <div className="color-picker-group">
                  <input
                    type="color"
                    className="color-picker"
                    value={config.text_color}
                    onChange={(e) => updateConfig('text_color', e.target.value)}
                  />
                  <input
                    type="text"
                    className="form-input"
                    value={config.text_color}
                    onChange={(e) => updateConfig('text_color', e.target.value)}
                    style={{ flex: 1 }}
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div className="card">
            <h2 className="card-title">AI Behavior</h2>
            
            <div className="form-group">
              <label className="form-label">Custom System Prompt</label>
              <textarea
                className="form-input"
                value={config.system_prompt || ''}
                onChange={(e) => updateConfig('system_prompt', e.target.value || null)}
                placeholder="Add custom instructions for your AI assistant..."
                style={{ minHeight: 150 }}
              />
              <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 8 }}>
                This text will be added to the AI's instructions. Use it to define your bot's personality, knowledge boundaries, and response style.
              </p>
            </div>
          </div>

          <div className="card">
            <h2 className="card-title">Voice Settings</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 24 }}>
              Choose the voice for your chatbot responses. The voice speaks all responses automatically.
            </p>
            
            <div className="form-group" style={{ marginBottom: 20 }}>
              <label className="form-label">Voice for Text-to-Speech</label>
              <select
                className="form-input"
                value={ttsVoice}
                onChange={(e) => setTtsVoice(e.target.value)}
              >
                <option value="Ara">Ara (Female, Natural)</option>
                <option value="Leo">Leo (Male, Natural)</option>
                <option value="Rex">Rex (Male, Deep)</option>
                <option value="Sal">Sal (Male, Friendly)</option>
                <option value="Eve">Eve (Female, Clear)</option>
              </select>
              <p style={{ color: 'var(--text-muted)', fontSize: 12, marginTop: 8 }}>
                Select the voice that will speak all chatbot responses. Default: Ara
              </p>
            </div>
            
            {(ttsVoice && ttsVoice !== (config?.tts_voice || 'Ara')) && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={async () => {
                  try {
                    const updateData: any = { tts_voice: ttsVoice }
                    
                    const res = await fetch('/api/config', {
                      method: 'PATCH',
                      headers: {
                        'Content-Type': 'application/json',
                        'X-API-Key': apiKey
                      },
                      body: JSON.stringify(updateData)
                    })
                    if (res.ok) {
                      const updated = await res.json()
                      setConfig(updated)
                      setSaved(true)
                      setTimeout(() => setSaved(false), 3000)
                    } else {
                      const errorData = await res.json().catch(() => ({}))
                      setError(errorData.detail || 'Failed to save voice settings')
                    }
                  } catch (error) {
                    console.error('Failed to save voice config:', error)
                    setError('Network error. Please try again.')
                  }
                }}
                style={{ marginTop: 8 }}
              >
                Save Voice Settings
              </button>
            )}
          </div>
          
          <div className="card">
            <h2 className="card-title">Widget Settings</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Position</label>
                <select
                  className="form-input"
                  value={config.position}
                  onChange={(e) => updateConfig('position', e.target.value)}
                >
                  <option value="bottom-right">Bottom Right</option>
                  <option value="bottom-left">Bottom Left</option>
                  <option value="top-right">Top Right</option>
                  <option value="top-left">Top Left</option>
                  <option value="center">Center</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">Auto Open</label>
                <select
                  className="form-input"
                  value={config.auto_open ? 'yes' : 'no'}
                  onChange={(e) => updateConfig('auto_open', e.target.value === 'yes')}
                >
                  <option value="no">No</option>
                  <option value="yes">Yes</option>
                </select>
              </div>
            </div>
            
            <div className="form-group">
              <label className="form-label">Show "Powered by Snip" Branding</label>
              <select
                className="form-input"
                value={config.show_branding ? 'yes' : 'no'}
                onChange={(e) => updateConfig('show_branding', e.target.value === 'yes')}
              >
                <option value="yes">Yes</option>
                <option value="no">No (Premium only)</option>
              </select>
            </div>
          </div>
          
          <div className="card">
            <h2 className="card-title">Advanced Customization</h2>
            
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Widget Width (px)</label>
                <input
                  type="number"
                  className="form-input"
                  value={config.widget_width || 380}
                  onChange={(e) => updateConfig('widget_width', e.target.value ? parseInt(e.target.value) : null)}
                  min={200}
                  max={800}
                  placeholder="380"
                />
                <small style={{ color: 'var(--text-muted)', fontSize: 12 }}>Default: 380px (200-800px)</small>
              </div>
              
              <div className="form-group">
                <label className="form-label">Widget Height (px)</label>
                <input
                  type="number"
                  className="form-input"
                  value={config.widget_height || 550}
                  onChange={(e) => updateConfig('widget_height', e.target.value ? parseInt(e.target.value) : null)}
                  min={300}
                  max={1000}
                  placeholder="550"
                />
                <small style={{ color: 'var(--text-muted)', fontSize: 12 }}>Default: 550px (300-1000px)</small>
              </div>
            </div>
            
            <div className="form-group">
              <label className="form-label">Theme</label>
              <select
                className="form-input"
                value={config.theme || 'auto'}
                onChange={(e) => updateConfig('theme', e.target.value)}
              >
                <option value="auto">Auto (System Preference)</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="custom">Custom (Use Custom CSS)</option>
              </select>
            </div>
            
            <div className="form-group">
              <label className="form-label">Custom CSS</label>
              <textarea
                className="form-input"
                value={config.custom_css || ''}
                onChange={(e) => updateConfig('custom_css', e.target.value || null)}
                placeholder=".snip-chat { border-radius: 20px; }"
                rows={6}
                style={{ fontFamily: 'monospace', fontSize: 13 }}
              />
              <small style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                Advanced: Add custom CSS to further customize the widget appearance. Use selectors like .snip-chat, .snip-button, etc.
              </small>
            </div>
          </div>
        </div>
        
        <div>
          <div style={{ position: 'sticky', top: 32 }}>
            <h3 style={{ marginBottom: 16, color: 'var(--text-muted)', fontSize: 14 }}>
              Live Preview
            </h3>
            <div className="preview-container">
              <div style={{
                width: '100%',
                height: '100%',
                background: config.background_color,
                borderRadius: 12,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden'
              }}>
                <div style={{
                  padding: '16px 20px',
                  background: `linear-gradient(135deg, ${config.primary_color} 0%, ${config.secondary_color} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 12
                }}>
                  <div style={{
                    width: 36,
                    height: 36,
                    borderRadius: '50%',
                    background: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 'bold',
                    color: config.primary_color
                  }}>
                    {config.bot_name.charAt(0)}
                  </div>
                  <span style={{ color: 'white', fontWeight: 600 }}>{config.bot_name}</span>
                </div>
                
                <div style={{ flex: 1, padding: 16 }}>
                  <div style={{
                    background: 'rgba(255,255,255,0.1)',
                    color: config.text_color,
                    padding: '12px 16px',
                    borderRadius: 16,
                    borderBottomLeftRadius: 4,
                    maxWidth: '85%',
                    fontSize: 14
                  }}>
                    {config.welcome_message}
                  </div>
                </div>
                
                <div style={{ padding: 16, borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                  <div style={{
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: 24,
                    padding: '12px 20px',
                    color: 'rgba(255,255,255,0.5)',
                    fontSize: 14
                  }}>
                    {config.placeholder_text}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Branding
