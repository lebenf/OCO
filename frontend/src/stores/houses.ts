// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import type { HouseMini } from '@/stores/auth'

export interface HouseOut {
  id: string
  name: string
  description: string | null
  code_prefix: string
  container_sequence: number
  is_disposal: boolean
  created_by: string
}

export interface LocationOut {
  id: string
  house_id: string
  name: string
  description: string | null
  is_active: boolean
}

export interface AllLocationsEntry {
  house: HouseMini
  locations: LocationOut[]
}

export const useHousesStore = defineStore('houses', () => {
  const selectedHouseId = ref<string | null>(null)

  const authStore = useAuthStore()

  const houses = computed<HouseMini[]>(() => authStore.user?.houses ?? [])

  const selectedHouse = computed<HouseMini | null>(
    () => houses.value.find((h) => h.id === selectedHouseId.value) ?? null,
  )

  function selectHouse(id: string): void {
    selectedHouseId.value = id
  }

  function autoSelect(): void {
    if (!selectedHouseId.value && houses.value.length > 0) {
      selectedHouseId.value = houses.value[0].id
    }
  }

  async function createHouse(data: { name: string; code_prefix: string; description?: string }): Promise<HouseOut> {
    const res = await api.post('/admin/houses', data)
    await authStore.fetchMe()
    return res.data
  }

  async function fetchLocations(houseId: string): Promise<LocationOut[]> {
    const res = await api.get(`/houses/${houseId}/locations`)
    return res.data
  }

  async function fetchAllLocations(): Promise<AllLocationsEntry[]> {
    const res = await api.get<AllLocationsEntry[]>('/houses/all-locations')
    return res.data
  }

  return {
    selectedHouseId,
    houses,
    selectedHouse,
    selectHouse,
    autoSelect,
    createHouse,
    fetchLocations,
    fetchAllLocations,
  }
})
