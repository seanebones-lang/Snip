import { useState, useEffect } from 'react'
import { Plus, Edit2, Trash2, Save, X } from 'lucide-react'
import { apiUrl } from '../api'

interface FAQsProps {
  apiKey: string
}

interface FAQ {
  id: string
  question: string
  answer: string
  category: string | null
  priority: number
  created_at: string
  updated_at: string
}

function FAQs({ apiKey }: FAQsProps) {
  const [faqs, setFaqs] = useState<FAQ[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({ question: '', answer: '', category: '', priority: 0 })
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchFAQs()
  }, [apiKey])

  const fetchFAQs = async () => {
    try {
      const res = await fetch(apiUrl('/api/faqs'), {
        headers: { 'X-API-Key': apiKey }
      })
      if (res.ok) {
        const data = await res.json()
        setFaqs(data.faqs || [])
      }
    } catch (error) {
      console.error('Failed to fetch FAQs:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!formData.question.trim() || !formData.answer.trim()) return

    try {
      const res = await fetch(apiUrl('/api/faqs'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify({
          question: formData.question,
          answer: formData.answer,
          category: formData.category || null,
          priority: formData.priority
        })
      })

      if (res.ok) {
        await fetchFAQs()
        setFormData({ question: '', answer: '', category: '', priority: 0 })
        setShowForm(false)
      } else {
        setError('Failed to create FAQ')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  const handleUpdate = async (id: string, data: Partial<FAQ>) => {
    try {
      const res = await fetch(apiUrl(`/api/faqs/${id}`), {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': apiKey
        },
        body: JSON.stringify(data)
      })

      if (res.ok) {
        await fetchFAQs()
        setEditingId(null)
      } else {
        setError('Failed to update FAQ')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this FAQ?')) return

    try {
      const res = await fetch(apiUrl(`/api/faqs/${id}`), {
        method: 'DELETE',
        headers: { 'X-API-Key': apiKey }
      })

      if (res.ok) {
        await fetchFAQs()
      } else {
        setError('Failed to delete FAQ')
      }
    } catch (error) {
      setError('Network error')
    }
  }

  if (loading) {
    return <div>Loading FAQs...</div>
  }

  return (
    <div>
      <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700, marginBottom: 8 }}>
            FAQ Management
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>
            Create and manage frequently asked questions for your chatbot.
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn btn-primary"
          style={{ display: 'flex', alignItems: 'center', gap: 8 }}
        >
          <Plus size={18} />
          Add FAQ
        </button>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: 24 }}>
          {error}
        </div>
      )}

      {showForm && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h2 className="card-title" style={{ marginBottom: 16 }}>Create New FAQ</h2>
          
          <div className="form-group" style={{ marginBottom: 16 }}>
            <label className="form-label">Question</label>
            <input
              type="text"
              className="form-input"
              value={formData.question}
              onChange={(e) => setFormData({ ...formData, question: e.target.value })}
              placeholder="What is your return policy?"
            />
          </div>

          <div className="form-group" style={{ marginBottom: 16 }}>
            <label className="form-label">Answer</label>
            <textarea
              className="form-input"
              value={formData.answer}
              onChange={(e) => setFormData({ ...formData, answer: e.target.value })}
              placeholder="We accept returns within 30 days..."
              rows={4}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div className="form-group">
              <label className="form-label">Category (optional)</label>
              <input
                type="text"
                className="form-input"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="Shipping, Returns, etc."
              />
            </div>

            <div className="form-group">
              <label className="form-label">Priority (higher = shown first)</label>
              <input
                type="number"
                className="form-input"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                min={0}
              />
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <button onClick={handleCreate} className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Save size={18} />
              Create FAQ
            </button>
            <button onClick={() => setShowForm(false)} className="btn btn-secondary">
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="card">
        <h2 className="card-title" style={{ marginBottom: 24 }}>
          Your FAQs ({faqs.length})
        </h2>

        {faqs.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 48, color: 'var(--text-muted)' }}>
            <p>No FAQs yet. Create your first FAQ to help your chatbot answer common questions.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {faqs.map((faq) => (
              <div
                key={faq.id}
                style={{
                  padding: 16,
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  background: 'var(--bg-card)'
                }}
              >
                {editingId === faq.id ? (
                  <FAQEditForm
                    faq={faq}
                    onSave={(data) => handleUpdate(faq.id, data)}
                    onCancel={() => setEditingId(null)}
                  />
                ) : (
                  <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, marginBottom: 8, color: 'var(--text)' }}>
                          Q: {faq.question}
                        </div>
                        <div style={{ color: 'var(--text-muted)', lineHeight: 1.6 }}>
                          A: {faq.answer}
                        </div>
                        {(faq.category || faq.priority > 0) && (
                          <div style={{ marginTop: 12, display: 'flex', gap: 12, fontSize: 12, color: 'var(--text-muted)' }}>
                            {faq.category && <span>Category: {faq.category}</span>}
                            {faq.priority > 0 && <span>Priority: {faq.priority}</span>}
                          </div>
                        )}
                      </div>
                      <div style={{ display: 'flex', gap: 8 }}>
                        <button
                          onClick={() => setEditingId(faq.id)}
                          className="btn btn-secondary"
                          style={{ padding: '8px 12px' }}
                        >
                          <Edit2 size={16} />
                        </button>
                        <button
                          onClick={() => handleDelete(faq.id)}
                          className="btn btn-secondary"
                          style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.2)', borderColor: '#ef4444', color: '#ef4444' }}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function FAQEditForm({ faq, onSave, onCancel }: { faq: FAQ, onSave: (data: Partial<FAQ>) => void, onCancel: () => void }) {
  const [data, setData] = useState({ question: faq.question, answer: faq.answer, category: faq.category || '', priority: faq.priority })

  return (
    <div>
      <div className="form-group" style={{ marginBottom: 12 }}>
        <label className="form-label">Question</label>
        <input
          type="text"
          className="form-input"
          value={data.question}
          onChange={(e) => setData({ ...data, question: e.target.value })}
        />
      </div>
      <div className="form-group" style={{ marginBottom: 12 }}>
        <label className="form-label">Answer</label>
        <textarea
          className="form-input"
          value={data.answer}
          onChange={(e) => setData({ ...data, answer: e.target.value })}
          rows={3}
        />
      </div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
        <div className="form-group" style={{ flex: 1 }}>
          <label className="form-label">Category</label>
          <input
            type="text"
            className="form-input"
            value={data.category}
            onChange={(e) => setData({ ...data, category: e.target.value })}
          />
        </div>
        <div className="form-group" style={{ width: 120 }}>
          <label className="form-label">Priority</label>
          <input
            type="number"
            className="form-input"
            value={data.priority}
            onChange={(e) => setData({ ...data, priority: parseInt(e.target.value) || 0 })}
          />
        </div>
      </div>
      <div style={{ display: 'flex', gap: 8 }}>
        <button onClick={() => onSave(data)} className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Save size={16} />
          Save
        </button>
        <button onClick={onCancel} className="btn btn-secondary">
          <X size={16} />
        </button>
      </div>
    </div>
  )
}

export default FAQs
