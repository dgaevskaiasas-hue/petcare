// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './store/auth'
import AuthPage  from './pages/AuthPage'
import PetsPage  from './pages/PetsPage'
import AiPage    from './pages/AiPage'
import ForumPage from './pages/ForumPage'

function Guard({ children }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<AuthPage />} />
        <Route path="/pets"  element={<Guard><PetsPage /></Guard>} />
        <Route path="/ai"    element={<Guard><AiPage /></Guard>} />
        <Route path="/forum" element={<Guard><ForumPage /></Guard>} />
        <Route path="*"      element={<Navigate to="/pets" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
