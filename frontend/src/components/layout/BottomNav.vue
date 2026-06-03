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

    <!-- More -->
    <button class="bn-item" :class="{ 'bn-item--active': menuOpen }" @click="menuOpen = true">
      <svg class="bn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/>
      </svg>
      <span class="bn-label">{{ $t('nav.more') }}</span>
    </button>
  </nav>

  <!-- Drawer overlay -->
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="menuOpen" class="drawer-overlay" @click.self="menuOpen = false">
        <div class="drawer">
          <div class="drawer-handle"></div>

          <!-- User section -->
          <div class="drawer-section">
            <RouterLink to="/account" class="drawer-item" @click="menuOpen = false">
              <svg class="di-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              {{ $t('nav.account') }}
            </RouterLink>
            <button class="drawer-item" @click="toggleTheme">
              <svg v-if="theme === 'dark'" class="di-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="5"/>
                <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
                <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
              </svg>
              <svg v-else class="di-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z"/>
              </svg>
              {{ theme === 'dark' ? $t('nav.theme_light') : $t('nav.theme_dark') }}
            </button>
            <button class="drawer-item drawer-item--danger" @click="handleLogout">
              <svg class="di-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
                <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
              {{ $t('nav.logout') }}
            </button>
          </div>

          <!-- Admin section -->
          <div v-if="authStore.user?.is_system_admin" class="drawer-section">
            <div class="drawer-section-label">Admin</div>
            <RouterLink to="/admin/users" class="drawer-item" @click="menuOpen = false">
              <svg class="di-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
                <circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
              </svg>
              {{ $t('nav.users') }}
            </RouterLink>
            <RouterLink to="/admin/houses" class="drawer-item" @click="menuOpen = false">
              <svg class="di-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/>
              </svg>
              {{ $t('nav.houses') }}
            </RouterLink>
            <RouterLink to="/admin/ai-config" class="drawer-item" @click="menuOpen = false">
              <svg class="di-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
              {{ $t('nav.ai_config') }}
            </RouterLink>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useHousesStore } from '@/stores/houses'
import { useInboxStore } from '@/stores/inbox'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'

const housesStore = useHousesStore()
const inboxStore = useInboxStore()
const authStore = useAuthStore()
const router = useRouter()
const { theme, toggle } = useTheme()
const hid = computed(() => housesStore.selectedHouseId)
const menuOpen = ref(false)

function toggleTheme(): void {
  toggle()
}

async function handleLogout(): Promise<void> {
  menuOpen.value = false
  inboxStore.stopPolling()
  await authStore.logout()
  router.push('/login')
}
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
  gap: 2px;
  padding: 10px 2px 6px;
  color: var(--oco-ink-4);
  text-decoration: none;
  font-size: 10px;
  font-weight: 500;
  transition: color 0.12s;
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--oco-font-sans);
}
.bn-item:hover { text-decoration: none; color: var(--oco-ink-2); }
.bn-item--active { color: var(--oco-primary); }
.bn-icon { width: 20px; height: 20px; }
.bn-label { font-size: 9px; font-weight: 500; letter-spacing: 0.1px; }
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
  width: 42px;
  height: 42px;
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

/* Drawer */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 300;
  display: flex;
  align-items: flex-end;
}
.drawer {
  width: 100%;
  background: var(--oco-surface);
  border-radius: var(--oco-r-xl) var(--oco-r-xl) 0 0;
  padding: var(--oco-s-3) var(--oco-s-4) max(env(safe-area-inset-bottom), 24px);
  display: flex;
  flex-direction: column;
  gap: var(--oco-s-2);
}
.drawer-handle {
  width: 40px;
  height: 4px;
  background: var(--oco-line-strong);
  border-radius: 2px;
  margin: 0 auto var(--oco-s-3);
}
.drawer-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
  border-top: 1px solid var(--oco-line);
  padding-top: var(--oco-s-2);
}
.drawer-section:first-of-type { border-top: none; padding-top: 0; }
.drawer-section-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.6px;
  text-transform: uppercase;
  color: var(--oco-ink-4);
  padding: 4px 8px 4px;
}
.drawer-item {
  display: flex;
  align-items: center;
  gap: var(--oco-s-3);
  padding: 12px var(--oco-s-3);
  border-radius: var(--oco-r-md);
  color: var(--oco-ink);
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  background: none;
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
  font-family: var(--oco-font-sans);
  transition: background 0.12s;
}
.drawer-item:hover { background: var(--oco-surface-2); text-decoration: none; }
.drawer-item--danger { color: var(--oco-danger); }
.di-icon { width: 20px; height: 20px; flex-shrink: 0; color: var(--oco-ink-3); }
.drawer-item--danger .di-icon { color: var(--oco-danger); }

/* Transitions */
.drawer-enter-active,
.drawer-leave-active { transition: opacity 0.2s ease; }
.drawer-enter-active .drawer,
.drawer-leave-active .drawer { transition: transform 0.25s ease; }
.drawer-enter-from,
.drawer-leave-to { opacity: 0; }
.drawer-enter-from .drawer,
.drawer-leave-to .drawer { transform: translateY(100%); }
</style>
