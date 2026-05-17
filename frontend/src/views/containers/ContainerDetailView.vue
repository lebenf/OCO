<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div v-if="container" class="container-detail">

    <!-- Header -->
    <div class="detail-header">
      <div class="header-top">
        <RouterLink :to="`/houses/${houseId}/containers`" class="back-link">
          ← {{ $t('nav.boxes') }}
        </RouterLink>
        <div class="header-actions">
          <Btn
            v-if="authStore.user?.is_system_admin"
            kind="danger"
            style="font-size:13px"
            @click="handleDelete"
          >
            {{ $t('common.delete') }}
          </Btn>
          <Btn kind="ghost" :to="`/houses/${houseId}/containers/${container.id}/edit`" style="font-size:13px">
            {{ $t('container.detail.edit') }}
          </Btn>
          <Btn
            v-if="container.status === 'open'"
            kind="soft"
            :to="`/houses/${houseId}/containers/${container.id}/capture`"
          >
            + {{ $t('container.detail.add_item') }}
          </Btn>
          <Btn
            v-if="container.status === 'open'"
            kind="warm"
            :disabled="hasDrafts && !false"
            @click="handleClose"
          >{{ $t('container.detail.close') }}</Btn>
          <Btn
            v-if="container.status === 'open' && hasDrafts"
            kind="danger"
            @click="handleForceClose"
          >{{ $t('container.detail.close_anyway') }}</Btn>
          <Btn v-if="container.status === 'closed'" kind="primary" @click="handleSeal">
            {{ $t('container.detail.seal') }}
          </Btn>
        </div>
      </div>

      <div class="header-info">
        <h2 class="container-code-display mono">{{ container.code }}</h2>
        <StatusBadge :kind="container.status" size="md" />
      </div>

      <div v-if="container.description" class="container-desc">{{ container.description }}</div>

      <div class="meta-chips">
        <span v-if="container.destination_location" class="meta-chip dest-chip">
          {{ container.destination_location.house_name }} · {{ container.destination_location.name }}
        </span>
        <span v-if="container.current_location" class="meta-chip">{{ container.current_location.name }}</span>
        <span v-if="container.parent" class="meta-chip">
          {{ $t('container.detail.in') }}: <span class="mono">{{ container.parent.code }}</span>
        </span>
        <span v-if="container.volume_liters" class="meta-chip mono">
          {{ container.volume_liters.toFixed(1) }}L
        </span>
      </div>
    </div>

    <div class="detail-body">
      <!-- Left column -->
      <div class="col-main">
        <!-- Items tabs -->
        <Panel>
          <template #action>
            <div class="tabs">
              <button :class="['tab', { active: activeTab === 'confirmed' }]" @click="activeTab = 'confirmed'">
                {{ $t('container.detail.items') }}
                <span class="tab-count num">{{ confirmedItems.length }}</span>
              </button>
              <button :class="['tab', { active: activeTab === 'draft' }]" @click="activeTab = 'draft'">
                {{ $t('container.detail.in_review') }}
                <span v-if="draftItems.length" class="tab-count num tab-count--draft">{{ draftItems.length }}</span>
              </button>
            </div>
          </template>

          <div v-if="activeTab === 'confirmed'">
            <p v-if="confirmedItems.length === 0" class="empty-msg">{{ $t('container.detail.no_items') }}</p>
            <div class="items-list">
              <ItemCard
                v-for="item in confirmedItems"
                :key="item.id"
                :item="item"
                @click="router.push(`/houses/${houseId}/items/${item.id}`)"
              />
            </div>
          </div>
          <div v-else>
            <p v-if="draftItems.length === 0" class="empty-msg">{{ $t('container.detail.no_drafts') }}</p>
            <div class="items-list">
              <ItemReviewCard
                v-for="item in draftInboxItems"
                :key="item.id"
                :item="item"
                :house-id="houseId"
                @confirmed="load"
                @retried="load"
              />
            </div>
          </div>
        </Panel>

        <!-- Children -->
        <Panel v-if="container.children.length > 0" :title="$t('container.detail.children')">
          <div class="children-grid">
            <ContainerCard
              v-for="c in container.children"
              :key="c.id"
              :container="c"
              @click="goToContainer(c.id)"
            />
          </div>
        </Panel>
      </div>

      <!-- Right column -->
      <div class="col-side">
        <!-- Photos -->
        <Panel :title="$t('container.detail.photos')">
          <div class="photos-grid">
            <div v-for="photo in container.photos" :key="photo.id" class="photo-item">
              <Photo :src="photo.url" ratio="1/1" />
              <button class="photo-del" @click="handleDeletePhoto(photo.id)">✕</button>
            </div>
            <label class="photo-add">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" opacity="0.5">
                <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
              <input type="file" accept="image/*" hidden @change="handlePhotoUpload" />
            </label>
          </div>
        </Panel>

        <!-- QR -->
        <Panel :title="$t('container.detail.qr')">
          <QRCodeDisplay :house-id="houseId" :container-id="container.id" :code="container.code" />
        </Panel>

        <!-- Dimensions -->
        <Panel v-if="container.width_cm" :title="'Dimensioni'">
          <p class="dim-text mono">
            {{ container.width_cm }} × {{ container.depth_cm }} × {{ container.height_cm }} cm
          </p>
        </Panel>
      </div>
    </div>

  </div>
  <div v-else class="loading-state">
    <div class="skeleton sk-title"></div>
    <div class="skeleton sk-body"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useContainersStore, type ContainerDetail } from '@/stores/containers'
import { useItemsStore, type ItemSummary } from '@/stores/items'
import { type DraftItemSummary } from '@/stores/inbox'
import { useAuthStore } from '@/stores/auth'
import StatusBadge from '@/components/primitives/StatusBadge.vue'
import Btn from '@/components/primitives/Btn.vue'
import Panel from '@/components/primitives/Panel.vue'
import Photo from '@/components/primitives/Photo.vue'
import QRCodeDisplay from '@/components/containers/QRCodeDisplay.vue'
import ContainerCard from '@/components/containers/ContainerCard.vue'
import ItemCard from '@/components/items/ItemCard.vue'
import ItemReviewCard from '@/views/items/ItemReviewCard.vue'

const props = defineProps<{ houseId: string; containerId: string }>()
const router = useRouter()
const { t } = useI18n()
const store = useContainersStore()
const itemsStore = useItemsStore()
const authStore = useAuthStore()

const container = ref<ContainerDetail | null>(null)
const confirmedItems = ref<ItemSummary[]>([])
const draftItems = ref<ItemSummary[]>([])
const activeTab = ref<'confirmed' | 'draft'>('confirmed')

const hasDrafts = computed(() => draftItems.value.length > 0)

const draftInboxItems = computed((): DraftItemSummary[] =>
  draftItems.value.map((i: ItemSummary) => ({
    id: i.id, item_type: i.item_type, status: i.status,
    ai_error: null, primary_photo_url: i.primary_photo_url, ai_result: null, created_at: '',
  }))
)

async function load(): Promise<void> {
  const [c, confirmedPage, draftPage] = await Promise.all([
    store.fetchContainer(props.houseId, props.containerId),
    itemsStore.fetchItems(props.houseId, { container_id: props.containerId, status: 'confirmed' }),
    itemsStore.fetchItems(props.houseId, { container_id: props.containerId, status: 'draft_ai_done,draft_ai_failed' }),
  ])
  container.value = c
  confirmedItems.value = confirmedPage.items
  draftItems.value = draftPage.items
}
async function handleClose(): Promise<void> {
  container.value = await store.closeContainer(props.houseId, props.containerId)
}
async function handleForceClose(): Promise<void> {
  await itemsStore.confirmAll(props.houseId, props.containerId)
  container.value = await store.closeContainer(props.houseId, props.containerId)
  await load()
}
async function handleSeal(): Promise<void> {
  container.value = await store.sealContainer(props.houseId, props.containerId)
}
async function handlePhotoUpload(event: Event): Promise<void> {
  const file = (event.target as HTMLInputElement).files?.[0]
  if (!file) return
  await store.uploadPhoto(props.houseId, props.containerId, file)
  await load()
}
async function handleDeletePhoto(photoId: string): Promise<void> {
  await store.deletePhoto(props.houseId, props.containerId, photoId)
  await load()
}
async function handleDelete(): Promise<void> {
  if (!confirm(t('container.detail.delete_confirm'))) return
  await store.deleteContainer(props.houseId, props.containerId)
  router.push(`/houses/${props.houseId}/containers`)
}
function goToContainer(id: string): void {
  router.push(`/houses/${props.houseId}/containers/${id}`)
}
onMounted(load)
</script>

<style scoped>
.container-detail { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 1100px; }

.detail-header {
  display: flex;
  flex-direction: column;
  gap: var(--oco-s-3);
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  padding: var(--oco-s-5);
}
.header-top { display: flex; justify-content: space-between; align-items: flex-start; gap: var(--oco-s-3); flex-wrap: wrap; }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { color: var(--oco-ink); text-decoration: none; }
.header-actions { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; }

.header-info { display: flex; align-items: center; gap: var(--oco-s-3); }
.container-code-display {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--oco-ink);
}
.container-desc { font-size: 14px; color: var(--oco-ink-3); }
.meta-chips { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; }
.meta-chip {
  font-size: 12px;
  font-weight: 500;
  padding: 3px 10px;
  border-radius: var(--oco-r-xl);
  background: var(--oco-surface-2);
  border: 1px solid var(--oco-line);
  color: var(--oco-ink-3);
}
.dest-chip { color: var(--oco-ink-2); }

.detail-body {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--oco-s-5);
  align-items: start;
}
@media (max-width: 900px) { .detail-body { grid-template-columns: 1fr; } }

.col-main { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.col-side { display: flex; flex-direction: column; gap: var(--oco-s-4); }

.tabs { display: flex; gap: var(--oco-s-2); }
.tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--oco-r-md);
  font-size: 13px;
  font-weight: 500;
  color: var(--oco-ink-3);
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.12s;
}
.tab.active { background: var(--oco-primary-soft); color: var(--oco-primary-ink); }
.tab-count {
  font-size: 11px;
  padding: 1px 5px;
  border-radius: 8px;
  background: var(--oco-surface-3);
  font-weight: 700;
}
.tab-count--draft { background: var(--oco-warn-soft); color: var(--oco-warn); }

.items-list { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.empty-msg { text-align: center; color: var(--oco-ink-4); padding: var(--oco-s-5); font-size: 13px; }

.children-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: var(--oco-s-3); }

.photos-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--oco-s-2); }
.photo-item { position: relative; }
.photo-del {
  position: absolute;
  top: 4px; right: 4px;
  background: rgba(0,0,0,0.5);
  color: white;
  border: none;
  border-radius: 50%;
  width: 20px; height: 20px;
  font-size: 10px;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.photo-add {
  display: flex;
  align-items: center;
  justify-content: center;
  aspect-ratio: 1;
  background: var(--oco-surface-2);
  border: 1px dashed var(--oco-line-strong);
  border-radius: var(--oco-r-md);
  cursor: pointer;
  transition: background 0.12s;
}
.photo-add:hover { background: var(--oco-surface-3); }

.dim-text { font-size: 14px; color: var(--oco-ink-2); margin: 0; }

.loading-state { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.skeleton { background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
.sk-title { height: 100px; }
.sk-body { height: 300px; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
