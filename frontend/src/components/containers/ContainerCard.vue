<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="container-card" @click="$emit('click', container)">
    <Photo :src="container.cover_photo_url" ratio="4/3" class="card-photo" />
    <div class="card-body">
      <div class="card-top">
        <ContainerCode :value="container.code" size="sm" />
        <StatusBadge :kind="container.status" size="sm" />
      </div>
      <div v-if="container.destination_location" class="card-dest">
        {{ container.destination_location.house_name }} · {{ container.destination_location.name }}
      </div>
      <div class="card-meta">
        <span class="num">{{ container.item_count }}</span> ogg.
        <template v-if="container.children_count > 0">
          · <span class="num">{{ container.children_count }}</span> ann.
        </template>
        <template v-if="container.volume_liters">
          · <span class="num">{{ container.volume_liters.toFixed(0) }}</span>L
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ContainerSummary } from '@/stores/containers'
import Photo from '@/components/primitives/Photo.vue'
import ContainerCode from '@/components/primitives/ContainerCode.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

const props = defineProps<{ container: ContainerSummary }>()
defineEmits<{ click: [container: ContainerSummary] }>()

</script>

<style scoped>
.container-card {
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  overflow: hidden;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
}
.container-card:hover { box-shadow: var(--oco-shadow-3); border-color: var(--oco-line-strong); }

.card-photo { border-radius: 0; }

.card-body { padding: var(--oco-s-3) var(--oco-s-3) var(--oco-s-3); display: flex; flex-direction: column; gap: var(--oco-s-2); }

.card-top { display: flex; justify-content: space-between; align-items: center; }

.card-dest {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--oco-r-xl);
  background: var(--oco-surface-2);
  color: var(--oco-ink-3);
  border: 1px solid var(--oco-line);
  align-self: flex-start;
}

.card-meta { font-size: 12px; color: var(--oco-ink-4); }
.num { font-family: var(--oco-mono); font-variant-numeric: tabular-nums; color: var(--oco-ink-2); }
</style>
