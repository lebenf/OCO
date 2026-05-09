<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div v-if="item" class="item-edit-view">
    <div class="edit-header">
      <button class="back-btn" @click="$router.back()">← {{ $t('admin.back') }}</button>
      <h2 class="view-title">{{ $t('item.edit.title') }}</h2>
    </div>

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
import { useItemsStore, type ItemDetail } from '@/stores/items'
import { useCategoriesStore, type CategoryOut } from '@/stores/categories'
import CategorySelector from '@/components/items/CategorySelector.vue'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string; itemId: string }>()
const router = useRouter()
const itemsStore = useItemsStore()
const categoriesStore = useCategoriesStore()

const item = ref<ItemDetail | null>(null)
const categories = ref<CategoryOut[]>([])
const saving = ref(false)
const error = ref('')

const form = ref({ name: '', description: '', brand: '', color: '', quantity: 1, category_ids: [] as string[] })

onMounted(async () => {
  const [itemData] = await Promise.all([
    itemsStore.fetchItem(props.houseId, props.itemId),
    categoriesStore.fetchCategories(props.houseId),
  ])
  item.value = itemData
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
