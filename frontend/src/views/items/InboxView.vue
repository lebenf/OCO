<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="inbox-view">
    <div class="inbox-header">
      <h2 class="view-title">
        {{ $t('item.inbox.title') }}
        <span v-if="inbox && inbox.total > 0" class="count-badge num">{{ inbox.total }}</span>
      </h2>
      <div class="count-pills">
        <span class="pill pill--warm">{{ $t('item.inbox.pending_ai') }} {{ inbox?.pending_ai ?? 0 }}</span>
        <span class="pill pill--ok">{{ $t('item.inbox.ready') }} {{ inbox?.ready_for_review ?? 0 }}</span>
        <span v-if="(inbox?.failed ?? 0) > 0" class="pill pill--danger">{{ $t('item.inbox.failed') }} {{ inbox?.failed ?? 0 }}</span>
      </div>
    </div>

    <div v-if="loading" class="skeleton-list">
      <div v-for="i in 3" :key="i" class="skeleton"></div>
    </div>

    <div v-else-if="!inbox || inbox.total === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.25">
        <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>
        <path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/>
      </svg>
      <p>{{ $t('item.inbox.empty') }}</p>
    </div>

    <div v-else class="groups">
      <Panel
        v-for="group in inbox.by_container"
        :key="group.container_id"
      >
        <template #action>
          <div class="group-header-inner">
            <RouterLink :to="`/houses/${houseId}/containers/${group.container_id}`" class="group-code mono">
              {{ group.container_code }}
            </RouterLink>
            <span class="num group-count">{{ group.items.length }}</span>
            <Btn kind="soft" style="font-size:12px;padding:4px 10px" @click="handleConfirmAll(group.container_id)">
              {{ $t('item.inbox.confirm_all') }}
            </Btn>
          </div>
        </template>
        <div class="items-list">
          <ItemReviewCard
            v-for="item in group.items"
            :key="item.id"
            :item="item"
            :house-id="houseId"
            @confirmed="onItemAction"
            @retried="onItemAction"
          />
        </div>
      </Panel>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useInboxStore } from '@/stores/inbox'
import { useItemsStore } from '@/stores/items'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'
import ItemReviewCard from '@/views/items/ItemReviewCard.vue'

const props = defineProps<{ houseId: string }>()
const inboxStore = useInboxStore()
const itemsStore = useItemsStore()
const inbox = computed(() => inboxStore.inbox)
const loading = ref(false)

async function load(): Promise<void> {
  loading.value = true
  try { await inboxStore.fetchInbox(props.houseId) }
  finally { loading.value = false }
}
async function handleConfirmAll(containerId: string): Promise<void> {
  await itemsStore.confirmAll(props.houseId, containerId)
  await load()
}
async function onItemAction(): Promise<void> { await load() }
onMounted(load)
</script>

<style scoped>
.inbox-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 760px; }

.inbox-header { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.view-title {
  font-size: 22px;
  font-weight: 600;
  letter-spacing: -0.4px;
  display: flex;
  align-items: center;
  gap: var(--oco-s-2);
}
.count-badge {
  font-size: 13px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: var(--oco-r-xl);
  background: var(--oco-primary-soft);
  color: var(--oco-primary);
}
.count-pills { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; }
.pill {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: var(--oco-r-xl);
}
.pill--warm { background: var(--oco-warm-soft); color: var(--oco-warm-2); }
.pill--ok   { background: var(--oco-ok-soft);   color: var(--oco-ok); }
.pill--danger { background: var(--oco-danger-soft); color: var(--oco-danger); }

.groups { display: flex; flex-direction: column; gap: var(--oco-s-4); }

.group-header-inner { display: flex; align-items: center; gap: var(--oco-s-3); }
.group-code { font-size: 14px; font-weight: 700; color: var(--oco-ink); letter-spacing: 0.5px; flex: 1; }
.group-code:hover { color: var(--oco-primary); text-decoration: none; }
.group-count { font-size: 12px; color: var(--oco-ink-4); background: var(--oco-surface-2); padding: 2px 6px; border-radius: var(--oco-r-sm); }

.items-list { display: flex; flex-direction: column; gap: var(--oco-s-2); }

.skeleton-list { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.skeleton { height: 200px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }

.empty-state {
  display: flex; flex-direction: column; align-items: center; gap: var(--oco-s-3);
  padding: var(--oco-s-8); color: var(--oco-ink-4); text-align: center; font-size: 14px;
}
</style>
