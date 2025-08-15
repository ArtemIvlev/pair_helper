import React, { useState, useEffect } from 'react'
import { getApiUrl } from '../config'

interface Question {
  id: number
  number: number
  text: string
  category: string
  partner_answered: boolean
  user_answered: boolean
}



const DailyQuestion: React.FC = () => {
  const [question, setQuestion] = useState<Question | null>(null)
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')
  const [recent, setRecent] = useState<{ id: number; number: number; text: string; category: string; partner_answered: boolean; user_answered: boolean }[]>([])
  const [selected, setSelected] = useState<null | {
    question: Question
    user_answer: { id: number; question_id: number; answer_text: string; created_at: string } | null
    partner_answer: { id: number; question_id: number; answer_text: string; created_at: string } | null
    partner_name: string
  }>(null)
  const [notifying, setNotifying] = useState(false)
  const [notifySuccess, setNotifySuccess] = useState<string>('')
  const [notifyCooldown, setNotifyCooldown] = useState<number | null>(null)

  const fetchCurrentQuestion = async () => {
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      console.log('DailyQuestion: initData =', initData)
      console.log('DailyQuestion: Telegram WebApp =', (window as any).Telegram?.WebApp)
      if (!initData) {
        setError('Ошибка аутентификации - нет initData')
        setLoading(false)
        return
      }

      const response = await fetch(getApiUrl('/v1/questions/current'), {
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        }
      })

      console.log('DailyQuestion: response status =', response.status)
      console.log('DailyQuestion: response ok =', response.ok)

      if (response.ok) {
        const data = await response.json()
        console.log('DailyQuestion: success data =', data)
        setQuestion(data)
        // Подтянем последние отвеченные вопросы для мини‑истории
        fetchRecent()
      } else if (response.status === 404) {
        const errorData = await response.json()
        console.log('DailyQuestion: 404 error =', errorData)
        setError(errorData.detail || 'Вопросы не найдены')
      } else {
        const errorText = await response.text()
        console.log('DailyQuestion: error status =', response.status, 'text =', errorText)
        setError(`Ошибка загрузки вопроса (${response.status})`)
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  const fetchRecent = async () => {
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) return
      const resp = await fetch(getApiUrl('/v1/questions/history?limit=5'), {
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        }
      })
      if (resp.ok) {
        const items = await resp.json()
        // только отвеченные пользователем уже приходят, но подстрахуемся
        const mapped = (items || []).map((x: any) => ({
          id: x.question.id,
          number: x.question.number,
          text: x.question.text,
          category: x.question.category,
          partner_answered: x.partner_answered,
          user_answered: x.user_answered
        }))
        setRecent(mapped)
      }
    } catch {}
  }

  const notifyPartner = async () => {
    // Защита от множественных кликов
    if (notifying || notifyCooldown) return
    
    try {
      setNotifySuccess('')
      setError('')
      setNotifying(true)
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) {
        setError('Ошибка аутентификации')
        return
      }
      const resp = await fetch(getApiUrl('/v1/questions/notify_partner'), {
        method: 'POST',
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        }
      })
      if (resp.ok) {
        const data = await resp.json()
        setNotifySuccess(data.message || 'Уведомление отправлено')
        
        // Устанавливаем кулдаун на 60 секунд
        setNotifyCooldown(60)
        const interval = setInterval(() => {
          setNotifyCooldown(prev => {
            if (prev && prev > 1) {
              return prev - 1
            } else {
              clearInterval(interval)
              return null
            }
          })
        }, 1000)
        
      } else if (resp.status === 429) {
        // Rate limit - показываем сообщение об ошибке
        const err = await resp.json().catch(() => ({}))
        setError(err.detail || 'Слишком много запросов. Попробуйте позже')
        
        // Устанавливаем кулдаун на основе сообщения об ошибке
        const match = err.detail?.match(/(\d+) минут/)
        if (match) {
          const minutes = parseInt(match[1])
          setNotifyCooldown(minutes * 60)
          const interval = setInterval(() => {
            setNotifyCooldown(prev => {
              if (prev && prev > 1) {
                return prev - 1
              } else {
                clearInterval(interval)
                return null
              }
            })
          }, 1000)
        }
      } else {
        const err = await resp.json().catch(() => ({}))
        setError(err.detail || 'Не удалось отправить уведомление')
      }
    } catch (e) {
      setError('Ошибка соединения при отправке уведомления')
    } finally {
      setNotifying(false)
    }
  }

  const fetchAnswers = async (questionId: number) => {
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      const response = await fetch(getApiUrl(`/v1/questions/answers/${questionId}`), {
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        }
      })
      if (response.ok) {
        const data = await response.json()
        setSelected(data)
      }
    } catch {}
  }

  useEffect(() => {
    fetchCurrentQuestion()
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!answer.trim() || !question) return

    setSubmitting(true)
    setError('')

    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      const response = await fetch(getApiUrl('/v1/questions/answer'), {
        method: 'POST',
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question_id: question.id,
          answer_text: answer.trim()
        })
      })

      if (response.ok) {
        setSubmitted(true)
        setAnswer('')
        // после ответа перезагрузим мини‑историю
        fetchRecent()
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Ошибка отправки ответа')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="main-content">
        <div className="container">
          <div className="loading">Загрузка вопроса...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="main-content">
        <div className="container">
          <div className="header">
            <h1>Вопросы для пар</h1>
            <p>Узнайте друг друга лучше</p>
          </div>
          <div className="card card-elevated fade-in">
            <div className="error" style={{ textAlign: 'center', padding: '20px' }}>
              <h3>😔</h3>
              <p style={{ color: 'var(--tg-theme-destructive-text-color)', marginBottom: '16px' }}>
                {error}
              </p>
              <button onClick={fetchCurrentQuestion} className="btn btn-primary">
                Попробовать снова
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!question) {
    return (
      <div className="main-content">
        <div className="container">
          <div className="header">
            <h1>Вопросы для пар</h1>
            <p>Узнайте друг друга лучше</p>
          </div>
          <div className="card card-elevated fade-in">
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <h3>🎉</h3>
              <h2 style={{ marginBottom: '16px' }}>Поздравляем!</h2>
              <p style={{ marginBottom: '24px' }}>
                Вы ответили на все доступные вопросы! Скоро появятся новые.
              </p>
              <button onClick={fetchCurrentQuestion} className="btn btn-primary">
                Проверить новые вопросы
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="main-content">
      <div className="container">
        <div className="header">
          <h1>Вопрос для пар</h1>
          <p>Поделись своими мыслями с партнером</p>
        </div>

        <div className="card card-elevated fade-in">
          <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
            <span className="badge" style={{ backgroundColor: 'var(--tg-theme-secondary-bg-color)' }}>
              {question.category}
            </span>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <h3 style={{ marginBottom: '8px' }}>🤔</h3>
            <p style={{ fontSize: '18px', lineHeight: '1.5', marginBottom: '16px' }}>
              {question.text}
            </p>
            
            {question.partner_answered && (
              <div style={{ 
                padding: '12px', 
                backgroundColor: 'var(--tg-theme-secondary-bg-color)', 
                borderRadius: '8px',
                marginBottom: '16px'
              }}>
                <small style={{ color: 'var(--tg-theme-accent-text-color)' }}>
                  ✅ Ваш партнер уже ответил на этот вопрос
                </small>
              </div>
            )}
          </div>

          {!submitted && !question.user_answered ? (
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="answer">Ваш ответ:</label>
                <textarea
                  id="answer"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Поделитесь своими мыслями..."
                  required
                  disabled={submitting}
                  style={{ minHeight: '120px' }}
                />
              </div>
              
              {error && (
                <div style={{ 
                  color: 'var(--tg-theme-destructive-text-color)', 
                  marginBottom: '16px',
                  padding: '8px',
                  backgroundColor: 'rgba(255, 0, 0, 0.1)',
                  borderRadius: '4px'
                }}>
                  {error}
                </div>
              )}

              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={submitting || !answer.trim()}
              >
                {submitting ? 'Отправляем...' : 'Отправить ответ'}
              </button>
            </form>
          ) : (
            <div className="success" style={{ textAlign: 'center' }}>
              <h3>✅ Вы уже ответили на сегодняшний вопрос</h3>
              <p style={{ marginBottom: '12px' }}>Возвращайтесь завтра за новым вопросом.</p>
              {/* Кнопка уведомить партнёра, если он ещё не ответил */}
              {question && question.user_answered && !question.partner_answered && (
                <div>
                  <button 
                    onClick={notifyPartner}
                    className="btn btn-primary"
                    disabled={notifying || notifyCooldown !== null}
                  >
                    {notifying ? 'Отправляем...' : 
                     notifyCooldown ? 
                       `Повторить через ${Math.floor(notifyCooldown / 60)}:${(notifyCooldown % 60).toString().padStart(2, '0')}` : 
                       'Напомнить партнёру ответить'}
                  </button>
                  {notifySuccess && (
                    <div style={{ marginTop: 8, color: 'var(--tg-theme-accent-text-color)' }}>{notifySuccess}</div>
                  )}
                  {error && (
                    <div style={{ marginTop: 8, color: '#ff6b6b' }}>{error}</div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Мини‑история последних ответов */}
        {recent.length > 0 && (
          <div className="card card-elevated fade-in" style={{ marginTop: '16px' }}>
            <h3 style={{ marginBottom: '12px' }}>🕑 Недавние ваши ответы</h3>
            <div style={{ display: 'grid', gap: '8px' }}>
              {recent.map((r) => (
                <div key={r.id} onClick={() => fetchAnswers(r.id)} style={{
                  padding: '10px',
                  backgroundColor: 'var(--tg-theme-secondary-bg-color)',
                  borderRadius: '8px',
                  border: '1px solid var(--tg-theme-hint-color)',
                  cursor: 'pointer'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '6px' }}>
                    <span className="badge" style={{ backgroundColor: 'var(--tg-theme-hint-color)', color: 'white' }}>{r.category}</span>
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--tg-theme-hint-color)' }}>
                    {r.text.length > 90 ? `${r.text.slice(0, 90)}...` : r.text}
                  </div>
                  <div style={{ marginTop: '6px', fontSize: '12px' }}>
                    <span style={{ color: r.user_answered ? 'var(--tg-theme-accent-text-color)' : 'var(--tg-theme-hint-color)' }}>Вы: {r.user_answered ? '✅' : '—'}</span>
                    <span style={{ marginLeft: 10, color: r.partner_answered ? '#f093fb' : 'var(--tg-theme-hint-color)' }}>Партнер: {r.partner_answered ? '✅' : '—'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Модальное окно с ответами */}
        {selected && (
          <div 
            role="dialog"
            aria-modal="true"
            onClick={() => setSelected(null)}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0,0,0,0.45)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
              padding: '16px'
            }}
          >
            <div
              onClick={(e) => e.stopPropagation()}
              style={{
                width: '100%',
                maxWidth: '640px',
                background: 'var(--tg-theme-bg-color)',
                borderRadius: '16px',
                boxShadow: '0 12px 40px rgba(0,0,0,0.35)',
                border: '1px solid var(--tg-theme-secondary-bg-color)'
              }}
            >
              <div style={{ padding: '16px 16px 0 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700 }}>Ответы на вопрос дня</div>
                  <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>{selected.question.category}</div>
                </div>
                <button className="btn btn-secondary" onClick={() => setSelected(null)}>Закрыть</button>
              </div>
              <div style={{ padding: '0 16px 16px 16px' }}>
                <p style={{ fontSize: '14px', marginTop: '12px' }}>{selected.question.text}</p>
                <div style={{ display: 'grid', gap: '12px', marginTop: '12px' }}>
                  {selected.user_answer && (
                    <div style={{ padding: '12px', background: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px', border: '2px solid var(--tg-theme-accent-text-color)' }}>
                      <strong style={{ color: 'var(--tg-theme-accent-text-color)' }}>Ваш ответ</strong>
                      <div style={{ marginTop: '6px' }}>{selected.user_answer.answer_text}</div>
                      <small style={{ color: 'var(--tg-theme-hint-color)' }}>{new Date(selected.user_answer.created_at).toLocaleString('ru-RU')}</small>
                    </div>
                  )}
                  {selected.partner_answer ? (
                    <div style={{ padding: '12px', background: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px', border: '2px solid #f093fb' }}>
                      <strong style={{ color: '#f093fb' }}>Ответ {selected.partner_name}</strong>
                      <div style={{ marginTop: '6px' }}>{selected.partner_answer.answer_text}</div>
                      <small style={{ color: 'var(--tg-theme-hint-color)' }}>{new Date(selected.partner_answer.created_at).toLocaleString('ru-RU')}</small>
                    </div>
                  ) : (
                    <div style={{ padding: '12px', background: 'var(--tg-theme-secondary-bg-color)', borderRadius: '8px', border: '2px dashed var(--tg-theme-hint-color)', textAlign: 'center' }}>
                      <strong style={{ color: 'var(--tg-theme-hint-color)' }}>Партнер пока не ответил</strong>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DailyQuestion
