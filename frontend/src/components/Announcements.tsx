import React, { useState, useEffect } from 'react';
import { getApiUrl } from '../config';

interface Announcement {
  id: number;
  title: string;
  content: string;
  priority: string;
  target_audience: string;
  is_active: boolean;
  created_at: string;
  published_at?: string;
}

const Announcements: React.FC = () => {
  const [announcements, setAnnouncements] = useState<Announcement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAnnouncements, setShowAnnouncements] = useState(false);

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      setLoading(true);
      const initData = (window as any).Telegram?.WebApp?.initData;
      if (!initData) {
        // Вне Telegram WebApp просто не показываем обращения
        setAnnouncements([]);
        setLoading(false);
        return;
      }

      const response = await fetch(getApiUrl('/v1/announcements/'), {
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Ошибка при загрузке обращений');
      }

      const data = await response.json();
      setAnnouncements(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'normal':
        return 'bg-blue-500';
      case 'low':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getPriorityText = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'Срочно';
      case 'high':
        return 'Важно';
      case 'normal':
        return 'Обычно';
      case 'low':
        return 'Информация';
      default:
        return 'Обычно';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-4">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return null;
  }

  if (announcements.length === 0) {
    return null; // Не показываем компонент, если обращений нет
  }

  return (
    <div className="mb-6">
      {announcements.length > 0 && (
        <div className="card fade-in" style={{ 
          textAlign: 'center', 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
          color: 'white',
          position: 'relative',
          overflow: 'hidden'
        }}>
          {/* Показываем самое важное обращение */}
          {announcements.slice(0, 1).map((announcement) => (
            <div key={announcement.id}>
              <div style={{ 
                position: 'absolute', 
                top: '8px', 
                right: '8px',
                background: 'rgba(255,255,255,0.2)',
                borderRadius: '50%',
                width: '24px',
                height: '24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '12px'
              }}>
                📢
              </div>
              
              <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: '600' }}>
                {announcement.title}
              </h3>
              
              <div 
                style={{ 
                  margin: 0, 
                  fontSize: '14px', 
                  lineHeight: '1.4',
                  opacity: 0.9
                }}
                dangerouslySetInnerHTML={{ 
                  __html: announcement.content
                }}
              />
              
              {/* Кнопка для показа всех обращений */}
              {announcements.length > 1 && (
                <button
                  onClick={() => setShowAnnouncements(!showAnnouncements)}
                  style={{
                    marginTop: '12px',
                    background: 'rgba(255,255,255,0.2)',
                    border: '1px solid rgba(255,255,255,0.3)',
                    color: 'white',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '12px',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.3)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
                  }}
                >
                  Показать все ({announcements.length})
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Список всех обращений (скрытый по умолчанию) */}
      {showAnnouncements && announcements.length > 1 && (
        <div className="space-y-4" style={{ marginTop: '16px' }}>
          {announcements.slice(1).map((announcement) => (
            <div
              key={announcement.id}
              style={{
                borderLeft: `4px solid ${getPriorityColor(announcement.priority) === 'bg-red-500' ? '#ef4444' : 
                                   getPriorityColor(announcement.priority) === 'bg-orange-500' ? '#f97316' :
                                   getPriorityColor(announcement.priority) === 'bg-blue-500' ? '#3b82f6' : '#6b7280'}`,
                background: 'var(--tg-theme-bg-color)',
                borderRadius: '8px',
                padding: '16px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'start', justifyContent: 'space-between', marginBottom: '8px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{
                    padding: '4px 8px',
                    fontSize: '10px',
                    fontWeight: '500',
                    color: 'white',
                    borderRadius: '4px',
                    background: getPriorityColor(announcement.priority) === 'bg-red-500' ? '#ef4444' : 
                               getPriorityColor(announcement.priority) === 'bg-orange-500' ? '#f97316' :
                               getPriorityColor(announcement.priority) === 'bg-blue-500' ? '#3b82f6' : '#6b7280'
                  }}>
                    {getPriorityText(announcement.priority)}
                  </span>
                  <span style={{ fontSize: '12px', color: 'var(--tg-theme-hint-color)' }}>
                    {formatDate(announcement.created_at)}
                  </span>
                </div>
              </div>
              
              <h3 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px', color: 'var(--tg-theme-text-color)' }}>
                {announcement.title}
              </h3>
              
              <div 
                style={{ 
                  color: 'var(--tg-theme-text-color)',
                  fontSize: '14px',
                  lineHeight: '1.4'
                }}
                dangerouslySetInnerHTML={{ __html: announcement.content }}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Announcements;
