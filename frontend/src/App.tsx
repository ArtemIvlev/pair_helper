import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Компоненты
import Home from './components/Home'
import DailyQuestion from './components/DailyQuestion'
import Mood from './components/Mood'
import Appreciation from './components/Appreciation'
import Calendar from './components/Calendar'
import Rituals from './components/Rituals'
import Stats from './components/Stats'
import Settings from './components/Settings'
import Navigation from './components/Navigation'

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
        ready: () => void
        expand: () => void
        close: () => void
      }
    }
  }
}

function App() {
  const [isTelegramWebApp, setIsTelegramWebApp] = useState(false)
  const [user, setUser] = useState<any>(null)

  useEffect(() => {
    // Проверяем, запущено ли приложение в Telegram
    if (window.Telegram?.WebApp) {
      setIsTelegramWebApp(true)
      window.Telegram.WebApp.ready()
      window.Telegram.WebApp.expand()
      
      // Получаем данные пользователя
      if (window.Telegram.WebApp.initDataUnsafe.user) {
        setUser(window.Telegram.WebApp.initDataUnsafe.user)
      }
    }
  }, [])

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

  return (
    <Router>
      <div className="tg-app">
        <Routes>
          <Route path="/" element={<Home user={user} />} />
          <Route path="/question" element={<DailyQuestion />} />
          <Route path="/mood" element={<Mood />} />
          <Route path="/appreciation" element={<Appreciation />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/rituals" element={<Rituals />} />
          <Route path="/stats" element={<Stats />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
        <Navigation />
      </div>
    </Router>
  )
}

export default App
