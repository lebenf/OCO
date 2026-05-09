<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div v-if="container" class="container-edit-view">
    <div class="edit-header">
      <RouterLink :to="`/houses/${houseId}/containers/${containerId}`" class="back-link">
        ← {{ container.code }}
      </RouterLink>
      <h2 class="view-title">{{ $t('container.edit.title') }}</h2>
    </div>

    <Panel>
      <form class="edit-form" @submit.prevent="handleSave">
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

        <p v-if="error" class="error-msg">{{ error }}</p>

        <div class="form-actions">
          <Btn type="submit" :disabled="saving">
            {{ saving ? $t('container.edit.saving') : $t('container.edit.save') }}
          </Btn>
          <Btn kind="ghost" :to="`/houses/${houseId}/containers/${containerId}`">
            {{ $t('container.edit.cancel') }}
          </Btn>
        </div>
      </form>
    </Panel>
  </div>

  <div v-else class="loading-state">
    <div v-for="i in 2" :key="i" class="skeleton"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useContainersStore, type ContainerDetail } from '@/stores/containers'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string; containerId: string }>()
const router = useRouter()
const store = useContainersStore()

const container = ref<ContainerDetail | null>(null)
const form = ref({ description: '', width_cm: null as number | null, depth_cm: null as number | null, height_cm: null as number | null })
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  container.value = await store.fetchContainer(props.houseId, props.containerId)
  form.value = {
    description: container.value.description ?? '',
    width_cm: container.value.width_cm,
    depth_cm: container.value.depth_cm,
    height_cm: container.value.height_cm,
  }
})

async function handleSave(): Promise<void> {
  saving.value = true
  error.value = ''
  try {
    await store.updateContainer(props.houseId, props.containerId, {
      description: form.value.description || null,
      width_cm: form.value.width_cm,
      depth_cm: form.value.depth_cm,
      height_cm: form.value.height_cm,
    })
    router.push(`/houses/${props.houseId}/containers/${props.containerId}`)
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e.response?.data?.detail ?? String(err)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.container-edit-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 600px; }
.edit-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.edit-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.form-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }
.form-row { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--oco-s-3); }
@media (max-width: 480px) { .form-row { grid-template-columns: 1fr 1fr; } }
.form-actions { display: flex; gap: var(--oco-s-3); }
.error-msg { color: var(--oco-danger); font-size: 13px; background: var(--oco-danger-soft); padding: var(--oco-s-3); border-radius: var(--oco-r-md); margin: 0; }

.loading-state { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.skeleton { height: 80px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
