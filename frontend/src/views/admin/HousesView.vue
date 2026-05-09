<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="admin-view">
    <h2 class="view-title">{{ $t('admin.houses.title') }}</h2>

    <Panel :title="$t('admin.create')">
      <form class="row-form" @submit.prevent="handleCreate">
        <input v-model="form.name" :placeholder="$t('admin.houses.name')" required />
        <input v-model="form.code_prefix" :placeholder="$t('admin.houses.prefix')" maxlength="1" required style="width:72px" />
        <input v-model="form.description" :placeholder="$t('admin.houses.description')" />
        <Btn type="submit" :disabled="saving">{{ $t('admin.create') }}</Btn>
      </form>
    </Panel>

    <Panel v-if="houses.length">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{{ $t('admin.houses.name') }}</th>
              <th>{{ $t('admin.houses.prefix') }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="h in houses" :key="h.id">
              <td>{{ h.name }}</td>
              <td><span class="code-pill mono">{{ h.code_prefix }}</span></td>
              <td>
                <Btn kind="ghost" :to="`/admin/houses/${h.id}`" style="font-size:12px;padding:3px 8px">
                  {{ $t('admin.manage') }}
                </Btn>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Panel>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import type { HouseOut } from '@/stores/houses'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

const houses = ref<HouseOut[]>([])
const saving = ref(false)
const form = ref({ name: '', code_prefix: '', description: '' })

async function loadHouses(): Promise<void> {
  const res = await api.get('/admin/houses')
  houses.value = res.data.items
}

async function handleCreate(): Promise<void> {
  saving.value = true
  try {
    await api.post('/admin/houses', form.value)
    form.value = { name: '', code_prefix: '', description: '' }
    await loadHouses()
  } finally {
    saving.value = false
  }
}

onMounted(loadHouses)
</script>

<style scoped>
.admin-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 700px; }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.row-form { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; align-items: center; }

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th {
  font-size: 10px; font-weight: 700; letter-spacing: 0.5px; text-transform: uppercase;
  color: var(--oco-ink-4); padding: var(--oco-s-2) var(--oco-s-3); text-align: left;
  border-bottom: 1px solid var(--oco-line);
}
td { padding: var(--oco-s-2) var(--oco-s-3); font-size: 14px; color: var(--oco-ink); border-bottom: 1px solid var(--oco-line); }
tr:last-child td { border-bottom: none; }

.code-pill {
  display: inline-block; padding: 2px 8px;
  background: var(--oco-surface-2); border-radius: var(--oco-r-sm);
  font-size: 13px; font-weight: 700; color: var(--oco-ink-2);
}
</style>
