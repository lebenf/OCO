<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="hint-type-selector">
    <label class="field-label">{{ $t('ai.hint_type.label') }}</label>
    <div class="options">
      <button
        v-for="opt in options"
        :key="opt.value"
        class="hint-btn"
        :class="{ active: modelValue === opt.value }"
        type="button"
        @click="emit('update:modelValue', opt.value)"
      >
        <span class="icon">{{ opt.icon }}</span>
        <span class="label">{{ $t(`ai.hint_type.${opt.value}`) }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
const options = [
  { value: 'auto', icon: '🔍' },
  { value: 'single', icon: '📦' },
  { value: 'set', icon: '📚' },
  { value: 'collection', icon: '🗂️' },
  { value: 'book', icon: '📖' },
]

defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<style scoped>
.hint-type-selector { display: flex; flex-direction: column; gap: 0.5rem; }
.field-label { font-size: 0.875rem; color: #555; }
.options { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.hint-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
  min-width: 70px;
  transition: all 0.15s;
}
.hint-btn:hover { border-color: #4a90e2; }
.hint-btn.active { border-color: #4a90e2; background: #e8f0fc; }
.icon { font-size: 1.25rem; }
.label { font-size: 0.7rem; color: #555; }
</style>
