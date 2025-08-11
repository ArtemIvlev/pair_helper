import React, { useState, useEffect } from 'react'
import { getApiUrl } from '../config'
import Feedback from './Feedback'

interface SettingsProps {
  user?: any
}

const Settings: React.FC<SettingsProps> = ({ user }) => {
  const [activeTab, setActiveTab] = useState('profile')
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState({
    firstName: user?.first_name || ''
  })
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (user) {
      setFormData({
        firstName: user.first_name || ''
      })
    }
  }, [user])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSave = async () => {
    if (!user) return

    setLoading(true)
    try {
      const response = await fetch(getApiUrl(`/v1/users/${user.id}`), {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          first_name: formData.firstName
        })
      })

      if (response.ok) {
        setEditing(false)
        // Можно добавить уведомление об успешном сохранении
      } else {
        const error = await response.json()
        alert(`Ошибка сохранения: ${error.detail}`)
      }
    } catch (error) {
      console.error('Ошибка сохранения:', error)
      alert('Ошибка при сохранении. Попробуйте еще раз.')
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      firstName: user?.first_name || ''
    })
    setEditing(false)
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="main-content">
      <div className="container">
        <div className="header">
          <h1>Настройки</h1>
          <p>Управление профилем и настройками</p>
        </div>

        {/* Табы */}
        <div className="card">
          <div style={{ display: 'flex', borderBottom: '1px solid var(--tg-theme-hint-color)' }}>
            <button
              onClick={() => setActiveTab('profile')}
              style={{
                flex: 1,
                padding: '12px',
                border: 'none',
                background: activeTab === 'profile' ? 'var(--tg-theme-button-color)' : 'transparent',
                color: activeTab === 'profile' ? 'var(--tg-theme-button-text-color)' : 'var(--tg-theme-text-color)',
                cursor: 'pointer',
                borderRadius: '8px 8px 0 0'
              }}
            >
              Профиль
            </button>
            <button
              onClick={() => setActiveTab('app')}
              style={{
                flex: 1,
                padding: '12px',
                border: 'none',
                background: activeTab === 'app' ? 'var(--tg-theme-button-color)' : 'transparent',
                color: activeTab === 'app' ? 'var(--tg-theme-button-text-color)' : 'var(--tg-theme-text-color)',
                cursor: 'pointer',
                borderRadius: '8px 8px 0 0'
              }}
            >
              Приложение
            </button>
            <button
              onClick={() => setActiveTab('feedback')}
              style={{
                flex: 1,
                padding: '12px',
                border: 'none',
                background: activeTab === 'feedback' ? 'var(--tg-theme-button-color)' : 'transparent',
                color: activeTab === 'feedback' ? 'var(--tg-theme-button-text-color)' : 'var(--tg-theme-text-color)',
                cursor: 'pointer',
                borderRadius: '8px 8px 0 0'
              }}
            >
              Обратная связь
            </button>
          </div>
        </div>

        {/* Содержимое табов */}
        {activeTab === 'profile' && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h3>Информация профиля</h3>
              {!editing && (
                <button
                  onClick={() => setEditing(true)}
                  className="btn btn-secondary"
                  style={{ width: 'auto', padding: '8px 16px' }}
                >
                  Редактировать
                </button>
              )}
            </div>

            {editing ? (
              <div>
                <div className="form-group">
                  <label htmlFor="firstName">Как вас зовут? *</label>
                  <input
                    type="text"
                    id="firstName"
                    name="firstName"
                    value={formData.firstName}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                  <button
                    onClick={handleSave}
                    className="btn btn-primary"
                    disabled={loading}
                    style={{ flex: 1 }}
                  >
                    {loading ? 'Сохранение...' : 'Сохранить'}
                  </button>
                  <button
                    onClick={handleCancel}
                    className="btn btn-secondary"
                    style={{ flex: 1 }}
                  >
                    Отмена
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color)', marginBottom: '4px' }}>
                    Имя
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '500' }}>
                    {user?.first_name || 'Не указано'}
                  </div>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color)', marginBottom: '4px' }}>
                    Telegram ID
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '500', fontFamily: 'monospace' }}>
                    {user?.telegram_id || 'Не указано'}
                  </div>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '14px', color: 'var(--tg-theme-hint-color)', marginBottom: '4px' }}>
                    Дата регистрации
                  </div>
                  <div style={{ fontSize: '16px', fontWeight: '500' }}>
                    {user?.created_at ? formatDate(user.created_at) : 'Не указано'}
                  </div>
                </div>

                <div style={{ 
                  padding: '12px', 
                  background: 'var(--tg-theme-secondary-bg-color)', 
                  borderRadius: '8px',
                  fontSize: '14px',
                  color: 'var(--tg-theme-hint-color)'
                }}>
                  <strong>ℹ️</strong> Telegram ID и дата регистрации не могут быть изменены
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'app' && (
          <div className="card">
            <h3>Настройки приложения</h3>
            <p style={{ color: 'var(--tg-theme-hint-color)' }}>
              Настройки приложения будут доступны в следующих обновлениях
            </p>
          </div>
        )}

        {activeTab === 'feedback' && (
          <div>
            <Feedback />
          </div>
        )}
      </div>
    </div>
  )
}

export default Settings
