<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <!-- Desktop sidebar -->
    <AppSidebar
      v-if="isDesktop || isTablet"
      :collapsed="sidebarCollapsed"
      @toggle="sidebarCollapsed = !sidebarCollapsed"
    />

    <!-- Main column -->
    <div class="shell-main">
      <AppTopbar />
      <main class="shell-content">
        <slot />
      </main>
    </div>

    <!-- Mobile bottom nav -->
    <BottomNav v-if="isMobile" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useBreakpoint } from '@/composables/useBreakpoint'
import AppSidebar from './AppSidebar.vue'
import AppTopbar from './AppTopbar.vue'
import BottomNav from './BottomNav.vue'

const { isMobile, isTablet, isDesktop } = useBreakpoint()
const sidebarCollapsed = ref(false)
</script>

<style scoped>
.app-shell {
  display: flex;
  min-height: 100vh;
  background: var(--oco-bg);
}
.shell-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 100vh;
}
.shell-content {
  flex: 1;
  padding: var(--oco-s-5) var(--oco-s-4);
  /* clearance for mobile bottom nav */
  padding-bottom: calc(var(--oco-s-5) + 80px);
}

@media (min-width: 768px) {
  .shell-content {
    padding: var(--oco-s-5) var(--oco-s-5);
    padding-bottom: var(--oco-s-5);
  }
}
@media (min-width: 1024px) {
  .shell-content {
    padding: var(--oco-s-6) var(--oco-s-7);
  }
}
</style>
