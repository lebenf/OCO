<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="container-create-view">
    <div class="create-header">
      <RouterLink :to="`/houses/${houseId}/containers`" class="back-link">← {{ $t('admin.back') }}</RouterLink>
      <h2 class="view-title">{{ $t('container.create.title') }}</h2>
    </div>

    <!-- Success state: show code + photo upload -->
    <div v-if="created" class="success-state">
      <ContainerCodeDisplay :code="created.code" />
      <p class="success-msg">{{ $t('container.create.success') }}</p>

      <Panel :title="$t('container.create.add_photo_prompt')">
        <label class="photo-upload">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" width="24" height="24" class="upload-icon">
            <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
          <span>{{ $t('container.create.upload_photo') }}</span>
          <input type="file" accept="image/*" hidden @change="handlePhotoUpload" />
        </label>
        <div v-if="uploadedPhoto" class="uploaded-preview">
          <Photo :src="uploadedPhoto.url" ratio="4/3" />
        </div>
      </Panel>

      <div class="step-actions">
        <Btn :to="`/houses/${houseId}/containers/${created.id}`">{{ $t('container.create.view_detail') }}</Btn>
        <Btn kind="ghost" :to="`/houses/${houseId}/containers`">{{ $t('container.create.back_to_list') }}</Btn>
      </div>
    </div>

    <!-- Create form -->
    <Panel v-else>
      <form class="create-form" @submit.prevent="handleCreate">
        <div class="form-group">
          <label class="field-label">{{ $t('container.create.description') }}</label>
          <input v-model="form.description" type="text" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="field-label">{{ $t('container.create.width_cm') }}</label>
            <input v-model.number="form.width_cm" type="number" min="0" step="0.1" />
          </div>
          <div class="form-group">
            <label class="field-label">{{ $t('container.create.depth_cm') }}</label>
            <input v-model.number="form.depth_cm" type="number" min="0" step="0.1" />
          </div>
          <div class="form-group">
            <label class="field-label">{{ $t('container.create.height_cm') }}</label>
            <input v-model.number="form.height_cm" type="number" min="0" step="0.1" />
          </div>
        </div>

        <div class="form-group">
          <label class="field-label">{{ $t('container.create.current_location') }}</label>
          <select v-model="form.current_location_id">
            <option :value="null">{{ $t('container.create.no_location') }}</option>
            <option v-for="loc in locations" :key="loc.id" :value="loc.id">{{ loc.name }}</option>
          </select>
        </div>

        <NestingSelector v-model="form.parent_id" :containers="availableContainers" />

        <p v-if="error" class="error-msg">{{ error }}</p>

        <Btn type="submit" :disabled="saving" style="align-self:flex-start">
          {{ saving ? $t('container.create.saving') : $t('container.create.submit') }}
        </Btn>
      </form>
    </Panel>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useContainersStore, type ContainerDetail, type PhotoOut, type ContainerSummary } from '@/stores/containers'
import { useHousesStore, type LocationOut } from '@/stores/houses'
import ContainerCodeDisplay from '@/components/containers/ContainerCodeDisplay.vue'
import NestingSelector from '@/components/containers/NestingSelector.vue'
import Photo from '@/components/primitives/Photo.vue'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string }>()
const store = useContainersStore()
const housesStore = useHousesStore()

const form = ref({
  description: '',
  width_cm: null as number | null,
  depth_cm: null as number | null,
  height_cm: null as number | null,
  parent_id: null as string | null,
  current_location_id: null as string | null,
})
const locations = ref<LocationOut[]>([])
const saving = ref(false)
const error = ref('')
const created = ref<ContainerDetail | null>(null)
const uploadedPhoto = ref<PhotoOut | null>(null)
const availableContainers = ref<ContainerSummary[]>([])

async function handleCreate(): Promise<void> {
  saving.value = true
  error.value = ''
  try {
    created.value = await store.createContainer(props.houseId, {
      description: form.value.description || null,
      width_cm: form.value.width_cm,
      depth_cm: form.value.depth_cm,
      height_cm: form.value.height_cm,
      parent_id: form.value.parent_id,
      current_location_id: form.value.current_location_id,
    })
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e.response?.data?.detail ?? String(err)
  } finally {
    saving.value = false
  }
}

async function handlePhotoUpload(event: Event): Promise<void> {
  if (!created.value) return
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadedPhoto.value = await store.uploadPhoto(props.houseId, created.value.id, file, 'empty')
}

onMounted(async () => {
  const [, locs] = await Promise.all([
    store.fetchContainers(props.houseId, { size: 100 }),
    housesStore.fetchLocations(props.houseId),
  ])
  availableContainers.value = store.containers
  locations.value = locs
})
</script>

<style scoped>
.container-create-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 600px; }
.create-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.create-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.form-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }
.form-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--oco-s-3); }
@media (max-width: 480px) { .form-row { grid-template-columns: 1fr 1fr; } }
.error-msg { color: var(--oco-danger); font-size: 13px; background: var(--oco-danger-soft); padding: var(--oco-s-3); border-radius: var(--oco-r-md); margin: 0; }

.success-state { display: flex; flex-direction: column; align-items: center; gap: var(--oco-s-4); text-align: center; }
.success-msg { font-size: 14px; font-weight: 600; color: var(--oco-ok); margin: 0; }
.photo-upload {
  display: flex; flex-direction: column; align-items: center; gap: var(--oco-s-2);
  padding: var(--oco-s-5); border: 2px dashed var(--oco-line-strong);
  border-radius: var(--oco-r-lg); cursor: pointer; color: var(--oco-ink-4); font-size: 14px;
  transition: border-color 0.15s, background 0.15s;
}
.photo-upload:hover { border-color: var(--oco-warm); background: var(--oco-warm-soft); }
.upload-icon { color: var(--oco-ink-4); }
.uploaded-preview { width: 200px; border-radius: var(--oco-r-lg); overflow: hidden; }
.step-actions { display: flex; gap: var(--oco-s-3); flex-wrap: wrap; }
</style>
