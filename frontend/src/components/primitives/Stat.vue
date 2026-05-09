<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="oco-stat">
    <div class="stat-value num">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="sub" class="stat-sub">{{ sub }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ value: string | number; label: string; sub?: string }>()
</script>

<style scoped>
.oco-stat {
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  padding: var(--oco-s-4) var(--oco-s-4);
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: var(--oco-primary);
  font-family: var(--oco-mono);
  font-variant-numeric: tabular-nums;
  letter-spacing: -1px;
  line-height: 1;
}
.stat-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.4px;
  text-transform: uppercase;
  color: var(--oco-ink-3);
  margin-top: var(--oco-s-1);
}
.stat-sub { font-size: 11px; color: var(--oco-ink-4); }
</style>
