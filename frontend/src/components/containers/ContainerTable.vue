<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="table-wrap">
    <table class="container-table">
      <thead>
        <tr>
          <th class="col-check">
            <input
              type="checkbox"
              :checked="allSelected"
              :title="$t('container.list.select_all_page_hint')"
              @change="toggleAll"
            />
          </th>
          <th v-for="col in columns" :key="col.key" class="sortable" @click="toggleSort(col.key)">
            <span class="th-label">
              {{ $t(col.labelKey) }}
              <svg
                v-if="sortKey === col.key"
                class="sort-icon"
                :class="{ desc: sortDir === 'desc' }"
                width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"
              >
                <polyline points="6 9 12 15 18 9"/>
              </svg>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="sortedContainers.length === 0">
          <td :colspan="columns.length + 1" class="empty-cell">{{ $t('container.list.empty') }}</td>
        </tr>
        <tr
          v-for="c in sortedContainers"
          :key="c.id"
          :class="{ selected: selected.has(c.id) }"
        >
          <td class="col-check">
            <input type="checkbox" :checked="selected.has(c.id)" @change="toggleRow(c.id)" />
          </td>
          <td @click="emit('row-click', c.id)"><ContainerCode :value="c.code" size="sm" /></td>
          <td class="desc-cell" @click="emit('row-click', c.id)">{{ c.description ?? '—' }}</td>
          <td @click="emit('row-click', c.id)"><StatusBadge :kind="c.status" size="sm" /></td>
          <td @click="emit('row-click', c.id)">{{ c.current_location?.name ?? '—' }}</td>
          <td @click="emit('row-click', c.id)">{{ c.destination_location?.name ?? '—' }}</td>
          <td class="num" @click="emit('row-click', c.id)">{{ c.item_count }}</td>
          <td class="num" @click="emit('row-click', c.id)">{{ c.volume_liters != null ? `${c.volume_liters.toFixed(0)}L` : '—' }}</td>
          <td class="num" @click="emit('row-click', c.id)">{{ c.children_count }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ContainerSummary } from '@/stores/containers'
import ContainerCode from '@/components/primitives/ContainerCode.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'

type SortKey =
  | 'code' | 'description' | 'status' | 'current_location' | 'destination_location'
  | 'item_count' | 'volume_liters' | 'children_count'

const props = defineProps<{ containers: ContainerSummary[] }>()
const emit = defineEmits<{ 'row-click': [id: string] }>()

const selected = defineModel<Set<string>>('selected', { required: true })

const columns: { key: SortKey; labelKey: string }[] = [
  { key: 'code', labelKey: 'container.list.col_code' },
  { key: 'description', labelKey: 'container.list.col_description' },
  { key: 'status', labelKey: 'container.list.col_status' },
  { key: 'current_location', labelKey: 'container.list.col_current_location' },
  { key: 'destination_location', labelKey: 'container.list.col_destination_location' },
  { key: 'item_count', labelKey: 'container.list.col_items' },
  { key: 'volume_liters', labelKey: 'container.list.col_volume' },
  { key: 'children_count', labelKey: 'container.list.col_children' },
]

const sortKey = ref<SortKey>('code')
const sortDir = ref<'asc' | 'desc'>('asc')

function toggleSort(key: SortKey): void {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function compareNullable(a: number | null, b: number | null, dir: number): number {
  if (a === null && b === null) return 0
  if (a === null) return 1
  if (b === null) return -1
  return (a - b) * dir
}

function compareNullableString(a: string | null, b: string | null, dir: number): number {
  const an = a === null || a === '' ? null : a
  const bn = b === null || b === '' ? null : b
  if (an === null && bn === null) return 0
  if (an === null) return 1
  if (bn === null) return -1
  return an.localeCompare(bn) * dir
}

const sortedContainers = computed(() => {
  const dir = sortDir.value === 'asc' ? 1 : -1
  const key = sortKey.value
  return [...props.containers].sort((a, b) => {
    switch (key) {
      case 'code':
        return a.code.localeCompare(b.code) * dir
      case 'description':
        return compareNullableString(a.description, b.description, dir)
      case 'status':
        return a.status.localeCompare(b.status) * dir
      case 'current_location':
        return compareNullableString(a.current_location?.name ?? null, b.current_location?.name ?? null, dir)
      case 'destination_location':
        return compareNullableString(a.destination_location?.name ?? null, b.destination_location?.name ?? null, dir)
      case 'item_count':
        return (a.item_count - b.item_count) * dir
      case 'volume_liters':
        return compareNullable(a.volume_liters, b.volume_liters, dir)
      case 'children_count':
        return (a.children_count - b.children_count) * dir
      default:
        return 0
    }
  })
})

const allSelected = computed(() =>
  sortedContainers.value.length > 0 && sortedContainers.value.every(c => selected.value.has(c.id))
)

function toggleRow(id: string): void {
  const next = new Set(selected.value)
  if (next.has(id)) { next.delete(id) } else { next.add(id) }
  selected.value = next
}

function toggleAll(): void {
  selected.value = allSelected.value
    ? new Set()
    : new Set(sortedContainers.value.map(c => c.id))
}
</script>

<style scoped>
.table-wrap { overflow-x: auto; }

.container-table { width: 100%; border-collapse: collapse; min-width: 720px; }

.container-table th {
  font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
  color: var(--oco-ink-4); padding: var(--oco-s-2) var(--oco-s-3); text-align: left;
  border-bottom: 1px solid var(--oco-line); white-space: nowrap;
}
.container-table th.sortable { cursor: pointer; user-select: none; }
.container-table th.sortable:hover { color: var(--oco-ink-2); }

.th-label { display: inline-flex; align-items: center; gap: 4px; }
.sort-icon { transition: transform 0.12s; }
.sort-icon.desc { transform: rotate(180deg); }

.container-table td {
  padding: var(--oco-s-2) var(--oco-s-3); font-size: 13px; color: var(--oco-ink);
  border-bottom: 1px solid var(--oco-line); cursor: pointer;
}
.container-table tr:last-child td { border-bottom: none; }
.container-table tr:hover td { background: var(--oco-surface-2); }
.container-table tr.selected td { background: var(--oco-primary-soft); }

.col-check { cursor: default; width: 32px; }
.desc-cell {
  max-width: 220px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  color: var(--oco-ink-3);
}
.num { font-family: var(--oco-mono); font-variant-numeric: tabular-nums; text-align: right; }

.empty-cell { text-align: center; padding: var(--oco-s-6); color: var(--oco-ink-4); font-size: 13px; cursor: default; }
</style>
