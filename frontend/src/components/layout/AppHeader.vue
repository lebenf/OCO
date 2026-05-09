<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <header class="app-header">
    <div class="brand">OCO</div>

    <select
      v-if="housesStore.houses.length > 1"
      :value="housesStore.selectedHouseId"
      class="house-selector"
      @change="housesStore.selectHouse(($event.target as HTMLSelectElement).value)"
    >
      <option v-for="h in housesStore.houses" :key="h.id" :value="h.id">
        {{ h.name }}
      </option>
    </select>
    <span v-else-if="housesStore.selectedHouse" class="house-name">
      {{ housesStore.selectedHouse.name }}
    </span>

    <GlobalSearchBar
      v-if="housesStore.selectedHouseId"
      :house-id="housesStore.selectedHouseId"
    />

    <nav class="nav">
      <RouterLink
        :to="housesStore.selectedHouseId ? `/houses/${housesStore.selectedHouseId}` : '/'"
      >
        {{ $t('nav.home') }}
      </RouterLink>
      <RouterLink
        v-if="housesStore.selectedHouseId"
        :to="`/houses/${housesStore.selectedHouseId}/containers`"
      >
        {{ $t('nav.containers') }}
      </RouterLink>
      <RouterLink
        v-if="housesStore.selectedHouseId"
        :to="`/houses/${housesStore.selectedHouseId}/transfers`"
      >
        {{ $t('nav.transfers') }}
      </RouterLink>
      <RouterLink
        v-if="housesStore.selectedHouseId && inboxStore.count.total > 0"
        :to="`/houses/${housesStore.selectedHouseId}/inbox`"
        class="inbox-link"
      >
        📥 {{ inboxStore.count.total }}
      </RouterLink>
      <RouterLink v-if="authStore.user?.is_system_admin" to="/admin/users">
        {{ $t('nav.admin') }}
      </RouterLink>
      <RouterLink v-if="authStore.user?.is_system_admin" to="/admin/ai-config">
        AI
      </RouterLink>
      <button class="logout-btn" @click="handleLogout">{{ $t('nav.logout') }}</button>
    </nav>
  </header>
</template>

<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useHousesStore } from '@/stores/houses'
import { useInboxStore } from '@/stores/inbox'
import GlobalSearchBar from '@/components/search/GlobalSearchBar.vue'

const authStore = useAuthStore()
const housesStore = useHousesStore()
const inboxStore = useInboxStore()
const router = useRouter()

onMounted(() => {
  housesStore.autoSelect()
})

watch(
  () => housesStore.selectedHouseId,
  (id) => {
    if (id) inboxStore.startPolling(id)
    else inboxStore.stopPolling()
  },
  { immediate: true },
)

async function handleLogout(): Promise<void> {
  inboxStore.stopPolling()
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  background: #1a1a2e;
  color: white;
}
.brand { font-size: 1.25rem; font-weight: 700; }
.house-selector {
  background: rgba(255,255,255,0.1);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
}
.house-name { color: rgba(255,255,255,0.7); font-size: 0.875rem; }
.nav { margin-left: auto; display: flex; align-items: center; gap: 1rem; }
.nav a { color: rgba(255,255,255,0.8); text-decoration: none; }
.nav a:hover, .nav a.router-link-active { color: white; }
.logout-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.4);
  color: rgba(255,255,255,0.8);
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
}
.logout-btn:hover { background: rgba(255,255,255,0.1); }
.inbox-link {
  background: rgba(255,200,0,0.2);
  border-radius: 12px;
  padding: 0.15rem 0.6rem;
  font-size: 0.875rem;
}
</style>
