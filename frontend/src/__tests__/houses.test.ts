// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useHousesStore } from '../stores/houses'
import { useAuthStore } from '../stores/auth'
import api from '../services/api'

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockApi = api as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> }

describe('useHousesStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('houses computed returns empty when no user', () => {
    const store = useHousesStore()
    expect(store.houses).toEqual([])
  })

  it('houses computed returns user houses', () => {
    const auth = useAuthStore()
    auth.user = {
      id: '1', username: 'a', email: 'a@b.com',
      is_system_admin: true, preferred_language: 'it',
      houses: [{ id: 'h1', name: 'House 1', role: 'admin' }],
    }
    const store = useHousesStore()
    expect(store.houses).toHaveLength(1)
  })

  it('autoSelect picks first house', () => {
    const auth = useAuthStore()
    auth.user = {
      id: '1', username: 'a', email: 'a@b.com',
      is_system_admin: false, preferred_language: 'it',
      houses: [
        { id: 'h1', name: 'House 1', role: 'member' },
        { id: 'h2', name: 'House 2', role: 'member' },
      ],
    }
    const store = useHousesStore()
    store.autoSelect()
    expect(store.selectedHouseId).toBe('h1')
  })

  it('selectHouse updates selectedHouseId', () => {
    const store = useHousesStore()
    store.selectHouse('h99')
    expect(store.selectedHouseId).toBe('h99')
  })

  it('fetchLocations returns data', async () => {
    mockApi.get.mockResolvedValue({ data: [{ id: 'l1', name: 'Cantina' }] })
    const store = useHousesStore()
    const locs = await store.fetchLocations('h1')
    expect(locs[0].name).toBe('Cantina')
  })
})
