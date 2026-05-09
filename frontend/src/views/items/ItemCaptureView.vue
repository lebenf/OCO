<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="capture-view">
    <div class="capture-header">
      <RouterLink :to="`/houses/${houseId}/containers/${containerId}`" class="back-link">
        ← {{ $t('admin.back') }}
      </RouterLink>
      <h2 class="capture-title">{{ $t('item.capture.title') }}</h2>
    </div>

    <!-- Pipeline steps indicator -->
    <div class="pipeline">
      <div v-for="(step, i) in steps" :key="i" class="pipeline-step" :class="{ active: pipelineStep === i, done: pipelineStep > i }">
        <div class="step-dot">{{ pipelineStep > i ? '✓' : i + 1 }}</div>
        <span class="step-label">{{ step }}</span>
      </div>
    </div>

    <!-- Success banner -->
    <div v-if="lastCreated" class="success-banner">
      <span class="success-icon">✓</span>
      <div>
        <div class="success-name">{{ lastCreated.name || $t('item.capture.queued') }}</div>
        <div class="success-sub">{{ $t('item.capture.ai_processing') }}</div>
      </div>
      <RouterLink :to="`/houses/${houseId}/inbox`" class="success-link">→ Inbox</RouterLink>
    </div>

    <form class="capture-form" @submit.prevent="handleCapture">
      <!-- Photo upload -->
      <div class="photo-section">
        <label class="photo-upload-area" :class="{ 'has-photos': selectedPhotos.length > 0 }">
          <div v-if="selectedPhotos.length === 0" class="upload-placeholder">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
              <circle cx="12" cy="13" r="4"/>
            </svg>
            <span>{{ $t('item.capture.take_photo') }}</span>
          </div>
          <div v-else class="photo-previews">
            <div v-for="(p, i) in selectedPhotos" :key="i" class="preview-thumb">
              <Photo :src="p.preview" ratio="1/1" />
            </div>
            <div class="preview-add">+</div>
          </div>
          <input type="file" accept="image/*" capture="environment" hidden multiple @change="handlePhotoSelect" />
        </label>
      </div>

      <HintTypeSelector v-model="form.hint_type" />

      <div class="form-group">
        <label class="field-label">{{ $t('item.capture.hint_name') }}</label>
        <input v-model="form.name" type="text" :placeholder="$t('item.capture.name_placeholder')" />
      </div>

      <div v-if="error" class="error-msg">{{ error }}</div>

      <Btn type="submit" :disabled="saving" style="width:100%;justify-content:center">
        {{ saving ? $t('item.capture.saving') : $t('item.capture.submit') }}
      </Btn>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useItemsStore, type ItemDetail } from '@/stores/items'
import HintTypeSelector from '@/components/ai/HintTypeSelector.vue'
import Photo from '@/components/primitives/Photo.vue'
import Btn from '@/components/primitives/Btn.vue'
import api from '@/services/api'

const props = defineProps<{ houseId: string; containerId: string }>()
const itemsStore = useItemsStore()
const { t } = useI18n()

const form = ref({ hint_type: 'auto', name: '' })
const selectedPhotos = ref<{ file: File; preview: string }[]>([])
const saving = ref(false)
const error = ref('')
const lastCreated = ref<ItemDetail | null>(null)
const pipelineStep = ref(0)

const steps = computed(() => [
  t('capture.step_photo'),
  t('capture.step_analysis'),
  t('capture.step_categories'),
])

function handlePhotoSelect(event: Event): void {
  const files = (event.target as HTMLInputElement).files
  if (!files) return
  selectedPhotos.value = Array.from(files).map((f) => ({
    file: f,
    preview: URL.createObjectURL(f),
  }))
  pipelineStep.value = 1
}

async function handleCapture(): Promise<void> {
  saving.value = true
  error.value = ''
  pipelineStep.value = 1
  try {
    const photoIds: string[] = []
    for (const { file } of selectedPhotos.value) {
      const formData = new FormData()
      formData.append('files', file)
      const res = await api.post<{ id: string; url: string }[]>(
        `/houses/${props.houseId}/ai/temp-photos`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      )
      photoIds.push(...res.data.map((p: { id: string; url: string }) => p.id))
    }
    pipelineStep.value = 2
    const item = await itemsStore.createItem(props.houseId, props.containerId, {
      item_type: 'single',
      hint_type: form.value.hint_type,
      photo_ids: photoIds,
      name: form.value.name || 'placeholder',
    })
    lastCreated.value = item
    pipelineStep.value = 0
    form.value.name = ''
    selectedPhotos.value = []
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e.response?.data?.detail ?? String(err)
    pipelineStep.value = 0
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.capture-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 480px; }

.capture-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.capture-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

/* Pipeline */
.pipeline { display: flex; gap: var(--oco-s-3); align-items: center; }
.pipeline-step { display: flex; align-items: center; gap: var(--oco-s-2); opacity: 0.35; transition: opacity 0.2s; }
.pipeline-step.active { opacity: 1; }
.pipeline-step.done { opacity: 0.6; }
.step-dot {
  width: 24px; height: 24px;
  border-radius: 50%;
  background: var(--oco-surface-3);
  border: 2px solid var(--oco-line);
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
  color: var(--oco-ink-3);
}
.pipeline-step.active .step-dot { background: var(--oco-warm-soft); border-color: var(--oco-warm); color: var(--oco-warm-2); }
.pipeline-step.done .step-dot { background: var(--oco-ok-soft); border-color: var(--oco-ok); color: var(--oco-ok); }
.step-label { font-size: 12px; font-weight: 500; color: var(--oco-ink-3); }
.pipeline-step.active .step-label { color: var(--oco-warm-2); }

/* Success */
.success-banner {
  display: flex;
  align-items: center;
  gap: var(--oco-s-3);
  background: var(--oco-ok-soft);
  border: 1px solid var(--oco-ok);
  border-radius: var(--oco-r-lg);
  padding: var(--oco-s-4);
}
.success-icon { font-size: 20px; color: var(--oco-ok); flex-shrink: 0; }
.success-name { font-size: 14px; font-weight: 600; color: var(--oco-ink); }
.success-sub { font-size: 12px; color: var(--oco-ink-3); }
.success-link { margin-left: auto; font-size: 13px; font-weight: 600; color: var(--oco-primary); flex-shrink: 0; }

/* Form */
.capture-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }

.photo-upload-area {
  display: block;
  border: 2px dashed var(--oco-line-strong);
  border-radius: var(--oco-r-lg);
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
  overflow: hidden;
}
.photo-upload-area:hover { border-color: var(--oco-warm); background: var(--oco-warm-soft); }
.photo-upload-area.has-photos { border-style: solid; border-color: var(--oco-line); }
.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--oco-s-3);
  padding: var(--oco-s-7);
  color: var(--oco-ink-4);
  font-size: 14px;
  font-weight: 500;
}
.photo-previews { display: flex; gap: var(--oco-s-2); padding: var(--oco-s-3); flex-wrap: wrap; }
.preview-thumb { width: 72px; height: 72px; border-radius: var(--oco-r-md); overflow: hidden; }
.preview-add {
  width: 72px; height: 72px;
  display: flex; align-items: center; justify-content: center;
  border: 1px dashed var(--oco-line-strong);
  border-radius: var(--oco-r-md);
  color: var(--oco-ink-4);
  font-size: 20px;
}
.form-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }
.error-msg { color: var(--oco-danger); font-size: 13px; padding: var(--oco-s-3); background: var(--oco-danger-soft); border-radius: var(--oco-r-md); }
</style>
