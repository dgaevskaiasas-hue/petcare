// src/store/auth.js
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../api'
import { errMsg } from '../api/client'

export const useAuth = create(
  persist(
    (set, get) => ({
      user:  null,
      token: null,

      login: async (email, password) => {
        const { data } = await authApi.login(email, password)
        set({ user: data.user, token: data.access_token })
      },

      register: async (email, password, username) => {
        const { data } = await authApi.register(email, password, username)
        set({ user: data.user, token: data.access_token })
      },

      logout: async () => {
        try { await authApi.logout() } catch {}
        set({ user: null, token: null })
      },

      isAuth: () => !!get().token,
    }),
    {
      name: 'pc-auth',
      partialize: s => ({ user: s.user, token: s.token }),
    }
  )
)
