<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <aside class="app-sidebar" :class="{ collapsed }">
    <!-- Brand -->
    <div class="sidebar-brand">
      <span class="brand-logo">OCO</span>
      <span v-if="!collapsed" class="brand-tagline">{{ housesStore.selectedHouse?.name ?? '—' }}</span>
      <button class="collapse-btn" :title="collapsed ? 'Espandi' : 'Comprimi'" @click="$emit('toggle')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <path v-if="!collapsed" d="M15 18l-6-6 6-6"/><path v-else d="M9 18l6-6-6-6"/>
        </svg>
      </button>
    </div>

    <!-- Nav group: Trasloco -->
    <nav v-if="hid" class="sidebar-nav">
      <div v-if="!collapsed" class="nav-group-label">{{ $t('nav.section_main') }}</div>
      <RouterLink v-if="hid" :to="`/houses/${hid}`" class="nav-item" exact-active-class="nav-item--active">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.home') }}</span>
      </RouterLink>
      <RouterLink v-if="hid" :to="`/houses/${hid}/containers`" class="nav-item" active-class="nav-item--active">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.boxes') }}</span>
      </RouterLink>
      <RouterLink v-if="hid" :to="`/houses/${hid}/inbox`" class="nav-item" active-class="nav-item--active">
        <span class="nav-icon-wrap">
          <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 16 12 14 15 10 15 8 12 2 12"/>
            <path d="M5.45 5.11L2 12v6a2 2 0 002 2h16a2 2 0 002-2v-6l-3.45-6.89A2 2 0 0016.76 4H7.24a2 2 0 00-1.79 1.11z"/>
          </svg>
          <span v-if="inboxStore.count.total > 0" class="nav-badge">{{ inboxStore.count.total }}</span>
        </span>
        <span v-if="!collapsed">{{ $t('nav.inbox') }}</span>
      </RouterLink>
      <RouterLink v-if="hid" :to="`/houses/${hid}/transfers`" class="nav-item" active-class="nav-item--active">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="1" y="3" width="15" height="13"/><polygon points="16 8 20 8 23 11 23 16 16 16 16 8"/>
          <circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.transfers') }}</span>
      </RouterLink>
      <RouterLink v-if="hid" :to="`/houses/${hid}/search`" class="nav-item" active-class="nav-item--active">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.search') }}</span>
      </RouterLink>
    </nav>

    <!-- Nav group: Admin -->
    <nav v-if="authStore.user?.is_system_admin" class="sidebar-nav sidebar-nav--admin">
      <div v-if="!collapsed" class="nav-group-label">Admin</div>
      <RouterLink to="/admin/users" class="nav-item" active-class="nav-item--active">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
          <circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.users') }}</span>
      </RouterLink>
      <RouterLink to="/admin/houses" class="nav-item" active-class="nav-item--active">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.houses') }}</span>
      </RouterLink>
      <RouterLink to="/admin/ai-config" class="nav-item" active-class="nav-item--active">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.ai_config') }}</span>
      </RouterLink>
    </nav>

    <!-- User section -->
    <div class="sidebar-user">
      <RouterLink to="/account" class="nav-item" active-class="nav-item--active">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.account') }}</span>
      </RouterLink>
      <button class="theme-btn" :title="theme === 'dark' ? 'Light mode' : 'Dark mode'" @click="toggle">
        <svg v-if="theme === 'dark'" class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg v-else class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
        </svg>
        <span v-if="!collapsed">{{ theme === 'dark' ? 'Light' : 'Dark' }}</span>
      </button>
      <button class="nav-item logout-btn" @click="handleLogout">
        <svg class="nav-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
          <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        <span v-if="!collapsed">{{ $t('nav.logout') }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useHousesStore } from '@/stores/houses'
import { useInboxStore } from '@/stores/inbox'
import { useTheme } from '@/composables/useTheme'

defineProps<{ collapsed: boolean }>()
defineEmits<{ toggle: [] }>()

const authStore = useAuthStore()
const housesStore = useHousesStore()
const inboxStore = useInboxStore()
const router = useRouter()
const { theme, toggle } = useTheme()

const hid = computed(() => housesStore.selectedHouseId)

onMounted(() => { housesStore.autoSelect() })
watch(() => housesStore.houses, () => { housesStore.autoSelect() })

async function handleLogout(): Promise<void> {
  inboxStore.stopPolling()
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-sidebar {
  width: 240px;
  min-height: 100vh;
  background: var(--oco-surface);
  border-right: 1px solid var(--oco-line);
  display: flex;
  flex-direction: column;
  transition: width 0.2s ease;
  flex-shrink: 0;
}
.app-sidebar.collapsed { width: 64px; }

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--oco-s-3);
  padding: var(--oco-s-4) var(--oco-s-4);
  height: 52px;
  border-bottom: 1px solid var(--oco-line);
}
.brand-logo {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.5px;
  color: var(--oco-primary);
  flex-shrink: 0;
}
.brand-tagline {
  font-size: 12px;
  color: var(--oco-ink-3);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
.collapse-btn {
  background: none;
  border: none;
  padding: 4px;
  color: var(--oco-ink-4);
  border-radius: var(--oco-r-xs);
  cursor: pointer;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  margin-left: auto;
}
.collapse-btn:hover { background: var(--oco-surface-2); color: var(--oco-ink); }

.sidebar-nav {
  padding: var(--oco-s-3) var(--oco-s-2);
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-bottom: 1px solid var(--oco-line);
}
.sidebar-nav--admin { flex: 1; }
.nav-group-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--oco-ink-4);
  padding: 4px 8px 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--oco-s-3);
  padding: 8px 10px;
  border-radius: var(--oco-r-md);
  color: var(--oco-ink-2);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.12s, color 0.12s;
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
}
.nav-item:hover { background: var(--oco-surface-2); color: var(--oco-ink); text-decoration: none; }
.nav-item--active { background: var(--oco-primary-soft); color: var(--oco-primary-ink); }
.nav-item--active:hover { background: var(--oco-primary-soft); }
.nav-icon { width: 18px; height: 18px; flex-shrink: 0; }
.nav-icon-wrap { position: relative; flex-shrink: 0; }
.nav-badge {
  position: absolute;
  top: -4px;
  right: -6px;
  background: var(--oco-danger);
  color: white;
  font-size: 9px;
  font-weight: 700;
  padding: 1px 4px;
  border-radius: 8px;
  min-width: 14px;
  text-align: center;
}

.sidebar-user {
  padding: var(--oco-s-2);
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: auto;
  border-top: 1px solid var(--oco-line);
}
.theme-btn {
  display: flex;
  align-items: center;
  gap: var(--oco-s-3);
  padding: 8px 10px;
  border-radius: var(--oco-r-md);
  color: var(--oco-ink-3);
  font-size: 13px;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
}
.theme-btn:hover { background: var(--oco-surface-2); color: var(--oco-ink); }
.logout-btn { color: var(--oco-ink-3); font-size: 13px; }

/* Collapsed state */
.collapsed .nav-item { justify-content: center; padding: 10px; }
.collapsed .theme-btn { justify-content: center; padding: 10px; }
.collapsed .logout-btn { justify-content: center; padding: 10px; }
</style>
