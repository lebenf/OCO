// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    ready: false,
  }),
})
