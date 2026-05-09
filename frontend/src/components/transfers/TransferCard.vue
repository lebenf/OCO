<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="transfer-card" @click="$emit('click')">
    <div class="card-header">
      <span class="transfer-name">{{ transfer.name }}</span>
      <StatusBadge :kind="transfer.status" size="sm" />
    </div>
    <div class="card-meta">
      <span v-if="transfer.destination_location" class="dest-chip">
        {{ transfer.destination_location.house_name }} · {{ transfer.destination_location.name }}
      </span>
      <span class="meta-num">{{ transfer.container_count }} boxes</span>
      <span v-if="transfer.total_volume_liters > 0" class="meta-num num">{{ transfer.total_volume_liters.toFixed(0) }}L</span>
      <span v-if="transfer.scheduled_date" class="meta-num num">{{ transfer.scheduled_date }}</span>
    </div>
    <VolumeIndicator
      v-if="transfer.vehicle_volume_liters"
      :used="transfer.total_volume_liters"
      :total="transfer.vehicle_volume_liters"
    />
  </div>
</template>

<script setup lang="ts">
import type { TransferSummary } from '@/stores/transfers'
import VolumeIndicator from './VolumeIndicator.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

defineProps<{ transfer: TransferSummary }>()
defineEmits<{ click: [] }>()
</script>

<style scoped>
.transfer-card {
  padding: var(--oco-s-3) var(--oco-s-4);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  background: var(--oco-surface);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: var(--oco-s-2);
  transition: border-color 0.12s, box-shadow 0.12s;
}
.transfer-card:hover { border-color: var(--oco-primary); box-shadow: var(--oco-shadow-sm); }

.card-header { display: flex; align-items: center; justify-content: space-between; gap: var(--oco-s-2); }
.transfer-name { font-weight: 600; font-size: 14px; color: var(--oco-ink); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.card-meta { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; align-items: center; }
.dest-chip {
  font-size: 12px; font-weight: 500;
  padding: 2px 8px; border-radius: var(--oco-r-xl);
  background: var(--oco-surface-2); color: var(--oco-ink-2);
}
.meta-num { font-size: 12px; color: var(--oco-ink-4); }
</style>
