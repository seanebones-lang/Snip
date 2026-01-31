import { NavLink } from 'react-router-dom'
import {
  Home,
  Palette,
  Code,
  FileText,
  BarChart3,
  LogOut,
  MessageSquare,
  MessageCircle,
  BookOpen,
  LifeBuoy
} from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
  apiKey: string
  onLogout: () => void
}

function Layout({ children, onLogout }: LayoutProps) {
  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="logo">Snip by NextEleven</div>
        <div className="sidebar-subtitle">Customer Dashboard</div>

        <nav className="nav">
          <div className="nav-section">
            <div className="nav-title">Overview</div>
            <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Home size={20} />
              Dashboard
            </NavLink>
            <NavLink to="/usage" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <BarChart3 size={20} />
              Usage
            </NavLink>
            <NavLink to="/conversations" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <MessageCircle size={20} />
              Conversations
            </NavLink>
          </div>

          <div className="nav-section">
            <div className="nav-title">Setup</div>
            <NavLink to="/branding" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Palette size={20} />
              Branding
            </NavLink>
            <NavLink to="/snippet" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <Code size={20} />
              Embed Snippet
            </NavLink>
            <NavLink to="/test" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <MessageSquare size={20} />
              Test Chat
            </NavLink>
          </div>

          <div className="nav-section">
            <div className="nav-title">Knowledge</div>
            <NavLink to="/documents" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <FileText size={20} />
              Documents
            </NavLink>
            <NavLink to="/faqs" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <BookOpen size={20} />
              FAQs
            </NavLink>
          </div>

          <div className="nav-section">
            <div className="nav-title">Support</div>
            <NavLink to="/help" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <LifeBuoy size={20} />
              Help Center
            </NavLink>
          </div>
        </nav>

        <div className="sidebar-footer">
          <a className="support-link" href="mailto:support@mothership-ai.com">
            support@mothership-ai.com
          </a>
          <button onClick={onLogout} className="nav-link nav-link-button">
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>
      
      <main className="main-content">
        <div className="content-inner">{children}</div>
      </main>
    </div>
  )
}

export default Layout
