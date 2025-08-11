import React, { useEffect, useState } from 'react'
import { getApiUrl } from '../config'

interface TuneQuestion {
  id: number
  number: number
  text: string | null
  category: string
  question_type: 'mcq' | 'text'
  option1?: string | null
  option2?: string | null
  option3?: string | null
  option4?: string | null
  text_about_partner?: string | null
  text_about_self?: string | null
}



interface TuneAnswersStatus {
  about_me?: number | null
  about_partner?: number | null
}

interface TunePartnerAnswersStatus {
  about_himself?: number | null
  about_me?: number | null
}

interface TuneAnswersResponse {
  question: TuneQuestion
  partner_name: string
  me?: TuneAnswersStatus | null
  partner?: TunePartnerAnswersStatus | null
}



const Tune: React.FC = () => {
  const [loading, setLoading] = useState(true)
  const [question, setQuestion] = useState<TuneQuestion | null>(null)
  const [error, setError] = useState('')
  const [selectedMe, setSelectedMe] = useState<number | null>(null)
  const [selectedPartner, setSelectedPartner] = useState<number | null>(null)
  const [submittingMe, setSubmittingMe] = useState(false)
  const [submittingPartner, setSubmittingPartner] = useState(false)
  const [answersData, setAnswersData] = useState<TuneAnswersResponse | null>(null)
  const [notifying, setNotifying] = useState(false)
  const [notifySuccess, setNotifySuccess] = useState('')

  const loadCurrent = async () => {
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) {
        setError('Ошибка аутентификации')
        setLoading(false)
        return
      }
      const resp = await fetch(getApiUrl('/v1/tune/current'), {
        headers: { 'X-Telegram-Init-Data': initData }
      })
      if (resp.ok) {
        const q = await resp.json()
        setQuestion(q)
        if (q) await loadAnswers(q.id)
      } else if (resp.status === 204) {
        setQuestion(null)
      } else {
        const txt = await resp.text()
        setError(`Ошибка загрузки (${resp.status}) ${txt}`)
      }
    } catch {
      setError('Ошибка соединения с сервером')
    } finally {
      setLoading(false)
    }
  }

  const loadAnswers = async (qid: number) => {
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) return
      const resp = await fetch(getApiUrl(`/v1/tune/answers/${qid}`), {
        headers: { 'X-Telegram-Init-Data': initData }
      })
      if (resp.ok) {
        const data = await resp.json()
        setAnswersData(data)

      }
    } catch {}
  }

  const submit = async (about: 'me' | 'partner') => {
    if (!question) return
    const selected = about === 'me' ? selectedMe : selectedPartner
    if (selected === null || selected === undefined) return
    about === 'me' ? setSubmittingMe(true) : setSubmittingPartner(true)
    setError('')
    try {
      const initData = (window as any).Telegram?.WebApp?.initData
      const resp = await fetch(getApiUrl('/v1/tune/answer'), {
        method: 'POST',
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question_id: question.id, about, selected_option: selected })
      })
      if (resp.ok) {
        await loadCurrent()
        if (about === 'me') setSelectedMe(null)
        else setSelectedPartner(null)
      } else {
        const data = await resp.json().catch(() => ({}))
        setError(data.detail || 'Не удалось отправить ответ')
      }
    } catch {
      setError('Ошибка соединения')
    } finally {
      about === 'me' ? setSubmittingMe(false) : setSubmittingPartner(false)
    }
  }

  const notifyPartner = async () => {
    try {
      setNotifySuccess('')
      setError('')
      setNotifying(true)
      const initData = (window as any).Telegram?.WebApp?.initData
      if (!initData) {
        setError('Ошибка аутентификации')
        return
      }
      const resp = await fetch(getApiUrl('/v1/tune/notify_partner'), {
        method: 'POST',
        headers: {
          'X-Telegram-Init-Data': initData,
          'Content-Type': 'application/json'
        }
      })
      if (resp.ok) {
        const data = await resp.json()
        setNotifySuccess(data.message || 'Уведомление отправлено')
      } else {
        const err = await resp.json().catch(() => ({}))
        setError(err.detail || 'Не удалось отправить уведомление')
      }
    } catch (e) {
      setError('Ошибка соединения при отправке уведомления')
    } finally {
      setNotifying(false)
    }
  }

  const submitBoth = async () => {
    if (!question) return
    const operations: ('me' | 'partner')[] = []
    if ((answersData?.me?.about_me === null || answersData?.me?.about_me === undefined) && selectedMe !== null) operations.push('me')
    if ((answersData?.me?.about_partner === null || answersData?.me?.about_partner === undefined) && selectedPartner !== null) operations.push('partner')
    if (operations.length === 0) return
    for (const op of operations) {
      // последовательная отправка, чтобы не возникали коллизии
      await submit(op)
    }
  }

  useEffect(() => {
    loadCurrent()
  }, [])

  if (loading) {
    return (
      <div className="main-content"><div className="container"><div className="loading">Загрузка...</div></div></div>
    )
  }

  return (
    <div className="main-content">
      <div className="container">
        <div className="header">
          <h1>Сонастройка</h1>
          <p>Ответьте на вопрос о себе и о партнере</p>
        </div>
        {error && (
          <div style={{ color: 'var(--tg-theme-destructive-text-color)', marginBottom: 12 }}>{error}</div>
        )}
        {!question ? (
          <div className="card card-elevated"><div style={{ padding: 16, textAlign: 'center' }}>На сегодня вопросов нет</div></div>
        ) : (
          <div className="card card-elevated">
            <div style={{ marginBottom: 16 }}>
              <div className="badge" style={{ background: 'var(--tg-theme-secondary-bg-color)' }}>{question.category}</div>
            </div>
            <div style={{ display: 'grid', gap: 16 }}>
              {(() => {
                // Проверяем совпадения для раскрашивания блоков
                let matchAboutMe = false
                let matchAboutPartner = false
                
                                if (answersData?.me && answersData?.partner) {
                  matchAboutMe = answersData.me.about_me === answersData.partner.about_me
                  matchAboutPartner = answersData.me.about_partner === answersData.partner.about_himself
                }
                
                return (
                  <>
                    <div style={{
                      padding: 16,
                      borderRadius: 8,
                      backgroundColor: matchAboutMe ? 'rgba(0, 200, 83, 0.1)' : undefined,
                      border: matchAboutMe ? '2px solid rgba(0, 200, 83, 0.5)' : undefined
                    }}>
                      <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
                        {question.text_about_self || question.text}
                      </div>
                      <div>
                        <div className="mood-grid">
                          {[question.option1, question.option2, question.option3, question.option4]
                            .map((opt, idx) => {
                                                                              // Для первого вопроса (про себя): мой ответ о себе vs партнёр о мне
                        const isMyAnswer = answersData?.me?.about_me === idx
                        const isPartnerAnswer = answersData?.me && answersData?.partner ? answersData.partner.about_me === idx : false
                        const isMatch = isMyAnswer && isPartnerAnswer
                              
                              return (
                                                        <div
                          key={idx}
                          className={`mood-item ${selectedMe === idx ? 'selected' : ''} ${answersData?.me?.about_me !== null && answersData?.me?.about_me !== undefined ? 'disabled' : ''}`}
                          onClick={() => (answersData?.me?.about_me === null || answersData?.me?.about_me === undefined) && setSelectedMe(idx)}
                                  style={{
                                    backgroundColor: isMatch ? 'rgba(0, 200, 83, 0.3)' : 
                                                    isMyAnswer ? 'rgba(0, 122, 255, 0.3)' : 
                                                    isPartnerAnswer ? 'rgba(255, 149, 0, 0.3)' : undefined,
                                    borderColor: isMatch ? 'rgba(0, 200, 83, 1)' : 
                                               isMyAnswer ? 'rgba(0, 122, 255, 1)' : 
                                               isPartnerAnswer ? 'rgba(255, 149, 0, 1)' : undefined,
                                    borderWidth: (isMatch || isMyAnswer || isPartnerAnswer) ? '3px' : undefined,
                                    borderStyle: (isMatch || isMyAnswer || isPartnerAnswer) ? 'solid' : undefined
                                  }}
                                >
                                  <div className="mood-text">{opt}</div>
                                  {(isMyAnswer || isPartnerAnswer) && (
                                    <div style={{ fontSize: 10, marginTop: 4 }}>
                                      {isMatch && '✅'}
                                      {isMyAnswer && !isPartnerAnswer && '👤'}
                                      {isPartnerAnswer && !isMyAnswer && '💬'}
                                    </div>
                                  )}
                                </div>
                              )
                            })}
                        </div>
                      </div>
                    </div>
                    <div style={{
                      padding: 16,
                      borderRadius: 8,
                      backgroundColor: matchAboutPartner ? 'rgba(0, 200, 83, 0.1)' : undefined,
                      border: matchAboutPartner ? '2px solid rgba(0, 200, 83, 0.5)' : undefined
                    }}>
                      <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>
                        {question.text_about_partner || question.text}
                      </div>
                      <div>
                        <div className="mood-grid">
                          {[question.option1, question.option2, question.option3, question.option4]
                            .map((opt, idx) => {
                              // Для второго вопроса (про партнёра): мой ответ о партнёре vs партнёр о себе
                              const isMyAnswer = answersData?.me?.about_partner === idx
                              const isPartnerAnswer = answersData?.me && answersData?.partner ? answersData.partner.about_himself === idx : false
                              const isMatch = isMyAnswer && isPartnerAnswer
                              
                              return (
                                                        <div
                          key={idx}
                          className={`mood-item ${selectedPartner === idx ? 'selected' : ''} ${answersData?.me?.about_partner !== null && answersData?.me?.about_partner !== undefined ? 'disabled' : ''}`}
                          onClick={() => (answersData?.me?.about_partner === null || answersData?.me?.about_partner === undefined) && setSelectedPartner(idx)}
                                  style={{
                                    backgroundColor: isMatch ? 'rgba(0, 200, 83, 0.3)' : 
                                                    isMyAnswer ? 'rgba(0, 122, 255, 0.3)' : 
                                                    isPartnerAnswer ? 'rgba(255, 149, 0, 0.3)' : undefined,
                                    borderColor: isMatch ? 'rgba(0, 200, 83, 1)' : 
                                               isMyAnswer ? 'rgba(0, 122, 255, 1)' : 
                                               isPartnerAnswer ? 'rgba(255, 149, 0, 1)' : undefined,
                                    borderWidth: (isMatch || isMyAnswer || isPartnerAnswer) ? '3px' : undefined,
                                    borderStyle: (isMatch || isMyAnswer || isPartnerAnswer) ? 'solid' : undefined
                                  }}
                                >
                                  <div className="mood-text">{opt}</div>
                                  {(isMyAnswer || isPartnerAnswer) && (
                                    <div style={{ fontSize: 10, marginTop: 4 }}>
                                      {isMatch && '✅'}
                                      {isMyAnswer && !isPartnerAnswer && '👤'}
                                      {isPartnerAnswer && !isMyAnswer && '💬'}
                                    </div>
                                  )}
                                </div>
                              )
                            })}
                        </div>
                      </div>
                    </div>
                  </>
                )
              })()}
            </div>

                                                {/* Кнопка для одной отправки обоих ответов - показываем только если есть что отправлять */}
                        {(answersData?.me?.about_me === null || answersData?.me?.about_me === undefined || answersData?.me?.about_partner === null || answersData?.me?.about_partner === undefined) && (
                          <div style={{ marginTop: 16 }}>
                            {(() => {
                              const needMe = answersData?.me?.about_me === null || answersData?.me?.about_me === undefined
                              const needPartner = answersData?.me?.about_partner === null || answersData?.me?.about_partner === undefined
                              const canSubmit = (needMe ? selectedMe !== null : true) && (needPartner ? selectedPartner !== null : true) && !(submittingMe || submittingPartner)
                  return (
                    <button className="btn btn-primary" disabled={!canSubmit} onClick={submitBoth}>
                      {(submittingMe || submittingPartner) ? 'Отправляем...' : 'Отправить ответы'}
                    </button>
                  )
                })()}
              </div>
            )}

            {/* Показываем ответы прямо в вопросах когда все ответы даны */}

            {/* Кнопка уведомить партнера - показываем только если я ответил, а партнер нет */}
            {answersData?.me?.about_me !== null && answersData?.me?.about_me !== undefined && 
             answersData?.me?.about_partner !== null && answersData?.me?.about_partner !== undefined && 
             (!answersData?.partner || 
              answersData?.partner?.about_himself === null || answersData?.partner?.about_himself === undefined ||
              answersData?.partner?.about_me === null || answersData?.partner?.about_me === undefined) && (
              <div style={{ marginTop: 16, textAlign: 'center' }}>
                <button 
                  onClick={notifyPartner}
                  className="btn btn-primary"
                  disabled={notifying}
                >
                  {notifying ? 'Отправляем...' : 'Напомнить партнёру ответить'}
                </button>
                {notifySuccess && (
                  <div style={{ marginTop: 8, color: 'var(--tg-theme-accent-text-color)' }}>{notifySuccess}</div>
                )}
              </div>
            )}

          </div>
        )}
      </div>
    </div>
  )
}

export default Tune


