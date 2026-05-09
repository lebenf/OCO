<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="category-selector">
    <label class="field-label">{{ $t('item.categories.label') }}</label>
    <div class="selected-chips">
      <span v-for="id in modelValue" :key="id" class="chip">
        {{ nameOf(id) }}
        <button type="button" class="remove-btn" @click="remove(id)">✕</button>
      </span>
    </div>
    <div class="add-row">
      <select @change="addExisting(($event.target as HTMLSelectElement).value); ($event.target as HTMLSelectElement).value = ''">
        <option value="">{{ $t('item.categories.add_existing') }}</option>
        <option v-for="cat in available" :key="cat.id" :value="cat.id">
          {{ cat.icon }} {{ cat.name }}
        </option>
      </select>
      <input
        v-model="newName"
        :placeholder="$t('item.categories.create_new')"
        @keydown.enter.prevent="createNew"
      />
      <button type="button" class="btn-add" @click="createNew" :disabled="!newName.trim()">+</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import type { CategoryOut } from '@/stores/categories'

const props = defineProps<{
  modelValue: string[]
  houseId: string
  allCategories: CategoryOut[]
}>()
const emit = defineEmits<{ 'update:modelValue': [ids: string[]] }>()

const store = useCategoriesStore()
const newName = ref('')

const available = computed(() =>
  props.allCategories.filter((c) => !props.modelValue.includes(c.id))
)

function nameOf(id: string): string {
  const cat = props.allCategories.find((c) => c.id === id)
  return cat ? `${cat.icon ?? ''} ${cat.name}`.trim() : id
}

function addExisting(id: string): void {
  if (id && !props.modelValue.includes(id)) {
    emit('update:modelValue', [...props.modelValue, id])
  }
}

function remove(id: string): void {
  emit('update:modelValue', props.modelValue.filter((x) => x !== id))
}

async function createNew(): Promise<void> {
  const name = newName.value.trim()
  if (!name) return
  const cat = await store.createCategory(props.houseId, { name })
  emit('update:modelValue', [...props.modelValue, cat.id])
  newName.value = ''
}
</script>

<style scoped>
.category-selector { display: flex; flex-direction: column; gap: 0.4rem; }
.field-label { font-size: 0.875rem; color: #555; }
.selected-chips { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.chip {
  display: inline-flex; align-items: center; gap: 0.25rem;
  background: #4a90e2; color: #fff; padding: 0.15rem 0.5rem;
  border-radius: 12px; font-size: 0.75rem;
}
.remove-btn { background: none; border: none; color: #fff; cursor: pointer; font-size: 0.75rem; padding: 0; }
.add-row { display: flex; gap: 0.4rem; }
.add-row select, .add-row input {
  padding: 0.35rem 0.5rem; border: 1px solid #ccc; border-radius: 4px; font-size: 0.875rem;
}
.btn-add {
  padding: 0.35rem 0.75rem; background: #4a90e2; color: #fff;
  border: none; border-radius: 4px; cursor: pointer; font-weight: 700;
}
.btn-add:disabled { opacity: 0.5; cursor: default; }
</style>
