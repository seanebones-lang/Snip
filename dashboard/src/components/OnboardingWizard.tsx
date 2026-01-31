import { useState, useEffect } from 'react'
import { ChevronLeft, ChevronRight, Check, X } from 'lucide-react'

interface OnboardingWizardProps {
  apiKey: string
  onComplete: () => void
  isOpen: boolean
  onClose: () => void
}

const steps = [
  {
    id: 1,
    title: 'Welcome to Snip by NextEleven',
    description: 'Get your chatbot live in 4 quick steps.',
    content: (
      <>
        <h3 style={{ marginBottom: 16 }}>What's next?</h3>
        <ol style={{ margin: 0 }}>
          <li>Customize your branding</li>
          <li>Get your embed code</li>
          <li>Add to your website</li>
          <li>Test it</li>
        </ol>
      </>
    )
  },
  {
    id: 2,
    title: 'Customize Branding',
    description: 'Make it look like your brand.',
    content: (
      <>
        <p>Go to the <strong>Branding</strong> page to customize colors, logo, and messages.</p>
        <a href="/branding" style={{ display: 'inline-block', marginTop: 16 }}>Customize Branding →</a>
      </>
    )
  },
  {
    id: 3,
    title: 'Get Your Embed Code',
    description: 'One line of code to add the widget.',
    content: (
      <>
        <p>Go to the <strong>Embed Snippet</strong> page to copy your code.</p>
        <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Paste it before the `</body>` tag on your site.</p>
        <a href="/snippet" style={{ display: 'inline-block', marginTop: 16 }}>Get Embed Code →</a>
      </>
    )
  },
  {
    id: 4,
    title: 'Test Your Bot',
    description: 'Send a test message to verify it works.',
    content: (
      <>
        <p>Go to the <strong>Test Chat</strong> page to try your bot.</p>
        <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>Once you see responses, you're ready to go live!</p>
        <a href="/test" style={{ display: 'inline-block', marginTop: 16 }}>Test Chat →</a>
      </>
    )
  }
]

function OnboardingWizard({ apiKey, onComplete, isOpen, onClose }: OnboardingWizardProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [hasCompletedOnboarding, setHasCompletedOnboarding] = useState(false)

  const completeOnboarding = async () => {
    try {
      const response = await fetch('/api/config', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify({ has_completed_onboarding: true })
      })
      if (response.ok) {
        setHasCompletedOnboarding(true)
        onComplete()
      }
    } catch (error) {
      console.error('Failed to complete onboarding:', error)
    }
  }

  if (!isOpen) return null

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.5)',
      zIndex: 10000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: 'white',
        borderRadius: 16,
        maxWidth: 600,
        maxHeight: '90vh',
        overflow: 'hidden',
        boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)'
      }}>
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #e5e7eb' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--primary)' }}>
              {currentStep}/{steps.length}
            </div>
            <h2>{steps[currentStep - 1].title}</h2>
          </div>
          <p style={{ margin: 0, color: 'var(--text-muted)' }}>
            {steps[currentStep - 1].description}
          </p>
        </div>

        <div style={{ padding: '32px', maxHeight: '400px', overflowY: 'auto' }}>
          {steps[currentStep - 1].content}
        </div>

        <div style={{ padding: '24px 32px', borderTop: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button 
            onClick={onClose}
            style={{ padding: '8px 16px', border: '1px solid #d1d5db', borderRadius: 8, background: 'white' }}
          >
            <X size={16} />
            Skip
          </button>
          
          <div style={{ display: 'flex', gap: 12 }}>
            {currentStep > 1 && (
              <button 
                onClick={() => setCurrentStep(currentStep - 1)}
                style={{ padding: '12px 24px', border: '1px solid #d1d5db', borderRadius: 8, background: 'white' }}
              >
                <ChevronLeft size={16} />
                Back
              </button>
            )}
            
            {currentStep === steps.length ? (
              <button 
                onClick={completeOnboarding}
                style={{ padding: '12px 24px', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: 8, fontWeight: 500 }}
              >
                Complete Setup <Check size={16} />
              </button>
            ) : (
              <button 
                onClick={() => setCurrentStep(currentStep + 1)}
                style={{ padding: '12px 24px', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: 8, fontWeight: 500 }}
              >
                Next <ChevronRight size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default OnboardingWizard