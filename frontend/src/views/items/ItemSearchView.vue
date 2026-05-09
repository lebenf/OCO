<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="item-search-view">
    <h2 class="view-title">{{ $t('item.search.title') }}</h2>

    <div class="search-bar">
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        v-model="query"
        type="search"
        class="search-input"
        :placeholder="$t('item.search.placeholder')"
        autofocus
        @input="debouncedSearch"
      />
    </div>

    <div v-if="loading" class="skeleton-list">
      <div v-for="i in 5" :key="i" class="skeleton"></div>
    </div>

    <div v-else-if="query && items.length === 0" class="empty-state">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <p>{{ $t('item.search.no_results') }}</p>
    </div>

    <div v-else class="results">
      <ItemCard
        v-for="item in items"
        :key="item.id"
        :item="item"
        @click="router.push(`/houses/${houseId}/items/${item.id}`)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useItemsStore, type ItemSummary } from '@/stores/items'
import ItemCard from '@/components/items/ItemCard.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const store = useItemsStore()

const query = ref('')
const items = ref<ItemSummary[]>([])
const loading = ref(false)
let debounceTimer: ReturnType<typeof setTimeout>

function debouncedSearch(): void {
  clearTimeout(debounceTimer)
  if (!query.value.trim()) { items.value = []; return }
  debounceTimer = setTimeout(async () => {
    loading.value = true
    try {
      const page = await store.fetchItems(props.houseId, { search: query.value, status: 'confirmed' })
      items.value = page.items
    } finally {
      loading.value = false
    }
  }, 300)
}
</script>

<style scoped>
.item-search-view { display: flex; flex-direction: column; gap: var(--oco-s-4); max-width: 700px; }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.search-bar {
  display: flex; align-items: center; gap: var(--oco-s-2);
  background: var(--oco-surface); border: 1.5px solid var(--oco-line);
  border-radius: var(--oco-r-lg); padding: 0 var(--oco-s-3);
  transition: border-color 0.15s;
}
.search-bar:focus-within { border-color: var(--oco-primary); }
.search-icon { color: var(--oco-ink-4); flex-shrink: 0; }
.search-input {
  flex: 1; border: none; background: none;
  padding: 11px 0; font-size: 15px; color: var(--oco-ink); outline: none;
}
.search-input::placeholder { color: var(--oco-ink-4); }

.results { display: flex; flex-direction: column; gap: var(--oco-s-1); }

.skeleton-list { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.skeleton { height: 56px; background: var(--oco-surface); border-radius: var(--oco-r-md); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty-state {
  display: flex; flex-direction: column; align-items: center; gap: var(--oco-s-3);
  padding: var(--oco-s-8); color: var(--oco-ink-4); font-size: 14px; text-align: center;
}
.empty-state p { margin: 0; }
</style>
