// src/pages/ForumPage.jsx
import { useEffect, useState } from 'react'
import { forumApi } from '../api'
import Layout, { PageHeader, Spinner, Empty, Avatar, ErrorMsg } from '../components/Layout'
import { formatDistanceToNow } from 'date-fns'
import { ru } from 'date-fns/locale'

const SPECIES_OPTS = [
  { value: '', label: 'Все' },
  { value: 'cat',    label: '🐱 Кошки' },
  { value: 'dog',    label: '🐶 Собаки' },
  { value: 'bird',   label: '🐦 Птицы' },
  { value: 'rabbit', label: '🐰 Кролики' },
]

export default function ForumPage() {
  const [posts, setPosts]     = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch]   = useState('')
  const [species, setSpecies] = useState('')
  const [openPost, setOpenPost] = useState(null)
  const [showCreate, setShowCreate] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const r = await forumApi.list({ search: search || undefined, species: species || undefined })
      setPosts(r.data)
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [species])

  const handleLike = async id => {
    const r = await forumApi.like(id)
    setPosts(ps => ps.map(p => p.id === id
      ? { ...p, like_count: p.like_count + (r.data.liked ? 1 : -1) }
      : p
    ))
  }

  return (
    <Layout>
      <PageHeader
        title="Форум сообщества"
        sub="Делитесь опытом, задавайте вопросы"
        action={
          <button className="btn btn-primary btn-sm" onClick={() => setShowCreate(true)}>
            + Написать пост
          </button>
        }
      />

      {/* Поиск + фильтры */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 20, flexWrap: 'wrap', alignItems: 'center' }}>
        <input
          className="input" placeholder="Поиск... (Enter)"
          value={search} onChange={e => setSearch(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && load()}
          style={{ flex: 1, minWidth: 200, maxWidth: 300 }}
        />
        <div style={{ display: 'flex', gap: 6 }}>
          {SPECIES_OPTS.map(o => (
            <button key={o.value}
              className={`btn btn-sm ${species === o.value ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setSpecies(o.value)}
            >{o.label}</button>
          ))}
        </div>
      </div>

      {/* Список постов */}
      {loading ? <Spinner /> : posts.length === 0
        ? <Empty icon="💬" title="Постов не найдено" sub="Будьте первым — создайте пост!" />
        : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {posts.map(p => (
              <PostCard key={p.id} post={p}
                onOpen={() => setOpenPost(p)}
                onLike={() => handleLike(p.id)}
              />
            ))}
          </div>
        )
      }

      {openPost && (
        <PostModal
          post={openPost}
          onClose={() => setOpenPost(null)}
          onLike={() => handleLike(openPost.id)}
        />
      )}

      {showCreate && (
        <CreateModal
          onClose={() => setShowCreate(false)}
          onCreated={p => { setPosts(ps => [p, ...ps]); setShowCreate(false) }}
        />
      )}
    </Layout>
  )
}

// ── Post card ─────────────────────────────────────────────────────────────────
function PostCard({ post: p, onOpen, onLike }) {
  const specLabel = SPECIES_OPTS.find(o => o.value === p.species_tag)?.label
  return (
    <div className="card" style={{
      padding: '16px 20px', cursor: 'pointer',
      transition: 'transform .15s, border-color .15s',
    }}
      onClick={onOpen}
      onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-1px)'; e.currentTarget.style.borderColor = 'var(--green-l)' }}
      onMouseLeave={e => { e.currentTarget.style.transform = 'none'; e.currentTarget.style.borderColor = 'var(--border2)' }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 9, marginBottom: 10 }}>
        <Avatar name={p.author_name} size={32} />
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 7, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 13, fontWeight: 700 }}>{p.author_name}</span>
            <span style={{ fontSize: 12, color: 'var(--text3)' }}>
              · {formatDistanceToNow(new Date(p.created_at), { locale: ru, addSuffix: true })}
            </span>
            {specLabel && <span className="badge badge-green" style={{ fontSize: 10 }}>{specLabel}</span>}
          </div>
        </div>
      </div>

      <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 7, lineHeight: 1.3 }}>{p.title}</h3>
      <p style={{
        fontSize: 13, color: 'var(--text2)', lineHeight: 1.6, marginBottom: 12,
        display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden',
      }}>{p.body}</p>

      <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <button onClick={e => { e.stopPropagation(); onLike() }} style={{
          display: 'flex', alignItems: 'center', gap: 5,
          fontSize: 13, color: 'var(--text2)', fontWeight: 600,
        }}>♥ {p.like_count}</button>
        <span style={{ fontSize: 13, color: 'var(--text2)' }}>💬 {p.comment_count}</span>
        {p.tags?.filter(Boolean).map(t => (
          <span key={t} className="badge" style={{ background: 'var(--warm)', color: 'var(--text2)', fontSize: 10 }}>#{t}</span>
        ))}
      </div>
    </div>
  )
}

// ── Post modal with comments ──────────────────────────────────────────────────
function PostModal({ post: p, onClose, onLike }) {
  const [comments, setComments] = useState([])
  const [loading, setLoading]   = useState(true)
  const [reply, setReply]       = useState('')
  const [sending, setSending]   = useState(false)

  useEffect(() => {
    forumApi.getComments(p.id)
      .then(r => setComments(r.data))
      .finally(() => setLoading(false))
  }, [p.id])

  const submit = async () => {
    if (!reply.trim()) return
    setSending(true)
    try {
      const r = await forumApi.addComment(p.id, reply)
      setComments(c => [...c, { ...r.data, replies: [], author_name: 'Вы' }])
      setReply('')
    } finally { setSending(false) }
  }

  return (
    <div onClick={e => e.target === e.currentTarget && onClose()} style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,.4)',
      display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
      zIndex: 100, padding: '40px 20px', overflowY: 'auto',
    }}>
      <div className="card fade-up" style={{ width: '100%', maxWidth: 620, padding: 28 }}>
        {/* Header */}
        <div style={{ display: 'flex', gap: 12, marginBottom: 16 }}>
          <Avatar name={p.author_name} size={38} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 13 }}>{p.author_name}</div>
            <div style={{ fontSize: 12, color: 'var(--text3)' }}>
              {formatDistanceToNow(new Date(p.created_at), { locale: ru, addSuffix: true })}
            </div>
          </div>
          <button onClick={onClose} style={{ fontSize: 22, color: 'var(--text3)', padding: '0 4px' }}>×</button>
        </div>

        <h2 style={{
          fontFamily: 'var(--font-display)', fontStyle: 'italic', fontWeight: 400,
          fontSize: 22, marginBottom: 12, lineHeight: 1.2,
        }}>{p.title}</h2>
        <p style={{ fontSize: 14, lineHeight: 1.7, color: 'var(--text2)', marginBottom: 18 }}>{p.body}</p>

        <button onClick={onLike} style={{
          display: 'flex', alignItems: 'center', gap: 6,
          fontSize: 14, color: 'var(--text2)', marginBottom: 24, fontWeight: 600,
        }}>♥ {p.like_count} лайков</button>

        <div style={{ borderTop: '1.5px solid var(--border2)', paddingTop: 20 }}>
          <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 14 }}>
            Комментарии ({p.comment_count})
          </div>

          {loading ? <Spinner /> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 20 }}>
              {comments.length === 0
                ? <p style={{ fontSize: 13, color: 'var(--text3)' }}>Будьте первым!</p>
                : comments.map(c => <CommentItem key={c.id} c={c} />)
              }
            </div>
          )}

          <div style={{ display: 'flex', gap: 10 }}>
            <input className="input" placeholder="Написать комментарий..."
              value={reply} onChange={e => setReply(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && submit()}
              style={{ flex: 1 }}
            />
            <button className="btn btn-primary btn-sm" onClick={submit} disabled={sending || !reply.trim()}>
              {sending ? '...' : 'Ответить'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

function CommentItem({ c, depth = 0 }) {
  return (
    <div style={{ marginLeft: depth * 20 }}>
      <div style={{ display: 'flex', gap: 9, alignItems: 'flex-start', marginBottom: 6 }}>
        <Avatar name={c.author_name} size={28} />
        <div style={{
          flex: 1, background: 'var(--warm)', borderRadius: 'var(--r2)',
          padding: '9px 13px',
        }}>
          <div style={{ fontWeight: 700, fontSize: 12, marginBottom: 3 }}>{c.author_name}</div>
          <div style={{ fontSize: 13, lineHeight: 1.5 }}>{c.body}</div>
        </div>
      </div>
      {c.replies?.map(r => <CommentItem key={r.id} c={r} depth={depth + 1} />)}
    </div>
  )
}

// ── Create post modal ─────────────────────────────────────────────────────────
function CreateModal({ onClose, onCreated }) {
  const [form, setForm] = useState({ title: '', body: '', species_tag: '', tags: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const s = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const tags = form.tags.split(',').map(t => t.trim()).filter(Boolean)
      const r = await forumApi.create({ ...form, tags, species_tag: form.species_tag || null })
      onCreated(r.data)
    } catch { setError('Ошибка публикации') } finally { setLoading(false) }
  }

  return (
    <div onClick={e => e.target === e.currentTarget && onClose()} style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,.4)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100,
    }}>
      <div className="card fade-up" style={{ width: 500, padding: 28 }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontWeight: 400, fontSize: 24, marginBottom: 22 }}>
          Новый пост
        </h3>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label className="label">Заголовок</label>
            <input className="input" placeholder="О чём ваш пост?" value={form.title} onChange={s('title')} required />
          </div>
          <div>
            <label className="label">Текст</label>
            <textarea className="input" placeholder="Поделитесь историей или задайте вопрос..."
              value={form.body} onChange={s('body')} required rows={5}
              style={{ resize: 'vertical', minHeight: 100 }} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label className="label">Вид животного</label>
              <select className="input" value={form.species_tag} onChange={s('species_tag')}>
                {SPECIES_OPTS.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Теги (через запятую)</label>
              <input className="input" placeholder="питание, здоровье" value={form.tags} onChange={s('tags')} />
            </div>
          </div>
          <ErrorMsg msg={error} />
          <div style={{ display: 'flex', gap: 10 }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Отмена</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : 'Опубликовать'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
