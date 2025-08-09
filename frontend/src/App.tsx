import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Компоненты
import Home from './components/Home'
import DailyQuestion from './components/DailyQuestion'
import Mood from './components/Mood'
import Settings from './components/Settings'
import Navigation from './components/Navigation'
import Registration from './components/Registration'

// Типы
declare global {
  interface Window {
    Telegram: {
      WebApp: {
        initData: string
        initDataUnsafe: {
          user?: {
            id: number
            first_name: string
            last_name?: string
            username?: string
          }
        }
        themeParams: {
          bg_color?: string
          text_color?: string
          hint_color?: string
          link_color?: string
          button_color?: string
          button_text_color?: string
        }
        viewportHeight: number
        viewportStableHeight: number
        headerColor: string
        backgroundColor: string
        isExpanded: boolean
        ready: () => void
        expand: () => void
        close: () => void
        showAlert: (message: string) => void
      }
    }
  }
}

function App() {
  const [isTelegramWebApp, setIsTelegramWebApp] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [registeredUser, setRegisteredUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)

  useEffect(() => {
    // Проверяем, запущено ли приложение в Telegram
    if (window.Telegram?.WebApp) {
      setIsTelegramWebApp(true)
      window.Telegram.WebApp.ready()
      window.Telegram.WebApp.expand()
      
      // Определяем режим открытия
      const viewportHeight = window.Telegram.WebApp.viewportHeight
      const viewportStableHeight = window.Telegram.WebApp.viewportStableHeight
      const isExpanded = window.Telegram.WebApp.isExpanded
      
      // Если высота viewport меньше стабильной высоты, значит есть элементы управления сверху
      setIsFullscreen(viewportHeight < viewportStableHeight || isExpanded)
      
      // Получаем данные пользователя
      if (window.Telegram.WebApp.initDataUnsafe.user) {
        const telegramUser = window.Telegram.WebApp.initDataUnsafe.user
        setUser(telegramUser)
        
        // Проверяем, зарегистрирован ли пользователь
        checkUserRegistration(telegramUser.id)
      }
    }
  }, [])

  const checkUserRegistration = async (telegramId: number) => {
    try {
      const response = await fetch(`https://gallery.homoludens.photos/pulse_of_pair/api/v1/users/me?telegram_id=${telegramId}`)
      if (response.ok) {
        const userData = await response.json()
        setRegisteredUser(userData)
        
        // Проверяем, есть ли параметр invite в URL или startapp от Telegram
        const urlParams = new URLSearchParams(window.location.search)
        const inviteCode = urlParams.get('invite') || urlParams.get('tgWebAppStartParam')?.replace('invite_', '')
        
        if (inviteCode) {
          console.log('Обнаружен код приглашения:', inviteCode)
          // Автоматически используем приглашение для уже зарегистрированного пользователя
          await useInvitation(inviteCode, telegramId)
        }
      }
      // Если пользователь не найден (404), он не зарегистрирован
    } catch (error) {
      console.error('Ошибка проверки регистрации:', error)
    } finally {
      setLoading(false)
    }
  }

  const useInvitation = async (inviteCode: string, telegramId: number) => {
    try {
      console.log('Используем приглашение:', inviteCode, 'для пользователя:', telegramId)
      const response = await fetch(`https://gallery.homoludens.photos/pulse_of_pair/api/v1/invitations/${inviteCode}/use?invitee_telegram_id=${telegramId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (response.ok) {
        console.log('Приглашение успешно использовано!')
        // Показываем уведомление пользователю
        if (window.Telegram?.WebApp?.showAlert) {
          window.Telegram.WebApp.showAlert('🎉 Вы успешно присоединились к паре! Теперь вы можете использовать все функции приложения вместе.')
        }
        
        // Обновляем данные пользователя, чтобы показать новую пару
        setTimeout(() => {
          checkUserRegistration(telegramId)
        }, 1000)
      } else {
        const error = await response.json()
        console.error('Ошибка использования приглашения:', error)
        if (window.Telegram?.WebApp?.showAlert) {
          window.Telegram.WebApp.showAlert(`❌ Ошибка: ${error.detail}`)
        }
      }
    } catch (error) {
      console.error('Ошибка при использовании приглашения:', error)
    }
  }

  const handleRegistrationComplete = (userData: any) => {
    setRegisteredUser(userData)
  }

  if (!isTelegramWebApp) {
    return (
      <div className="container">
        <div className="header">
          <h1>Pair Helper</h1>
          <p>Это приложение должно быть запущено в Telegram</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className={`main-content ${isFullscreen ? 'fullscreen' : 'embedded'}`}>
        <div className="container">
          <div className="header">
            <h1>Загрузка...</h1>
            <p>Проверяем ваш профиль</p>
          </div>
        </div>
      </div>
    )
  }

  // Если пользователь не зарегистрирован, показываем форму регистрации
  if (!registeredUser) {
    return (
      <Router>
        <div className={`tg-app ${isFullscreen ? 'fullscreen' : 'embedded'}`}>
          <Routes>
            <Route path="/pulse_of_pair/register" element={
              <Registration 
                user={user} 
                onRegistrationComplete={handleRegistrationComplete}
              />
            } />
            <Route path="*" element={<Navigate to="/pulse_of_pair/register" replace />} />
          </Routes>
        </div>
      </Router>
    )
  }

  // Если пользователь зарегистрирован, показываем основное приложение
  return (
    <Router>
      <div className={`tg-app ${isFullscreen ? 'fullscreen' : 'embedded'}`}>
        <Routes>
          <Route path="/pulse_of_pair/" element={<Home user={registeredUser} />} />
          <Route path="/pulse_of_pair/question" element={<DailyQuestion />} />
          <Route path="/pulse_of_pair/mood" element={<Mood />} />
          <Route path="/pulse_of_pair/settings" element={<Settings user={registeredUser} />} />
          <Route path="*" element={<Navigate to="/pulse_of_pair/" replace />} />
        </Routes>
        <Navigation />
      </div>
    </Router>
  )
}

export default App
