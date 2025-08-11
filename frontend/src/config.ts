// Конфигурация API
export const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || '/pulse_of_pair/api'

// Полный URL для API запросов
export const getApiUrl = (endpoint: string) => {
  // Если VITE_API_BASE_URL начинается с http, используем его как есть
  if ((import.meta as any).env?.VITE_API_BASE_URL?.startsWith('http')) {
    return `${(import.meta as any).env.VITE_API_BASE_URL}${endpoint}`
  }
  // Иначе используем относительный путь
  return `${API_BASE_URL}${endpoint}`
}
