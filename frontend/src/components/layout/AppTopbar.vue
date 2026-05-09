<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <header class="app-topbar">
    <!-- Mobile: brand + house selector + search icon -->
    <div class="topbar-mobile">
      <span class="topbar-brand">OCO</span>
      <HouseSelector class="topbar-house" />
      <RouterLink
        v-if="housesStore.selectedHouseId"
        :to="`/houses/${housesStore.selectedHouseId}/search`"
        class="topbar-icon-btn"
        :aria-label="$t('nav.search')"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
      </RouterLink>
    </div>

    <!-- Desktop: breadcrumb + search -->
    <div class="topbar-desktop">
      <nav class="topbar-breadcrumb" aria-label="breadcrumb">
        <HouseSelector v-if="housesStore.selectedHouseId" />
        <template v-for="(crumb, i) in breadcrumbs" :key="i">
          <span class="bc-sep">›</span>
          <RouterLink v-if="crumb.to" :to="crumb.to" class="bc-link">{{ crumb.label }}</RouterLink>
          <span v-else class="bc-current">{{ crumb.label }}</span>
        </template>
      </nav>

      <div class="topbar-right">
        <RouterLink
          v-if="housesStore.selectedHouseId"
          :to="`/houses/${housesStore.selectedHouseId}/search`"
          class="topbar-search-btn"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          {{ $t('nav.search') }}
          <kbd>⌘K</kbd>
        </RouterLink>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useHousesStore } from '@/stores/houses'
import { useI18n } from 'vue-i18n'
import HouseSelector from './HouseSelector.vue'

const route = useRoute()
const housesStore = useHousesStore()
const { t } = useI18n()

interface Crumb { label: string; to?: string }

const breadcrumbs = computed((): Crumb[] => {
  const path = route.path
  const hid = housesStore.selectedHouseId
  if (!hid) return []
  const crumbs: Crumb[] = []

  if (path.includes('/containers/') && path.includes('/capture')) {
    crumbs.push({ label: t('nav.boxes'), to: `/houses/${hid}/containers` })
    crumbs.push({ label: t('item.capture.title') })
  } else if (path.endsWith('/containers/create')) {
    crumbs.push({ label: t('nav.boxes'), to: `/houses/${hid}/containers` })
    crumbs.push({ label: t('container.create.title') })
  } else if (path.includes('/containers/') && path.includes('/edit')) {
    crumbs.push({ label: t('nav.boxes'), to: `/houses/${hid}/containers` })
    crumbs.push({ label: t('container.edit.title') })
  } else if (path.includes(`/houses/${hid}/containers/`)) {
    crumbs.push({ label: t('nav.boxes'), to: `/houses/${hid}/containers` })
    crumbs.push({ label: route.params.containerId as string ?? '' })
  } else if (path.endsWith('/containers')) {
    crumbs.push({ label: t('nav.boxes') })
  } else if (path.endsWith('/transfers/plan')) {
    crumbs.push({ label: t('nav.transfers'), to: `/houses/${hid}/transfers` })
    crumbs.push({ label: t('transfer.plan.title') })
  } else if (path.endsWith('/transfers/create')) {
    crumbs.push({ label: t('nav.transfers'), to: `/houses/${hid}/transfers` })
    crumbs.push({ label: t('transfer.create.title') })
  } else if (path.includes(`/houses/${hid}/transfers/`)) {
    crumbs.push({ label: t('nav.transfers'), to: `/houses/${hid}/transfers` })
  } else if (path.endsWith('/transfers')) {
    crumbs.push({ label: t('nav.transfers') })
  } else if (path.endsWith('/inbox')) {
    crumbs.push({ label: t('nav.inbox') })
  } else if (path.endsWith('/search')) {
    crumbs.push({ label: t('nav.search') })
  } else if (path.startsWith('/admin')) {
    crumbs.push({ label: 'Admin' })
    if (path.endsWith('/users')) crumbs.push({ label: t('nav.users') })
    else if (path.endsWith('/houses')) crumbs.push({ label: t('nav.houses') })
    else if (path.endsWith('/ai-config')) crumbs.push({ label: t('nav.ai_config') })
  }
  return crumbs
})
</script>

<style scoped>
.app-topbar {
  background: var(--oco-surface);
  border-bottom: 1px solid var(--oco-line);
  padding-top: max(env(safe-area-inset-top), 8px);
  position: sticky;
  top: 0;
  z-index: 100;
}

/* Mobile layout */
.topbar-mobile {
  display: flex;
  align-items: center;
  gap: var(--oco-s-3);
  padding: 10px var(--oco-s-4);
}
.topbar-brand {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--oco-primary);
  flex-shrink: 0;
}
.topbar-house { flex: 1; min-width: 0; }
.topbar-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--oco-r-md);
  color: var(--oco-ink-3);
  flex-shrink: 0;
  transition: background 0.15s;
}
.topbar-icon-btn:hover { background: var(--oco-surface-2); color: var(--oco-ink); text-decoration: none; }

/* Desktop layout — hidden on mobile */
.topbar-desktop { display: none; }

@media (min-width: 1024px) {
  .topbar-mobile { display: none; }
  .topbar-desktop {
    display: flex;
    align-items: center;
    gap: var(--oco-s-4);
    padding: 0 var(--oco-s-6);
    height: 52px;
  }
  .topbar-breadcrumb {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    flex: 1;
    min-width: 0;
  }
  .bc-link { color: var(--oco-ink-3); font-weight: 500; }
  .bc-link:hover { color: var(--oco-ink); text-decoration: none; }
  .bc-sep { color: var(--oco-ink-4); font-size: 12px; }
  .bc-current { color: var(--oco-ink); font-weight: 600; }
  .topbar-right { display: flex; align-items: center; gap: var(--oco-s-3); }
  .topbar-search-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    background: var(--oco-surface-2);
    border: 1px solid var(--oco-line);
    border-radius: var(--oco-r-md);
    color: var(--oco-ink-3);
    font-size: 12px;
    font-weight: 500;
    transition: all 0.15s;
  }
  .topbar-search-btn:hover {
    background: var(--oco-surface-3);
    color: var(--oco-ink);
    text-decoration: none;
  }
  kbd {
    background: var(--oco-line);
    border-radius: var(--oco-r-xs);
    padding: 1px 4px;
    font-size: 10px;
    font-family: var(--oco-mono);
  }
}
</style>
