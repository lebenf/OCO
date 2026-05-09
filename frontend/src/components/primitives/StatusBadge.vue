<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <span class="status-badge" :class="[`status-${kind}`, `size-${size}`]">{{ label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = withDefaults(
  defineProps<{ kind: string; size?: 'sm' | 'md' }>(),
  { size: 'sm' }
)

const { t } = useI18n()

const label = computed(() => {
  const keyMap: Record<string, string> = {
    open: 'status.open', closed: 'status.closed', sealed: 'status.sealed',
    in_transit: 'status.in_transit', delivered: 'status.delivered',
    pending: 'status.pending', draft: 'status.pending',
    ready_for_review: 'status.ready', draft_ai_done: 'status.ready',
    confirmed: 'status.confirmed',
    failed: 'status.failed', draft_ai_failed: 'status.failed',
  }
  const key = keyMap[props.kind] ?? props.kind
  try { return t(key) } catch { return props.kind }
})
</script>

<style scoped>
.status-badge {
  display: inline-flex;
  align-items: center;
  font-weight: 600;
  border-radius: var(--oco-r-xl);
  white-space: nowrap;
}
.size-sm { font-size: 11px; padding: 2px 8px; }
.size-md { font-size: 13px; padding: 4px 12px; }

.status-open          { color: var(--oco-ok);      background: var(--oco-ok-soft); }
.status-closed        { color: var(--oco-warn);     background: var(--oco-warn-soft); }
.status-sealed        { color: var(--oco-info);     background: var(--oco-info-soft); }
.status-in_transit    { color: var(--oco-info);     background: var(--oco-info-soft); }
.status-delivered     { color: var(--oco-mute);     background: var(--oco-mute-soft); }
.status-pending       { color: var(--oco-warm-2);   background: var(--oco-warm-soft); }
.status-draft         { color: var(--oco-warm-2);   background: var(--oco-warm-soft); }
.status-ready_for_review { color: var(--oco-primary); background: var(--oco-primary-soft); }
.status-draft_ai_done { color: var(--oco-primary);  background: var(--oco-primary-soft); }
.status-confirmed     { color: var(--oco-ok);       background: var(--oco-ok-soft); }
.status-failed        { color: var(--oco-danger);   background: var(--oco-danger-soft); }
.status-draft_ai_failed { color: var(--oco-danger); background: var(--oco-danger-soft); }
.status-planned       { color: var(--oco-info);     background: var(--oco-info-soft); }
.status-in_progress   { color: var(--oco-warn);     background: var(--oco-warn-soft); }
.status-completed     { color: var(--oco-ok);       background: var(--oco-ok-soft); }
.status-cancelled     { color: var(--oco-mute);     background: var(--oco-mute-soft); }
</style>
