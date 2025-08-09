import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Heart, MessageCircle } from 'lucide-react'
import InvitePartner from './InvitePartner'

interface HomeProps {
  user: any
}

const Home: React.FC<HomeProps> = ({ user }) => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    questionStreak: 0,
    moodStreak: 0
  })

  useEffect(() => {
    // Имитация загрузки данных
    setTimeout(() => {
      setLoading(false)
      setStats({
        questionStreak: 5,
        moodStreak: 3
      })
    }, 1000)
  }, [])

  const quickActions = [
    {
      title: 'Вопрос дня',
      description: 'Ответить на ежедневный вопрос',
      icon: MessageCircle,
      path: '/pulse_of_pair/question',
      color: '#667eea'
    },
    {
      title: 'Настроение',
      description: 'Отметить настроение дня',
      icon: Heart,
      path: '/pulse_of_pair/mood',
      color: '#f093fb'
    }
  ]

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Загрузка...</div>
      </div>
    )
  }

  return (
    <div className="main-content">
      <div className="container">
        <div className="header fade-in">
        <h1>Привет, {user?.first_name || 'дорогой'}! 👋</h1>
        <p>Как дела сегодня?</p>
      </div>

      {/* Статистика */}
      <div className="card card-elevated fade-in">
        <h3>Ваша активность</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px', marginTop: '16px' }}>
          <div className="text-center">
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#667eea' }}>
              {stats.questionStreak}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>
              дней подряд отвечаете на вопросы
            </div>
          </div>
          <div className="text-center">
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f093fb' }}>
              {stats.moodStreak}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>
              дней подряд отмечаете настроение
            </div>
          </div>
        </div>
      </div>

      {/* Быстрые действия */}
      <div className="card card-elevated fade-in">
        <h3>Быстрые действия</h3>
        <div style={{ marginTop: '16px' }}>
          {quickActions.map((action) => {
            const Icon = action.icon
            return (
              <div
                key={action.path}
                className="quick-action"
                onClick={() => navigate(action.path)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '16px',
                  margin: '8px 0',
                  borderRadius: '12px',
                  background: 'var(--tg-theme-secondary-bg-color)',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  border: '1px solid var(--tg-theme-hint-color)'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)'
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)'
                  e.currentTarget.style.boxShadow = 'none'
                }}
              >
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: action.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginRight: '16px'
                  }}
                >
                  <Icon size={20} color="white" />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: '600', marginBottom: '4px' }}>
                    {action.title}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>
                    {action.description}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Мотивационное сообщение */}
      <div className="card fade-in" style={{ textAlign: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
        <h3>💕</h3>
        <p style={{ margin: 0, fontSize: '14px' }}>
          Каждый день - это новая возможность стать ближе друг к другу
        </p>
      </div>

      {/* Компонент приглашения партнера */}
      <InvitePartner user={user} />
      </div>
    </div>
  )
}

export default Home
