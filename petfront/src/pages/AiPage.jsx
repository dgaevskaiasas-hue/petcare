// src/pages/AiPage.jsx
import { useEffect, useRef, useState } from 'react'
import { aiApi, petsApi } from '../api'
import Layout, { PageHeader, Spinner, Avatar } from '../components/Layout'
import { format } from 'date-fns'

export default function AiPage() {
  const [pets, setPets]       = useState([])
  const [petId, setPetId]     = useState(null)
  const [messages, setMessages] = useState([])
  const [hints, setHints]     = useState([])
  const [input, setInput]     = useState('')
  const [loading, setLoading] = useState(false)
  const [histLoading, setHistLoading] = useState(true)
  const bottomRef = useRef(null)

  // Загружаем питомцев
  useEffect(() => {
    petsApi.list().then(r => {
      setPets(r.data)
      if (r.data.length) setPetId(r.data[0].id)
    })
  }, [])

  // Загружаем историю + подсказки при смене питомца
  useEffect(() => {
    setHistLoading(true)
    const species = pets.find(p => p.id === petId)?.species
    Promise.all([
      aiApi.history(petId, 50),
      aiApi.hints(species ?? null),
    ]).then(([h, hn]) => {
      setMessages(h.data)
      setHints(hn.data)
    }).finally(() => setHistLoading(false))
  }, [petId])

  // Скролл вниз при новых сообщениях
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (text) => {
    const msg = text ?? input.trim()
    if (!msg || loading) return
    setInput('')
    setLoading(true)

    // Оптимистично добавляем сообщение пользователя
    const optimistic = { id: Date.now(), role: 'user', content: msg, created_at: new Date().toISOString() }
    setMessages(m => [...m, optimistic])

    try {
      const r = await aiApi.send(msg, petId)
      setMessages(m => [...m, r.data])
    } catch {
      setMessages(m => [...m, {
        id: Date.now() + 1, role: 'assistant',
        content: 'Произошла ошибка. Попробуйте ещё раз.',
        created_at: new Date().toISOString(),
      }])
    } finally { setLoading(false) }
  }

  const currentPet = pets.find(p => p.id === petId)

  return (
    <Layout>
      <PageHeader title="AI-ассистент" sub="Задайте любой вопрос о питомце" />

      {/* Выбор питомца */}
      {pets.length > 0 && (
        <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
          <button
            className={`btn btn-sm ${!petId ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setPetId(null)}
          >Без контекста</button>
          {pets.map(p => (
            <button key={p.id}
              className={`btn btn-sm ${petId === p.id ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setPetId(p.id)}
            >
              {{ cat:'🐱',dog:'🐶',bird:'🐦',rabbit:'🐰',other:'🐾' }[p.species]} {p.name}
            </button>
          ))}
        </div>
      )}

      {/* Чат */}
      <div className="card" style={{ display: 'flex', flexDirection: 'column', height: 540 }}>
        {/* Бар контекста */}
        {currentPet && (
          <div style={{
            padding: '10px 20px', background: 'var(--green-ll)',
            borderBottom: '1.5px solid var(--green-l)',
            fontSize: 13, fontWeight: 700, color: 'var(--green)',
            borderRadius: 'var(--r) var(--r) 0 0',
            display: 'flex', alignItems: 'center', gap: 8,
          }}>
            <span style={{ width: 8, height: 8, background: 'var(--green)', borderRadius: '50%', display: 'inline-block' }} />
            Контекст: {currentPet.name}
            <span style={{ fontWeight: 400, color: 'var(--green-m)', fontSize: 12 }}>
              · {currentPet.species}{currentPet.breed ? `, ${currentPet.breed}` : ''}
              {currentPet.is_neutered ? ', стерилизован(а)' : ''}
            </span>
          </div>
        )}

        {/* Сообщения */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 20px 0' }}>
          {histLoading ? <Spinner /> : (
            <>
              {messages.length === 0 && (
                <div style={{ textAlign: 'center', paddingTop: 40 }}>
                  <div style={{ fontSize: 40, opacity: .3, marginBottom: 12 }}>🤖</div>
                  <p style={{ color: 'var(--text2)', fontSize: 15, marginBottom: 20 }}>
                    Спросите что угодно о вашем питомце
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                    {hints.map(h => (
                      <button key={h} onClick={() => send(h)} style={{
                        padding: '8px 14px', border: '1.5px solid var(--border)',
                        borderRadius: 'var(--r3)', fontSize: 13, background: 'var(--card)',
                        cursor: 'pointer', transition: 'border-color .15s',
                      }}
                        onMouseEnter={e => e.target.style.borderColor = 'var(--green)'}
                        onMouseLeave={e => e.target.style.borderColor = 'var(--border)'}
                      >{h}</button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map(m => <ChatBubble key={m.id} msg={m} />)}

              {loading && (
                <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 16 }}>
                  <AiIcon />
                  <div style={{ background: 'var(--warm)', borderRadius: '3px 14px 14px 14px', padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: 4 }}>
                      {[0,1,2].map(i => (
                        <div key={i} style={{
                          width: 6, height: 6, borderRadius: '50%', background: 'var(--text3)',
                          animation: 'pulse 1.2s ease infinite',
                          animationDelay: `${i * 0.2}s`,
                        }} />
                      ))}
                    </div>
                  </div>
                </div>
              )}

              <div ref={bottomRef} />
            </>
          )}
        </div>

        {/* Подсказки (если есть история) */}
        {messages.length > 0 && hints.length > 0 && (
          <div style={{ padding: '10px 20px 0', display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {hints.slice(0, 3).map(h => (
              <button key={h} onClick={() => send(h)} style={{
                padding: '5px 12px', border: '1.5px solid var(--border)',
                borderRadius: 'var(--r3)', fontSize: 12, background: 'var(--card)', cursor: 'pointer',
              }}>{h}</button>
            ))}
          </div>
        )}

        {/* Поле ввода */}
        <div style={{ padding: '14px 20px', borderTop: '1.5px solid var(--border2)', display: 'flex', gap: 10 }}>
          <input
            className="input"
            placeholder={currentPet ? `Спросите о ${currentPet.name}...` : 'Спросите о питомце...'}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
            disabled={loading}
            style={{ flex: 1 }}
          />
          <button className="btn btn-primary" onClick={() => send()} disabled={loading || !input.trim()}>
            Отправить
          </button>
        </div>
      </div>

      <style>{`
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
      `}</style>
    </Layout>
  )
}

function AiIcon() {
  return (
    <div style={{
      width: 32, height: 32, background: 'var(--green)',
      borderRadius: 9, display: 'flex', alignItems: 'center',
      justifyContent: 'center', fontSize: 15, color: '#fff', flexShrink: 0,
    }}>🤖</div>
  )
}

function ChatBubble({ msg }) {
  const isUser = msg.role === 'user'
  return (
    <div style={{
      display: 'flex', gap: 10, marginBottom: 16,
      flexDirection: isUser ? 'row-reverse' : 'row',
      alignItems: 'flex-start',
    }}>
      {isUser
        ? <div className="avatar" style={{ width: 32, height: 32, fontSize: 12, background: 'var(--green-l)', color: 'var(--green)', flexShrink: 0 }}>Я</div>
        : <AiIcon />
      }
      <div style={{
        maxWidth: '72%',
        padding: '12px 16px',
        borderRadius: isUser ? '14px 3px 14px 14px' : '3px 14px 14px 14px',
        background: isUser ? 'var(--green)' : 'var(--warm)',
        color: isUser ? '#fff' : 'var(--text)',
        fontSize: 14, lineHeight: 1.65, whiteSpace: 'pre-wrap',
      }}>
        {msg.content}
      </div>
    </div>
  )
}
