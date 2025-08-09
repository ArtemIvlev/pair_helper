import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { 
  Home, 
  MessageCircle, 
  Heart, 
  Settings 
} from 'lucide-react'

const Navigation: React.FC = () => {
  const location = useLocation()
  const navigate = useNavigate()

  const navItems = [
    { path: '/pulse_of_pair/', icon: Home, label: 'Главная' },
    { path: '/pulse_of_pair/question', icon: MessageCircle, label: 'Вопрос' },
    { path: '/pulse_of_pair/mood', icon: Heart, label: 'Настроение' },
    { path: '/pulse_of_pair/settings', icon: Settings, label: 'Настройки' },
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
