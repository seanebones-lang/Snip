/**
 * Snip Widget - Embeddable Chatbot
 * 
 * Usage:
 * <script src="https://snip.yourdomain.com/widget.js" data-client-id="xxx" async></script>
 */

interface WidgetConfig {
  botName: string
  logoUrl: string | null
  colors: {
    primary: string
    secondary: string
    background: string
    text: string
  }
  welcomeMessage: string
  placeholderText: string
  position: 'bottom-right' | 'bottom-left'
  autoOpen: boolean
  showBranding: boolean
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

class SnipWidget {
  private clientId: string
  private apiUrl: string
  private config: WidgetConfig | null = null
  private container: HTMLElement | null = null
  private isOpen: boolean = false
  private messages: Message[] = []
  private isLoading: boolean = false

  constructor(clientId: string, apiUrl: string) {
    this.clientId = clientId
    this.apiUrl = apiUrl
    this.init()
  }

  private async init() {
    try {
      // Fetch config from API
      const response = await fetch(`${this.apiUrl}/api/widget/config/${this.clientId}`, {
        headers: {
          'Origin': window.location.origin
        }
      })
      
      if (!response.ok) {
        console.error('Snip Widget: Failed to load config')
        return
      }
      
      this.config = await response.json()
      this.injectStyles()
      this.render()
      
      // Add welcome message
      this.messages.push({
        role: 'assistant',
        content: this.config!.welcomeMessage,
        timestamp: new Date()
      })
      
      if (this.config!.autoOpen) {
        this.open()
      }
    } catch (error) {
      console.error('Snip Widget: Initialization failed', error)
    }
  }

  private injectStyles() {
    if (!this.config) return
    
    const { colors } = this.config
    
    const style = document.createElement('style')
    style.textContent = `
      .snip-widget-container {
        --snip-primary: ${colors.primary};
        --snip-secondary: ${colors.secondary};
        --snip-bg: ${colors.background};
        --snip-text: ${colors.text};
        
        position: fixed;
        ${this.config.position === 'bottom-right' ? 'right: 20px;' : 'left: 20px;'}
        bottom: 20px;
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
      }
      
      .snip-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--snip-primary) 0%, var(--snip-secondary) 100%);
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, box-shadow 0.2s;
      }
      
      .snip-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
      }
      
      .snip-button svg {
        width: 28px;
        height: 28px;
        fill: white;
      }
      
      .snip-chat {
        display: none;
        width: 380px;
        height: 550px;
        background: var(--snip-bg);
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        flex-direction: column;
        overflow: hidden;
        position: absolute;
        bottom: 70px;
        ${this.config.position === 'bottom-right' ? 'right: 0;' : 'left: 0;'}
      }
      
      .snip-chat.open {
        display: flex;
        animation: snip-slide-up 0.3s ease;
      }
      
      @keyframes snip-slide-up {
        from {
          opacity: 0;
          transform: translateY(20px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
      
      .snip-header {
        background: linear-gradient(135deg, var(--snip-primary) 0%, var(--snip-secondary) 100%);
        padding: 16px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      
      .snip-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      
      .snip-logo {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
      }
      
      .snip-logo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      
      .snip-logo-placeholder {
        font-size: 18px;
        font-weight: bold;
        color: var(--snip-primary);
      }
      
      .snip-title {
        color: white;
        font-size: 16px;
        font-weight: 600;
        margin: 0;
      }
      
      .snip-close {
        background: none;
        border: none;
        cursor: pointer;
        padding: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .snip-close svg {
        width: 24px;
        height: 24px;
        fill: white;
      }
      
      .snip-messages {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      
      .snip-message {
        max-width: 85%;
        padding: 12px 16px;
        border-radius: 16px;
        font-size: 14px;
        line-height: 1.5;
        animation: snip-fade-in 0.2s ease;
      }
      
      @keyframes snip-fade-in {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      .snip-message.user {
        align-self: flex-end;
        background: var(--snip-primary);
        color: white;
        border-bottom-right-radius: 4px;
      }
      
      .snip-message.assistant {
        align-self: flex-start;
        background: rgba(255, 255, 255, 0.1);
        color: var(--snip-text);
        border-bottom-left-radius: 4px;
      }
      
      .snip-typing {
        display: flex;
        gap: 4px;
        padding: 12px 16px;
      }
      
      .snip-typing span {
        width: 8px;
        height: 8px;
        background: var(--snip-primary);
        border-radius: 50%;
        animation: snip-bounce 1.4s infinite ease-in-out;
      }
      
      .snip-typing span:nth-child(1) { animation-delay: -0.32s; }
      .snip-typing span:nth-child(2) { animation-delay: -0.16s; }
      
      @keyframes snip-bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
      }
      
      .snip-input-container {
        padding: 16px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        gap: 12px;
      }
      
      .snip-input {
        flex: 1;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 24px;
        padding: 12px 20px;
        color: var(--snip-text);
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s;
      }
      
      .snip-input::placeholder {
        color: rgba(255, 255, 255, 0.5);
      }
      
      .snip-input:focus {
        border-color: var(--snip-primary);
      }
      
      .snip-send {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--snip-primary);
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s, transform 0.1s;
      }
      
      .snip-send:hover {
        background: var(--snip-secondary);
      }
      
      .snip-send:active {
        transform: scale(0.95);
      }
      
      .snip-send:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      .snip-send svg {
        width: 20px;
        height: 20px;
        fill: white;
      }
      
      .snip-branding {
        text-align: center;
        padding: 8px;
        font-size: 11px;
        color: rgba(255, 255, 255, 0.4);
      }
      
      .snip-branding a {
        color: rgba(255, 255, 255, 0.6);
        text-decoration: none;
      }
      
      .snip-branding a:hover {
        text-decoration: underline;
      }
      
      @media (max-width: 480px) {
        .snip-chat {
          width: calc(100vw - 40px);
          height: calc(100vh - 100px);
          bottom: 70px;
          ${this.config.position === 'bottom-right' ? 'right: 0;' : 'left: 0;'}
        }
      }
    `
    document.head.appendChild(style)
  }

  private render() {
    if (!this.config) return
    
    this.container = document.createElement('div')
    this.container.className = 'snip-widget-container'
    this.container.innerHTML = this.getHTML()
    document.body.appendChild(this.container)
    
    this.bindEvents()
    this.renderMessages()
  }

  private getHTML(): string {
    if (!this.config) return ''
    
    const logoHTML = this.config.logoUrl 
      ? `<img src="${this.config.logoUrl}" alt="${this.config.botName}">`
      : `<span class="snip-logo-placeholder">${this.config.botName.charAt(0)}</span>`
    
    return `
      <button class="snip-button" aria-label="Open chat">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
        </svg>
      </button>
      
      <div class="snip-chat">
        <div class="snip-header">
          <div class="snip-header-left">
            <div class="snip-logo">${logoHTML}</div>
            <h3 class="snip-title">${this.config.botName}</h3>
          </div>
          <button class="snip-close" aria-label="Close chat">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
            </svg>
          </button>
        </div>
        
        <div class="snip-messages" id="snip-messages"></div>
        
        <div class="snip-input-container">
          <input 
            type="text" 
            class="snip-input" 
            placeholder="${this.config.placeholderText}"
            id="snip-input"
          >
          <button class="snip-send" id="snip-send" aria-label="Send message">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
            </svg>
          </button>
        </div>
        
        ${this.config.showBranding ? `
          <div class="snip-branding">
            Powered by <a href="https://snip.dev" target="_blank" rel="noopener">Snip</a>
          </div>
        ` : ''}
      </div>
    `
  }

  private bindEvents() {
    if (!this.container) return
    
    const button = this.container.querySelector('.snip-button') as HTMLButtonElement
    const closeBtn = this.container.querySelector('.snip-close') as HTMLButtonElement
    const input = this.container.querySelector('#snip-input') as HTMLInputElement
    const sendBtn = this.container.querySelector('#snip-send') as HTMLButtonElement
    
    button.addEventListener('click', () => this.toggle())
    closeBtn.addEventListener('click', () => this.close())
    
    sendBtn.addEventListener('click', () => this.sendMessage())
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage()
    })
  }

  private toggle() {
    this.isOpen ? this.close() : this.open()
  }

  private open() {
    if (!this.container) return
    this.isOpen = true
    const chat = this.container.querySelector('.snip-chat') as HTMLElement
    const button = this.container.querySelector('.snip-button') as HTMLElement
    chat.classList.add('open')
    button.style.display = 'none'
  }

  private close() {
    if (!this.container) return
    this.isOpen = false
    const chat = this.container.querySelector('.snip-chat') as HTMLElement
    const button = this.container.querySelector('.snip-button') as HTMLElement
    chat.classList.remove('open')
    button.style.display = 'flex'
  }

  private renderMessages() {
    if (!this.container) return
    
    const messagesContainer = this.container.querySelector('#snip-messages') as HTMLElement
    messagesContainer.innerHTML = ''
    
    this.messages.forEach(msg => {
      const div = document.createElement('div')
      div.className = `snip-message ${msg.role}`
      div.textContent = msg.content
      messagesContainer.appendChild(div)
    })
    
    if (this.isLoading) {
      const typing = document.createElement('div')
      typing.className = 'snip-message assistant snip-typing'
      typing.innerHTML = '<span></span><span></span><span></span>'
      messagesContainer.appendChild(typing)
    }
    
    messagesContainer.scrollTop = messagesContainer.scrollHeight
  }

  private async sendMessage() {
    if (!this.container || this.isLoading) return
    
    const input = this.container.querySelector('#snip-input') as HTMLInputElement
    const message = input.value.trim()
    
    if (!message) return
    
    // Add user message
    this.messages.push({
      role: 'user',
      content: message,
      timestamp: new Date()
    })
    
    input.value = ''
    this.isLoading = true
    this.renderMessages()
    
    try {
      const response = await fetch(`${this.apiUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          client_id: this.clientId,
          message: message
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to get response')
      }
      
      const data = await response.json()
      
      this.messages.push({
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      })
    } catch (error) {
      this.messages.push({
        role: 'assistant',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again.",
        timestamp: new Date()
      })
    } finally {
      this.isLoading = false
      this.renderMessages()
    }
  }
}

// Auto-initialize from script tag
(function() {
  const scripts = document.querySelectorAll('script[data-client-id]')
  const currentScript = scripts[scripts.length - 1] as HTMLScriptElement
  
  if (currentScript) {
    const clientId = currentScript.getAttribute('data-client-id')
    // Determine API URL - use data-api-url or default to script origin
    const scriptSrc = currentScript.src
    const apiUrl = currentScript.getAttribute('data-api-url') || 
      scriptSrc.substring(0, scriptSrc.lastIndexOf('/'))
    
    if (clientId) {
      // Wait for DOM to be ready
      if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
          new SnipWidget(clientId, apiUrl)
        })
      } else {
        new SnipWidget(clientId, apiUrl)
      }
    }
  }
})()

// Export for manual initialization
;(window as any).SnipWidget = SnipWidget
