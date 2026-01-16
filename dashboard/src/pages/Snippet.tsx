import { useState, useEffect } from 'react'
import { Copy, Check, ExternalLink } from 'lucide-react'

interface SnippetProps {
  apiKey: string
}

interface SnippetData {
  html: string
  script_url: string
  client_id: string
}

function Snippet({ apiKey }: SnippetProps) {
  const [snippet, setSnippet] = useState<SnippetData | null>(null)
  const [loading, setLoading] = useState(true)
  const [copied, setCopied] = useState(false)
  
  useEffect(() => {
    const fetchSnippet = async () => {
      try {
        const res = await fetch('/api/embed-snippet', {
          headers: { 'X-API-Key': apiKey }
        })
        if (res.ok) {
          setSnippet(await res.json())
        }
      } catch (error) {
        console.error('Failed to fetch snippet:', error)
      } finally {
        setLoading(false)
      }
    }
    
    fetchSnippet()
  }, [apiKey])
  
  const handleCopy = () => {
    if (!snippet) return
    navigator.clipboard.writeText(snippet.html)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  
  if (loading) {
    return <div>Loading...</div>
  }
  
  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
          Embed Snippet
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Copy this code and paste it into your website's HTML, just before the closing &lt;/body&gt; tag.
        </p>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Your Embed Code</h2>
          <button 
            className={`btn ${copied ? 'btn-primary' : 'btn-secondary'}`}
            onClick={handleCopy}
          >
            {copied ? <Check size={18} /> : <Copy size={18} />}
            {copied ? 'Copied!' : 'Copy Code'}
          </button>
        </div>
        
        <div className="code-block">
          <pre>{snippet?.html || 'Loading...'}</pre>
        </div>
      </div>
      
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 16 }}>Installation Instructions</h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          <div>
            <h3 style={{ fontSize: 16, marginBottom: 8, color: 'var(--primary)' }}>1. Copy the code</h3>
            <p style={{ color: 'var(--text-muted)' }}>
              Click the "Copy Code" button above to copy the embed snippet to your clipboard.
            </p>
          </div>
          
          <div>
            <h3 style={{ fontSize: 16, marginBottom: 8, color: 'var(--primary)' }}>2. Paste in your website</h3>
            <p style={{ color: 'var(--text-muted)' }}>
              Open your website's HTML file and paste the code just before the closing <code style={{ background: 'var(--bg-input)', padding: '2px 6px', borderRadius: 4 }}>&lt;/body&gt;</code> tag.
            </p>
          </div>
          
          <div>
            <h3 style={{ fontSize: 16, marginBottom: 8, color: 'var(--primary)' }}>3. Deploy your changes</h3>
            <p style={{ color: 'var(--text-muted)' }}>
              Save your file and deploy your website. The chat widget will appear in the bottom corner!
            </p>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 16 }}>Platform-Specific Instructions</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16 }}>
          <div style={{ background: 'var(--bg-input)', padding: 20, borderRadius: 12 }}>
            <h4 style={{ marginBottom: 8 }}>WordPress</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 12 }}>
              Go to Appearance → Theme File Editor → footer.php and paste the code before &lt;/body&gt;
            </p>
            <a href="#" className="btn btn-secondary" style={{ fontSize: 12, padding: '8px 12px' }}>
              View Guide <ExternalLink size={14} />
            </a>
          </div>
          
          <div style={{ background: 'var(--bg-input)', padding: 20, borderRadius: 12 }}>
            <h4 style={{ marginBottom: 8 }}>Shopify</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 12 }}>
              Go to Online Store → Themes → Edit Code → theme.liquid and paste before &lt;/body&gt;
            </p>
            <a href="#" className="btn btn-secondary" style={{ fontSize: 12, padding: '8px 12px' }}>
              View Guide <ExternalLink size={14} />
            </a>
          </div>
          
          <div style={{ background: 'var(--bg-input)', padding: 20, borderRadius: 12 }}>
            <h4 style={{ marginBottom: 8 }}>Squarespace</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 12 }}>
              Go to Settings → Advanced → Code Injection → Footer and paste the code
            </p>
            <a href="#" className="btn btn-secondary" style={{ fontSize: 12, padding: '8px 12px' }}>
              View Guide <ExternalLink size={14} />
            </a>
          </div>
          
          <div style={{ background: 'var(--bg-input)', padding: 20, borderRadius: 12 }}>
            <h4 style={{ marginBottom: 8 }}>Wix</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 12 }}>
              Add an "Embed HTML" element and paste the code, or use Wix Dev Mode
            </p>
            <a href="#" className="btn btn-secondary" style={{ fontSize: 12, padding: '8px 12px' }}>
              View Guide <ExternalLink size={14} />
            </a>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 16 }}>Technical Details</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16 }}>
          <div>
            <p style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 4 }}>Client ID</p>
            <code style={{ 
              background: 'var(--bg-input)', 
              padding: '8px 12px', 
              borderRadius: 6,
              display: 'block',
              fontSize: 13
            }}>
              {snippet?.client_id}
            </code>
          </div>
          
          <div>
            <p style={{ color: 'var(--text-muted)', fontSize: 12, marginBottom: 4 }}>Script URL</p>
            <code style={{ 
              background: 'var(--bg-input)', 
              padding: '8px 12px', 
              borderRadius: 6,
              display: 'block',
              fontSize: 13,
              wordBreak: 'break-all'
            }}>
              {snippet?.script_url}
            </code>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Snippet
