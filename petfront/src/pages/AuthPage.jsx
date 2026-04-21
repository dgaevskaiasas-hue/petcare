// src/pages/AuthPage.jsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../store/auth'
import { errMsg } from '../api/client'
import { ErrorMsg } from '../components/Layout'

export default function AuthPage() {
  const [mode, setMode]     = useState('login')   // 'login' | 'register'
  const [email, setEmail]   = useState('')
  const [pass, setPass]     = useState('')
  const [name, setName]     = useState('')
  const [error, setError]   = useState('')
  const [loading, setLoad]  = useState(false)

  const { login, register } = useAuth()
  const navigate = useNavigate()

  const submit = async e => {
    e.preventDefault()
    setError('')
    setLoad(true)
    try {
      if (mode === 'login') await login(email, pass)
      else await register(email, pass, name)
      navigate('/pets')
    } catch (err) {
      setError(errMsg(err))
    } finally {
      setLoad(false)
    }
  }

  const toggle = () => { setMode(m => m === 'login' ? 'register' : 'login'); setError('') }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>

      {/* ── Левая панель ── */}
      <div style={{
        width: '42%', background: 'var(--green)',
        display: 'flex', flexDirection: 'column',
        justifyContent: 'flex-end', padding: '48px 44px',
        backgroundImage: 'radial-gradient(ellipse at 20% 50%, #40916C 0%, transparent 60%)',
        flexShrink: 0,
      }}>
        <div style={{ color: '#fff' }}>
          <div style={{ fontSize: 52, marginBottom: 14 }}>🐾</div>
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontStyle: 'italic', fontWeight: 400,
            fontSize: 40, lineHeight: 1.15, marginBottom: 14,
          }}>Pet<br/>Community</h1>
          <p style={{ fontSize: 15, opacity: .75, lineHeight: 1.7, marginBottom: 36, maxWidth: 280 }}>
            Медкарты питомцев, AI-советы и тёплое сообщество таких же любящих владельцев
          </p>

          {[
            ['📋', 'Медкарта и история визитов'],
            ['🤖', 'AI-ассистент с контекстом питомца'],
            ['💬', 'Форум владельцев'],
            ['📄', 'Экспорт медкарты в PDF'],
          ].map(([ic, txt]) => (
            <div key={txt} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              fontSize: 14, opacity: .85, marginBottom: 12,
            }}>
              <div style={{
                width: 28, height: 28,
                background: 'rgba(255,255,255,.15)',
                borderRadius: 8, display: 'flex',
                alignItems: 'center', justifyContent: 'center',
                fontSize: 14, flexShrink: 0,
              }}>{ic}</div>
              {txt}
            </div>
          ))}
        </div>
      </div>

      {/* ── Правая панель ── */}
      <div style={{
        flex: 1, display: 'flex', alignItems: 'center',
        justifyContent: 'center', padding: 48,
        background: 'var(--cream)',
      }}>
        <div style={{ width: '100%', maxWidth: 360 }} className="fade-up">
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontStyle: 'italic', fontWeight: 400,
            fontSize: 30, marginBottom: 6,
          }}>
            {mode === 'login' ? 'Добро пожаловать' : 'Создать аккаунт'}
          </h2>
          <p style={{ color: 'var(--text2)', fontSize: 14, marginBottom: 32 }}>
            {mode === 'login' ? 'Войдите в свой аккаунт' : 'Зарегистрируйтесь бесплатно'}
          </p>

          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {mode === 'register' && (
              <div>
                <label className="label">Имя пользователя</label>
                <input className="input" placeholder="petlover42"
                  value={name} onChange={e => setName(e.target.value)}
                  required minLength={3} pattern="[a-zA-Z0-9_]+"
                  title="Только буквы, цифры и _"
                />
              </div>
            )}

            <div>
              <label className="label">Email</label>
              <input className="input" type="email" placeholder="you@example.com"
                value={email} onChange={e => setEmail(e.target.value)} required />
            </div>

            <div>
              <label className="label">Пароль</label>
              <input className="input" type="password" placeholder="Минимум 8 символов"
                value={pass} onChange={e => setPass(e.target.value)} required minLength={8} />
            </div>

            <ErrorMsg msg={error} />

            <button className="btn btn-primary" type="submit" disabled={loading}
              style={{ width: '100%', justifyContent: 'center', padding: 13, marginTop: 4, fontSize: 15 }}>
              {loading
                ? <span className="spinner" style={{ width: 18, height: 18 }} />
                : mode === 'login' ? 'Войти →' : 'Зарегистрироваться →'
              }
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: 24, fontSize: 14, color: 'var(--text2)' }}>
            {mode === 'login' ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}{' '}
            <button onClick={toggle} style={{
              color: 'var(--green)', fontWeight: 700, fontSize: 14,
            }}>
              {mode === 'login' ? 'Зарегистрироваться' : 'Войти'}
            </button>
          </p>
        </div>
      </div>
    </div>
  )
}
