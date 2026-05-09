<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="result-row" @click="$emit('click')">
    <div class="result-thumb">
      <Photo :src="container.cover_photo_url" ratio="1/1" />
    </div>
    <div class="result-body">
      <div class="result-top">
        <ContainerCode :value="container.code" size="sm" />
        <span v-if="container.destination_location" class="dest-name">{{ container.destination_location.house_name }} · {{ container.destination_location.name }}</span>
      </div>
      <div class="result-meta">
        <span class="meta-num">{{ container.item_count }} obj</span>
        <span v-if="container.volume_liters" class="meta-num">{{ container.volume_liters.toFixed(0) }}L</span>
      </div>
    </div>
    <StatusBadge :kind="container.status" size="sm" />
  </div>
</template>

<script setup lang="ts">
import type { ContainerSummary } from '@/stores/containers'
import Photo from '@/components/primitives/Photo.vue'
import ContainerCode from '@/components/primitives/ContainerCode.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

defineProps<{ container: ContainerSummary }>()
defineEmits<{ click: [] }>()
</script>

<style scoped>
.result-row {
  display: flex;
  align-items: center;
  gap: var(--oco-s-3);
  padding: var(--oco-s-2) var(--oco-s-3);
  border-radius: var(--oco-r-md);
  cursor: pointer;
  transition: background 0.12s;
}
.result-row:hover { background: var(--oco-surface-2); }

.result-thumb { width: 44px; height: 44px; flex-shrink: 0; border-radius: var(--oco-r-sm); overflow: hidden; }
.result-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.result-top { display: flex; align-items: center; gap: var(--oco-s-2); }
.dest-name { font-size: 12px; color: var(--oco-ink-3); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.result-meta { display: flex; gap: var(--oco-s-2); }
.meta-num { font-size: 12px; color: var(--oco-ink-4); font-variant-numeric: tabular-nums; }
</style>
