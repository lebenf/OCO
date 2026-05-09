// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface CategoryMini {
  id: string
  name: string
  icon: string | null
}

export interface ItemPhotoOut {
  id: string
  url: string
  is_primary: boolean
  sort_order: number
}

export interface ItemSummary {
  id: string
  name: string
  status: string
  item_type: string
  brand: string | null
  color: string | null
  quantity: number
  ai_generated: boolean
  container_id: string
  primary_photo_url: string | null
  categories: CategoryMini[]
}

export interface ItemDetail extends ItemSummary {
  description: string | null
  model: string | null
  author: string | null
  title: string | null
  ai_confidence: number | null
  ai_provider: string | null
  ai_error: string | null
  ai_result_raw: string | null
  notes: string | null
  tags: string[]
  photos: ItemPhotoOut[]
  created_at: string
  updated_at: string
}

export interface ItemCreate {
  item_type?: string
  hint_type?: string
  photo_ids?: string[]
  language?: string
  name?: string
}

export interface ItemConfirm {
  name: string
  description?: string | null
  brand?: string | null
  model?: string | null
  author?: string | null
  title?: string | null
  color?: string | null
  quantity?: number
  item_type?: string
  notes?: string | null
  tags?: string[]
  category_ids?: string[]
}

export interface Page<T> {
  items: T[]
  total: number
  page: number
  pages: number
}

export const useItemsStore = defineStore('items', () => {
  const items = ref<ItemSummary[]>([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchItems(
    houseId: string,
    params: {
      status?: string
      container_id?: string
      category_id?: string
      search?: string
      page?: number
      size?: number
    } = {},
  ): Promise<Page<ItemSummary>> {
    loading.value = true
    try {
      const res = await api.get<Page<ItemSummary>>(`/houses/${houseId}/items`, { params })
      items.value = res.data.items
      total.value = res.data.total
      return res.data
    } finally {
      loading.value = false
    }
  }

  async function fetchItem(houseId: string, itemId: string): Promise<ItemDetail> {
    const res = await api.get<ItemDetail>(`/houses/${houseId}/items/${itemId}`)
    return res.data
  }

  async function createItem(houseId: string, containerId: string, data: ItemCreate): Promise<ItemDetail> {
    const res = await api.post<ItemDetail>(`/houses/${houseId}/containers/${containerId}/items`, data)
    return res.data
  }

  async function updateItem(houseId: string, itemId: string, data: Partial<ItemConfirm>): Promise<ItemDetail> {
    const res = await api.put<ItemDetail>(`/houses/${houseId}/items/${itemId}`, data)
    return res.data
  }

  async function confirmItem(houseId: string, itemId: string, data: ItemConfirm): Promise<ItemDetail> {
    const res = await api.put<ItemDetail>(`/houses/${houseId}/items/${itemId}/confirm`, data)
    return res.data
  }

  async function deleteItem(houseId: string, itemId: string): Promise<void> {
    await api.delete(`/houses/${houseId}/items/${itemId}`)
  }

  async function retryAI(houseId: string, itemId: string): Promise<{ job_id: string }> {
    const res = await api.post<{ job_id: string }>(`/houses/${houseId}/items/${itemId}/retry-ai`)
    return res.data
  }

  async function confirmAll(houseId: string, containerId: string): Promise<{ confirmed: number; skipped_failed: number; skipped_pending: number }> {
    const res = await api.post(`/houses/${houseId}/containers/${containerId}/confirm-all`)
    return res.data
  }

  async function uploadPhoto(houseId: string, itemId: string, file: File): Promise<ItemPhotoOut> {
    const form = new FormData()
    form.append('file', file)
    const res = await api.post<ItemPhotoOut>(`/houses/${houseId}/items/${itemId}/photos`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return res.data
  }

  return {
    items,
    total,
    loading,
    fetchItems,
    fetchItem,
    createItem,
    updateItem,
    confirmItem,
    deleteItem,
    retryAI,
    confirmAll,
    uploadPhoto,
  }
})
