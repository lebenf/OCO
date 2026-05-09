<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="container-list-view">
    <div class="view-header">
      <h2 class="view-title">{{ $t('container.list.title') }}</h2>
      <Btn :to="`/houses/${houseId}/containers/create`">+ {{ $t('container.list.create') }}</Btn>
    </div>

    <div class="filters">
      <input v-model="searchQuery" :placeholder="$t('container.list.search')" @input="debouncedFetch" />
      <select v-model="statusFilter" @change="() => doFetch()">
        <option value="">{{ $t('container.list.all_statuses') }}</option>
        <option value="open">{{ $t('status.open') }}</option>
        <option value="closed">{{ $t('status.closed') }}</option>
        <option value="sealed">{{ $t('status.sealed') }}</option>
      </select>
    </div>

    <div v-if="store.loading" class="grid">
      <div v-for="i in 8" :key="i" class="skeleton"></div>
    </div>

    <div v-else-if="store.containers.length === 0" class="empty">
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3">
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      </svg>
      <p>{{ $t('container.list.empty') }}</p>
    </div>

    <div v-else class="grid">
      <ContainerCard
        v-for="c in store.containers"
        :key="c.id"
        :container="c"
        @click="goToContainer(c.id)"
      />
    </div>

    <div v-if="store.totalPages > 1" class="pagination">
      <button :disabled="store.currentPage <= 1" class="page-btn" @click="changePage(store.currentPage - 1)">‹</button>
      <span class="page-info num">{{ store.currentPage }} / {{ store.totalPages }}</span>
      <button :disabled="store.currentPage >= store.totalPages" class="page-btn" @click="changePage(store.currentPage + 1)">›</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useContainersStore } from '@/stores/containers'
import ContainerCard from '@/components/containers/ContainerCard.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const store = useContainersStore()

const searchQuery = ref('')
const statusFilter = ref('')
let debounceTimer: ReturnType<typeof setTimeout>

async function doFetch(page = 1): Promise<void> {
  await store.fetchContainers(props.houseId, {
    search: searchQuery.value || undefined,
    status: statusFilter.value || undefined,
    page,
  })
}
function debouncedFetch(): void {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => doFetch(), 300)
}
function changePage(page: number): void { doFetch(page) }
function goToContainer(id: string): void {
  router.push(`/houses/${props.houseId}/containers/${id}`)
}
onMounted(() => doFetch())
</script>

<style scoped>
.container-list-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 1100px; }

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.view-title {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.4px;
}

.filters {
  display: flex;
  gap: var(--oco-s-3);
}
.filters input { flex: 1; }
.filters select { width: 180px; flex-shrink: 0; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--oco-s-4);
}

.skeleton {
  height: 200px;
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--oco-s-3);
  padding: var(--oco-s-8);
  color: var(--oco-ink-4);
  text-align: center;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--oco-s-3);
}
.page-btn {
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-md);
  padding: 6px 14px;
  font-size: 16px;
  color: var(--oco-ink-2);
  cursor: pointer;
}
.page-btn:disabled { opacity: 0.4; cursor: default; }
.page-info { font-size: 13px; color: var(--oco-ink-3); }
</style>
