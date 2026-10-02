<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="multi-pick">
    <input
      v-model="query"
      type="text"
      class="pick-search"
      :placeholder="$t('container.list.search')"
    />

    <div v-if="loading" class="pick-list">
      <div v-for="i in 3" :key="i" class="skeleton"></div>
    </div>
    <div v-else-if="filtered.length === 0" class="empty">
      {{ $t('container.list.empty') }}
    </div>
    <div v-else class="pick-list">
      <label
        v-for="c in filtered"
        :key="c.id"
        class="pick-row"
        :class="{ selected: selected.has(c.id) }"
      >
        <input type="checkbox" :checked="selected.has(c.id)" @change="toggle(c.id)" />
        <ContainerCode :value="c.code" size="sm" />
        <span v-if="c.description" class="pick-desc">{{ c.description }}</span>
        <span v-if="c.current_location" class="pick-loc">{{ c.current_location.name }}</span>
        <StatusBadge :kind="c.status" size="sm" />
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useContainersStore, type ContainerSummary } from '@/stores/containers'
import ContainerCode from '@/components/primitives/ContainerCode.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

const props = defineProps<{ houseId: string; excludeIds?: string[] }>()

const selected = defineModel<Set<string>>('selected', { required: true })

const store = useContainersStore()
const query = ref('')
const loading = ref(true)
const containers = ref<ContainerSummary[]>([])

const excludeSet = computed(() => new Set(props.excludeIds ?? []))

const filtered = computed(() => {
  const q = query.value.trim().toLowerCase()
  const base = containers.value.filter(c => !excludeSet.value.has(c.id))
  if (!q) return base
  return base.filter(c =>
    c.code.toLowerCase().includes(q) ||
    c.description?.toLowerCase().includes(q) ||
    c.current_location?.name.toLowerCase().includes(q)
  )
})

function toggle(id: string): void {
  const next = new Set(selected.value)
  if (next.has(id)) { next.delete(id) } else { next.add(id) }
  selected.value = next
}

onMounted(async () => {
  loading.value = true
  try {
    await store.fetchContainers(props.houseId, { size: 100 })
    containers.value = store.containers
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.multi-pick { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.pick-search {
  padding: 8px 10px; border: 1px solid var(--oco-line); border-radius: var(--oco-r-md);
  font-size: 14px; background: var(--oco-surface);
}

.pick-list { display: flex; flex-direction: column; gap: 2px; max-height: 280px; overflow-y: auto; }
.pick-row {
  display: flex; align-items: center; gap: var(--oco-s-2);
  padding: var(--oco-s-2) var(--oco-s-2); border-radius: var(--oco-r-md);
  font-size: 13px; cursor: pointer; transition: background 0.1s;
}
.pick-row:hover { background: var(--oco-surface-2); }
.pick-row.selected { background: var(--oco-primary-soft); }
.pick-desc {
  flex: 1; font-size: 12px; color: var(--oco-ink-3);
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.pick-loc { font-size: 12px; color: var(--oco-ink-4); }

.empty { color: var(--oco-ink-4); font-size: 13px; text-align: center; padding: var(--oco-s-4); }
.skeleton { height: 36px; background: var(--oco-surface-2); border-radius: var(--oco-r-md); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
