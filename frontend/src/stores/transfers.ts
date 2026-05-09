// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'
import type { ContainerSummary, LocationMini } from '@/stores/containers'

export interface TransferSummary {
  id: string
  name: string
  status: string
  destination_location: LocationMini | null
  scheduled_date: string | null
  vehicle_volume_liters: number | null
  container_count: number
  total_volume_liters: number
}

export interface TransferDetail extends TransferSummary {
  notes: string | null
  containers: ContainerSummary[]
  created_at: string
  updated_at: string
}

export interface TripPlan {
  trip_number: number
  containers: ContainerSummary[]
  total_volume_liters: number
  vehicle_fill_percent: number
  scheduled_date: string | null
}

export interface TransferPlanResponse {
  trips: TripPlan[]
  unassigned_containers: ContainerSummary[]
  algorithm: string
}

export interface LocationSummaryOut {
  location: LocationMini
  container_count: number
  total_volume_liters: number
  transferred_count: number
  planned_transfers: TransferSummary[]
  containers: ContainerSummary[]
}

export const useTransfersStore = defineStore('transfers', () => {
  const transfers = ref<TransferSummary[]>([])

  async function fetchTransfers(
    houseId: string,
    params?: { status?: string; destination_location_id?: string },
  ): Promise<TransferSummary[]> {
    const resp = await api.get<TransferSummary[]>(`/houses/${houseId}/transfers`, { params })
    transfers.value = resp.data
    return resp.data
  }

  async function fetchTransfer(houseId: string, transferId: string): Promise<TransferDetail> {
    const resp = await api.get<TransferDetail>(`/houses/${houseId}/transfers/${transferId}`)
    return resp.data
  }

  async function createTransfer(
    houseId: string,
    data: {
      name: string
      destination_location_id: string
      scheduled_date?: string | null
      vehicle_volume_liters?: number | null
      notes?: string | null
      container_ids?: string[]
    },
  ): Promise<TransferDetail> {
    const resp = await api.post<TransferDetail>(`/houses/${houseId}/transfers`, data)
    return resp.data
  }

  async function updateTransfer(
    houseId: string,
    transferId: string,
    data: Partial<{
      name: string
      destination_location_id: string
      scheduled_date: string | null
      vehicle_volume_liters: number | null
      notes: string | null
    }>,
  ): Promise<TransferDetail> {
    const resp = await api.put<TransferDetail>(`/houses/${houseId}/transfers/${transferId}`, data)
    return resp.data
  }

  async function startTransfer(houseId: string, transferId: string): Promise<TransferDetail> {
    const resp = await api.post<TransferDetail>(
      `/houses/${houseId}/transfers/${transferId}/start`,
    )
    return resp.data
  }

  async function completeTransfer(houseId: string, transferId: string): Promise<TransferDetail> {
    const resp = await api.post<TransferDetail>(
      `/houses/${houseId}/transfers/${transferId}/complete`,
    )
    return resp.data
  }

  async function addContainers(
    houseId: string,
    transferId: string,
    containerIds: string[],
  ): Promise<TransferDetail> {
    const resp = await api.post<TransferDetail>(
      `/houses/${houseId}/transfers/${transferId}/containers`,
      { container_ids: containerIds },
    )
    return resp.data
  }

  async function removeContainer(
    houseId: string,
    transferId: string,
    containerId: string,
  ): Promise<TransferDetail> {
    const resp = await api.delete<TransferDetail>(
      `/houses/${houseId}/transfers/${transferId}/containers/${containerId}`,
    )
    return resp.data
  }

  async function planTransfers(
    houseId: string,
    data: {
      destination_house_id: string
      vehicle_volume_liters: number
      scheduled_dates?: string[]
    },
  ): Promise<TransferPlanResponse> {
    const resp = await api.post<TransferPlanResponse>(
      `/houses/${houseId}/transfers/plan`,
      data,
    )
    return resp.data
  }

  async function fetchLocationSummary(
    houseId: string,
    locationId: string,
  ): Promise<LocationSummaryOut> {
    const resp = await api.get<LocationSummaryOut>(
      `/houses/${houseId}/locations/${locationId}/summary`,
    )
    return resp.data
  }

  return {
    transfers,
    fetchTransfers,
    fetchTransfer,
    createTransfer,
    updateTransfer,
    startTransfer,
    completeTransfer,
    addContainers,
    removeContainer,
    planTransfers,
    fetchLocationSummary,
  }
})
