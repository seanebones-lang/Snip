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
  position: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'center'
  autoOpen: boolean
  showBranding: boolean
  width?: number | null
  height?: number | null
  customCss?: string | null
  theme?: string | null
}

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  audio_url?: string // Backend-provided TTS audio URL (base64 data URL)
}

class SnipWidget {
  private clientId: string
  private apiUrl: string
  private config: WidgetConfig | null = null
  private container: HTMLElement | null = null
  private isOpen: boolean = false
  private messages: Message[] = []
  private isLoading: boolean = false
  private currentAudio: HTMLAudioElement | null = null // Track current audio for cleanup

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
      
      // Set up message watcher for TTS (like original implementation)
      this.setupTTSWatcher()
    } catch (error) {
      console.error('Snip Widget: Initialization failed', error)
    }
  }
  
  private lastTTSIndex = -1
  private isPlayingAudio: boolean = false // Prevent race conditions
  
  private setupTTSWatcher() {
    // Watch for new assistant messages and play TTS automatically
    const checkMessages = () => {
      // Don't start new audio if already playing
      if (this.isPlayingAudio) return
      
      if (this.messages.length > this.lastTTSIndex + 1) {
        // Find last assistant message we haven't played yet
        for (let i = this.messages.length - 1; i > this.lastTTSIndex; i--) {
          if (this.messages[i].role === 'assistant') {
            this.lastTTSIndex = i
            // Use audio_url if available, otherwise generate TTS
            if (this.messages[i].audio_url) {
              this.playAudioFromUrl(this.messages[i].audio_url, this.messages[i].content)
            } else {
              this.generateAndPlayAudio(this.messages[i].content)
            }
            break
          }
        }
      }
    }
    
    // Check for new messages periodically
    setInterval(checkMessages, 500)
  }

  private injectStyles() {
    if (!this.config) return
    
    const { colors } = this.config
    const width = this.config.width || 380
    const height = this.config.height || 550
    
    // Calculate position based on extended options
    const position = this.config.position || 'bottom-right'
    let positionCss = ''
    if (position === 'center') {
      positionCss = 'left: 50%; top: 50%; transform: translate(-50%, -50%);'
    } else if (position.includes('top')) {
      positionCss = position === 'top-right' ? 'right: 20px; top: 20px;' : 'left: 20px; top: 20px;'
    } else {
      positionCss = position === 'bottom-right' ? 'right: 20px; bottom: 20px;' : 'left: 20px; bottom: 20px;'
    }
    
    const style = document.createElement('style')
    style.textContent = `
      .snip-widget-container {
        --snip-primary: ${colors.primary};
        --snip-secondary: ${colors.secondary};
        --snip-bg: ${colors.background};
        --snip-text: ${colors.text};
        
        position: fixed;
        ${positionCss}
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
        width: ${width}px;
        height: ${height}px;
        background: var(--snip-bg);
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        flex-direction: column;
        overflow: hidden;
        position: absolute;
        ${position === 'center' ? 'top: 0; left: 0;' : position.includes('top') ? (position === 'top-right' ? 'top: 70px; right: 0;' : 'top: 70px; left: 0;') : (position === 'bottom-right' ? 'bottom: 70px; right: 0;' : 'bottom: 70px; left: 0;')}
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
          ${position === 'center' ? 'top: 50%; left: 50%; transform: translate(-50%, -50%);' : position.includes('top') ? (position === 'top-right' ? 'top: 70px; right: 0;' : 'top: 70px; left: 0;') : (position === 'bottom-right' ? 'bottom: 70px; right: 0;' : 'bottom: 70px; left: 0;')}
        }
      }
      ${this.config.customCss || ''}
    `
    document.head.appendChild(style)
    
    // Apply theme if specified
    if (this.config.theme && this.config.theme !== 'auto' && this.config.theme !== 'custom') {
      const themeStyle = document.createElement('style')
      if (this.config.theme === 'light') {
        themeStyle.textContent = `
          .snip-widget-container {
            --snip-bg: #ffffff;
            --snip-text: #111827;
          }
          .snip-message.assistant {
            background: rgba(0, 0, 0, 0.05);
            color: #111827;
          }
        `
      } else if (this.config.theme === 'dark') {
        themeStyle.textContent = `
          .snip-widget-container {
            --snip-bg: #111827;
            --snip-text: #F3F4F6;
          }
          .snip-message.assistant {
            background: rgba(255, 255, 255, 0.1);
            color: #F3F4F6;
          }
        `
      }
      if (themeStyle.textContent) {
        document.head.appendChild(themeStyle)
      }
    }
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

  private playAudioFromUrl(audioUrl: string, fallbackText?: string) {
    try {
      // Stop any currently playing audio to prevent overlap
      this.stopAudio()
      
      console.log('[TTS] Playing audio from backend URL (base64 data URL)')
      const audio = new Audio(audioUrl)
      this.currentAudio = audio
      this.isPlayingAudio = true
      
      // Accessibility: Announce audio playback start
      this.announceAudioState('playing')
      
      audio.addEventListener('ended', () => {
        console.log('[TTS] Audio playback finished')
        this.isPlayingAudio = false
        this.currentAudio = null
        this.announceAudioState('finished')
      })
      
      audio.addEventListener('error', (e) => {
        console.error('[TTS] Audio playback error:', e)
        this.isPlayingAudio = false
        this.currentAudio = null
        this.announceAudioState('error')
        
        // Error recovery: Fallback to text-to-speech if text available
        if (fallbackText) {
          console.log('[TTS] Falling back to browser TTS due to audio playback error')
          setTimeout(() => {
            this.fallbackBrowserTTS(fallbackText)
          }, 100)
        }
      })
      
      audio.addEventListener('loadstart', () => {
        console.log('[TTS] Audio loading started')
      })
      
      audio.addEventListener('canplay', () => {
        console.log('[TTS] Audio ready to play')
      })
      
      audio.play().catch(err => {
        console.error('[TTS] Failed to play audio:', err)
        this.isPlayingAudio = false
        this.currentAudio = null
        
        // Error recovery: Fallback to text-to-speech if text available
        if (fallbackText) {
          console.log('[TTS] Falling back to browser TTS due to play() error')
          this.fallbackBrowserTTS(fallbackText)
        }
      })
      
      console.log('[TTS] Playing audio from backend')
    } catch (err) {
      console.error('[TTS] Error playing audio from URL:', err)
      this.isPlayingAudio = false
      this.currentAudio = null
      
      // Error recovery: Fallback to text-to-speech
      if (fallbackText) {
        console.log('[TTS] Falling back to browser TTS due to exception')
        this.fallbackBrowserTTS(fallbackText)
      }
    }
  }
  
  private stopAudio() {
    // Stop HTML5 audio if playing
    if (this.currentAudio) {
      try {
        this.currentAudio.pause()
        this.currentAudio.currentTime = 0
        this.currentAudio = null
      } catch (e) {
        console.warn('[TTS] Error stopping audio:', e)
      }
    }
    
    // Stop browser TTS if speaking
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel()
      } catch (e) {
        console.warn('[TTS] Error stopping speech synthesis:', e)
      }
    }
    
    this.isPlayingAudio = false
  }
  
  private announceAudioState(state: 'playing' | 'finished' | 'error') {
    // Accessibility: Announce audio state for screen readers
    if (this.container) {
      const announcement = this.container.querySelector('.snip-audio-announcement') as HTMLElement
      if (announcement) {
        announcement.remove()
      }
      
      const ariaLive = document.createElement('div')
      ariaLive.className = 'snip-audio-announcement'
      ariaLive.setAttribute('role', 'status')
      ariaLive.setAttribute('aria-live', 'polite')
      ariaLive.setAttribute('aria-atomic', 'true')
      ariaLive.style.cssText = 'position: absolute; left: -10000px; width: 1px; height: 1px; overflow: hidden;'
      
      const messages: Record<string, string> = {
        playing: 'Audio response is playing',
        finished: 'Audio response finished',
        error: 'Audio playback failed, using text-to-speech'
      }
      
      ariaLive.textContent = messages[state] || ''
      this.container.appendChild(ariaLive)
      
      // Clean up after announcement
      setTimeout(() => {
        ariaLive.remove()
      }, 1000)
    }
  }

  private async textToSpeech(text: string, voiceId: string = 'female_british'): Promise<Blob | null> {
    // OLD METHOD REMOVED - This caused CORS issues
    // TTS should come from backend as audio_url (base64 data URL)
    // If audio_url is missing, fallback to browser TTS instead
    console.log('[TTS] External TTS API call removed - using backend audio_url or browser fallback')
    return null
  }

  private createAudioUrl(blob: Blob): string {
    return URL.createObjectURL(blob)
  }

  private revokeAudioUrl(url: string): void {
    URL.revokeObjectURL(url)
  }

  private async generateAndPlayAudio(text: string) {
    // TTS should come from backend as audio_url (base64 data URL)
    // If backend doesn't provide audio_url, use browser TTS fallback
    // No external API calls from browser (prevents CORS issues)
    console.log('[TTS] Using browser TTS fallback (backend should provide audio_url)')
    this.fallbackBrowserTTS(text)
  }

  private fallbackBrowserTTS(text: string) {
    if (!('speechSynthesis' in window)) {
      console.warn('[TTS] Browser speech synthesis not supported')
      return
    }
    
    try {
      // Stop any currently playing audio
      this.stopAudio()
      
      // Handle long text by splitting into chunks (browser TTS has limits)
      const maxLength = 200 // Conservative limit per chunk
      if (text.length > maxLength) {
        // Split by sentences for natural breaks
        const sentences = text.match(/[^.!?]+[.!?]+/g) || [text]
        let currentChunk = ''
        
        const speakChunk = (chunkIndex: number) => {
          if (chunkIndex >= sentences.length) return
          
          const chunk = sentences[chunkIndex].trim()
          if (!chunk) {
            speakChunk(chunkIndex + 1)
            return
          }
          
          currentChunk = chunk
          this.speakTextChunk(chunk, () => {
            speakChunk(chunkIndex + 1)
          })
        }
        
        speakChunk(0)
        return
      }
      
      this.speakTextChunk(text)
    } catch (err) {
      console.error('[TTS] Browser TTS failed:', err)
      this.isPlayingAudio = false
    }
  }
  
  private speakTextChunk(text: string, onEnd?: () => void) {
    if (!('speechSynthesis' in window)) return
    
    try {
      this.isPlayingAudio = true
      const utterance = new SpeechSynthesisUtterance(text)
      
      // Try to find a British English voice, otherwise use default
      const voices = window.speechSynthesis.getVoices()
      const britishVoice = voices.find(v => 
        v.lang.includes('en-GB') || 
        v.name.toLowerCase().includes('british') ||
        v.name.toLowerCase().includes('uk')
      )
      
      if (britishVoice) {
        utterance.voice = britishVoice
        console.log('[TTS] Using British voice:', britishVoice.name)
      } else {
        // Use first English voice available
        const englishVoice = voices.find(v => v.lang.startsWith('en'))
        if (englishVoice) {
          utterance.voice = englishVoice
          console.log('[TTS] Using English voice:', englishVoice.name)
        }
      }
      
      utterance.rate = 0.95 // Slightly slower for clarity
      utterance.pitch = 1.0
      utterance.volume = 1.0
      
      utterance.onstart = () => {
        console.log('[TTS] Browser speech started')
        this.announceAudioState('playing')
      }
      
      utterance.onend = () => {
        console.log('[TTS] Browser speech finished')
        this.isPlayingAudio = false
        this.announceAudioState('finished')
        if (onEnd) onEnd()
      }
      
      utterance.onerror = (e) => {
        console.error('[TTS] Browser speech error:', e)
        this.isPlayingAudio = false
        this.announceAudioState('error')
        if (onEnd) onEnd()
      }
      
      // Voices may not be loaded immediately
      if (voices.length === 0) {
        window.speechSynthesis.onvoiceschanged = () => {
          this.speakTextChunk(text, onEnd)
        }
        return
      }
      
      window.speechSynthesis.speak(utterance)
      console.log('[TTS] Browser TTS playing')
    } catch (err) {
      console.error('[TTS] Browser TTS chunk failed:', err)
      this.isPlayingAudio = false
      if (onEnd) onEnd()
    }
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
        timestamp: new Date(),
        audio_url: data.audio_url
      })
      
      // Use audio_url from backend if provided (already generated), otherwise generate TTS
      if (data.audio_url) {
        this.playAudioFromUrl(data.audio_url, data.response) // Pass text as fallback
      } else {
        // Fallback: generate TTS client-side if backend didn't provide audio
        this.generateAndPlayAudio(data.response)
      }
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
