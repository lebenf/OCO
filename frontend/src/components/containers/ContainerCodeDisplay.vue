<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="code-display">
    <div class="code-label">{{ $t('container.code_display.label') }}</div>
    <div class="code-value">{{ code }}</div>
    <div v-if="description" class="code-desc">{{ description }}</div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ code: string; description?: string }>()
</script>

<style scoped>
.code-display { text-align: center; padding: 1.5rem; }
.code-label { font-size: 0.875rem; color: #888; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.05em; }
.code-value {
  font-family: monospace;
  font-size: 2.5rem;
  font-weight: 700;
  color: #222;
  background: #f4f6f9;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  display: inline-block;
}
.code-desc { margin-top: 0.5rem; color: #666; font-size: 0.875rem; }
</style>
