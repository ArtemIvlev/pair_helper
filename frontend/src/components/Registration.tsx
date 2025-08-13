import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { getApiUrl } from '../config'

interface RegistrationProps {
  user: any
  onRegistrationComplete: (userData: any) => void
}

const Registration: React.FC<RegistrationProps> = ({ user, onRegistrationComplete }) => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    firstName: user?.first_name || '',
    acceptTerms: false,
    acceptPrivacy: false
  })
  const [loading, setLoading] = useState(false)
  const [invitationInfo, setInvitationInfo] = useState<any>(null)
  const [inviteCode, setInviteCode] = useState<string | null>(null)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  // Проверяем приглашение при загрузке
  useEffect(() => {
    // Получаем параметр из разных источников
    const directInvite = searchParams.get('invite')
    const startParam = searchParams.get('tgWebAppStartParam') || searchParams.get('start') || ''
    const telegramStartParam = (window.Telegram?.WebApp?.initDataUnsafe as any)?.start_param || ''
    
    // Извлекаем код приглашения только если есть префикс invite_
    const startAppInvite = startParam.startsWith('invite_') ? startParam.replace('invite_', '') : null
    const telegramInvite = telegramStartParam.startsWith('invite_') ? telegramStartParam.replace('invite_', '') : null
    
    const invite = directInvite || startAppInvite || telegramInvite
    
    if (invite) {
      setInviteCode(invite)
      // Получаем информацию о приглашении
              fetch(getApiUrl(`/v1/invitations/${invite}`))
        .then(response => response.json())
        .then(data => {
          if (data.code) {
            setInvitationInfo(data)
          }
        })
        .catch(error => {
          console.error('Ошибка при получении информации о приглашении:', error)
        })
    }
  }, [searchParams])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.acceptTerms || !formData.acceptPrivacy) {
      alert('Необходимо принять все соглашения')
      return
    }

    setLoading(true)
    
    const requestBody = {
      telegram_id: user.id,
      first_name: formData.firstName,
      accept_terms: formData.acceptTerms,
      accept_privacy: formData.acceptPrivacy,
      invite_code: inviteCode
    }
    
    try {
      // Регистрируем пользователя
      const response = await fetch(getApiUrl('/v1/users/register'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })

      if (response.ok) {
        const userData = await response.json()
        
        onRegistrationComplete(userData)
        navigate('/pulse_of_pair/')
      } else {
        const error = await response.json()
        alert(`Ошибка регистрации: ${error.detail}`)
      }
    } catch (error) {
      console.error('Ошибка регистрации:', error)
      alert('Ошибка при регистрации. Попробуйте еще раз.')
    } finally {
      setLoading(false)
    }
  }

  if (step === 1) {
    return (
      <div className="main-content">
        <div className="container">
                  <div className="header">
          <h1>Добро пожаловать! 👋</h1>
          <p>Добро пожаловать в Пульс ваших отношений - приложение для укрепления отношений в паре</p>
          

          
          {invitationInfo && (
            <div className="invitation-notice" style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '16px',
              borderRadius: '12px',
              marginTop: '16px',
              textAlign: 'center'
            }}>
              <h3 style={{ margin: '0 0 8px 0' }}>🎉 Вы приглашены!</h3>
              <p style={{ margin: '0', opacity: '0.9' }}>
                {invitationInfo.inviter_name} приглашает вас присоединиться к паре. 
                Зарегистрируйтесь, и вы автоматически станете партнерами!
              </p>
            </div>
          )}
        </div>

          <div className="card card-elevated fade-in">
            <h3>Что вас ждет?</h3>
            <div style={{ textAlign: 'left', marginTop: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontSize: '20px', marginRight: '12px' }}>💬</span>
                <span>Ежедневные вопросы для общения</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontSize: '20px', marginRight: '12px' }}>❤️</span>
                <span>Отслеживание настроения</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontSize: '20px', marginRight: '12px' }}>📅</span>
                <span>Общий календарь событий</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                <span style={{ fontSize: '20px', marginRight: '12px' }}>🎯</span>
                <span>Ритуалы и привычки</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center' }}>
                <span style={{ fontSize: '20px', marginRight: '12px' }}>📊</span>
                <span>Статистика отношений</span>
              </div>
            </div>
          </div>

          <button 
            className="btn btn-primary" 
            onClick={() => setStep(2)}
            style={{ marginTop: '16px' }}
          >
            Начать регистрацию
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="main-content">
      <div className="container">
        <div className="header">
          <h1>Регистрация</h1>
          <p>Завершите настройку профиля</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="card card-elevated fade-in">
            <div className="form-group">
              <label htmlFor="firstName">Как вас зовут? *</label>
              <input
                type="text"
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleInputChange}
                required
                placeholder="Ваше имя"
              />
            </div>
          </div>

          <div className="card card-elevated fade-in">
            <h3>Соглашения</h3>
            
            <div className="form-group" style={{ marginBottom: '16px' }}>
              <label style={{ 
                display: 'flex', 
                alignItems: 'flex-start', 
                cursor: 'pointer',
                gap: '8px',
                width: '100%'
              }}>
                <input
                  type="checkbox"
                  name="acceptTerms"
                  checked={formData.acceptTerms}
                  onChange={handleInputChange}
                  style={{ 
                    marginTop: '2px',
                    flexShrink: 0,
                    width: '16px',
                    height: '16px'
                  }}
                />
                <span style={{ 
                  fontSize: '14px', 
                  lineHeight: '1.4',
                  flex: '1',
                  wordBreak: 'break-word',
                  overflowWrap: 'break-word'
                }}>
                  Я принимаю <strong>Пользовательское соглашение</strong> и соглашаюсь с правилами использования приложения
                </span>
              </label>
            </div>

            <div className="form-group">
              <label style={{ 
                display: 'flex', 
                alignItems: 'flex-start', 
                cursor: 'pointer',
                gap: '8px',
                width: '100%'
              }}>
                <input
                  type="checkbox"
                  name="acceptPrivacy"
                  checked={formData.acceptPrivacy}
                  onChange={handleInputChange}
                  style={{ 
                    marginTop: '2px',
                    flexShrink: 0,
                    width: '16px',
                    height: '16px'
                  }}
                />
                <span style={{ 
                  fontSize: '14px', 
                  lineHeight: '1.4',
                  flex: '1',
                  wordBreak: 'break-word',
                  overflowWrap: 'break-word'
                }}>
                  Я даю согласие на <strong>обработку персональных данных</strong> в соответствии с Политикой конфиденциальности
                </span>
              </label>
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading || !formData.acceptTerms || !formData.acceptPrivacy}
            style={{ marginTop: '16px' }}
          >
            {loading ? 'Регистрация...' : 'Завершить регистрацию'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default Registration
