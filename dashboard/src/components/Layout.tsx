import { NavLink } from 'react-router-dom'
import { Home, Palette, Code, FileText, BarChart3, LogOut, MessageSquare, HelpCircle, MessageCircle } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
  apiKey: string
  onLogout: () => void
}

function Layout({ children, onLogout }: LayoutProps) {
  return (
    <div className="dashboard-layout">
      <aside className="sidebar">
        <div className="logo">Snip</div>
        
        <nav className="nav">
          <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <Home size={20} />
            Dashboard
          </NavLink>
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
          <NavLink to="/conversations" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <MessageCircle size={20} />
            Conversations
          </NavLink>
          <NavLink to="/faqs" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <HelpCircle size={20} />
            FAQs
          </NavLink>
          <NavLink to="/documents" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <FileText size={20} />
            Documents
          </NavLink>
          <NavLink to="/usage" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <BarChart3 size={20} />
            Usage
          </NavLink>
        </nav>
        
        <button onClick={onLogout} className="nav-link" style={{ marginTop: 'auto' }}>
          <LogOut size={20} />
          Logout
        </button>
      </aside>
      
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

export default Layout
