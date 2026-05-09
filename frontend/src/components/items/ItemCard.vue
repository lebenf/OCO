<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="item-card" @click="$emit('click', item)">
    <div class="item-thumb">
      <Photo :src="item.primary_photo_url" ratio="1/1" />
    </div>
    <div class="item-body">
      <div class="item-name">{{ item.name }}</div>
      <div v-if="item.brand" class="item-brand">{{ item.brand }}</div>
      <StatusBadge :kind="item.status" size="sm" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ItemSummary } from '@/stores/items'
import Photo from '@/components/primitives/Photo.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

defineProps<{ item: ItemSummary }>()
defineEmits<{ click: [item: ItemSummary] }>()
</script>

<style scoped>
.item-card {
  display: flex;
  align-items: center;
  gap: var(--oco-s-3);
  padding: var(--oco-s-3);
  border-radius: var(--oco-r-md);
  cursor: pointer;
  transition: background 0.12s;
}
.item-card:hover { background: var(--oco-surface-2); }
.item-thumb { width: 48px; height: 48px; flex-shrink: 0; border-radius: var(--oco-r-sm); overflow: hidden; }
.item-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.item-name { font-size: 14px; font-weight: 600; color: var(--oco-ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.item-brand { font-size: 12px; color: var(--oco-ink-3); }
</style>
