import React, { useState, useEffect } from 'react'
import { getApiUrl } from '../config'

interface MoodData {
  id: number
  user_id: number
  date: string
  mood_code: string
  note?: string
  user: {
    first_name: string
    last_name?: string
  }
}

const Mood: React.FC = () => {
  const [selectedMood, setSelectedMood] = useState('')
  const [note, setNote] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [recentMoods, setRecentMoods] = useState<MoodData[]>([])
  const [loadingMoods, setLoadingMoods] = useState(false)

  const moods = [
    { code: 'joyful', emoji: '😊', text: 'Радостный' },
    { code: 'calm', emoji: '😌', text: 'Спокойный' },
    { code: 'tired', emoji: '😴', text: 'Уставший' },
    { code: 'anxious', emoji: '😰', text: 'Тревожный' },
    { code: 'sad', emoji: '😢', text: 'Грустный' },
    { code: 'irritable', emoji: '😤', text: 'Раздражённый' },
    { code: 'grateful', emoji: '🙏', text: 'Благодарный' },
  ]

  const moodEmojis: { [key: string]: string } = {
    'joyful': '😊',
    'calm': '😌',
    'tired': '😴',
    'anxious': '😰',
    'sad': '😢',
    'irritable': '😤',
    'grateful': '🙏'
  }

  const loadRecentMoods = async () => {
    setLoadingMoods(true)
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) return

      const response = await fetch(getApiUrl('/v1/mood/'), {
        headers: {
          'X-Telegram-Init-Data': initData
        }
      })

      if (response.ok) {
        const moods = await response.json()
        setRecentMoods(moods.slice(0, 6)) // Показываем последние 6 настроений
      }
    } catch (err) {
      console.error('Ошибка загрузки настроений:', err)
    } finally {
      setLoadingMoods(false)
    }
  }

  useEffect(() => {
    loadRecentMoods()
  }, [])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)
    
    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня'
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Вчера'
    } else {
      return date.toLocaleDateString('ru-RU', { 
        day: 'numeric', 
        month: 'short' 
      })
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedMood) return

    setLoading(true)
    setError('')

    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) {
        setError('Ошибка аутентификации')
        return
      }

      const response = await fetch(getApiUrl('/v1/mood/'), {
        method: 'POST',
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mood_code: selectedMood,
          note: note.trim() || null
        })
      })

      if (response.ok) {
        setSubmitted(true)
        // Перезагружаем список настроений после успешного сохранения
        await loadRecentMoods()
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Ошибка сохранения настроения')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="main-content">
      <div className="container">
        <div className="header">
        <h1>Настроение дня</h1>
        <p>Как ты себя чувствуешь сегодня?</p>
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
            <div className="mood-grid">
              {moods.map((mood) => (
                <div
                  key={mood.code}
                  className={`mood-item ${selectedMood === mood.code ? 'selected' : ''}`}
                  onClick={() => setSelectedMood(mood.code)}
                >
                  <div className="mood-emoji">{mood.emoji}</div>
                  <div className="mood-text">{mood.text}</div>
                </div>
              ))}
            </div>

            <div className="form-group">
              <label htmlFor="note">Дополнительная заметка (необязательно):</label>
              <textarea
                id="note"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Расскажи подробнее о своём настроении..."
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={!selectedMood || loading}
            >
              {loading ? 'Сохранение...' : 'Сохранить настроение'}
            </button>
          </form>
        </div>
      ) : (
        <div className="card card-elevated fade-in">
          <div className="success">
            <h3>✅ Настроение сохранено!</h3>
            <p>Твой партнёр сможет увидеть твоё настроение.</p>
          </div>
        </div>
      )}

      {/* Последние настроения */}
      <div className="card card-elevated fade-in" style={{ marginTop: '20px' }}>
        <h3>Последние настроения</h3>
        {loadingMoods ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <div className="loading-spinner"></div>
            <p>Загрузка...</p>
          </div>
        ) : recentMoods.length > 0 ? (
          <div className="recent-moods">
            {recentMoods.map((mood) => (
              <div key={mood.id} className="mood-entry">
                <div className="mood-entry-header">
                  <span className="mood-emoji-large">{moodEmojis[mood.mood_code] || '😊'}</span>
                  <div className="mood-entry-info">
                    <div className="mood-entry-name">
                      {mood.user.first_name} {mood.user.last_name || ''}
                    </div>
                    <div className="mood-entry-date">{formatDate(mood.date)}</div>
                  </div>
                </div>
                {mood.note && (
                  <div className="mood-entry-note">{mood.note}</div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text-secondary)' }}>
            <p>Пока нет сохранённых настроений</p>
          </div>
        )}
      </div>
      </div>
    </div>
  )
}

export default Mood
