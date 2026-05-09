<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div v-if="summary" class="dest-summary-view">
    <div class="summary-header">
      <RouterLink :to="`/houses/${houseId}/transfers`" class="back-link">← {{ $t('transfer.list.title') }}</RouterLink>
      <h2 class="view-title">
        {{ summary.location.house_name }} · {{ summary.location.name }}
      </h2>
    </div>

    <div class="stats-row">
      <Stat :value="String(summary.container_count)" :label="$t('transfer.dest.containers')" />
      <Stat :value="`${summary.total_volume_liters.toFixed(0)}L`" :label="$t('transfer.dest.total_volume')" />
      <Stat :value="String(summary.transferred_count)" :label="$t('transfer.dest.transferred')" />
    </div>

    <Panel v-if="summary.planned_transfers.length > 0" :title="$t('transfer.dest.active_transfers')">
      <div class="transfer-list">
        <TransferCard
          v-for="t in summary.planned_transfers"
          :key="t.id"
          :transfer="t"
          @click="router.push(`/houses/${houseId}/transfers/${t.id}`)"
        />
      </div>
    </Panel>

    <Panel :title="$t('transfer.dest.all_containers')">
      <ContainerTransferList :containers="summary.containers" :removable="false" />
    </Panel>
  </div>

  <div v-else class="loading-state">
    <div v-for="i in 3" :key="i" class="skeleton"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTransfersStore, type LocationSummaryOut } from '@/stores/transfers'
import TransferCard from '@/components/transfers/TransferCard.vue'
import ContainerTransferList from '@/components/transfers/ContainerTransferList.vue'
import Stat from '@/components/primitives/Stat.vue'
import Panel from '@/components/primitives/Panel.vue'

const props = defineProps<{ houseId: string; locationId: string }>()
const router = useRouter()
const store = useTransfersStore()

const summary = ref<LocationSummaryOut | null>(null)

onMounted(async () => {
  summary.value = await store.fetchLocationSummary(props.houseId, props.locationId)
})
</script>

<style scoped>
.dest-summary-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 800px; }
.summary-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--oco-s-3); }
@media (max-width: 480px) { .stats-row { grid-template-columns: 1fr 1fr; } }

.transfer-list { display: flex; flex-direction: column; gap: var(--oco-s-2); }

.loading-state { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.skeleton { height: 80px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
