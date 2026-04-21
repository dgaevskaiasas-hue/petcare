// src/pages/PetsPage.jsx
import { useEffect, useState } from 'react'
import { petsApi } from '../api'
import Layout, { PageHeader, Spinner, Empty, Avatar, ErrorMsg } from '../components/Layout'
import { format } from 'date-fns'
import { ru } from 'date-fns/locale'

const SPECIES = { cat: '🐱', dog: '🐶', bird: '🐦', rabbit: '🐰', other: '🐾' }
const REC_TYPES = ['vaccination','analysis','diagnosis','prescription','weight','grooming']
const REC_LABELS = {
  vaccination: 'Вакцинация', analysis: 'Анализ', diagnosis: 'Диагноз',
  prescription: 'Назначение', weight: 'Вес', grooming: 'Груминг',
}
const REC_BADGE = {
  vaccination: 'badge-green', analysis: 'badge-amber',
  diagnosis: 'badge-terra', prescription: 'badge-purple',
  weight: '', grooming: '',
}

export default function PetsPage() {
  const [pets, setPets]       = useState([])
  const [selected, setSelected] = useState(null)
  const [tab, setTab]         = useState('health')
  const [health, setHealth]   = useState([])
  const [behaviour, setBehaviour] = useState([])
  const [alerts, setAlerts]   = useState([])
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [showAddPet, setShowAddPet]   = useState(false)
  const [showAddRec, setShowAddRec]   = useState(false)
  const [showAddBeh, setShowAddBeh]   = useState(false)

  // Загрузка списка питомцев
  useEffect(() => {
    petsApi.list()
      .then(r => { setPets(r.data); if (r.data.length) setSelected(r.data[0]) })
      .finally(() => setLoading(false))
  }, [])

  // Загрузка деталей выбранного питомца
  useEffect(() => {
    if (!selected) return
    setDetailLoading(true)
    Promise.all([
      petsApi.getHealth(selected.id),
      petsApi.getBehaviour(selected.id, 30),
    ]).then(([h, b]) => {
      setHealth(h.data)
      setBehaviour(b.data)
      setAlerts([])
    }).finally(() => setDetailLoading(false))
  }, [selected])

  if (loading) return <Layout><Spinner /></Layout>

  return (
    <Layout>
      <PageHeader
        title="Мои питомцы"
        sub="Профили и медицинские карты"
        action={
          <button className="btn btn-primary btn-sm" onClick={() => setShowAddPet(true)}>
            + Добавить питомца
          </button>
        }
      />

      <div style={{ display: 'flex', gap: 20 }}>

        {/* ── Список питомцев ── */}
        <div style={{ width: 180, flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {pets.length === 0 && (
            <Empty icon="🐾" title="Питомцев нет" sub="Добавьте первого" />
          )}
          {pets.map(p => (
            <button key={p.id} onClick={() => setSelected(p)} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '12px 14px', borderRadius: 'var(--r)',
              border: '1.5px solid',
              borderColor: selected?.id === p.id ? 'var(--green)' : 'var(--border2)',
              background: selected?.id === p.id ? 'var(--green-ll)' : 'var(--card)',
              cursor: 'pointer', transition: 'all .15s', textAlign: 'left',
            }}>
              <span style={{ fontSize: 24 }}>{SPECIES[p.species] || '🐾'}</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: selected?.id === p.id ? 'var(--green)' : 'var(--text)' }}>{p.name}</div>
                <div style={{ fontSize: 11, color: 'var(--text2)' }}>{p.breed || p.species}</div>
              </div>
            </button>
          ))}
        </div>

        {/* ── Детали питомца ── */}
        {selected ? (
          <div className="card fade-up" style={{ flex: 1, padding: 24 }}>

            {/* Профиль */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 24 }}>
              <span style={{ fontSize: 48 }}>{SPECIES[selected.species]}</span>
              <div style={{ flex: 1 }}>
                <h2 style={{
                  fontFamily: 'var(--font-display)', fontStyle: 'italic',
                  fontWeight: 400, fontSize: 26, marginBottom: 4,
                }}>{selected.name}</h2>
                <p style={{ fontSize: 13, color: 'var(--text2)' }}>
                  {[selected.breed, selected.species, selected.sex === 'female' ? 'самка' : selected.sex === 'male' ? 'самец' : null, selected.is_neutered ? 'стерилизован(а)' : null].filter(Boolean).join(' · ')}
                  {selected.birth_date && ` · ${format(new Date(selected.birth_date), 'd MMM yyyy', { locale: ru })}`}
                </p>
              </div>
            </div>

            {/* Вкладки */}
            <div style={{ display: 'flex', borderBottom: '1.5px solid var(--border2)', marginBottom: 20 }}>
              {[['health','Медкарта'],['behaviour','Дневник'],['add-rec','+ Запись в медкарту'],['add-beh','+ Дневник']].map(([t, l]) => (
                <button key={t} onClick={() => setTab(t)} style={{
                  padding: '9px 16px', fontSize: 13,
                  fontWeight: tab === t ? 700 : 600,
                  color: tab === t ? 'var(--green)' : 'var(--text2)',
                  borderBottom: tab === t ? '2.5px solid var(--green)' : '2.5px solid transparent',
                  marginBottom: -1.5, transition: 'all .15s',
                }}>{l}</button>
              ))}
            </div>

            {detailLoading ? <Spinner /> : <>
              {tab === 'health' && <HealthTab records={health} petId={selected.id} onDeleted={id => setHealth(h => h.filter(r => r.id !== id))} />}
              {tab === 'behaviour' && <BehaviourTab logs={behaviour} alerts={alerts} />}
              {tab === 'add-rec' && (
                <AddHealthForm petId={selected.id} onSaved={rec => {
                  setHealth(h => [rec, ...h])
                  setTab('health')
                }} />
              )}
              {tab === 'add-beh' && (
                <AddBehaviourForm petId={selected.id} onSaved={(log, als) => {
                  setBehaviour(b => [log, ...b])
                  setAlerts(als)
                  setTab('behaviour')
                }} />
              )}
            </>}
          </div>
        ) : (
          <div className="card" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Empty icon="🐾" title="Выберите питомца" sub="или добавьте нового" />
          </div>
        )}
      </div>

      {showAddPet && (
        <AddPetModal
          onClose={() => setShowAddPet(false)}
          onSaved={pet => { setPets(p => [...p, pet]); setSelected(pet); setShowAddPet(false) }}
        />
      )}
    </Layout>
  )
}

// ── Health records tab ────────────────────────────────────────────────────────
function HealthTab({ records, petId, onDeleted }) {
  if (!records.length) return (
    <Empty icon="📋" title="Записей нет" sub="Добавьте первую запись во вкладке + Запись" />
  )
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {records.map(r => (
        <div key={r.id} style={{
          display: 'flex', alignItems: 'center', gap: 12,
          padding: '12px 16px', background: 'var(--warm)',
          borderRadius: 'var(--r2)', border: '1px solid var(--border)',
        }}>
          <span className={`badge ${REC_BADGE[r.record_type] || ''}`}
            style={!REC_BADGE[r.record_type] ? { background: 'var(--border2)', color: 'var(--text2)' } : {}}>
            {REC_LABELS[r.record_type]}
          </span>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, fontWeight: 700 }}>{r.title}</div>
            {r.description && <div style={{ fontSize: 12, color: 'var(--text2)', marginTop: 2 }}>{r.description}</div>}
            {(r.vet_name || r.clinic_name) && (
              <div style={{ fontSize: 11, color: 'var(--text3)', marginTop: 2 }}>
                {[r.vet_name, r.clinic_name].filter(Boolean).join(' · ')}
              </div>
            )}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text3)', flexShrink: 0 }}>
            {r.recorded_at ? format(new Date(r.recorded_at), 'dd.MM.yyyy') : ''}
          </div>
          <button onClick={async () => {
            await petsApi.deleteHealth(petId, r.id)
            onDeleted(r.id)
          }} style={{ color: 'var(--text3)', fontSize: 16, padding: '2px 6px' }}>×</button>
        </div>
      ))}
    </div>
  )
}

// ── Behaviour tab ─────────────────────────────────────────────────────────────
function BehaviourTab({ logs, alerts }) {
  const dot = v => v ? '●'.repeat(v) + '○'.repeat(5 - v) : '—'
  return (
    <div>
      {alerts.map((a, i) => (
        <div key={i} style={{
          padding: '12px 16px', borderRadius: 'var(--r2)', marginBottom: 10,
          background: a.level === 'danger' ? 'var(--terra-l)' : 'var(--amber-l)',
          border: `1.5px solid ${a.level === 'danger' ? '#F5C4B3' : '#F8D99A'}`,
          fontSize: 13, fontWeight: 600,
          color: a.level === 'danger' ? 'var(--terra)' : '#8B5E00',
        }}>
          {a.level === 'danger' ? '⚠️ ' : '🔔 '}{a.message}
        </div>
      ))}
      {logs.length === 0
        ? <Empty icon="📓" title="Дневник пуст" sub="Заполняйте ежедневно для алертов" />
        : logs.map(l => (
          <div key={l.id} style={{
            display: 'grid', gridTemplateColumns: '90px 1fr 1fr 1fr 70px',
            gap: 10, padding: '10px 14px',
            background: 'var(--warm)', borderRadius: 'var(--r2)',
            fontSize: 12, marginBottom: 6, alignItems: 'center',
          }}>
            <span style={{ color: 'var(--text2)' }}>
              {l.logged_at ? format(new Date(l.logged_at), 'd MMM', { locale: ru }) : ''}
            </span>
            <span>Аппетит: <b style={{ color: 'var(--green)' }}>{dot(l.appetite)}</b></span>
            <span>Активность: <b style={{ color: 'var(--green)' }}>{dot(l.activity)}</b></span>
            <span>Настроение: <b style={{ color: 'var(--green)' }}>{dot(l.mood)}</b></span>
            {l.weight_kg && <span style={{ color: 'var(--text2)' }}>{l.weight_kg} кг</span>}
          </div>
        ))
      }
    </div>
  )
}

// ── Add health record form ────────────────────────────────────────────────────
function AddHealthForm({ petId, onSaved }) {
  const [form, setForm] = useState({ record_type: 'vaccination', title: '', description: '', vet_name: '', clinic_name: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const s = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const r = await petsApi.addHealth(petId, form)
      onSaved(r.data)
    } catch (err) {
      setError('Ошибка сохранения')
    } finally { setLoading(false) }
  }

  return (
    <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14, maxWidth: 420 }}>
      <div>
        <label className="label">Тип записи</label>
        <select className="input" value={form.record_type} onChange={s('record_type')}>
          {REC_TYPES.map(t => <option key={t} value={t}>{REC_LABELS[t]}</option>)}
        </select>
      </div>
      <div>
        <label className="label">Название</label>
        <input className="input" placeholder="Например: FVRCP вакцина" value={form.title} onChange={s('title')} required />
      </div>
      <div>
        <label className="label">Описание</label>
        <input className="input" placeholder="Дополнительные детали" value={form.description} onChange={s('description')} />
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <div>
          <label className="label">Врач</label>
          <input className="input" placeholder="Имя врача" value={form.vet_name} onChange={s('vet_name')} />
        </div>
        <div>
          <label className="label">Клиника</label>
          <input className="input" placeholder="Название клиники" value={form.clinic_name} onChange={s('clinic_name')} />
        </div>
      </div>
      <ErrorMsg msg={error} />
      <button className="btn btn-primary" type="submit" disabled={loading} style={{ alignSelf: 'flex-start' }}>
        {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : 'Сохранить'}
      </button>
    </form>
  )
}

// ── Add behaviour log form ────────────────────────────────────────────────────
function AddBehaviourForm({ petId, onSaved }) {
  const [form, setForm] = useState({ appetite: 3, activity: 3, mood: 3, stool: 'normal', weight_kg: '', notes: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const s = k => e => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = { ...form, appetite: +form.appetite, activity: +form.activity, mood: +form.mood }
      if (!payload.weight_kg) delete payload.weight_kg
      const r = await petsApi.addBehaviour(petId, payload)
      onSaved(r.data.log, r.data.alerts)
    } catch { setError('Ошибка сохранения') } finally { setLoading(false) }
  }

  return (
    <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14, maxWidth: 420 }}>
      {[['appetite','Аппетит'],['activity','Активность'],['mood','Настроение']].map(([k, l]) => (
        <div key={k}>
          <label className="label">{l}: {form[k]}/5</label>
          <input type="range" min="1" max="5" value={form[k]} onChange={s(k)}
            style={{ width: '100%', accentColor: 'var(--green)' }} />
        </div>
      ))}
      <div>
        <label className="label">Стул</label>
        <select className="input" value={form.stool} onChange={s('stool')}>
          <option value="normal">Норма</option>
          <option value="loose">Жидкий</option>
          <option value="hard">Твёрдый</option>
          <option value="absent">Отсутствует</option>
        </select>
      </div>
      <div>
        <label className="label">Вес (кг)</label>
        <input className="input" type="number" step="0.1" placeholder="5.2" value={form.weight_kg} onChange={s('weight_kg')} />
      </div>
      <div>
        <label className="label">Заметки</label>
        <input className="input" placeholder="Что заметили сегодня?" value={form.notes} onChange={s('notes')} />
      </div>
      <ErrorMsg msg={error} />
      <button className="btn btn-primary" type="submit" disabled={loading} style={{ alignSelf: 'flex-start' }}>
        {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : 'Записать'}
      </button>
    </form>
  )
}

// ── Add pet modal ─────────────────────────────────────────────────────────────
function AddPetModal({ onClose, onSaved }) {
  const [form, setForm] = useState({ name: '', species: 'cat', breed: '', sex: 'female', is_neutered: false })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const s = k => e => setForm(f => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))

  const submit = async e => {
    e.preventDefault()
    setLoading(true)
    try {
      const r = await petsApi.create(form)
      onSaved(r.data)
    } catch (err) {
      setError('Ошибка создания')
    } finally { setLoading(false) }
  }

  return (
    <div onClick={e => e.target === e.currentTarget && onClose()} style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,.35)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100,
    }}>
      <div className="card fade-up" style={{ width: 420, padding: 28 }}>
        <h3 style={{ fontFamily: 'var(--font-display)', fontStyle: 'italic', fontWeight: 400, fontSize: 24, marginBottom: 22 }}>
          Новый питомец
        </h3>
        <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          <div>
            <label className="label">Кличка</label>
            <input className="input" value={form.name} onChange={s('name')} required />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label className="label">Вид</label>
              <select className="input" value={form.species} onChange={s('species')}>
                {Object.entries(SPECIES).map(([v, e]) => <option key={v} value={v}>{e} {v}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Пол</label>
              <select className="input" value={form.sex} onChange={s('sex')}>
                <option value="female">Самка</option>
                <option value="male">Самец</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">Порода</label>
            <input className="input" placeholder="Необязательно" value={form.breed} onChange={s('breed')} />
          </div>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 14, cursor: 'pointer' }}>
            <input type="checkbox" checked={form.is_neutered} onChange={s('is_neutered')} style={{ accentColor: 'var(--green)', width: 16, height: 16 }} />
            Кастрирован / стерилизован
          </label>
          <ErrorMsg msg={error} />
          <div style={{ display: 'flex', gap: 10, marginTop: 4 }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>Отмена</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : 'Добавить'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
