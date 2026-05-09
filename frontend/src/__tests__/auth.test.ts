// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

vi.mock('../services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
  },
}))

const mockApi = api as {
  post: ReturnType<typeof vi.fn>
  get: ReturnType<typeof vi.fn>
  put: ReturnType<typeof vi.fn>
}

const fakeUser = {
  id: '1',
  username: 'admin',
  email: 'admin@example.com',
  is_system_admin: true,
  preferred_language: 'it',
  houses: [],
}

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('login sets user from response', async () => {
    mockApi.post.mockResolvedValue({ data: { user: fakeUser } })
    const store = useAuthStore()
    await store.login('admin', 'pass')
    expect(store.user).toEqual(fakeUser)
  })

  it('logout clears user', async () => {
    mockApi.post.mockResolvedValue({})
    const store = useAuthStore()
    store.user = fakeUser
    await store.logout()
    expect(store.user).toBeNull()
  })

  it('fetchMe populates user', async () => {
    mockApi.get.mockResolvedValue({ data: fakeUser })
    const store = useAuthStore()
    await store.fetchMe()
    expect(store.user?.username).toBe('admin')
  })

  it('updateLanguage updates user language', async () => {
    const updated = { ...fakeUser, preferred_language: 'en' }
    mockApi.put.mockResolvedValue({ data: updated })
    const store = useAuthStore()
    store.user = fakeUser
    await store.updateLanguage('en')
    expect(store.user?.preferred_language).toBe('en')
  })

  it('login failure does not set user', async () => {
    mockApi.post.mockRejectedValue(new Error('401'))
    const store = useAuthStore()
    await expect(store.login('admin', 'wrong')).rejects.toThrow()
    expect(store.user).toBeNull()
  })
})
