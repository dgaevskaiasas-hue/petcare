// src/components/Layout.jsx
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../store/auth'

const NAV = [
  { to: '/pets',  icon: '🐾', label: 'Питомцы'     },
  { to: '/ai',    icon: '🤖', label: 'AI-ассистент' },
  { to: '/forum', icon: '💬', label: 'Форум'        },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate  = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* ── Sidebar ── */}
      <aside style={{
        width: 210, flexShrink: 0,
        background: 'var(--card)',
        borderRight: '1.5px solid var(--border2)',
        display: 'flex', flexDirection: 'column',
        padding: '22px 12px',
        position: 'sticky', top: 0, height: '100vh',
      }}>
        {/* Logo */}
        <Link to="/pets" style={{
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '6px 10px', marginBottom: 24, textDecoration: 'none',
        }}>
          <div style={{
            width: 34, height: 34, background: 'var(--green)',
            borderRadius: 10, display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: 17, flexShrink: 0,
          }}>🐾</div>
          <span style={{
            fontFamily: 'var(--font-display)',
            fontStyle: 'italic', fontSize: 16,
            color: 'var(--text)',
          }}>PetCommunity</span>
        </Link>

        {/* Nav */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: 3, flex: 1 }}>
          {NAV.map(({ to, icon, label }) => {
            const active = location.pathname.startsWith(to)
            return (
              <Link key={to} to={to} style={{
                display: 'flex', alignItems: 'center', gap: 10,
                padding: '10px 12px', borderRadius: 'var(--r2)',
                background: active ? 'var(--green-ll)' : 'transparent',
                color: active ? 'var(--green)' : 'var(--text2)',
                fontWeight: active ? 700 : 600,
                fontSize: 14, transition: 'all .15s', textDecoration: 'none',
              }}>
                <span style={{ fontSize: 17, width: 22, textAlign: 'center' }}>{icon}</span>
                {label}
              </Link>
            )
          })}
        </nav>

        {/* User */}
        {user && (
          <div style={{
            borderTop: '1.5px solid var(--border2)',
            paddingTop: 16,
          }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 9,
              padding: '6px 10px', marginBottom: 8,
            }}>
              <Avatar name={user.username} size={32} />
              <div>
                <div style={{ fontSize: 13, fontWeight: 700 }}>{user.username}</div>
                <div style={{ fontSize: 11, color: 'var(--text3)' }}>{user.role}</div>
              </div>
            </div>
            <button onClick={handleLogout} style={{
              width: '100%', padding: '8px 12px',
              borderRadius: 'var(--r2)', fontSize: 13,
              color: 'var(--text2)', fontWeight: 600,
              transition: 'background .15s',
            }}
              onMouseEnter={e => e.currentTarget.style.background = 'var(--warm)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              Выйти
            </button>
          </div>
        )}
      </aside>

      {/* ── Main content ── */}
      <main style={{ flex: 1, padding: '36px 44px', overflowY: 'auto' }}>
        {children}
      </main>
    </div>
  )
}

// ── Shared UI components ──────────────────────────────────────────────────────

export function Avatar({ name = '?', size = 36, src }) {
  const colors = ['#2D6A4F','#C8553D','#6B5CE7','#E9A84C','#264653']
  let h = 0
  for (const c of String(name)) h = c.charCodeAt(0) + ((h << 5) - h)
  const bg = colors[Math.abs(h) % colors.length]

  if (src) return (
    <img src={src} alt={name}
      style={{ width: size, height: size, borderRadius: '50%', objectFit: 'cover', flexShrink: 0 }}
    />
  )
  return (
    <div className="avatar" style={{
      width: size, height: size,
      fontSize: size * 0.38,
      background: bg + '22',
      color: bg,
    }}>
      {String(name)[0]?.toUpperCase()}
    </div>
  )
}

export function PageHeader({ title, sub, action }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 28 }}>
      <div>
        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontStyle: 'italic', fontWeight: 400,
          fontSize: 32, lineHeight: 1.2, marginBottom: 5,
        }}>{title}</h1>
        {sub && <p style={{ fontSize: 14, color: 'var(--text2)' }}>{sub}</p>}
      </div>
      {action}
    </div>
  )
}

export function Spinner({ size = 24 }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', padding: 40 }}>
      <div className="spinner" style={{ width: size, height: size }} />
    </div>
  )
}

export function Empty({ icon = '🔍', title, sub }) {
  return (
    <div style={{ textAlign: 'center', padding: '60px 20px', color: 'var(--text2)' }}>
      <div style={{ fontSize: 40, marginBottom: 12, opacity: .4 }}>{icon}</div>
      <div style={{ fontWeight: 700, marginBottom: 5 }}>{title}</div>
      {sub && <div style={{ fontSize: 13 }}>{sub}</div>}
    </div>
  )
}

export function ErrorMsg({ msg }) {
  if (!msg) return null
  return (
    <div style={{
      background: 'var(--terra-l)', border: '1.5px solid #F5C4B3',
      borderRadius: 'var(--r2)', padding: '10px 14px',
      fontSize: 13, color: 'var(--terra)', marginTop: 12,
    }}>
      {msg}
    </div>
  )
}
