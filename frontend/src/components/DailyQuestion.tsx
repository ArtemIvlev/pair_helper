import React, { useState, useEffect } from 'react'

const DailyQuestion: React.FC = () => {
  const [question, setQuestion] = useState('')
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    // Имитация загрузки вопроса
    setTimeout(() => {
      setQuestion('Что сегодня заставило тебя улыбнуться?')
      setLoading(false)
    }, 1000)
  }, [])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (answer.trim()) {
      setSubmitted(true)
      // Здесь будет отправка на сервер
    }
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Загрузка вопроса...</div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header">
        <h1>Вопрос дня</h1>
        <p>Поделись своими мыслями</p>
      </div>

      <div className="card card-elevated fade-in">
        <h3 style={{ marginBottom: '16px' }}>🤔</h3>
        <p style={{ fontSize: '18px', lineHeight: '1.5', marginBottom: '24px' }}>
          {question}
        </p>

        {!submitted ? (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="answer">Твой ответ:</label>
              <textarea
                id="answer"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Напиши свой ответ..."
                required
              />
            </div>
            <button type="submit" className="btn btn-primary">
              Отправить ответ
            </button>
          </form>
        ) : (
          <div className="success">
            <h3>✅ Ответ отправлен!</h3>
            <p>Твой партнёр сможет увидеть твой ответ после того, как тоже ответит на вопрос.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default DailyQuestion
