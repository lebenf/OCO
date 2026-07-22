<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="print-page">
    <div class="no-print controls">
      <label>
        {{ $t('print.labels.count') }}
        <input type="number" v-model.number="count" min="1" max="60" />
      </label>
      <label>
        {{ $t('print.labels.columns') }}
        <input type="number" v-model.number="columns" min="1" max="6" />
      </label>
      <a :href="pdfUrl" target="_blank" rel="noopener" class="btn">{{ $t('print.labels.open_pdf') }}</a>
    </div>

    <iframe :src="pdfUrl" class="pdf-frame"></iframe>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = defineProps<{ houseId: string; containerId: string }>()

const STORAGE_KEY = 'oco.labels.layout'
const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}')

const count = ref<number>(stored.count ?? 6)
const columns = ref<number>(stored.columns ?? 2)

const pdfUrl = computed(
  () =>
    `/api/houses/${props.houseId}/containers/${props.containerId}/labels/pdf?count=${count.value}&columns=${columns.value}`
)

watch([count, columns], () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ count: count.value, columns: columns.value }))
})
</script>

<style scoped>
.print-page { display: flex; flex-direction: column; height: 100vh; font-family: sans-serif; background: #fff; }
.controls { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.5rem; border-bottom: 1px solid #eee; }
.controls label { display: flex; flex-direction: column; gap: .25rem; font-size: .85rem; color: #555; }
.controls input { width: 70px; padding: .3rem .5rem; border: 1px solid #ccc; border-radius: 4px; }
.btn {
  margin-left: auto;
  padding: .5rem 1.2rem; background: #7c3aed; color: #fff;
  border: none; border-radius: 6px; cursor: pointer; font-size: .9rem;
  text-decoration: none;
}
.pdf-frame { flex: 1; border: none; width: 100%; }

@media print {
  .no-print { display: none !important; }
}
</style>
