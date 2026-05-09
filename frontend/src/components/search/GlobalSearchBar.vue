<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="global-search">
    <button class="search-trigger" @click="open = true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <span class="trigger-text">{{ $t('search.placeholder') }}</span>
      <kbd class="kbd">⌘K</kbd>
    </button>

    <Teleport to="body">
      <div v-if="open" class="overlay" @click.self="close">
        <div class="modal">
          <div class="modal-search">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16" class="modal-icon">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              ref="inputRef"
              v-model="query"
              class="modal-input"
              :placeholder="$t('search.placeholder')"
              @input="debouncedSearch"
              @keydown.escape="close"
            />
            <button v-if="query" class="clear-btn" @click="query = ''; results = null">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <div v-if="loading" class="modal-feedback">
            <div class="sk-list">
              <div v-for="i in 3" :key="i" class="sk"></div>
            </div>
          </div>

          <div v-else-if="results && query.length >= 2" class="modal-results">
            <div v-if="results.items.length === 0 && results.containers.length === 0" class="modal-feedback">
              {{ $t('search.no_results') }}
            </div>

            <template v-if="results.containers.length > 0">
              <div class="section-label">{{ $t('search.containers') }}</div>
              <SearchResultContainer
                v-for="c in results.containers"
                :key="c.id"
                :container="c"
                @click="goToContainer(c)"
              />
            </template>

            <template v-if="results.items.length > 0">
              <div class="section-label">{{ $t('search.items') }}</div>
              <SearchResultItem
                v-for="item in results.items"
                :key="item.id"
                :item="item"
                @click="goToItem(item)"
              />
            </template>
          </div>

          <div v-else-if="!query" class="modal-hint">
            {{ $t('search.start_typing') }}
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore, type SearchResults } from '@/stores/dashboard'
import type { ItemSummary } from '@/stores/items'
import type { ContainerSummary } from '@/stores/containers'
import SearchResultItem from './SearchResultItem.vue'
import SearchResultContainer from './SearchResultContainer.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const dashboardStore = useDashboardStore()

const open = ref(false)
const query = ref('')
const loading = ref(false)
const results = ref<SearchResults | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

let debounceTimer: ReturnType<typeof setTimeout>

watch(open, async (val) => {
  if (val) {
    query.value = ''
    results.value = null
    await nextTick()
    inputRef.value?.focus()
  }
})

function debouncedSearch(): void {
  clearTimeout(debounceTimer)
  if (query.value.length < 2) { results.value = null; return }
  debounceTimer = setTimeout(async () => {
    loading.value = true
    try {
      results.value = await dashboardStore.search(props.houseId, query.value)
    } finally {
      loading.value = false
    }
  }, 300)
}

function close(): void { open.value = false }

function goToItem(item: ItemSummary): void { router.push(`/houses/${props.houseId}/items/${item.id}`); close() }
function goToContainer(c: ContainerSummary): void { router.push(`/houses/${props.houseId}/containers/${c.id}`); close() }

function handleKeydown(e: KeyboardEvent): void {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); open.value = !open.value }
}

onMounted(() => document.addEventListener('keydown', handleKeydown))
onUnmounted(() => document.removeEventListener('keydown', handleKeydown))
</script>

<style scoped>
.search-trigger {
  display: flex;
  align-items: center;
  gap: var(--oco-s-2);
  background: var(--oco-surface-2);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-xl);
  padding: 6px 12px;
  cursor: pointer;
  color: var(--oco-ink-3);
  transition: border-color 0.12s, background 0.12s;
}
.search-trigger:hover { border-color: var(--oco-primary); background: var(--oco-primary-soft); color: var(--oco-primary); }
.trigger-text { font-size: 13px; font-family: var(--oco-font-sans); }
.kbd {
  font-size: 11px;
  font-family: var(--oco-font-mono);
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-sm);
  padding: 1px 5px;
  color: var(--oco-ink-4);
}

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(20,18,28,0.4);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 10vh;
  z-index: 400;
  backdrop-filter: blur(2px);
}

.modal {
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-xl);
  width: min(640px, 90vw);
  max-height: 70vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--oco-shadow-lg);
  overflow: hidden;
}

.modal-search {
  display: flex;
  align-items: center;
  gap: var(--oco-s-2);
  padding: 0 var(--oco-s-4);
  border-bottom: 1px solid var(--oco-line);
}
.modal-icon { color: var(--oco-ink-4); flex-shrink: 0; }
.modal-input {
  flex: 1;
  border: none;
  background: none;
  padding: 16px 0;
  font-size: 16px;
  color: var(--oco-ink);
  outline: none;
  font-family: var(--oco-font-sans);
}
.modal-input::placeholder { color: var(--oco-ink-4); }
.clear-btn {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border: none;
  background: var(--oco-surface-2);
  border-radius: 50%;
  color: var(--oco-ink-3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-results { overflow-y: auto; padding: var(--oco-s-2) var(--oco-s-2); }
.modal-feedback { padding: var(--oco-s-5); text-align: center; color: var(--oco-ink-4); font-size: 14px; }
.modal-hint { padding: var(--oco-s-4) var(--oco-s-5); font-size: 13px; color: var(--oco-ink-4); }

.section-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--oco-ink-4);
  padding: var(--oco-s-3) var(--oco-s-3) var(--oco-s-1);
}

.sk-list { display: flex; flex-direction: column; gap: var(--oco-s-2); padding: var(--oco-s-3); }
.sk { height: 48px; background: var(--oco-surface-2); border-radius: var(--oco-r-md); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
