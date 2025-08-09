import React, { useState, useEffect } from 'react'

interface Question {
  id: number
  number: number
  text: string
  category: string
  partner_answered: boolean
}

interface QuestionStatus {
  question: Question
  user_answered: boolean
  partner_answered: boolean
  can_view_answers: boolean
}

interface UserAnswer {
  id: number
  question_id: number
  answer_text: string
  created_at: string
}

interface PairAnswers {
  question: Question
  user_answer: UserAnswer | null
  partner_answer: UserAnswer | null
  partner_name: string
}

const QuestionHistory: React.FC = () => {
  const [questions, setQuestions] = useState<QuestionStatus[]>([])
  const [selectedQuestion, setSelectedQuestion] = useState<PairAnswers | null>(null)
  const [loading, setLoading] = useState(true)

  const [error, setError] = useState('')
  const [stats, setStats] = useState({
    total_questions: 0,
    user_answered: 0,
    partner_answered: 0,
    both_answered: 0,
    completion_percentage: 0
  })
  const fetchHistory = async () => {
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) {
        setError('Ошибка аутентификации')
        return
      }

      const [historyResponse, statsResponse] = await Promise.all([
        fetch('/pulse_of_pair/api/v1/questions/history', {
          headers: {
            'X-Telegram-Init-Data': initData,
            'Content-Type': 'application/json'
          }
        }),
        fetch('/pulse_of_pair/api/v1/questions/stats', {
          headers: {
            'X-Telegram-Init-Data': initData,
            'Content-Type': 'application/json'
          }
        })
      ])

      if (historyResponse.ok && statsResponse.ok) {
        const historyData = await historyResponse.json()
        const statsData = await statsResponse.json()
        setQuestions(historyData)
        setStats(statsData)
      } else {
        setError('Ошибка загрузки данных')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  const fetchAnswers = async (questionId: number) => {
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      const response = await fetch(`/pulse_of_pair/api/v1/questions/answers/${questionId}`, {
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        setSelectedQuestion(data)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Ошибка загрузки ответов')
      }
    } catch (err) {
      setError('Ошибка соединения с сервером')
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  if (loading) {
    return (
      <div className="main-content">
        <div className="container">
          <div className="loading">Загрузка истории вопросов...</div>
        </div>
      </div>
    )
  }

  if (selectedQuestion) {
    return (
      <div className="main-content">
        <div className="container">
          <div className="header">
            <button 
              onClick={() => setSelectedQuestion(null)}
              className="btn btn-secondary"
              style={{ marginBottom: '16px' }}
            >
              ← Назад к истории
            </button>
            <h1>Ответы на вопрос #{selectedQuestion.question.number}</h1>
            <p>{selectedQuestion.question.category}</p>
          </div>

          <div className="card card-elevated fade-in">
            <div style={{ marginBottom: '24px' }}>
              <h3 style={{ marginBottom: '16px' }}>🤔 Вопрос:</h3>
              <p style={{ fontSize: '18px', lineHeight: '1.5', marginBottom: '24px' }}>
                {selectedQuestion.question.text}
              </p>
            </div>

            <div className="answers-container" style={{ display: 'grid', gap: '20px' }}>
              {/* Ответ пользователя */}
              {selectedQuestion.user_answer && (
                <div className="answer-card" style={{
                  padding: '16px',
                  backgroundColor: 'var(--tg-theme-secondary-bg-color)',
                  borderRadius: '12px',
                  border: '2px solid var(--tg-theme-accent-text-color)'
                }}>
                  <h4 style={{ marginBottom: '12px', color: 'var(--tg-theme-accent-text-color)' }}>
                    💭 Ваш ответ
                  </h4>
                  <p style={{ lineHeight: '1.5', marginBottom: '8px' }}>
                    {selectedQuestion.user_answer.answer_text}
                  </p>
                  <small style={{ color: 'var(--tg-theme-hint-color)' }}>
                    {new Date(selectedQuestion.user_answer.created_at).toLocaleString('ru-RU')}
                  </small>
                </div>
              )}

              {/* Ответ партнера */}
              {selectedQuestion.partner_answer ? (
                <div className="answer-card" style={{
                  padding: '16px',
                  backgroundColor: 'var(--tg-theme-secondary-bg-color)',
                  borderRadius: '12px',
                  border: '2px solid #f093fb'
                }}>
                  <h4 style={{ marginBottom: '12px', color: '#f093fb' }}>
                    💕 Ответ {selectedQuestion.partner_name}
                  </h4>
                  <p style={{ lineHeight: '1.5', marginBottom: '8px' }}>
                    {selectedQuestion.partner_answer.answer_text}
                  </p>
                  <small style={{ color: 'var(--tg-theme-hint-color)' }}>
                    {new Date(selectedQuestion.partner_answer.created_at).toLocaleString('ru-RU')}
                  </small>
                </div>
              ) : (
                <div className="answer-card" style={{
                  padding: '16px',
                  backgroundColor: 'var(--tg-theme-secondary-bg-color)',
                  borderRadius: '12px',
                  border: '2px dashed var(--tg-theme-hint-color)',
                  textAlign: 'center'
                }}>
                  <h4 style={{ marginBottom: '12px', color: 'var(--tg-theme-hint-color)' }}>
                    💭 Ответ {selectedQuestion.partner_name}
                  </h4>
                  <p style={{ color: 'var(--tg-theme-hint-color)' }}>
                    Пока не ответил на этот вопрос
                  </p>
                </div>
              )}
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
          <h1>История вопросов</h1>
          <p>Ваши ответы и ответы партнера</p>
        </div>

        {/* Статистика */}
        <div className="card card-elevated fade-in" style={{ marginBottom: '20px' }}>
          <h3 style={{ marginBottom: '16px' }}>📊 Статистика</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: 'var(--tg-theme-accent-text-color)' }}>
                {stats.user_answered}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>
                ваших ответов
              </div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f093fb' }}>
                {stats.partner_answered}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>
                ответов партнера
              </div>
            </div>
          </div>
          <div style={{ 
            marginTop: '16px', 
            textAlign: 'center',
            padding: '12px',
            backgroundColor: 'var(--tg-theme-secondary-bg-color)',
            borderRadius: '8px'
          }}>
            <strong>{stats.both_answered}</strong> из <strong>{stats.total_questions}</strong> вопросов отвечены обоими
            <br />
            <small style={{ color: 'var(--tg-theme-hint-color)' }}>
              ({stats.completion_percentage}% завершено)
            </small>
          </div>
        </div>

        {/* Список вопросов */}
        <div className="card card-elevated fade-in">
          <h3 style={{ marginBottom: '16px' }}>📝 Все вопросы</h3>
          
          {questions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <h3>📭</h3>
              <p style={{ color: 'var(--tg-theme-hint-color)' }}>
                Пока нет вопросов для отображения
              </p>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '12px' }}>
              {questions.map((item) => (
                <div
                  key={item.question.id}
                  className="question-item"
                  style={{
                    padding: '16px',
                    backgroundColor: 'var(--tg-theme-secondary-bg-color)',
                    borderRadius: '8px',
                    cursor: item.can_view_answers ? 'pointer' : 'default',
                    opacity: item.can_view_answers ? 1 : 0.7,
                    border: item.can_view_answers ? '1px solid var(--tg-theme-accent-text-color)' : '1px solid var(--tg-theme-hint-color)'
                  }}
                  onClick={() => item.can_view_answers && fetchAnswers(item.question.id)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <span className="badge" style={{ 
                      backgroundColor: 'var(--tg-theme-accent-text-color)', 
                      color: 'white',
                      fontSize: '12px'
                    }}>
                      #{item.question.number}
                    </span>
                    <span className="badge" style={{ 
                      backgroundColor: 'var(--tg-theme-hint-color)', 
                      color: 'white',
                      fontSize: '12px'
                    }}>
                      {item.question.category}
                    </span>
                  </div>
                  
                  <p style={{ fontSize: '14px', lineHeight: '1.4', marginBottom: '12px' }}>
                    {item.question.text.length > 100 
                      ? `${item.question.text.substring(0, 100)}...` 
                      : item.question.text
                    }
                  </p>
                  
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <span style={{ 
                        fontSize: '12px',
                        color: item.user_answered ? 'var(--tg-theme-accent-text-color)' : 'var(--tg-theme-hint-color)'
                      }}>
                        {item.user_answered ? '✅' : '❌'} Вы
                      </span>
                      <span style={{ 
                        fontSize: '12px',
                        color: item.partner_answered ? '#f093fb' : 'var(--tg-theme-hint-color)'
                      }}>
                        {item.partner_answered ? '✅' : '❌'} Партнер
                      </span>
                    </div>
                    
                    {item.can_view_answers ? (
                      <span style={{ fontSize: '12px', color: 'var(--tg-theme-accent-text-color)' }}>
                        Посмотреть ответы →
                      </span>
                    ) : (
                      <span style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>
                        Сначала ответьте
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {error && (
          <div style={{ 
            color: 'var(--tg-theme-destructive-text-color)', 
            marginTop: '16px',
            padding: '12px',
            backgroundColor: 'rgba(255, 0, 0, 0.1)',
            borderRadius: '8px',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}
      </div>
    </div>
  )
}

export default QuestionHistory
