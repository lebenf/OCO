// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

interface InboxCount {
  total: number
  pending_ai: number
  ready_for_review: number
  failed: number
}

export interface DraftItemSummary {
  id: string
  item_type: string
  status: string
  ai_error: string | null
  primary_photo_url: string | null
  ai_result: Record<string, unknown> | null
  created_at: string
}

export interface ContainerInboxGroup {
  container_id: string
  container_code: string
  items: DraftItemSummary[]
}

export interface InboxResponse extends InboxCount {
  by_container: ContainerInboxGroup[]
}

export const useInboxStore = defineStore('inbox', () => {
  const count = ref<InboxCount>({ total: 0, pending_ai: 0, ready_for_review: 0, failed: 0 })
  const inbox = ref<InboxResponse | null>(null)
  let pollTimer: ReturnType<typeof setInterval> | null = null

  async function fetchCount(houseId: string): Promise<void> {
    try {
      const res = await api.get<InboxCount>(`/houses/${houseId}/inbox/count`)
      count.value = res.data
    } catch {
      // silently ignore — badge non-critical
    }
  }

  async function fetchInbox(houseId: string): Promise<void> {
    const res = await api.get<InboxResponse>(`/houses/${houseId}/inbox`)
    inbox.value = res.data
    count.value = {
      total: res.data.total,
      pending_ai: res.data.pending_ai,
      ready_for_review: res.data.ready_for_review,
      failed: res.data.failed,
    }
  }

  function startPolling(houseId: string): void {
    stopPolling()
    fetchCount(houseId)
    pollTimer = setInterval(() => fetchCount(houseId), 30_000)
  }

  function stopPolling(): void {
    if (pollTimer !== null) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return { count, inbox, fetchCount, fetchInbox, startPolling, stopPolling }
})
