<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="container-transfer-list">
    <div v-if="containers.length === 0" class="empty">{{ $t('transfer.detail.no_containers') }}</div>
    <div v-for="c in containers" :key="c.id" class="container-row">
      <ContainerCode :value="c.code" size="sm" />
      <span v-if="c.destination_location" class="dest-name">{{ c.destination_location.name }}</span>
      <span v-if="c.volume_liters" class="volume num">{{ c.volume_liters.toFixed(1) }}L</span>
      <StatusBadge :kind="c.status" size="sm" />
      <button v-if="removable" class="remove-btn" @click="$emit('remove', c.id)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ContainerSummary } from '@/stores/containers'
import ContainerCode from '@/components/primitives/ContainerCode.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

defineProps<{ containers: ContainerSummary[]; removable?: boolean }>()
defineEmits<{ remove: [id: string] }>()
</script>

<style scoped>
.container-transfer-list { display: flex; flex-direction: column; gap: 2px; }
.container-row {
  display: flex;
  align-items: center;
  gap: var(--oco-s-2);
  padding: var(--oco-s-2) var(--oco-s-2);
  border-radius: var(--oco-r-md);
  font-size: 13px;
  transition: background 0.1s;
}
.container-row:hover { background: var(--oco-surface-2); }
.dest-name { flex: 1; font-size: 12px; color: var(--oco-ink-3); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.volume { font-size: 12px; color: var(--oco-ink-4); }
.remove-btn {
  flex-shrink: 0; width: 22px; height: 22px;
  border: none; background: transparent;
  color: var(--oco-ink-4); cursor: pointer;
  border-radius: var(--oco-r-sm); display: flex; align-items: center; justify-content: center;
  transition: background 0.12s, color 0.12s;
}
.remove-btn:hover { background: var(--oco-danger-soft); color: var(--oco-danger); }
.empty { color: var(--oco-ink-4); font-size: 13px; text-align: center; padding: var(--oco-s-4); }
</style>
