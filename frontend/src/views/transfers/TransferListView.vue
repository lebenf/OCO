<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="transfer-list-view">
    <div class="list-header">
      <h2 class="view-title">{{ $t('transfer.list.title') }}</h2>
      <div class="header-actions">
        <Btn kind="soft" :to="`/houses/${houseId}/transfers/plan`">
          {{ $t('transfer.list.plan') }}
        </Btn>
        <Btn :to="`/houses/${houseId}/transfers/create`">
          + {{ $t('transfer.list.create') }}
        </Btn>
      </div>
    </div>

    <div class="filters">
      <select v-model="statusFilter" @change="load">
        <option value="">{{ $t('transfer.list.all_statuses') }}</option>
        <option value="planned">{{ $t('transfer.status.planned') }}</option>
        <option value="in_progress">{{ $t('transfer.status.in_progress') }}</option>
        <option value="completed">{{ $t('transfer.status.completed') }}</option>
        <option value="cancelled">{{ $t('transfer.status.cancelled') }}</option>
      </select>
    </div>

    <div v-if="loading" class="skeleton-list">
      <div v-for="i in 3" :key="i" class="skeleton"></div>
    </div>

    <div v-else-if="transfers.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.25">
        <rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
        <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
      </svg>
      <p>{{ $t('transfer.list.empty') }}</p>
      <Btn :to="`/houses/${houseId}/transfers/create`">{{ $t('transfer.list.create') }}</Btn>
    </div>

    <div v-else class="list">
      <TransferCard
        v-for="t in transfers"
        :key="t.id"
        :transfer="t"
        @click="router.push(`/houses/${houseId}/transfers/${t.id}`)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTransfersStore, type TransferSummary } from '@/stores/transfers'
import TransferCard from '@/components/transfers/TransferCard.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const store = useTransfersStore()

const transfers = ref<TransferSummary[]>([])
const loading = ref(false)
const statusFilter = ref('')

async function load(): Promise<void> {
  loading.value = true
  try {
    transfers.value = await store.fetchTransfers(props.houseId, {
      status: statusFilter.value || undefined,
    })
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.transfer-list-view { display: flex; flex-direction: column; gap: var(--oco-s-4); max-width: 800px; }
.list-header { display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: var(--oco-s-3); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }
.header-actions { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; }
.filters select { font-size: 13px; }
.list { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.skeleton-list { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.skeleton { height: 72px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.empty-state {
  display: flex; flex-direction: column; align-items: center; gap: var(--oco-s-3);
  padding: var(--oco-s-8); color: var(--oco-ink-4); font-size: 14px; text-align: center;
}
.empty-state p { margin: 0; }
</style>
