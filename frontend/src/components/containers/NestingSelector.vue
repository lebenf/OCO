<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="nesting-selector">
    <label class="field-label">{{ $t('container.nesting.label') }}</label>
    <select :value="modelValue" @change="emit('update:modelValue', ($event.target as HTMLSelectElement).value || null)">
      <option value="">{{ $t('container.nesting.none') }}</option>
      <option v-for="c in eligibleContainers" :key="c.id" :value="c.id">
        {{ c.code }} ({{ $t(`container.status.${c.status}`) }})
      </option>
    </select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ContainerSummary } from '@/stores/containers'

const props = defineProps<{
  modelValue: string | null
  containers: ContainerSummary[]
  excludeId?: string
}>()
const emit = defineEmits<{ 'update:modelValue': [value: string | null] }>()

const eligibleContainers = computed(() =>
  props.containers.filter(
    (c) => c.id !== props.excludeId && c.nesting_level < 2 && c.status === 'open',
  ),
)
</script>

<style scoped>
.nesting-selector { display: flex; flex-direction: column; gap: 0.25rem; }
.field-label { font-size: 0.875rem; color: #555; }
select {
  padding: 0.4rem 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
  background: #fff;
}
</style>
