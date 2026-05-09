<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <span class="container-code" :class="`size-${size}`">{{ value }}</span>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ value: string; size?: 'sm' | 'md' }>(), { size: 'md' })
</script>

<style scoped>
.container-code {
  font-family: var(--oco-mono);
  font-feature-settings: 'zero','ss01';
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  background: var(--oco-surface-2);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-sm);
  letter-spacing: 0.5px;
  color: var(--oco-ink);
}
.size-sm { font-size: 11px; padding: 2px 6px; }
.size-md { font-size: 14px; padding: 4px 10px; }
</style>
