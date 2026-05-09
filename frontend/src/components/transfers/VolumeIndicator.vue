<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="volume-indicator">
    <div class="bar-track">
      <div class="bar-fill" :class="fillClass" :style="{ width: `${clampedPercent}%` }"></div>
    </div>
    <span class="vi-label num">{{ used.toFixed(0) }}L / {{ total.toFixed(0) }}L</span>
    <span class="vi-pct num" :class="fillClass">{{ percent.toFixed(0) }}%</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ used: number; total: number }>()

const percent = computed(() => props.total > 0 ? (props.used / props.total) * 100 : 0)
const clampedPercent = computed(() => Math.min(percent.value, 100))
const fillClass = computed(() => {
  if (percent.value >= 85) return 'fill-danger'
  if (percent.value >= 65) return 'fill-warn'
  return 'fill-ok'
})
</script>

<style scoped>
.volume-indicator { display: flex; align-items: center; gap: var(--oco-s-2); }
.bar-track { flex: 1; height: 6px; background: var(--oco-surface-3); border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.4s ease; }
.fill-ok     { background: var(--oco-primary); color: var(--oco-primary); }
.fill-warn   { background: var(--oco-warn);    color: var(--oco-warn); }
.fill-danger { background: var(--oco-danger);  color: var(--oco-danger); }
.vi-label { font-size: 11px; color: var(--oco-ink-4); white-space: nowrap; }
.vi-pct   { font-size: 11px; font-weight: 700; white-space: nowrap; }
</style>
