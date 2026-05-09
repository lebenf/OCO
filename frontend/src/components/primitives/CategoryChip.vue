<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <span class="category-chip">
    <span class="chip-dot" :style="{ background: dotColor }"></span>
    {{ label }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ label: string; hue?: number }>()

const dotColor = computed(() =>
  props.hue !== undefined ? `oklch(0.60 0.13 ${props.hue})` : 'var(--oco-ink-4)'
)
</script>

<style scoped>
.category-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: var(--oco-r-xl);
  background: var(--oco-surface-2);
  border: 1px solid var(--oco-line);
  color: var(--oco-ink-2);
}
.chip-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>
