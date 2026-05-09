// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { ref, watchEffect } from 'vue'

const THEME_KEY = 'oco.theme'
const theme = ref<'light' | 'dark'>(
  (localStorage.getItem(THEME_KEY) as 'light' | 'dark') || 'light'
)

watchEffect(() => {
  if (theme.value === 'dark') document.documentElement.setAttribute('data-theme', 'dark')
  else document.documentElement.removeAttribute('data-theme')
  localStorage.setItem(THEME_KEY, theme.value)
})

export function useTheme() {
  return { theme, toggle: () => (theme.value = theme.value === 'dark' ? 'light' : 'dark') }
}
