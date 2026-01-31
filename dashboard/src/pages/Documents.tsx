import { useState, useEffect, useRef } from 'react'
import { Upload, FileText, Trash2, Clock, CheckCircle, XCircle, Loader } from 'lucide-react'

interface DocumentsProps {
  apiKey: string
}

interface Document {
  id: string
  filename: string
  file_type: string
  file_size: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  chunk_count: number
  created_at: string
  processed_at: string | null
  error_message: string | null
}

interface ClientInfo {
  tier: 'basic' | 'standard' | 'premium'
}

function Documents({ apiKey }: DocumentsProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [client, setClient] = useState<ClientInfo | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/documents', {
        headers: { 'X-API-Key': apiKey }
      })
      if (res.ok) {
        const data = await res.json()
        setDocuments(data.documents)
      }
    } catch (error) {
      console.error('Failed to fetch documents:', error)
    }
  }
  
  useEffect(() => {
    const init = async () => {
      try {
        const [clientRes] = await Promise.all([
          fetch('/api/clients/me', {
            headers: { 'X-API-Key': apiKey }
          })
        ])
        
        if (clientRes.ok) {
          setClient(await clientRes.json())
        }
        
        await fetchDocuments()
      } catch (error) {
        console.error('Failed to initialize:', error)
      } finally {
        setLoading(false)
      }
    }
    
    init()
  }, [apiKey])
  
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    
    setUploading(true)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const res = await fetch('/api/documents', {
        method: 'POST',
        headers: {
          'X-API-Key': apiKey
        },
        body: formData
      })
      
      if (res.ok) {
        await fetchDocuments()
      } else {
        const error = await res.json()
        alert(error.detail || 'Failed to upload document')
      }
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Failed to upload document')
    } finally {
      setUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }
  
  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return
    
    try {
      const res = await fetch(`/api/documents/${docId}`, {
        method: 'DELETE',
        headers: { 'X-API-Key': apiKey }
      })
      
      if (res.ok) {
        setDocuments(docs => docs.filter(d => d.id !== docId))
      }
    } catch (error) {
      console.error('Delete failed:', error)
    }
  }
  
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }
  
  const getStatusIcon = (status: Document['status']) => {
    switch (status) {
      case 'pending':
        return <Clock size={16} color="var(--warning)" />
      case 'processing':
        return <Loader size={16} color="var(--primary)" className="spin" />
      case 'completed':
        return <CheckCircle size={16} color="var(--success)" />
      case 'failed':
        return <XCircle size={16} color="var(--danger)" />
    }
  }
  
  if (loading) {
    return <div>Loading...</div>
  }
  
  const isStandardOrHigher = client?.tier !== 'basic'
  
  return (
    <div>
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
          Documents
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Upload documents to train your chatbot with custom knowledge.
        </p>
      </div>
      
      {!isStandardOrHigher && (
        <div className="alert alert-warning">
          <span>⚡</span>
          <div>
            <strong>Premium Feature</strong>
            <p style={{ margin: 0, marginTop: 4 }}>
              Document upload and RAG training is available on the Premium plan. 
              Upgrade to unlock this feature.
            </p>
          </div>
        </div>
      )}
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Your Documents</h2>
          <div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleUpload}
              accept=".pdf,.docx,.doc,.txt,.md,.markdown,.html,.htm,.csv,.xlsx,.xls"
              style={{ display: 'none' }}
              disabled={!isStandardOrHigher}
            />
            <button 
              className="btn btn-primary"
              onClick={() => fileInputRef.current?.click()}
              disabled={!isStandardOrHigher || uploading}
            >
              <Upload size={18} />
              {uploading ? 'Uploading...' : 'Upload Document'}
            </button>
          </div>
        </div>
        
        <p style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 24 }}>
          Supported formats: PDF, DOCX, TXT, MD, HTML, CSV, XLSX, XLS (max 500MB per file)
        </p>
        
        {documents.length === 0 ? (
          <div style={{ 
            textAlign: 'center', 
            padding: 48, 
            background: 'var(--bg-input)', 
            borderRadius: 12 
          }}>
            <FileText size={48} color="var(--text-muted)" style={{ marginBottom: 16 }} />
            <p style={{ color: 'var(--text-muted)' }}>
              {isStandardOrHigher 
                ? "No documents uploaded yet. Upload your first document to get started."
                : "Upgrade to Premium to upload documents."
              }
            </p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {documents.map(doc => (
              <div 
                key={doc.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                  padding: 16,
                  background: 'var(--bg-input)',
                  borderRadius: 8,
                }}
              >
                <FileText size={24} color="var(--primary)" />
                
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 500, marginBottom: 4 }}>{doc.filename}</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                    {formatFileSize(doc.file_size)} • {doc.chunk_count} chunks • 
                    Uploaded {new Date(doc.created_at).toLocaleDateString()}
                  </div>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    {getStatusIcon(doc.status)}
                    <span style={{ 
                      fontSize: 12, 
                      textTransform: 'capitalize',
                      color: 'var(--text-muted)'
                    }}>
                      {doc.status}
                    </span>
                  </div>
                  {doc.status === 'failed' && doc.error_message && (
                    <span style={{ fontSize: 11, color: 'var(--danger)', maxWidth: 280, textAlign: 'right' }} title={doc.error_message}>
                      {doc.error_message.length > 60 ? doc.error_message.slice(0, 60) + '…' : doc.error_message}
                    </span>
                  )}
                </div>
                
                <button
                  onClick={() => handleDelete(doc.id)}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 8,
                    color: 'var(--text-muted)',
                    transition: 'color 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.color = 'var(--danger)'}
                  onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-muted)'}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
      
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 16 }}>How RAG Training Works</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 24 }}>
          <div>
            <div style={{
              width: 48,
              height: 48,
              borderRadius: 12,
              background: 'rgba(99, 102, 241, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16
            }}>
              <span style={{ fontSize: 20 }}>1</span>
            </div>
            <h4 style={{ marginBottom: 8 }}>Upload</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
              Upload your documents - FAQs, product info, policies, manuals, etc.
            </p>
          </div>
          
          <div>
            <div style={{
              width: 48,
              height: 48,
              borderRadius: 12,
              background: 'rgba(236, 72, 153, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16
            }}>
              <span style={{ fontSize: 20 }}>2</span>
            </div>
            <h4 style={{ marginBottom: 8 }}>Process</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
              We split documents into chunks and create searchable embeddings.
            </p>
          </div>
          
          <div>
            <div style={{
              width: 48,
              height: 48,
              borderRadius: 12,
              background: 'rgba(34, 197, 94, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16
            }}>
              <span style={{ fontSize: 20 }}>3</span>
            </div>
            <h4 style={{ marginBottom: 8 }}>Answer</h4>
            <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
              When users ask questions, relevant content is retrieved to generate accurate answers.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Documents
