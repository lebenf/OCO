<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <span class="item-status-badge" :class="`status-${status}`">
    <span class="dot"></span>
    {{ $t(`ai.item_status.${status}`) }}
  </span>
</template>

<script setup lang="ts">
defineProps<{ status: string }>()
</script>

<style scoped>
.item-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  background: #e9ecef;
  color: #555;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
.status-draft { background: #e9ecef; color: #888; }
.status-draft_ai_done { background: #d4edda; color: #155724; }
.status-draft_ai_failed { background: #f8d7da; color: #721c24; }
.status-confirmed { background: #cce5ff; color: #004085; }
</style>
