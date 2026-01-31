import { Link } from 'react-router-dom'

const pricingPlans = [
  {
    id: 'basic',
    name: 'Basic',
    price: '$25/mo',
    description: 'Great for getting live quickly.',
    features: ['Custom branding', 'Voice selection', 'FAQ management']
  },
  {
    id: 'standard',
    name: 'Standard',
    price: '$40/mo',
    description: 'Best for growing teams.',
    features: ['Everything in Basic', 'Document upload (RAG)', 'Hide branding'],
    highlight: true
  },
  {
    id: 'premium',
    name: 'Premium',
    price: '$60/mo',
    description: 'Advanced capabilities and insights.',
    features: ['Everything in Standard', 'Fine tuning', 'Advanced analytics']
  }
]

const featureCards = [
  {
    title: 'White-label experience',
    body: 'Your brand, your colors, your voice. Keep the experience consistent across every touchpoint.'
  },
  {
    title: 'Knowledge + RAG',
    body: 'Upload your documents and let the chatbot answer with accurate, grounded responses.'
  },
  {
    title: 'Embed in minutes',
    body: 'Copy the snippet once and drop it into any website to go live immediately.'
  },
  {
    title: 'Live testing',
    body: 'Use the Test Chat screen to validate behavior before publishing changes.'
  },
  {
    title: 'Usage insights',
    body: 'Track conversations, usage, and performance to keep quality high.'
  },
  {
    title: 'Dedicated support',
    body: 'Reach us anytime at support@mothership-ai.com for onboarding and troubleshooting.'
  }
]

const setupSteps = [
  {
    title: 'Choose a plan',
    body: 'Pick Basic, Standard, or Premium based on your needs.'
  },
  {
    title: 'Customize branding',
    body: 'Set colors, name, welcome message, and voice preferences.'
  },
  {
    title: 'Add knowledge',
    body: 'Upload docs or manage FAQs so the bot is ready to answer.'
  },
  {
    title: 'Embed and test',
    body: 'Paste the snippet into your site and run a test chat.'
  }
]

function Landing() {
  return (
    <div className="landing">
      <header className="landing-hero">
        <div className="landing-hero-content">
          <div className="landing-kicker">Snip by NextEleven</div>
          <h1 className="landing-title">Custom AI chatbots for your business</h1>
          <p className="landing-subtitle">
            Launch a fully branded chatbot in minutes. Customize the experience, add your knowledge,
            and embed on any website.
          </p>
          <div className="landing-cta">
            <Link className="btn btn-primary" to="/signup">Get Started</Link>
            <Link className="btn btn-secondary" to="/login">I have an API key</Link>
          </div>
          <div className="landing-subcards">
            <div className="landing-subcard">
              <h3>Fast setup</h3>
              <p>Go live in under 10 minutes.</p>
            </div>
            <div className="landing-subcard">
              <h3>Fully branded</h3>
              <p>Match your site and voice instantly.</p>
            </div>
            <div className="landing-subcard">
              <h3>Enterprise-ready</h3>
              <p>Analytics and advanced controls included.</p>
            </div>
          </div>
        </div>
        <div className="landing-hero-panel">
          <h2>Launch in 4 steps</h2>
          <div className="landing-step-list">
            {setupSteps.map((step) => (
              <div className="landing-step" key={step.title}>
                <div className="landing-step-title">{step.title}</div>
                <div className="landing-step-body">{step.body}</div>
              </div>
            ))}
          </div>
          <Link className="btn btn-primary landing-panel-cta" to="/signup">
            Start now
          </Link>
        </div>
      </header>

      <section className="landing-section">
        <div className="landing-section-header">
          <h2>Everything you need to launch</h2>
          <p>From customization to testing, the dashboard includes the full toolkit.</p>
        </div>
        <div className="landing-grid">
          {featureCards.map((card) => (
            <div className="landing-card" key={card.title}>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="landing-section">
        <div className="landing-section-header">
          <h2>Simple pricing</h2>
          <p>Pick the plan that fits your team today. Upgrade anytime.</p>
        </div>
        <div className="landing-grid landing-pricing">
          {pricingPlans.map((plan) => (
            <div
              key={plan.id}
              className={`landing-card landing-pricing-card ${plan.highlight ? 'is-highlighted' : ''}`}
            >
              {plan.highlight && <span className="landing-badge">Most popular</span>}
              <h3>{plan.name}</h3>
              <div className="landing-price">{plan.price}</div>
              <p className="landing-price-subtitle">{plan.description}</p>
              <ul>
                {plan.features.map((feature) => (
                  <li key={feature}>{feature}</li>
                ))}
              </ul>
              <Link className="btn btn-secondary" to={`/signup?tier=${plan.id}`}>
                Choose {plan.name}
              </Link>
            </div>
          ))}
        </div>
      </section>

      <section className="landing-section">
        <div className="landing-banner">
          <div>
            <h2>Ready to launch your chatbot?</h2>
            <p>Start now or reach out to support@mothership-ai.com for onboarding help.</p>
          </div>
          <Link className="btn btn-primary" to="/signup">Get Started</Link>
        </div>
      </section>
    </div>
  )
}

export default Landing
