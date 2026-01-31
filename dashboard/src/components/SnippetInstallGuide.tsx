import { useState } from 'react'
import { Copy } from 'lucide-react'

interface SnippetInstallGuideProps {
  snippetCode: string
}

const platforms = [
  {
    name: 'Generic HTML',
    instructions: 'Paste the code just before the closing `</body>` tag in your HTML file.',
    example: `<!DOCTYPE html>
<html>
<head>
  <title>My Site</title>
</head>
<body>
  <h1>Welcome</h1>
  <!-- Your content here -->
  
  <!-- PASTE SNIPPET HERE -->
  <script src="https://widget-sigma-sage.vercel.app/widget.js" 
          data-client-id="YOUR_CLIENT_ID"
          data-api-url="https://snip.mothership-ai.com" 
          async></script>
</body>
</html>`
  },
  {
    name: 'WordPress',
    instructions: 'Appearance → Theme File Editor → footer.php → before `</body>`',
    example: `<footer>
  <!-- WordPress footer content -->
</footer>

<!-- PASTE SNIPPET HERE -->
<script src="https://widget-sigma-sage.vercel.app/widget.js" 
        data-client-id="YOUR_CLIENT_ID"
        data-api-url="https://snip.mothership-ai.com" 
        async></script>
</body>
</html>`
  },
  {
    name: 'Shopify',
    instructions: 'Online Store → Themes → Edit Code → theme.liquid → before `</body>`',
    example: `<!-- Shopify theme content -->
</main>

<!-- PASTE SNIPPET HERE -->
<script src="https://widget-sigma-sage.vercel.app/widget.js" 
        data-client-id="YOUR_CLIENT_ID"
        data-api-url="https://snip.mothership-ai.com" 
        async></script>

</body>
</html>`
  },
  {
    name: 'Squarespace',
    instructions: 'Settings → Advanced → Code Injection → Footer',
    example: `<!-- Squarespace content -->

<!-- PASTE SNIPPET HERE -->
<script src="https://widget-sigma-sage.vercel.app/widget.js" 
        data-client-id="YOUR_CLIENT_ID"
        data-api-url="https://snip.mothership-ai.com" 
        async></script>`
  },
  {
    name: 'Wix',
    instructions: 'Add HTML iframe element → paste code inside',
    example: `<!-- Wix HTML element -->
<script src="https://widget-sigma-sage.vercel.app/widget.js" 
        data-client-id="YOUR_CLIENT_ID"
        data-api-url="https://snip.mothership-ai.com" 
        async></script>`
  }
]

function SnippetInstallGuide({ snippetCode }: SnippetInstallGuideProps) {
  const [activePlatform, setActivePlatform] = useState(0)

  const handleCopy = () => {
    navigator.clipboard.writeText(snippetCode)
  }

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 24 }}>
        {platforms.map((platform, index) => (
          <button
            key={platform.name}
            className={`platform-tab ${activePlatform === index ? 'active' : ''}`}
            onClick={() => setActivePlatform(index)}
          >
            {platform.name}
          </button>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 380px', gap: 32 }}>
        <div>
          <div style={{ background: '#f8f9fa', padding: 24, borderRadius: 12, marginBottom: 24 }}>
            <h3 style={{ marginBottom: 12 }}>📋 Instructions</h3>
            <p>{platforms[activePlatform].instructions}</p>
          </div>

          <div style={{ background: '#1e1e1e', padding: 20, borderRadius: 12, position: 'relative' }}>
            <div style={{ position: 'absolute', top: 8, right: 12, fontSize: 12, color: '#888' }}>
              Mock HTML
            </div>
            <pre style={{ margin: 0, fontSize: 13, lineHeight: 1.5, color: '#e6e6e6' }}>
{platforms[activePlatform].example.split('\n').map((line, i) => (
  line.includes('<!-- PASTE SNIPPET HERE -->') ? (
    <span key={i} style={{ background: '#3b82f6', color: 'white', padding: '2px 4px', borderRadius: 4, fontWeight: 'bold' }}>
      {line}
    </span>
  ) : (
    <span key={i}>{line}</span>
  )
))}
            </pre>
          </div>
        </div>

        <div>
          <div style={{ position: 'sticky', top: 32 }}>
            <h3 style={{ marginBottom: 16 }}>📝 Your Snippet Code</h3>
            <button 
              className="btn btn-primary" 
              onClick={handleCopy}
              style={{ width: '100%', marginBottom: 16 }}
            >
              <Copy size={18} />
              Copy Code
            </button>
            <div style={{ background: '#1e1e1e', padding: 16, borderRadius: 8, maxHeight: 400, overflow: 'auto' }}>
              <pre style={{ margin: 0, fontSize: 12, lineHeight: 1.4, color: '#e6e6e6' }}>
{snippetCode}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SnippetInstallGuide