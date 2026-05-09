<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="transfer-create-view">
    <div class="create-header">
      <RouterLink :to="`/houses/${houseId}/transfers`" class="back-link">← {{ $t('transfer.list.title') }}</RouterLink>
      <h2 class="view-title">{{ $t('transfer.create.title') }}</h2>
    </div>

    <Panel>
      <form class="create-form" @submit.prevent="handleCreate">
        <div class="form-group">
          <label class="field-label">{{ $t('transfer.create.name') }} *</label>
          <input v-model="form.name" type="text" required />
        </div>

        <div class="form-group">
          <label class="field-label">{{ $t('transfer.create.destination') }} *</label>
          <select v-model="form.destination_location_id" required>
            <option value="">{{ $t('transfer.create.select_destination') }}</option>
            <template v-for="entry in allLocations" :key="entry.house.id">
              <optgroup :label="entry.house.name">
                <option v-for="loc in entry.locations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
              </optgroup>
            </template>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="field-label">{{ $t('transfer.create.scheduled_date') }}</label>
            <input v-model="form.scheduled_date" type="date" />
          </div>
          <div class="form-group">
            <label class="field-label">{{ $t('transfer.create.vehicle_volume') }}</label>
            <input v-model.number="form.vehicle_volume_liters" type="number" min="0" step="100" />
          </div>
        </div>

        <div class="form-group">
          <label class="field-label">{{ $t('transfer.create.notes') }}</label>
          <textarea v-model="form.notes" rows="3"></textarea>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <Btn type="submit" :disabled="saving" style="align-self:flex-start">
          {{ saving ? $t('container.edit.saving') : $t('transfer.create.submit') }}
        </Btn>
      </form>
    </Panel>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTransfersStore } from '@/stores/transfers'
import { useHousesStore, type AllLocationsEntry } from '@/stores/houses'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const store = useTransfersStore()
const housesStore = useHousesStore()

const allLocations = ref<AllLocationsEntry[]>([])
const saving = ref(false)
const error = ref('')

const form = ref({
  name: '',
  destination_location_id: '',
  scheduled_date: '',
  vehicle_volume_liters: null as number | null,
  notes: '',
})

onMounted(async () => {
  allLocations.value = await housesStore.fetchAllLocations()
})

async function handleCreate(): Promise<void> {
  saving.value = true
  error.value = ''
  try {
    const transfer = await store.createTransfer(props.houseId, {
      name: form.value.name,
      destination_location_id: form.value.destination_location_id,
      scheduled_date: form.value.scheduled_date || null,
      vehicle_volume_liters: form.value.vehicle_volume_liters,
      notes: form.value.notes || null,
    })
    router.push(`/houses/${props.houseId}/transfers/${transfer.id}`)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e.response?.data?.detail ?? String(err)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.transfer-create-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 600px; }
.create-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.create-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.form-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--oco-s-3); }
@media (max-width: 480px) { .form-row { grid-template-columns: 1fr; } }
.error-msg { color: var(--oco-danger); font-size: 13px; background: var(--oco-danger-soft); padding: var(--oco-s-3); border-radius: var(--oco-r-md); margin: 0; }
</style>
