<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="house-selector" ref="rootEl">
    <button
      class="hs-trigger"
      :class="{ 'hs-trigger--open': open }"
      @click="toggle"
      type="button"
    >
      <span class="hs-name">{{ housesStore.selectedHouse?.name ?? 'OCO' }}</span>
      <svg
        v-if="housesStore.houses.length > 1"
        class="hs-chevron"
        :class="{ 'hs-chevron--open': open }"
        width="12" height="12" viewBox="0 0 24 24"
        fill="none" stroke="currentColor" stroke-width="2.5"
      >
        <polyline points="6 9 12 15 18 9"/>
      </svg>
    </button>

    <Teleport to="body">
      <div v-if="open" class="hs-backdrop" @click="close" />
      <div v-if="open" class="hs-dropdown" :style="dropdownStyle">
        <div class="hs-dropdown-inner">
          <button
            v-for="h in housesStore.houses"
            :key="h.id"
            class="hs-option"
            :class="{ 'hs-option--active': h.id === housesStore.selectedHouseId }"
            type="button"
            @click="select(h.id)"
          >
            <span class="hs-option-name">{{ h.name }}</span>
            <svg v-if="h.id === housesStore.selectedHouseId"
              width="14" height="14" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="2.5"
            >
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </button>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useHousesStore } from '@/stores/houses'

const housesStore = useHousesStore()
const router = useRouter()
const rootEl = ref<HTMLElement | null>(null)
const open = ref(false)
const triggerRect = ref<DOMRect | null>(null)

const dropdownStyle = computed(() => {
  const r = triggerRect.value
  if (!r) return {}
  return {
    position: 'fixed' as const,
    top: `${r.bottom + 4}px`,
    left: `${r.left}px`,
    minWidth: `${Math.max(r.width, 160)}px`,
    zIndex: 500,
  }
})

function toggle() {
  if (housesStore.houses.length <= 1) {
    router.push(`/houses/${housesStore.selectedHouseId}`)
    return
  }
  if (!open.value) {
    triggerRect.value = rootEl.value?.getBoundingClientRect() ?? null
  }
  open.value = !open.value
}

function close() {
  open.value = false
}

function select(id: string) {
  housesStore.selectHouse(id)
  open.value = false
  router.push(`/houses/${id}`)
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') close()
}

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
</script>

<style scoped>
.house-selector { position: relative; display: inline-flex; }

.hs-trigger {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: var(--oco-r-sm);
  transition: background 0.12s;
  max-width: 200px;
}
.hs-trigger:hover { background: var(--oco-surface-2); }
.hs-trigger--open { background: var(--oco-surface-2); }

.hs-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--oco-ink-2);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hs-chevron {
  color: var(--oco-ink-4);
  flex-shrink: 0;
  transition: transform 0.15s;
}
.hs-chevron--open { transform: rotate(180deg); }

.hs-backdrop {
  position: fixed;
  inset: 0;
  z-index: 499;
}

.hs-dropdown {
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  box-shadow: var(--oco-shadow-lg);
  overflow: hidden;
}
.hs-dropdown-inner {
  display: flex;
  flex-direction: column;
  padding: 4px;
}

.hs-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--oco-s-3);
  padding: 8px 10px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: var(--oco-r-md);
  text-align: left;
  transition: background 0.1s;
  width: 100%;
}
.hs-option:hover { background: var(--oco-surface-2); }
.hs-option--active { color: var(--oco-primary); }

.hs-option-name {
  font-size: 13px;
  font-weight: 500;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
