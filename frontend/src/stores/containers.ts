// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface LocationMini {
  id: string
  name: string
  house_id: string
  house_name: string
}

export interface ContainerMini {
  id: string
  code: string
  status: string
}

export interface PhotoOut {
  id: string
  url: string
  phase: string | null
  sort_order: number
}

export interface ItemSummaryOut {
  id: string
  name: string
  status: string
  item_type: string
}

export interface UserMini {
  id: string
  username: string
}

export interface ContainerSummary {
  id: string
  code: string
  status: string
  current_location: LocationMini | null
  destination_location: LocationMini | null
  item_count: number
  volume_liters: number | null
  cover_photo_url: string | null
  nesting_level: number
  children_count: number
}

export interface ContainerDetail extends ContainerSummary {
  description: string | null
  width_cm: number | null
  depth_cm: number | null
  height_cm: number | null
  photos: PhotoOut[]
  items: ItemSummaryOut[]
  children: ContainerSummary[]
  parent: ContainerMini | null
  volume_calculated: number
  created_by: UserMini
  created_at: string
  updated_at: string
}

export interface ContainerCreate {
  parent_id?: string | null
  destination_location_id?: string | null
  current_location_id?: string | null
  width_cm?: number | null
  depth_cm?: number | null
  height_cm?: number | null
  description?: string | null
}

export interface ContainerUpdate extends ContainerCreate {}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  pages: number
}

export const useContainersStore = defineStore('containers', () => {
  const containers = ref<ContainerSummary[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const totalPages = ref(1)
  const loading = ref(false)

  async function fetchContainers(
    houseId: string,
    params: {
      status?: string
      destination_location_id?: string
      destination_house_id?: string
      current_location_id?: string
      parent_id?: string
      search?: string
      page?: number
      size?: number
    } = {},
  ): Promise<void> {
    loading.value = true
    try {
      const res = await api.get<Page<ContainerSummary>>(`/houses/${houseId}/containers`, { params })
      containers.value = res.data.items
      total.value = res.data.total
      currentPage.value = res.data.page
      totalPages.value = res.data.pages
    } finally {
      loading.value = false
    }
  }

  async function fetchContainer(houseId: string, codeOrId: string): Promise<ContainerDetail> {
    const res = await api.get<ContainerDetail>(`/houses/${houseId}/containers/${codeOrId}`)
    return res.data
  }

  async function createContainer(houseId: string, data: ContainerCreate): Promise<ContainerDetail> {
    const res = await api.post<ContainerDetail>(`/houses/${houseId}/containers`, data)
    return res.data
  }

  async function updateContainer(houseId: string, containerId: string, data: ContainerUpdate): Promise<ContainerDetail> {
    const res = await api.put<ContainerDetail>(`/houses/${houseId}/containers/${containerId}`, data)
    return res.data
  }

  async function closeContainer(
    houseId: string,
    containerId: string,
    data: { destination_location_id?: string; current_location_id?: string } = {},
  ): Promise<ContainerDetail> {
    const res = await api.post<ContainerDetail>(`/houses/${houseId}/containers/${containerId}/close`, data)
    return res.data
  }

  async function sealContainer(houseId: string, containerId: string): Promise<ContainerDetail> {
    const res = await api.post<ContainerDetail>(`/houses/${houseId}/containers/${containerId}/seal`, {})
    return res.data
  }

  async function uploadPhoto(houseId: string, containerId: string, file: File, phase?: string): Promise<PhotoOut> {
    const form = new FormData()
    form.append('file', file)
    if (phase) form.append('phase', phase)
    const res = await api.post<PhotoOut>(`/houses/${houseId}/containers/${containerId}/photos`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  }

  async function deletePhoto(houseId: string, containerId: string, photoId: string): Promise<void> {
    await api.delete(`/houses/${houseId}/containers/${containerId}/photos/${photoId}`)
  }

  function qrUrl(houseId: string, containerId: string): string {
    return `/api/houses/${houseId}/containers/${containerId}/qr`
  }

  return {
    containers,
    total,
    currentPage,
    totalPages,
    loading,
    fetchContainers,
    fetchContainer,
    createContainer,
    updateContainer,
    closeContainer,
    sealContainer,
    uploadPhoto,
    deletePhoto,
    qrUrl,
  }
})
