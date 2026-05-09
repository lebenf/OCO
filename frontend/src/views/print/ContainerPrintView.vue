<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="print-page">
    <div class="no-print controls">
      <button @click="doPrint">{{ $t('print.container.print') }}</button>
    </div>

    <div v-if="loading" class="loading">{{ $t('container.list.loading') }}</div>

    <div v-else-if="container" class="container-sheet">
      <div class="header">
        <div class="code-block">
          <div class="code">{{ container.code }}</div>
          <div v-if="container.description" class="name">{{ container.description }}</div>
        </div>
        <img :src="qrSrc" class="qr" alt="QR" />
      </div>

      <div v-if="container.width_cm" class="dimensions">
        {{ container.width_cm }} × {{ container.depth_cm }} × {{ container.height_cm }} cm
      </div>

      <h3>{{ $t('print.container.items') }}</h3>
      <ul v-if="container.items?.length" class="items-list">
        <li v-for="item in container.items" :key="item.id">
          <strong>{{ item.name }}</strong>
          <span v-if="item.brand" class="meta"> — {{ item.brand }}</span>
          <span v-if="item.quantity && item.quantity > 1" class="meta"> ×{{ item.quantity }}</span>
          <p v-if="item.description" class="desc">{{ item.description }}</p>
        </li>
      </ul>
      <p v-else class="empty">{{ $t('print.container.no_items') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const props = defineProps<{ houseId: string; code: string }>()

interface ItemOut {
  id: string
  name: string
  brand?: string
  quantity?: number
  description?: string
}
interface ContainerOut {
  id: string
  code: string
  description?: string
  width_cm?: number
  depth_cm?: number
  height_cm?: number
  items?: ItemOut[]
}

const loading = ref(true)
const container = ref<ContainerOut | null>(null)
const qrSrc = computed(() =>
  container.value ? `/api/houses/${props.houseId}/containers/${container.value.id}/qr` : ''
)

function doPrint() {
  window.print()
}

onMounted(async () => {
  const { data } = await api.get<ContainerOut>(`/houses/${props.houseId}/containers/${props.code}`)
  container.value = data
  loading.value = false
})
</script>

<style scoped>
.print-page { font-family: sans-serif; color: #000; background: #fff; padding: 1.5rem; min-height: 100vh; }
.controls { margin-bottom: 1rem; }
.controls button { padding: .5rem 1.2rem; background: #7c3aed; color: #fff; border: none; border-radius: 6px; cursor: pointer; font-size: 1rem; }
.container-sheet { max-width: 640px; }
.header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 1rem; gap: 1rem; }
.code-block { flex: 1; }
.code { font-size: 2.5rem; font-weight: 700; letter-spacing: .05em; line-height: 1; }
.name { font-size: 1.1rem; color: #555; margin-top: .4rem; }
.qr { width: 120px; height: 120px; flex-shrink: 0; }
.dimensions { font-size: .9rem; color: #666; margin-bottom: 1rem; }
h3 { font-size: 1rem; text-transform: uppercase; letter-spacing: .05em; color: #444; margin-bottom: .5rem; }
.items-list { list-style: none; padding: 0; margin: 0; }
.items-list li { padding: .5rem 0; border-bottom: 1px solid #eee; }
.meta { color: #666; font-size: .9rem; }
.desc { font-size: .85rem; color: #888; margin: .15rem 0 0; }
.empty { color: #999; }

@media print {
  .no-print { display: none !important; }
  .print-page { padding: 0; }
}
</style>
