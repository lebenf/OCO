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
      <button :class="['group-btn', { active: groupByLocation }]" @click="groupByLocation = !groupByLocation">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
        </svg>
        {{ $t('container.list.group_by_location') }}
      </button>
    </div>

    <div v-if="store.loading" class="grid">
      <div v-for="i in 8" :key="i" class="skeleton"></div>
    </div>

    <template v-else-if="groupByLocation">
      <div v-if="store.containers.length === 0" class="empty">
        <p>{{ $t('container.list.empty') }}</p>
      </div>
      <div v-else class="groups">
        <div v-for="group in locationGroups" :key="group.locationId ?? '__none__'" class="location-group">
          <div class="location-header">
            <span class="location-name">{{ group.locationName }}</span>
            <span class="location-count num">{{ group.containers.length }}</span>
          </div>
          <div class="grid">
            <ContainerCard
              v-for="c in group.containers"
              :key="c.id"
              :container="c"
              @click="goToContainer(c.id)"
            />
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div v-if="store.containers.length === 0" class="empty">
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
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useContainersStore, type ContainerSummary } from '@/stores/containers'
import ContainerCard from '@/components/containers/ContainerCard.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const store = useContainersStore()
const { t } = useI18n()

const searchQuery = ref('')
const statusFilter = ref('')
const groupByLocation = ref(false)
let debounceTimer: ReturnType<typeof setTimeout>

async function doFetch(page = 1): Promise<void> {
  await store.fetchContainers(props.houseId, {
    search: searchQuery.value || undefined,
    status: statusFilter.value || undefined,
    page,
    size: groupByLocation.value ? 100 : 20,
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

interface LocationGroup {
  locationId: string | null
  locationName: string
  containers: ContainerSummary[]
}

const locationGroups = computed((): LocationGroup[] => {
  const map = new Map<string, LocationGroup>()
  const noLocKey = '__none__'

  for (const c of store.containers) {
    const key = c.current_location?.id ?? noLocKey
    if (!map.has(key)) {
      map.set(key, {
        locationId: c.current_location?.id ?? null,
        locationName: c.current_location?.name ?? t('container.list.no_location'),
        containers: [],
      })
    }
    map.get(key)!.containers.push(c)
  }

  // Sort: named locations first (alphabetically), then "no location"
  return [...map.values()].sort((a, b) => {
    if (a.locationId === null) return 1
    if (b.locationId === null) return -1
    return a.locationName.localeCompare(b.locationName)
  })
})

watch(groupByLocation, () => doFetch())
onMounted(() => doFetch())
</script>

<style scoped>
.container-list-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 1100px; }

.view-header { display: flex; justify-content: space-between; align-items: center; }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.filters { display: flex; gap: var(--oco-s-3); flex-wrap: wrap; }
.filters input { flex: 1; min-width: 140px; }
.filters select { width: 180px; flex-shrink: 0; }

.group-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 0 12px; height: 36px; border-radius: var(--oco-r-md);
  border: 1px solid var(--oco-line); background: var(--oco-surface);
  color: var(--oco-ink-3); font-size: 12px; font-weight: 500; cursor: pointer;
  white-space: nowrap; transition: all 0.12s;
}
.group-btn:hover { border-color: var(--oco-line-strong); color: var(--oco-ink); }
.group-btn.active { background: var(--oco-primary-soft); border-color: var(--oco-primary); color: var(--oco-primary-ink); }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--oco-s-4);
}

.groups { display: flex; flex-direction: column; gap: var(--oco-s-6); }
.location-group { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.location-header {
  display: flex; align-items: center; gap: var(--oco-s-2);
  padding-bottom: var(--oco-s-2);
  border-bottom: 2px solid var(--oco-line);
}
.location-name { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--oco-ink-3); }
.location-count {
  font-size: 11px; font-weight: 700;
  background: var(--oco-surface-2); color: var(--oco-ink-4);
  padding: 1px 6px; border-radius: 8px;
}

.skeleton {
  height: 200px; background: var(--oco-surface);
  border: 1px solid var(--oco-line); border-radius: var(--oco-r-lg);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty {
  display: flex; flex-direction: column; align-items: center;
  gap: var(--oco-s-3); padding: var(--oco-s-8);
  color: var(--oco-ink-4); text-align: center; font-size: 14px;
}

.pagination { display: flex; justify-content: center; align-items: center; gap: var(--oco-s-3); }
.page-btn {
  background: var(--oco-surface); border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-md); padding: 6px 14px;
  font-size: 16px; color: var(--oco-ink-2); cursor: pointer;
}
.page-btn:disabled { opacity: 0.4; cursor: default; }
.page-info { font-size: 13px; color: var(--oco-ink-3); }
</style>
