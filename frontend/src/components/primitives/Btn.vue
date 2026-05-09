<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <component
    :is="to ? 'RouterLink' : 'button'"
    class="oco-btn"
    :class="`btn-${kind}`"
    :to="to"
    :type="to ? undefined : type"
    :disabled="disabled"
    v-bind="$attrs"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    kind?: 'primary' | 'accent' | 'ghost' | 'soft' | 'warm' | 'danger'
    type?: 'button' | 'submit' | 'reset'
    disabled?: boolean
    to?: string
  }>(),
  { kind: 'primary', type: 'button', disabled: false }
)
</script>

<style scoped>
.oco-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--oco-r-md);
  font-family: var(--oco-font);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  text-decoration: none;
  transition: background 0.15s, opacity 0.15s, box-shadow 0.15s;
  white-space: nowrap;
  line-height: 1;
}
.oco-btn:hover { text-decoration: none; }
.oco-btn:disabled { opacity: 0.55; cursor: not-allowed; pointer-events: none; }

.btn-primary   { background: var(--oco-primary);      color: #fff; }
.btn-primary:hover   { background: var(--oco-primary-2); }
.btn-accent    { background: var(--oco-warm);          color: #fff; }
.btn-accent:hover    { background: var(--oco-warm-2); }
.btn-ghost     { background: transparent; color: var(--oco-ink-2); border: 1px solid var(--oco-line); }
.btn-ghost:hover     { background: var(--oco-surface-2); }
.btn-soft      { background: var(--oco-primary-soft);  color: var(--oco-primary-ink); }
.btn-soft:hover      { background: var(--oco-primary-soft); filter: brightness(0.95); }
.btn-warm      { background: var(--oco-warm-soft);     color: var(--oco-warm-2); border: 1px solid var(--oco-warm-soft); }
.btn-warm:hover      { background: var(--oco-warm); color: #fff; }
.btn-danger    { background: var(--oco-danger-soft);   color: var(--oco-danger); border: 1px solid var(--oco-danger-soft); }
.btn-danger:hover    { background: var(--oco-danger); color: #fff; }
</style>
