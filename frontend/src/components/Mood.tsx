import React, { useState } from 'react'

const Mood: React.FC = () => {
  const [selectedMood, setSelectedMood] = useState('')
  const [note, setNote] = useState('')
  const [submitted, setSubmitted] = useState(false)

  const moods = [
    { code: 'joyful', emoji: '😊', text: 'Радостный' },
    { code: 'calm', emoji: '😌', text: 'Спокойный' },
    { code: 'tired', emoji: '😴', text: 'Уставший' },
    { code: 'anxious', emoji: '😰', text: 'Тревожный' },
    { code: 'sad', emoji: '😢', text: 'Грустный' },
    { code: 'irritable', emoji: '😤', text: 'Раздражённый' },
    { code: 'grateful', emoji: '🙏', text: 'Благодарный' },
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (selectedMood) {
      setSubmitted(true)
      // Здесь будет отправка на сервер
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
              disabled={!selectedMood}
            >
              Сохранить настроение
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
      </div>
    </div>
  )
}

export default Mood
