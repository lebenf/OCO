<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <nav class="bottom-nav">
    <RouterLink v-if="hid" :to="`/houses/${hid}`" class="bn-item" exact-active-class="bn-item--active">
      <svg class="bn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
      <span class="bn-label">{{ $t('nav.home') }}</span>
    </RouterLink>

    <RouterLink v-if="hid" :to="`/houses/${hid}/containers`" class="bn-item" active-class="bn-item--active">
      <svg class="bn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
      </svg>
      <span class="bn-label">{{ $t('nav.boxes') }}</span>
    </RouterLink>

    <!-- FAB scan -->
    <RouterLink v-if="hid" :to="`/houses/${hid}/search`" class="bn-item bn-fab" active-class="bn-item--active">
      <span class="fab-circle">
        <svg class="bn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
          <rect x="3" y="14" width="7" height="7" rx="1"/>
          <path d="M14 14h2v2h-2zm4 0h2v2h-2zm0 4h2v2h-2zm-4 4h2v2h-2zm4-4h2v2h-2z" fill="currentColor" stroke="none"/>
        </svg>
      </span>
      <span class="bn-label">{{ $t('nav.scan') }}</span>
    </RouterLink>

    <RouterLink v-if="hid" :to="`/houses/${hid}/inbox`" class="bn-item" active-class="bn-item--active">
      <span class="bn-icon-wrap">
        <svg class="bn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>
          <path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/>
        </svg>
        <span v-if="inboxStore.count.total > 0" class="bn-badge">{{ inboxStore.count.total }}</span>
      </span>
      <span class="bn-label">{{ $t('nav.inbox') }}</span>
    </RouterLink>

    <RouterLink v-if="hid" :to="`/houses/${hid}/transfers`" class="bn-item" active-class="bn-item--active">
      <svg class="bn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
        <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
      </svg>
      <span class="bn-label">{{ $t('nav.transfers') }}</span>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useHousesStore } from '@/stores/houses'
import { useInboxStore } from '@/stores/inbox'

const housesStore = useHousesStore()
const inboxStore = useInboxStore()
const hid = computed(() => housesStore.selectedHouseId)
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: flex-end;
  background: var(--oco-surface);
  border-top: 1px solid var(--oco-line);
  padding-bottom: max(env(safe-area-inset-bottom), 12px);
  z-index: 200;
  box-shadow: 0 -2px 12px rgba(20,18,28,0.06);
}
.bn-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  padding: 10px 4px 6px;
  color: var(--oco-ink-4);
  text-decoration: none;
  font-size: 10px;
  font-weight: 500;
  transition: color 0.12s;
}
.bn-item:hover { text-decoration: none; color: var(--oco-ink-2); }
.bn-item--active { color: var(--oco-primary); }
.bn-icon { width: 22px; height: 22px; }
.bn-label { font-size: 10px; font-weight: 500; letter-spacing: 0.1px; }
.bn-icon-wrap { position: relative; }
.bn-badge {
  position: absolute;
  top: -4px;
  right: -8px;
  background: var(--oco-danger);
  color: white;
  font-size: 9px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 8px;
  min-width: 14px;
  text-align: center;
}

/* FAB */
.bn-fab { flex: 1.2; }
.fab-circle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: var(--oco-primary);
  border-radius: 50%;
  color: white;
  margin-top: -14px;
  box-shadow: 0 4px 14px rgba(82, 70, 200, 0.35);
  transition: transform 0.15s;
}
.bn-fab:hover .fab-circle { transform: scale(1.05); }
.bn-fab.bn-item--active .fab-circle { background: var(--oco-primary-2); }
.bn-fab .bn-label { color: var(--oco-primary); }
</style>
