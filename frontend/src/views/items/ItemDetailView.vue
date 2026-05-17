<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div v-if="item" class="item-detail-view">
    <div class="detail-header">
      <button class="back-btn" @click="$router.back()">← {{ $t('admin.back') }}</button>
      <div class="header-top">
        <h2 class="view-title">{{ item.name }}</h2>
        <div class="header-actions">
          <Btn
            v-if="authStore.user?.is_system_admin"
            kind="danger"
            style="font-size:13px"
            @click="handleDelete"
          >
            {{ $t('common.delete') }}
          </Btn>
          <Btn kind="soft" :to="`/houses/${houseId}/items/${itemId}/edit`">{{ $t('item.detail.edit') }}</Btn>
        </div>
      </div>
      <div class="header-meta">
        <StatusBadge :kind="item.status" />
        <span v-if="item.brand" class="meta-chip">{{ item.brand }}</span>
        <span v-if="item.color" class="meta-chip">{{ item.color }}</span>
        <span v-if="item.quantity > 1" class="meta-chip mono">×{{ item.quantity }}</span>
      </div>
    </div>

    <ItemPhotoGallery :photos="item.photos" />

    <div class="content-grid">
      <Panel v-if="item.description || item.model || item.author">
        <dl class="meta-dl">
          <template v-if="item.description">
            <dt>{{ $t('item.fields.description') }}</dt>
            <dd>{{ item.description }}</dd>
          </template>
          <template v-if="item.model">
            <dt>{{ $t('item.fields.model') }}</dt>
            <dd>{{ item.model }}</dd>
          </template>
          <template v-if="item.author">
            <dt>{{ $t('item.fields.author') }}</dt>
            <dd>{{ item.author }}</dd>
          </template>
        </dl>
      </Panel>

      <Panel v-if="item.categories.length" :title="$t('item.fields.categories')">
        <div class="chips-row">
          <CategoryChip
            v-for="cat in item.categories"
            :key="cat.id"
            :label="cat.name"
            :icon="cat.icon"
          />
        </div>
      </Panel>

      <Panel v-if="item.tags.length" :title="$t('item.fields.tags')">
        <div class="chips-row">
          <span v-for="tag in item.tags" :key="tag" class="tag-chip">{{ tag }}</span>
        </div>
      </Panel>

      <Panel v-if="item.ai_generated" :title="$t('item.detail.ai_generated')">
        <p class="ai-info">{{ item.ai_provider }}<span v-if="item.ai_confidence" class="num"> — {{ Math.round(item.ai_confidence * 100) }}%</span></p>
      </Panel>
    </div>
  </div>

  <div v-else class="loading-state">
    <div v-for="i in 4" :key="i" class="skeleton"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useItemsStore, type ItemDetail } from '@/stores/items'
import { useAuthStore } from '@/stores/auth'
import StatusBadge from '@/components/primitives/StatusBadge.vue'
import CategoryChip from '@/components/primitives/CategoryChip.vue'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'
import ItemPhotoGallery from '@/components/items/ItemPhotoGallery.vue'

const props = defineProps<{ houseId: string; itemId: string }>()
const router = useRouter()
const { t } = useI18n()
const store = useItemsStore()
const authStore = useAuthStore()
const item = ref<ItemDetail | null>(null)

async function handleDelete(): Promise<void> {
  if (!confirm(t('item.detail.delete_confirm'))) return
  await store.deleteItem(props.houseId, props.itemId)
  router.back()
}

onMounted(async () => {
  item.value = await store.fetchItem(props.houseId, props.itemId)
})
</script>

<style scoped>
.item-detail-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 600px; }

.detail-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-btn { background: none; border: none; font-size: 13px; color: var(--oco-ink-3); font-weight: 500; cursor: pointer; padding: 0; text-align: left; font-family: var(--oco-font-sans); }
.back-btn:hover { color: var(--oco-ink); }
.header-top { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--oco-s-3); }
.header-actions { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; flex: 1; }
.header-meta { display: flex; align-items: center; gap: var(--oco-s-2); flex-wrap: wrap; }
.meta-chip {
  font-size: 12px; color: var(--oco-ink-3);
  background: var(--oco-surface-2); padding: 2px 8px; border-radius: var(--oco-r-xl);
}

.content-grid { display: flex; flex-direction: column; gap: var(--oco-s-4); }

.meta-dl { display: grid; grid-template-columns: auto 1fr; gap: var(--oco-s-1) var(--oco-s-4); margin: 0; }
dt { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-4); align-self: start; padding-top: 2px; }
dd { font-size: 14px; color: var(--oco-ink); margin: 0; }

.chips-row { display: flex; flex-wrap: wrap; gap: var(--oco-s-2); }
.tag-chip {
  font-size: 12px; color: var(--oco-ink-3);
  background: var(--oco-surface-2); padding: 3px 10px; border-radius: var(--oco-r-xl);
}

.ai-info { font-size: 13px; color: var(--oco-ink-3); margin: 0; }

.loading-state { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.skeleton { height: 80px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
