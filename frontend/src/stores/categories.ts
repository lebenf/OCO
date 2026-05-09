// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export interface CategoryOut {
  id: string
  name: string
  icon: string | null
  parent_id: string | null
  is_system: boolean
  house_id: string | null
}

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<CategoryOut[]>([])

  async function fetchCategories(houseId: string): Promise<void> {
    const res = await api.get<CategoryOut[]>(`/houses/${houseId}/categories`)
    categories.value = res.data
  }

  async function createCategory(houseId: string, data: { name: string; icon?: string }): Promise<CategoryOut> {
    const res = await api.post<CategoryOut>(`/houses/${houseId}/categories`, data)
    categories.value.push(res.data)
    return res.data
  }

  async function deleteCategory(houseId: string, categoryId: string): Promise<void> {
    await api.delete(`/houses/${houseId}/categories/${categoryId}`)
    categories.value = categories.value.filter((c) => c.id !== categoryId)
  }

  return { categories, fetchCategories, createCategory, deleteCategory }
})
