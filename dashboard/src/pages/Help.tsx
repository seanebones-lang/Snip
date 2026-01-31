import { useState } from 'react'
import { AlertCircle, Mail } from 'lucide-react'

function Help() {
  const [activeTab, setActiveTab] = useState('troubleshooting')

  const troubleshooting = [
    {
      title: 'Widget not appearing',
      content: `1. Verify code is placed before </body> tag
2. Check browser console for errors (F12 → Console)
3. Verify Client ID in data-client-id matches your embed code
4. Clear browser cache and hard refresh (Ctrl/Cmd+Shift+R)
5. Ensure website is published (not draft/preview mode)
6. Test on incognito/private browsing`
    },
    {
      title: 'Chat not responding',
      content: `1. Check browser console (F12) for API errors
2. Verify data-api-url points to https://snip-production.up.railway.app
3. Test your Client ID with Test Chat page
4. Check if your site blocks external scripts
5. Verify Stripe subscription is active (Dashboard → Usage)`
    },
    {
      title: 'Wrong colors/branding',
      content: `1. Save changes in Branding page
2. Clear browser cache (Ctrl/Cmd+Shift+R)
3. Verify hex colors are valid (#RRGGBB format)
4. Check logo URL loads directly in browser
5. Widget may cache config for 5 minutes`
    },
    {
      title: 'Mobile display issues',
      content: `1. Widget is responsive by default (380px width)
2. Customize width/height in advanced settings (200-800px)
3. Test on actual mobile device (not just dev tools)
4. Check CSS conflicts with position: fixed`
    }
  ]

  const faqs = [
    {
      question: 'How do I get my API key?',
      answer: 'Your API key was emailed to you after signup. Check spam folder if missing. Contact support@mothership-ai.com if you need it resent.'
    },
    {
      question: 'Where do I paste the embed code?',
      answer: 'Paste the script tag just before the closing </body> tag in your HTML. See the visual guide on the Snippet page.'
    },
    {
      question: 'How long does document processing take?',
      answer: 'Small files (<10MB): seconds. Large files (100MB+): 15-60 minutes. Check status in Documents page.'
    },
    {
      question: 'What\'s the difference between tiers?',
      answer: 'Basic ($25): Core features. Standard ($40): +Documents (RAG). Premium ($60): +Advanced analytics.'
    },
    {
      question: 'Can I upgrade my plan?',
      answer: 'Yes! Go to Dashboard → Upgrade buttons or contact support@mothership-ai.com.'
    }
  ]

  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>Help & Support</h1>
        <p style={{ color: 'var(--text-muted)' }}>Troubleshooting and FAQs for Snip by NextEleven.</p>
      </div>

      <div className="card" style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 1, borderBottom: '2px solid var(--bg-input)' }}>
          <button 
            className={`tab-button ${activeTab === 'troubleshooting' ? 'active' : ''}`}
            onClick={() => setActiveTab('troubleshooting')}
          >
            Troubleshooting
          </button>
          <button 
            className={`tab-button ${activeTab === 'faq' ? 'active' : ''}`}
            onClick={() => setActiveTab('faq')}
          >
            FAQs
          </button>
        </div>

        {activeTab === 'troubleshooting' && (
          <div style={{ padding: 24 }}>
            {troubleshooting.map((item, index) => (
              <div key={index} style={{ marginBottom: 24, paddingBottom: 24, borderBottom: '1px solid #e5e7eb' }}>
                <h3 style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                  <AlertCircle size={20} color="#f59e0b" />
                  {item.title}
                </h3>
                <div style={{ lineHeight: 1.6, color: 'var(--text-muted)' }}>
                  {item.content.split('\n').map((line, i) => (
                    line ? <div key={i}>{line}</div> : <br key={i} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'faq' && (
          <div style={{ padding: 24 }}>
            {faqs.map((faq, index) => (
              <div key={index} style={{ marginBottom: 24, paddingBottom: 24, borderBottom: '1px solid #e5e7eb' }}>
                <h3 style={{ marginBottom: 8, fontSize: 16 }}>{faq.question}</h3>
                <p style={{ margin: 0, color: 'var(--text-muted)' }}>{faq.answer}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="card">
        <div style={{ textAlign: 'center', padding: 32 }}>
          <Mail size={48} color="var(--primary)" style={{ marginBottom: 16 }} />
          <h2 style={{ marginBottom: 16 }}>Still stuck?</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>
            Our support team is here to help you get set up.
          </p>
          <a href="mailto:support@mothership-ai.com" className="btn btn-primary" style={{ fontSize: 16 }}>
            Email Support
          </a>
        </div>
      </div>
    </div>
  )
}

export default Help