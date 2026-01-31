import { useState, useEffect } from 'react'
import { Check, AlertCircle } from 'lucide-react'

interface SetupChecklistProps {
  apiKey: string
}

function SetupChecklist({ apiKey }: SetupChecklistProps) {
  const [checklist, setChecklist] = useState({
    brandingDone: false,
    snippetCopied: false,
    widgetDeployed: false,
    testDone: false,
    documentsUploaded: false
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Optional: fetch checklist progress from backend
    // For now, use local state - could be enhanced with API
    setChecklist({
      brandingDone: true, // Assume done if config saved
      snippetCopied: false,
      widgetDeployed: false,
      testDone: false,
      documentsUploaded: false
    })
    setLoading(false)
  }, [apiKey])

  const totalSteps = Object.keys(checklist).length
  const completedSteps = Object.values(checklist).filter(Boolean).length

  return (
    <div className="card" style={{ marginBottom: 24 }}>
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
          <Check size={24} color="var(--primary)" />
        </div>
        <div>
          <h3 style={{ margin: 0, fontSize: 18 }}>Setup Checklist</h3>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: 14 }}>
            {completedSteps}/{totalSteps} steps complete
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 20, height: 20, borderRadius: 50, background: checklist.brandingDone ? 'var(--success)' : 'var(--bg-input)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {checklist.brandingDone && <Check size={14} color="white" />}
          </div>
          <div>
            <div style={{ fontWeight: 500 }}>Customize branding</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Set bot name, colors, logo</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 20, height: 20, borderRadius: 50, background: checklist.snippetCopied ? 'var(--success)' : 'var(--bg-input)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {checklist.snippetCopied && <Check size={14} color="white" />}
          </div>
          <div>
            <div style={{ fontWeight: 500 }}>Copy embed code</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>From the Embed Snippet page</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 20, height: 20, borderRadius: 50, background: checklist.widgetDeployed ? 'var(--success)' : 'var(--bg-input)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {checklist.widgetDeployed && <Check size={14} color="white" />}
          </div>
          <div>
            <div style={{ fontWeight: 500 }}>Add widget to site</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Paste code before `</body>` tag</div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 20, height: 20, borderRadius: 50, background: checklist.testDone ? 'var(--success)' : 'var(--bg-input)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {checklist.testDone && <Check size={14} color="white" />}
          </div>
          <div>
            <div style={{ fontWeight: 500 }}>Test your bot</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Send a test message in Test Chat</div>
          </div>
        </div>

        {checklist.documentsUploaded !== undefined && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 20, height: 20, borderRadius: 50, background: checklist.documentsUploaded ? 'var(--success)' : 'var(--bg-input)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {checklist.documentsUploaded && <Check size={14} color="white" />}
            </div>
            <div>
              <div style={{ fontWeight: 500 }}>Upload documents</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Train your bot with your content</div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SetupChecklist