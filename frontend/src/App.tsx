import { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import './App.css'
import { getApiUrl } from './config'

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
  const [navigateToQuestion, setNavigateToQuestion] = useState(false)
  const [navigateToMood, setNavigateToMood] = useState(false)

  useEffect(() => {
    // Проверяем, запущено ли приложение в Telegram
    if (window.Telegram?.WebApp) {
      setIsTelegramWebApp(true)
      window.Telegram.WebApp.ready()
      window.Telegram.WebApp.expand()
      
      // Определяем тему Telegram и устанавливаем атрибут
      const themeParams = window.Telegram.WebApp.themeParams
      const bgColor = themeParams.bg_color || '#ffffff'
      
      // Определяем темную/светлую тему по цвету фона
      const isDarkTheme = isColorDark(bgColor)
      const theme = isDarkTheme ? 'dark' : 'light'
      
      // Устанавливаем атрибут темы на корневой элемент
      document.documentElement.setAttribute('data-theme', theme)
      
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

  // Функция для определения темной темы по цвету
  const isColorDark = (color: string): boolean => {
    // Убираем # если есть
    const hex = color.replace('#', '')
    
    // Конвертируем в RGB
    const r = parseInt(hex.substr(0, 2), 16)
    const g = parseInt(hex.substr(2, 2), 16)
    const b = parseInt(hex.substr(4, 2), 16)
    
    // Вычисляем яркость (формула из WCAG)
    const brightness = (r * 299 + g * 587 + b * 114) / 1000
    
    // Если яркость меньше 128, считаем темной темой
    return brightness < 128
  }

  const checkUserRegistration = async (telegramId: number) => {
    try {
              const response = await fetch(getApiUrl(`/v1/users/me?telegram_id=${telegramId}`))
      if (response.ok) {
        const userData = await response.json()
        setRegisteredUser(userData)
        
        // Проверяем параметры URL и startapp от Telegram
        const urlParams = new URLSearchParams(window.location.search)
        const startParam = urlParams.get('tgWebAppStartParam') || ''
        
        // Проверяем диплинк на приглашение
        const directInviteCode = urlParams.get('invite')
        const startAppInviteCode = startParam.startsWith('invite_') ? startParam.replace('invite_', '') : null
        const inviteCode = directInviteCode || startAppInviteCode
        
        if (inviteCode) {
          console.log('Обнаружен код приглашения:', inviteCode)
          // Автоматически используем приглашение для уже зарегистрированного пользователя
          await useInvitation(inviteCode, telegramId)
        }

        // Проверяем диплинк на страницу вопросов
        const directQuestionParam = urlParams.get('question')
        const startAppQuestionParam = startParam.startsWith('question_') ? startParam.replace('question_', '') : null
        const questionParam = directQuestionParam || startAppQuestionParam
        
        if (questionParam === 'daily') {
          console.log('Обнаружен диплинк на вопрос дня')
          // Сохраняем намерение перехода на вопросы после загрузки
          setNavigateToQuestion(true)
        }

        // Проверяем диплинк на страницу настроения
        const directMoodParam = urlParams.get('mood')
        const startAppMoodParam = startParam === 'mood' ? 'mood' : null
        const moodParam = directMoodParam || startAppMoodParam
        
        if (moodParam === 'mood') {
          console.log('Обнаружен диплинк на настроение')
          // Сохраняем намерение перехода на настроение после загрузки
          setNavigateToMood(true)
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
              const response = await fetch(getApiUrl(`/v1/invitations/${inviteCode}/use?invitee_telegram_id=${telegramId}`), {
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
          <h1>Пульс ваших отношений</h1>
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
      <AppContent 
        user={registeredUser} 
        isFullscreen={isFullscreen}
        navigateToQuestion={navigateToQuestion}
        setNavigateToQuestion={setNavigateToQuestion}
        navigateToMood={navigateToMood}
        setNavigateToMood={setNavigateToMood}
      />
    </Router>
  )
}

// Компонент содержимого приложения с доступом к навигации
interface AppContentProps {
  user: any
  isFullscreen: boolean
  navigateToQuestion: boolean
  setNavigateToQuestion: (value: boolean) => void
  navigateToMood: boolean
  setNavigateToMood: (value: boolean) => void
}

function AppContent({ user, isFullscreen, navigateToQuestion, setNavigateToQuestion, navigateToMood, setNavigateToMood }: AppContentProps) {
  const navigate = useNavigate()

  useEffect(() => {
    if (navigateToQuestion) {
      console.log('Переходим на страницу вопросов по диплинку')
      navigate('/pulse_of_pair/question')
      setNavigateToQuestion(false) // Сбрасываем флаг
    }
  }, [navigateToQuestion, navigate, setNavigateToQuestion])

  useEffect(() => {
    if (navigateToMood) {
      console.log('Переходим на страницу настроения по диплинку')
      navigate('/pulse_of_pair/mood')
      setNavigateToMood(false) // Сбрасываем флаг
    }
  }, [navigateToMood, navigate, setNavigateToMood])

  return (
    <div className={`tg-app ${isFullscreen ? 'fullscreen' : 'embedded'}`}>
      <Routes>
        <Route path="/pulse_of_pair/" element={<Home user={user} />} />
        <Route path="/pulse_of_pair/question" element={<DailyQuestion />} />
        <Route path="/pulse_of_pair/mood" element={<Mood />} />
        <Route path="/pulse_of_pair/settings" element={<Settings user={user} />} />
        <Route path="*" element={<Navigate to="/pulse_of_pair/" replace />} />
      </Routes>
      <Navigation />
    </div>
  )
}

export default App
