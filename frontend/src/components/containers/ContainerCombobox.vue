<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="combobox" ref="rootEl">
    <div class="combobox-input-wrap">
      <input
        ref="inputEl"
        v-model="query"
        type="text"
        :placeholder="placeholder"
        autocomplete="off"
        @focus="open"
        @keydown.down.prevent="moveDown"
        @keydown.up.prevent="moveUp"
        @keydown.enter.prevent="confirmHighlighted"
        @keydown.escape="close"
        @input="onInput"
      />
      <button class="combobox-arrow" tabindex="-1" @mousedown.prevent="toggleDropdown">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>
    </div>

    <Teleport to="body">
      <div v-if="isOpen" class="combobox-dropdown" :style="dropdownStyle">
        <div v-if="filtered.length === 0" class="combobox-empty">{{ $t('container.list.empty') }}</div>
        <button
          v-for="(c, i) in filtered"
          :key="c.id"
          :class="['combobox-item', { highlighted: i === highlightedIndex }]"
          @mousedown.prevent="select(c)"
          @mouseover="highlightedIndex = i"
        >
          <span class="item-code mono">{{ c.code }}</span>
          <StatusBadge :kind="c.status" size="sm" />
          <span v-if="c.current_location" class="item-loc">{{ c.current_location.name }}</span>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useContainersStore, type ContainerSummary } from '@/stores/containers'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

const props = defineProps<{
  houseId: string
  placeholder?: string
}>()

const emit = defineEmits<{
  select: [container: ContainerSummary]
}>()

const store = useContainersStore()
const rootEl = ref<HTMLElement | null>(null)
const inputEl = ref<HTMLInputElement | null>(null)
const query = ref('')
const isOpen = ref(false)
const highlightedIndex = ref(-1)
const dropdownStyle = ref({})

const containers = computed(() => store.containers)

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return containers.value
  return containers.value.filter(c =>
    c.code.toLowerCase().includes(q) ||
    c.current_location?.name.toLowerCase().includes(q)
  )
})

function computeDropdownPosition(): void {
  if (!rootEl.value) return
  const rect = rootEl.value.getBoundingClientRect()
  dropdownStyle.value = {
    position: 'fixed',
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`,
    zIndex: 9999,
  }
}

async function open(): Promise<void> {
  if (!store.containers.length) {
    await store.fetchContainers(props.houseId, { size: 100 })
  }
  computeDropdownPosition()
  isOpen.value = true
  highlightedIndex.value = -1
}

function close(): void {
  isOpen.value = false
  highlightedIndex.value = -1
}

function toggleDropdown(): void {
  if (isOpen.value) { close() } else { inputEl.value?.focus(); open() }
}

function onInput(): void {
  isOpen.value = true
  highlightedIndex.value = -1
}

function select(c: ContainerSummary): void {
  query.value = c.code
  emit('select', c)
  close()
}

function moveDown(): void {
  if (!isOpen.value) { open(); return }
  highlightedIndex.value = Math.min(highlightedIndex.value + 1, filtered.value.length - 1)
}

function moveUp(): void {
  highlightedIndex.value = Math.max(highlightedIndex.value - 1, 0)
}

function confirmHighlighted(): void {
  if (highlightedIndex.value >= 0 && filtered.value[highlightedIndex.value]) {
    select(filtered.value[highlightedIndex.value])
  }
}

function onClickOutside(e: MouseEvent): void {
  if (rootEl.value && !rootEl.value.contains(e.target as Node)) close()
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', onClickOutside))
</script>

<style scoped>
.combobox { position: relative; width: 100%; }

.combobox-input-wrap {
  display: flex;
  align-items: stretch;
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-md);
  overflow: hidden;
  background: var(--oco-surface);
  transition: border-color 0.12s;
}
.combobox-input-wrap:focus-within { border-color: var(--oco-primary); }

.combobox-input-wrap input {
  flex: 1;
  border: none;
  outline: none;
  padding: 8px 10px;
  background: transparent;
  font-size: 14px;
  color: var(--oco-ink);
}

.combobox-arrow {
  display: flex; align-items: center; justify-content: center;
  width: 32px; border: none; border-left: 1px solid var(--oco-line);
  background: var(--oco-surface-2); color: var(--oco-ink-3); cursor: pointer;
  transition: background 0.12s;
  flex-shrink: 0;
}
.combobox-arrow:hover { background: var(--oco-surface-3); color: var(--oco-ink); }
</style>

<style>
.combobox-dropdown {
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  box-shadow: var(--oco-shadow-lg);
  max-height: 260px;
  overflow-y: auto;
  padding: 4px;
}

.combobox-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 7px 10px;
  border: none;
  background: none;
  border-radius: var(--oco-r-md);
  cursor: pointer;
  text-align: left;
  transition: background 0.1s;
}
.combobox-item.highlighted,
.combobox-item:hover { background: var(--oco-surface-2); }

.item-code { font-size: 13px; font-weight: 600; color: var(--oco-ink); flex-shrink: 0; }
.item-loc { font-size: 12px; color: var(--oco-ink-4); flex: 1; text-align: right; }

.combobox-empty { padding: 12px; font-size: 13px; color: var(--oco-ink-4); text-align: center; }
</style>
