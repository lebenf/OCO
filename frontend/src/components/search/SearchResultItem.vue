<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="result-row" @click="$emit('click')">
    <div class="result-thumb">
      <Photo :src="item.primary_photo_url" ratio="1/1" />
    </div>
    <div class="result-body">
      <div class="result-name">{{ item.name }}</div>
      <div class="result-meta">
        <span v-if="item.brand" class="meta-chip">{{ item.brand }}</span>
        <span v-if="item.color" class="meta-chip">{{ item.color }}</span>
        <span v-if="item.quantity > 1" class="meta-chip mono">×{{ item.quantity }}</span>
      </div>
      <div v-if="item.categories.length" class="result-cats">
        <CategoryChip
          v-for="cat in item.categories.slice(0, 3)"
          :key="cat.id"
          :label="cat.name"
          :icon="cat.icon"
        />
      </div>
    </div>
    <StatusBadge :kind="item.status" size="sm" />
  </div>
</template>

<script setup lang="ts">
import type { ItemSummary } from '@/stores/items'
import Photo from '@/components/primitives/Photo.vue'
import CategoryChip from '@/components/primitives/CategoryChip.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

defineProps<{ item: ItemSummary }>()
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
.result-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 3px; }
.result-name { font-size: 14px; font-weight: 600; color: var(--oco-ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.result-meta { display: flex; gap: var(--oco-s-1); flex-wrap: wrap; }
.meta-chip { font-size: 11px; color: var(--oco-ink-3); }
.result-cats { display: flex; gap: var(--oco-s-1); flex-wrap: wrap; }
</style>
