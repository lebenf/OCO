<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="search-view">
    <div class="search-header">
      <h2 class="view-title">{{ $t('search.title') }}</h2>
    </div>

    <!-- Search input -->
    <div class="search-bar">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        ref="inputRef"
        v-model="query"
        type="search"
        class="search-input"
        :placeholder="$t('search.placeholder')"
        autofocus
        @input="debouncedSearch"
      />
      <button v-if="query" class="clear-btn" @click="clearSearch">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="14" height="14">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>

    <!-- QR scan button -->
    <button class="qr-trigger" @click="showScanner = true">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
        <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
        <rect x="3" y="14" width="7" height="7" rx="1"/>
        <path d="M14 14h2v2h-2zm4 0h2v2h-2zm0 4h2v2h-2zm-4 4h2v2h-2zm4-4h2v2h-2z" fill="currentColor" stroke="none"/>
      </svg>
      {{ $t('search.qr_start') }}
    </button>

    <!-- Loading -->
    <div v-if="loading" class="skeleton-list">
      <div v-for="i in 4" :key="i" class="skeleton"></div>
    </div>

    <!-- No query yet -->
    <div v-else-if="!query" class="empty-state">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <p>{{ $t('search.start_typing') }}</p>
    </div>

    <!-- Results -->
    <div v-else-if="results" class="results">
      <div v-if="results.items.length === 0 && results.containers.length === 0" class="empty-state">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <p>{{ $t('search.no_results') }}</p>
      </div>

      <template v-if="results.containers.length > 0">
        <div class="section-label">{{ $t('search.containers') }} <span class="count">{{ results.containers.length }}</span></div>
        <SearchResultContainer
          v-for="c in results.containers"
          :key="c.id"
          :container="c"
          @click="router.push(`/houses/${houseId}/containers/${c.id}`)"
        />
      </template>

      <template v-if="results.items.length > 0">
        <div class="section-label">{{ $t('search.items') }} <span class="count">{{ results.items.length }}</span></div>
        <SearchResultItem
          v-for="item in results.items"
          :key="item.id"
          :item="item"
          @click="router.push(`/houses/${houseId}/items/${item.id}`)"
        />
      </template>
    </div>

    <QRScanner v-if="showScanner" @close="showScanner = false" @scanned="handleQR" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useDashboardStore, type SearchResults } from '@/stores/dashboard'
import { useContainersStore } from '@/stores/containers'
import SearchResultItem from '@/components/search/SearchResultItem.vue'
import SearchResultContainer from '@/components/search/SearchResultContainer.vue'
import QRScanner from '@/components/qr/QRScanner.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const dashboardStore = useDashboardStore()
const containersStore = useContainersStore()

const query = ref('')
const results = ref<SearchResults | null>(null)
const loading = ref(false)
const showScanner = ref(false)

let debounceTimer: ReturnType<typeof setTimeout>

function clearSearch(): void {
  query.value = ''
  results.value = null
}

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

async function handleQR(data: string): Promise<void> {
  showScanner.value = false
  const match = data.match(/([A-Z]-\d+)$/)
  const code = match ? match[1] : data.trim()
  try {
    const container = await containersStore.fetchContainer(props.houseId, code)
    router.push(`/houses/${props.houseId}/containers/${container.id}`)
  } catch {
    query.value = code
    debouncedSearch()
  }
}
</script>

<style scoped>
.search-view { display: flex; flex-direction: column; gap: var(--oco-s-4); max-width: 700px; }
.search-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.search-bar {
  display: flex;
  align-items: center;
  gap: var(--oco-s-2);
  background: var(--oco-surface);
  border: 1.5px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  padding: 0 var(--oco-s-3);
  transition: border-color 0.15s;
}
.search-bar:focus-within { border-color: var(--oco-primary); }
.search-icon { color: var(--oco-ink-4); flex-shrink: 0; }
.search-input {
  flex: 1;
  border: none;
  background: none;
  padding: 11px 0;
  font-size: 15px;
  color: var(--oco-ink);
  outline: none;
}
.search-input::placeholder { color: var(--oco-ink-4); }
.clear-btn {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border: none;
  background: var(--oco-surface-2);
  border-radius: 50%;
  color: var(--oco-ink-3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.qr-trigger {
  display: flex;
  align-items: center;
  gap: var(--oco-s-2);
  align-self: flex-start;
  padding: 9px var(--oco-s-4);
  border: 1.5px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  background: var(--oco-surface);
  color: var(--oco-ink-2);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  font-family: var(--oco-font-sans);
  transition: border-color 0.12s, background 0.12s;
}
.qr-trigger:hover { border-color: var(--oco-primary); background: var(--oco-primary-soft); color: var(--oco-primary); }

.results { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.section-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--oco-ink-4);
  padding: var(--oco-s-3) 0 var(--oco-s-1);
  display: flex;
  align-items: center;
  gap: var(--oco-s-2);
}
.count {
  font-size: 11px;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: var(--oco-r-xl);
  background: var(--oco-surface-2);
  color: var(--oco-ink-3);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--oco-s-3);
  padding: var(--oco-s-8);
  color: var(--oco-ink-4);
  font-size: 14px;
  text-align: center;
}
.empty-state p { margin: 0; }

.skeleton-list { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.skeleton { height: 56px; background: var(--oco-surface); border-radius: var(--oco-r-md); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
