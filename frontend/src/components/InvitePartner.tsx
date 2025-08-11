import React, { useState, useEffect } from 'react'
import { getApiUrl } from '../config'

interface InvitePartnerProps {
  user: any
}

interface Pair {
  id: number
  user1_id: number
  user2_id: number
  created_at: string
  user1?: {
    id: number
    first_name: string
    telegram_id: number
  }
  user2?: {
    id: number
    first_name: string
    telegram_id: number
  }
}

const InvitePartner: React.FC<InvitePartnerProps> = ({ user }) => {
  const [loading, setLoading] = useState(false)
  const [inviteLink, setInviteLink] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [pair, setPair] = useState<Pair | null>(null)
  const [checkingPair, setCheckingPair] = useState(true)

  // Проверяем существующую пару при загрузке
  useEffect(() => {
    checkExistingPair()
  }, [user])

  const checkExistingPair = async () => {
    if (!user?.id) return

    try {
      const response = await fetch(getApiUrl('/v1/pair/'), {
        headers: {
          'Content-Type': 'application/json',
          'X-Telegram-User-ID': user.telegram_id.toString()
        }
      })

      if (response.ok) {
        const pairData = await response.json()
        setPair(pairData)
      }
    } catch (error) {
      console.error('Ошибка при проверке пары:', error)
    } finally {
      setCheckingPair(false)
    }
  }

  const generateInvite = async () => {
    if (!user?.telegram_id) {
      setError('Пользователь не найден')
      return
    }

    setLoading(true)
    setError(null)
    setInviteLink(null)

    try {
      const response = await fetch(getApiUrl(`/v1/invitations/generate?inviter_telegram_id=${user.telegram_id}`), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (response.ok) {
        const data = await response.json()
                            const link = `https://t.me/PulseOfPair_Bot/pulse_of_pair?startapp=invite_${data.code}`
        setInviteLink(link)
      } else {
        const errorData = await response.json()
        setError(errorData.detail || 'Ошибка при создании приглашения')
      }
    } catch (error) {
      console.error('Ошибка при создании приглашения:', error)
      setError('Ошибка при создании приглашения')
    } finally {
      setLoading(false)
    }
  }

  const copyToClipboard = async () => {
    if (inviteLink) {
      try {
        await navigator.clipboard.writeText(inviteLink)
        if (window.Telegram?.WebApp?.showAlert) {
          window.Telegram.WebApp.showAlert('Ссылка скопирована!')
        } else {
          alert('Ссылка скопирована!')
        }
      } catch (error) {
        console.error('Ошибка при копировании:', error)
        setError('Ошибка при копировании ссылки')
      }
    }
  }

  const shareViaTelegram = () => {
    if (inviteLink) {
      const shareUrl = `https://t.me/share/url?url=${encodeURIComponent(inviteLink)}&text=${encodeURIComponent('Привет! Присоединяйся ко мне в Пульс ваших отношений - приложении для пар! 💕')}`
      window.open(shareUrl, '_blank')
    }
  }

  // Если проверяем пару, показываем загрузку
  if (checkingPair) {
    return (
      <div className="invite-partner">
        <div className="card">
          <h3>🎫 Пригласить партнера</h3>
          <p>Проверяем вашу пару...</p>
        </div>
      </div>
    )
  }

  // Если пара уже существует, показываем информацию о партнере
  if (pair) {
    const partner = pair.user1_id === user.id ? pair.user2 : pair.user1
    const pairCreatedDate = new Date(pair.created_at).toLocaleDateString('ru-RU')

    return (
      <div className="invite-partner">
        <div className="card">
          <h3>💕 Ваша пара</h3>
          <div className="pair-info">
            <div className="partner-details">
              <h4>Партнер: {partner?.first_name || 'Неизвестно'}</h4>
              <p>Пара создана: {pairCreatedDate}</p>
            </div>
            
            <div className="pair-status">
              <span className="status-badge">✅ Активна</span>
            </div>
          </div>
          
        </div>
      </div>
    )
  }

  // Если пары нет, показываем форму создания приглашения
  return (
    <div className="invite-partner">
      <div className="card">
        <h3>🎫 Пригласить партнера</h3>
        <p>Создайте ссылку-приглашение для вашего партнера</p>
        
        {!inviteLink ? (
          <button 
            className="btn btn-primary" 
            onClick={generateInvite}
            disabled={loading}
          >
            {loading ? 'Создаю ссылку...' : 'Создать приглашение'}
          </button>
        ) : (
          <div className="invite-result">
            <div className="invite-link">
              <label>Ваша ссылка-приглашение:</label>
              <div className="link-container">
                <input 
                  type="text" 
                  value={inviteLink} 
                  readOnly 
                  className="link-input"
                />
                <button 
                  className="btn btn-secondary copy-btn"
                  onClick={copyToClipboard}
                  title="Копировать ссылку"
                >
                  📋
                </button>
              </div>
            </div>
            
            <div className="share-actions">
              <button 
                className="btn btn-primary"
                onClick={shareViaTelegram}
              >
                📤 Поделиться в Telegram
              </button>
              
              <button 
                className="btn btn-secondary"
                onClick={() => setInviteLink(null)}
              >
                Создать новую ссылку
              </button>
            </div>
            
            <div className="invite-info">
              <p><strong>Как это работает:</strong></p>
              <ol>
                <li>Отправьте эту ссылку вашему партнеру</li>
                <li>Партнер перейдет по ссылке и попадет в бота</li>
                <li>После регистрации вы автоматически станете парой</li>
              </ol>
              <p><em>Ссылка действительна 7 дней</em></p>
            </div>
          </div>
        )}
        
        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}
      </div>
    </div>
  )
}

export default InvitePartner
