<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="oco-field">
    <label v-if="label" class="field-label">{{ label }}<span v-if="required" class="req">*</span></label>
    <slot />
    <span v-if="hint" class="field-hint">{{ hint }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label?: string; hint?: string; required?: boolean }>()
</script>

<style scoped>
.oco-field { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--oco-ink-3);
}
.req { color: var(--oco-danger); margin-left: 2px; }
.field-hint { font-size: 11px; color: var(--oco-ink-4); }

/* Global style for inputs inside Field — applied via :deep in consuming components,
   but also providing a global .oco-input class for convenience */
</style>
