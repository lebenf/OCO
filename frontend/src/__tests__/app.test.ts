// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createI18n } from 'vue-i18n'
import App from '../App.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div>home</div>' } },
    { path: '/login', component: { template: '<div>login</div>' }, meta: { public: true } },
  ],
})

const i18n = createI18n({ legacy: false, locale: 'it', messages: { it: {} } })

describe('App', () => {
  it('mounts without errors', async () => {
    const wrapper = mount(App, {
      global: {
        plugins: [createPinia(), router, i18n],
      },
    })
    expect(wrapper.exists()).toBe(true)
  })
})
