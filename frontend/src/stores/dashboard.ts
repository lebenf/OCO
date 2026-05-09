// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'
import api from '@/services/api'
import type { ContainerSummary } from '@/stores/containers'
import type { ItemSummary } from '@/stores/items'
import type { TransferSummary } from '@/stores/transfers'
import type { HouseMini } from '@/stores/auth'

export interface ContainersByStatus {
  total: number
  by_status: Record<string, number>
}

export interface DestinationHouseStats {
  house: HouseMini
  container_count: number
  total_volume_liters: number
  delivered: number
}

export interface DashboardResponse {
  containers: ContainersByStatus
  items: { total: number }
  by_destination_house: DestinationHouseStats[]
  upcoming_transfers: TransferSummary[]
  recent_containers: ContainerSummary[]
}

export interface SearchResults {
  query: string
  items: ItemSummary[]
  containers: ContainerSummary[]
}

export const useDashboardStore = defineStore('dashboard', () => {
  async function fetchDashboard(houseId: string): Promise<DashboardResponse> {
    const resp = await api.get<DashboardResponse>(`/houses/${houseId}/dashboard`)
    return resp.data
  }

  async function search(houseId: string, q: string): Promise<SearchResults> {
    const resp = await api.get<SearchResults>(`/houses/${houseId}/search`, { params: { q } })
    return resp.data
  }

  return { fetchDashboard, search }
})
