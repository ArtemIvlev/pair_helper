import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { 
  Home, 
  MessageCircle, 
  Heart, 
  Calendar, 
  Target, 
  BarChart3, 
  Settings 
} from 'lucide-react'

const Navigation: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()

  const navItems = [
    { path: '/', icon: Home, label: 'Главная' },
    { path: '/question', icon: MessageCircle, label: 'Вопрос' },
    { path: '/mood', icon: Heart, label: 'Настроение' },
    { path: '/appreciation', icon: Heart, label: 'Признание' },
    { path: '/calendar', icon: Calendar, label: 'Календарь' },
    { path: '/rituals', icon: Target, label: 'Ритуалы' },
    { path: '/stats', icon: BarChart3, label: 'Статистика' },
    { path: '/settings', icon: Settings, label: 'Настройки' },
  ]

  return (
    <nav className="nav">
      {navItems.map((item) => {
        const Icon = item.icon
        const isActive = location.pathname === item.path
        
        return (
          <div
            key={item.path}
            className={`nav-item ${isActive ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
          >
            <Icon className="nav-icon" />
            <span className="nav-text">{item.label}</span>
          </div>
        )
      })}
    </nav>
  )
}

export default Navigation
