// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { ref, onMounted, onUnmounted } from 'vue'

export function useBreakpoint() {
  const isMobile = ref(typeof window !== 'undefined' ? window.innerWidth < 768 : false)
  const isTablet = ref(typeof window !== 'undefined' ? window.innerWidth >= 768 && window.innerWidth < 1024 : false)
  const isDesktop = ref(typeof window !== 'undefined' ? window.innerWidth >= 1024 : true)

  function update() {
    isMobile.value = window.innerWidth < 768
    isTablet.value = window.innerWidth >= 768 && window.innerWidth < 1024
    isDesktop.value = window.innerWidth >= 1024
  }

  onMounted(() => window.addEventListener('resize', update))
  onUnmounted(() => window.removeEventListener('resize', update))

  return { isMobile, isTablet, isDesktop }
}
