<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div v-if="item" class="item-edit-view">
    <div class="edit-header">
      <button class="back-btn" @click="$router.back()">← {{ $t('admin.back') }}</button>
      <h2 class="view-title">{{ $t('item.edit.title') }}</h2>
    </div>

    <!-- Photo section -->
    <Panel :title="$t('item.edit.photos')">
      <div class="photos-grid">
        <div v-for="photo in photos" :key="photo.id" class="photo-thumb">
          <img :src="photo.url" :alt="item.name" />
          <button
            class="photo-delete-btn"
            :disabled="deletingPhotoId === photo.id"
            :title="$t('item.edit.delete_photo')"
            @click="handleDeletePhoto(photo.id)"
          >
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="1" y1="1" x2="11" y2="11"/><line x1="11" y1="1" x2="1" y2="11"/>
            </svg>
          </button>
        </div>
        <label class="photo-add-btn" :class="{ uploading: uploadingPhoto }">
          <svg v-if="!uploadingPhoto" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
            <circle cx="12" cy="13" r="4"/>
          </svg>
          <span v-if="uploadingPhoto" class="spinner"></span>
          <span class="photo-add-label">{{ $t('item.edit.add_photo') }}</span>
          <input type="file" accept="image/*" hidden :disabled="uploadingPhoto" @change="handleAddPhoto" />
        </label>
      </div>

      <div class="retry-ai-row">
        <Btn kind="soft" :disabled="retrying || item.status === 'draft'" @click="handleRetryAI">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-4.95"/>
          </svg>
          {{ retrying ? '...' : $t('item.edit.retry_ai') }}
        </Btn>
        <span v-if="retryQueued" class="retry-queued-msg">✓ {{ $t('item.edit.retry_queued') }}</span>
      </div>
    </Panel>

    <Panel>
      <form class="edit-form" @submit.prevent="handleSave">
        <div class="form-group">
          <label class="field-label">{{ $t('item.fields.name') }} *</label>
          <input v-model="form.name" type="text" required />
        </div>

        <div class="form-group">
          <label class="field-label">{{ $t('item.fields.description') }}</label>
          <textarea v-model="form.description" rows="3"></textarea>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="field-label">{{ $t('item.fields.brand') }}</label>
            <input v-model="form.brand" type="text" />
          </div>
          <div class="form-group">
            <label class="field-label">{{ $t('item.fields.color') }}</label>
            <input v-model="form.color" type="text" />
          </div>
          <div class="form-group form-group--narrow">
            <label class="field-label">{{ $t('item.fields.quantity') }}</label>
            <input v-model.number="form.quantity" type="number" min="1" />
          </div>
        </div>

        <CategorySelector v-model="form.category_ids" :house-id="houseId" :all-categories="categories" />

        <p v-if="error" class="error-msg">{{ error }}</p>

        <div class="form-actions">
          <Btn type="submit" :disabled="saving">
            {{ saving ? $t('container.edit.saving') : $t('container.edit.save') }}
          </Btn>
          <Btn kind="soft" type="button" :disabled="saving || item.status === 'confirmed'" @click="handleConfirm">
            {{ $t('item.edit.confirm') }}
          </Btn>
        </div>
      </form>
    </Panel>
  </div>

  <div v-else class="loading-state">
    <div v-for="i in 3" :key="i" class="skeleton"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useItemsStore, type ItemDetail, type ItemPhotoOut } from '@/stores/items'
import { useCategoriesStore, type CategoryOut } from '@/stores/categories'
import CategorySelector from '@/components/items/CategorySelector.vue'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'
import { useI18n } from 'vue-i18n'

const props = defineProps<{ houseId: string; itemId: string }>()
const router = useRouter()
const itemsStore = useItemsStore()
const categoriesStore = useCategoriesStore()
const { t } = useI18n()

const item = ref<ItemDetail | null>(null)
const photos = ref<ItemPhotoOut[]>([])
const categories = ref<CategoryOut[]>([])
const saving = ref(false)
const error = ref('')
const uploadingPhoto = ref(false)
const deletingPhotoId = ref<string | null>(null)
const retrying = ref(false)
const retryQueued = ref(false)

const form = ref({ name: '', description: '', brand: '', color: '', quantity: 1, category_ids: [] as string[] })

onMounted(async () => {
  const [itemData] = await Promise.all([
    itemsStore.fetchItem(props.houseId, props.itemId),
    categoriesStore.fetchCategories(props.houseId),
  ])
  item.value = itemData
  photos.value = [...itemData.photos]
  categories.value = categoriesStore.categories
  form.value = {
    name: itemData.name,
    description: itemData.description ?? '',
    brand: itemData.brand ?? '',
    color: itemData.color ?? '',
    quantity: itemData.quantity,
    category_ids: itemData.categories.map((c: { id: string }) => c.id),
  }
})

async function handleAddPhoto(event: Event): Promise<void> {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingPhoto.value = true
  try {
    const photo = await itemsStore.uploadPhoto(props.houseId, props.itemId, file)
    photos.value.push(photo)
  } finally {
    uploadingPhoto.value = false
    ;(event.target as HTMLInputElement).value = ''
  }
}

async function handleDeletePhoto(photoId: string): Promise<void> {
  deletingPhotoId.value = photoId
  try {
    await itemsStore.deletePhoto(props.houseId, props.itemId, photoId)
    photos.value = photos.value.filter((p) => p.id !== photoId)
  } finally {
    deletingPhotoId.value = null
  }
}

async function handleRetryAI(): Promise<void> {
  if (!confirm(t('item.edit.retry_ai_confirm'))) return
  retrying.value = true
  retryQueued.value = false
  try {
    await itemsStore.retryAI(props.houseId, props.itemId)
    retryQueued.value = true
    if (item.value) item.value.status = 'draft'
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e.response?.data?.detail ?? String(err)
  } finally {
    retrying.value = false
  }
}

async function handleSave(): Promise<void> {
  saving.value = true
  error.value = ''
  try {
    await itemsStore.updateItem(props.houseId, props.itemId, {
      name: form.value.name,
      description: form.value.description || null,
      brand: form.value.brand || null,
      color: form.value.color || null,
      quantity: form.value.quantity,
      category_ids: form.value.category_ids,
    })
    router.back()
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e.response?.data?.detail ?? String(err)
  } finally {
    saving.value = false
  }
}

async function handleConfirm(): Promise<void> {
  saving.value = true
  error.value = ''
  try {
    await itemsStore.confirmItem(props.houseId, props.itemId, {
      name: form.value.name,
      description: form.value.description || null,
      brand: form.value.brand || null,
      color: form.value.color || null,
      quantity: form.value.quantity,
      category_ids: form.value.category_ids,
    })
    router.back()
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e.response?.data?.detail ?? String(err)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.item-edit-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 600px; }
.edit-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-btn { background: none; border: none; font-size: 13px; color: var(--oco-ink-3); font-weight: 500; cursor: pointer; padding: 0; text-align: left; font-family: var(--oco-font-sans); }
.back-btn:hover { color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

/* Photos */
.photos-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--oco-s-2);
  margin-bottom: var(--oco-s-4);
}
.photo-thumb {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: var(--oco-r-md);
  overflow: visible;
  flex-shrink: 0;
}
.photo-thumb img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: var(--oco-r-md);
  display: block;
}
.photo-delete-btn {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--oco-danger);
  color: #fff;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  z-index: 1;
}
.photo-delete-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.photo-add-btn {
  width: 80px;
  height: 80px;
  border-radius: var(--oco-r-md);
  border: 2px dashed var(--oco-line-strong);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  color: var(--oco-ink-4);
  transition: border-color 0.15s, background 0.15s;
  flex-shrink: 0;
}
.photo-add-btn:hover { border-color: var(--oco-primary); background: var(--oco-surface-2); color: var(--oco-primary); }
.photo-add-btn.uploading { opacity: 0.6; cursor: not-allowed; }
.photo-add-label { font-size: 10px; font-weight: 600; text-align: center; line-height: 1.2; }

.retry-ai-row { display: flex; align-items: center; gap: var(--oco-s-3); flex-wrap: wrap; }
.retry-queued-msg { font-size: 13px; color: var(--oco-ok); font-weight: 500; }

@keyframes spin { to { transform: rotate(360deg); } }
.spinner {
  width: 16px; height: 16px;
  border: 2px solid var(--oco-line-strong);
  border-top-color: var(--oco-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

/* Form */
.edit-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.form-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.form-group--narrow { max-width: 100px; }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }
.form-row { display: grid; grid-template-columns: 1fr 1fr 80px; gap: var(--oco-s-3); }
@media (max-width: 480px) { .form-row { grid-template-columns: 1fr 1fr; } }
.form-actions { display: flex; gap: var(--oco-s-3); flex-wrap: wrap; }
.error-msg { color: var(--oco-danger); font-size: 13px; background: var(--oco-danger-soft); padding: var(--oco-s-3); border-radius: var(--oco-r-md); margin: 0; }

.loading-state { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.skeleton { height: 80px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
