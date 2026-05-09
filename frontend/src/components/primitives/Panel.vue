<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <section class="oco-panel">
    <div v-if="title || $slots.action" class="panel-header">
      <h3 class="panel-title">{{ title }}</h3>
      <div v-if="$slots.action" class="panel-action"><slot name="action" /></div>
    </div>
    <div class="panel-body"><slot /></div>
  </section>
</template>

<script setup lang="ts">
defineProps<{ title?: string }>()
</script>

<style scoped>
.oco-panel {
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  overflow: hidden;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--oco-s-4) var(--oco-s-5);
  border-bottom: 1px solid var(--oco-line);
}
.panel-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.3px;
  text-transform: uppercase;
  color: var(--oco-ink-3);
}
.panel-action { flex-shrink: 0; }
.panel-body { padding: var(--oco-s-4) var(--oco-s-5); }
</style>
