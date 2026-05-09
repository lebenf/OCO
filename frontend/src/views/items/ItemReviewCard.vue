<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="review-card" :class="`card--${item.status}`">
    <div class="card-thumb">
      <Photo :src="item.primary_photo_url" ratio="1/1" />
    </div>

    <div class="card-body">
      <StatusBadge :kind="item.status" size="sm" />

      <div v-if="item.status === 'draft'" class="ai-pending">
        {{ $t('item.review.ai_pending') }}
      </div>

      <div v-else-if="item.status === 'draft_ai_failed'" class="ai-error">
        {{ item.ai_error || $t('item.review.ai_error_generic') }}
      </div>

      <div v-else-if="item.ai_result" class="ai-result">
        <div class="ai-name">{{ item.ai_result['name'] }}</div>
        <div v-if="item.ai_result['description']" class="ai-desc">{{ item.ai_result['description'] }}</div>
      </div>
    </div>

    <div class="card-actions">
      <Btn
        v-if="item.status === 'draft_ai_done'"
        style="font-size:12px;padding:5px 12px"
        :disabled="confirming"
        @click="handleConfirm"
      >
        {{ $t('item.review.confirm') }}
      </Btn>
      <Btn kind="ghost" :to="`/houses/${houseId}/items/${item.id}/edit`" style="font-size:12px;padding:5px 12px">
        {{ $t('item.review.edit') }}
      </Btn>
      <Btn
        v-if="item.status === 'draft_ai_failed'"
        kind="soft"
        style="font-size:12px;padding:5px 12px"
        :disabled="retrying"
        @click="handleRetry"
      >
        {{ $t('item.review.retry') }}
      </Btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useItemsStore } from '@/stores/items'
import { type DraftItemSummary } from '@/stores/inbox'
import Photo from '@/components/primitives/Photo.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ item: DraftItemSummary; houseId: string }>()
const emit = defineEmits<{ confirmed: []; retried: [] }>()

const itemsStore = useItemsStore()
const confirming = ref(false)
const retrying = ref(false)

async function handleConfirm(): Promise<void> {
  if (!props.item.ai_result) return
  confirming.value = true
  try {
    await itemsStore.confirmItem(props.houseId, props.item.id, {
      name: String(props.item.ai_result['name'] ?? ''),
      description: props.item.ai_result['description'] ? String(props.item.ai_result['description']) : null,
    })
    emit('confirmed')
  } finally {
    confirming.value = false
  }
}

async function handleRetry(): Promise<void> {
  retrying.value = true
  try {
    await itemsStore.retryAI(props.houseId, props.item.id)
    emit('retried')
  } finally {
    retrying.value = false
  }
}
</script>

<style scoped>
.review-card {
  display: flex;
  align-items: flex-start;
  gap: var(--oco-s-3);
  padding: var(--oco-s-3);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  background: var(--oco-surface);
}
.card--draft_ai_failed { border-color: var(--oco-danger); background: var(--oco-danger-soft); }
.card--draft_ai_done  { border-color: var(--oco-ok); }

.card-thumb { width: 56px; height: 56px; flex-shrink: 0; border-radius: var(--oco-r-md); overflow: hidden; }
.card-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: var(--oco-s-1); }
.ai-pending { font-size: 12px; color: var(--oco-ink-4); }
.ai-error { font-size: 12px; color: var(--oco-danger); font-weight: 500; }
.ai-name { font-size: 14px; font-weight: 600; color: var(--oco-ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.ai-desc { font-size: 12px; color: var(--oco-ink-3); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.card-actions { display: flex; flex-direction: column; gap: var(--oco-s-1); align-items: flex-end; flex-shrink: 0; }
</style>
