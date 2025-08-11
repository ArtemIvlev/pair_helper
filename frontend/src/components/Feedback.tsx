import React, { useState, useEffect } from 'react'
import { getApiUrl } from '../config'

interface FeedbackData {
  id: number
  user_id: number
  feedback_type: 'bug' | 'feature' | 'general' | 'other'
  subject: string
  message: string
  status: 'new' | 'in_progress' | 'resolved' | 'closed'
  admin_response?: string
  created_at: string
  updated_at: string
  user: {
    first_name: string
    last_name?: string
  }
}

const Feedback: React.FC = () => {
  const [feedbackType, setFeedbackType] = useState<'bug' | 'feature' | 'general' | 'other'>('general')
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [userFeedback, setUserFeedback] = useState<FeedbackData[]>([])
  const [loadingFeedback, setLoadingFeedback] = useState(false)

  const feedbackTypes = [
    { code: 'bug', text: '🐛 Ошибка', description: 'Что-то не работает' },
    { code: 'feature', text: '💡 Предложение', description: 'Хочу новую функцию' },
    { code: 'general', text: '💬 Общее', description: 'Общий вопрос или комментарий' },
    { code: 'other', text: '📝 Другое', description: 'Что-то еще' },
  ]

  const statusLabels = {
    'new': '🆕 Новое',
    'in_progress': '⚡ В работе',
    'resolved': '✅ Решено',
    'closed': '🔒 Закрыто'
  }

  const loadUserFeedback = async () => {
    setLoadingFeedback(true)
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) return

      const response = await fetch(getApiUrl('/v1/feedback/'), {
        headers: {
          'X-Telegram-Init-Data': initData
        }
      })

      if (response.ok) {
        const feedback = await response.json()
        setUserFeedback(feedback)
      }
    } catch (err) {
      console.error('Ошибка загрузки обратной связи:', err)
    } finally {
      setLoadingFeedback(false)
    }
  }

  useEffect(() => {
    loadUserFeedback()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!subject.trim() || !message.trim()) return

    setLoading(true)
    setError('')

    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) {
        setError('Ошибка аутентификации')
        return
      }

      const response = await fetch(getApiUrl('/v1/feedback/'), {
        method: 'POST',
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          feedback_type: feedbackType,
          subject: subject.trim(),
          message: message.trim()
        })
      })

      if (response.ok) {
        setSubmitted(true)
        setSubject('')
        setMessage('')
        // Перезагружаем список обращений
        await loadUserFeedback()
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Ошибка отправки обратной связи')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="main-content">
      <div className="container">
        <div className="header">
          <h1>Обратная связь</h1>
          <p>Расскажите нам о проблемах или предложениях</p>
        </div>

        {!submitted ? (
          <div className="card card-elevated fade-in">
            {error && (
              <div style={{ 
                color: 'var(--tg-theme-destructive-text-color)', 
                fontSize: '14px', 
                textAlign: 'center', 
                padding: '12px',
                marginBottom: '16px',
                background: 'var(--tg-theme-secondary-bg-color)',
                borderRadius: '8px'
              }}>
                {error}
              </div>
            )}
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Тип обращения:</label>
                <div className="feedback-type-grid">
                  {feedbackTypes.map((type) => (
                    <div
                      key={type.code}
                      className={`feedback-type-item ${feedbackType === type.code ? 'selected' : ''}`}
                      onClick={() => setFeedbackType(type.code as any)}
                    >
                      <div className="feedback-type-text">{type.text}</div>
                      <div className="feedback-type-description">{type.description}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="subject">Тема:</label>
                <input
                  id="subject"
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Кратко опишите проблему или предложение..."
                  maxLength={200}
                />
              </div>

              <div className="form-group">
                <label htmlFor="message">Сообщение:</label>
                <textarea
                  id="message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Подробно опишите вашу проблему, предложение или вопрос..."
                  rows={6}
                />
              </div>

              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={!subject.trim() || !message.trim() || loading}
              >
                {loading ? 'Отправка...' : 'Отправить'}
              </button>
            </form>
          </div>
        ) : (
          <div className="card card-elevated fade-in">
            <div className="success">
              <h3>✅ Обращение отправлено!</h3>
              <p>Мы рассмотрим ваше сообщение и ответим в ближайшее время.</p>
              <button 
                className="btn btn-secondary"
                onClick={() => setSubmitted(false)}
              >
                Отправить еще
              </button>
            </div>
          </div>
        )}

        {/* История обращений */}
        <div className="card card-elevated fade-in" style={{ marginTop: '20px' }}>
          <h3>Мои обращения</h3>
          {loadingFeedback ? (
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <div className="loading-spinner"></div>
              <p>Загрузка...</p>
            </div>
          ) : userFeedback.length > 0 ? (
            <div className="feedback-list">
              {userFeedback.map((feedback) => (
                <div key={feedback.id} className="feedback-entry">
                  <div className="feedback-entry-header">
                    <div className="feedback-entry-info">
                      <div className="feedback-entry-subject">{feedback.subject}</div>
                      <div className="feedback-entry-meta">
                        <span className="feedback-type-badge">
                          {feedbackTypes.find(t => t.code === feedback.feedback_type)?.text}
                        </span>
                        <span className="feedback-status-badge">
                          {statusLabels[feedback.status]}
                        </span>
                        <span className="feedback-date">{formatDate(feedback.created_at)}</span>
                      </div>
                    </div>
                  </div>
                  <div className="feedback-entry-message">{feedback.message}</div>
                  {feedback.admin_response && (
                    <div className="feedback-admin-response">
                      <div className="feedback-admin-response-header">Ответ администрации:</div>
                      <div className="feedback-admin-response-text">{feedback.admin_response}</div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-secondary)' }}>
              <p>У вас пока нет обращений</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Feedback
