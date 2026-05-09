// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface HouseMini {
  id: string
  name: string
  role: 'admin' | 'member'
}

export interface UserProfile {
  id: string
  username: string
  email: string
  is_system_admin: boolean
  preferred_language: string
  houses: HouseMini[]
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserProfile | null>(null)
  const loading = ref(false)

  async function login(username: string, password: string): Promise<void> {
    const res = await api.post('/auth/login', { username, password })
    user.value = res.data.user
  }

  async function logout(): Promise<void> {
    await api.post('/auth/logout').catch(() => {})
    user.value = null
  }

  async function refreshToken(): Promise<void> {
    await api.post('/auth/refresh')
  }

  async function fetchMe(): Promise<void> {
    const res = await api.get('/auth/me')
    user.value = res.data
  }

  async function updateLanguage(lang: string): Promise<void> {
    const res = await api.put('/auth/me', { preferred_language: lang })
    user.value = res.data
  }

  return { user, loading, login, logout, refreshToken, fetchMe, updateLanguage }
})
