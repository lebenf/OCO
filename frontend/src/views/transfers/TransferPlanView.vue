<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="plan-view">
    <div class="plan-header">
      <RouterLink :to="`/houses/${houseId}/transfers`" class="back-link">← {{ $t('transfer.list.title') }}</RouterLink>
      <h2 class="view-title">{{ $t('transfer.plan.title') }}</h2>
    </div>

    <Panel>
      <form class="plan-form" @submit.prevent="handlePlan">
        <div class="form-row">
          <div class="form-group">
            <label class="field-label">{{ $t('transfer.plan.destination') }} *</label>
            <select v-model="form.destination_house_id" required>
              <option value="">{{ $t('transfer.create.select_destination') }}</option>
              <option v-for="entry in allLocations" :key="entry.house.id" :value="entry.house.id">
                {{ entry.house.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label class="field-label">{{ $t('transfer.plan.vehicle_volume') }} *</label>
            <input v-model.number="form.vehicle_volume_liters" type="number" min="1" required />
            <span class="field-hint">{{ $t('transfer.plan.volume_hint') }}</span>
          </div>
        </div>
        <Btn type="submit" :disabled="planning" style="align-self:flex-start">
          {{ planning ? $t('container.list.loading') : $t('transfer.plan.calculate') }}
        </Btn>
      </form>
    </Panel>

    <div v-if="result" class="results">
      <div class="results-heading">
        {{ $t('transfer.plan.result') }}:
        <strong class="num">{{ result.trips.length }}</strong> {{ $t('transfer.plan.trips') }}
      </div>

      <div class="trips-grid">
        <div v-for="trip in result.trips" :key="trip.trip_number" class="trip-card">
          <div class="trip-header">
            <span class="trip-label">{{ $t('transfer.plan.trip') }} <span class="num">{{ trip.trip_number }}</span></span>
            <VolumeIndicator :used="trip.total_volume_liters" :total="form.vehicle_volume_liters!" />
          </div>
          <ContainerTransferList :containers="trip.containers" :removable="false" />
          <Btn kind="soft" style="align-self:flex-end;font-size:13px" @click="handleCreateFromTrip(trip)">
            {{ $t('transfer.plan.create_transfer') }}
          </Btn>
        </div>
      </div>

      <Panel v-if="result.unassigned_containers.length > 0" :title="`${$t('transfer.plan.unassigned')} (${result.unassigned_containers.length})`">
        <p class="hint-text">{{ $t('transfer.plan.unassigned_hint') }}</p>
        <ContainerTransferList :containers="result.unassigned_containers" :removable="false" />
      </Panel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useTransfersStore, type TransferPlanResponse, type TripPlan } from '@/stores/transfers'
import { useHousesStore, type AllLocationsEntry } from '@/stores/houses'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'
import VolumeIndicator from '@/components/transfers/VolumeIndicator.vue'
import ContainerTransferList from '@/components/transfers/ContainerTransferList.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const { t } = useI18n()
const store = useTransfersStore()
const housesStore = useHousesStore()

const allLocations = ref<AllLocationsEntry[]>([])
const planning = ref(false)
const result = ref<TransferPlanResponse | null>(null)
const form = ref({ destination_house_id: '', vehicle_volume_liters: null as number | null })

onMounted(async () => {
  allLocations.value = await housesStore.fetchAllLocations()
})

async function handlePlan(): Promise<void> {
  if (!form.value.vehicle_volume_liters) return
  planning.value = true
  result.value = null
  try {
    result.value = await store.planTransfers(props.houseId, {
      destination_house_id: form.value.destination_house_id,
      vehicle_volume_liters: form.value.vehicle_volume_liters,
    })
  } finally {
    planning.value = false
  }
}

async function handleCreateFromTrip(trip: TripPlan): Promise<void> {
  const entry = allLocations.value.find((e: AllLocationsEntry) => e.house.id === form.value.destination_house_id)
  const destName = entry?.house.name ?? 'Transfer'
  const firstLocation = entry?.locations[0]
  if (!firstLocation) return
  const transfer = await store.createTransfer(props.houseId, {
    name: `${destName} — ${t('transfer.plan.trip')} ${trip.trip_number}`,
    destination_location_id: firstLocation.id,
    vehicle_volume_liters: form.value.vehicle_volume_liters,
    container_ids: trip.containers.map((c: { id: string }) => c.id),
  })
  router.push(`/houses/${props.houseId}/transfers/${transfer.id}`)
}
</script>

<style scoped>
.plan-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 900px; }
.plan-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }
.plan-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: var(--oco-s-4); }
@media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }
.form-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }
.field-hint { font-size: 11px; color: var(--oco-ink-4); }
.results { display: flex; flex-direction: column; gap: var(--oco-s-5); }
.results-heading { font-size: 16px; color: var(--oco-ink-2); }
.trips-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--oco-s-4); }
.trip-card {
  background: var(--oco-surface); border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg); padding: var(--oco-s-4);
  display: flex; flex-direction: column; gap: var(--oco-s-3);
}
.trip-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.trip-label { font-size: 13px; font-weight: 600; color: var(--oco-ink-2); }
.hint-text { font-size: 13px; color: var(--oco-ink-3); margin: 0 0 var(--oco-s-3); }
</style>
