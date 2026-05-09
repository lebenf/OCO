// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import ContainerCard from '../ContainerCard.vue'
import type { ContainerSummary } from '@/stores/containers'

const messages = {
  it: {
    status: { open: 'Aperta', closed: 'Chiusa', sealed: 'Sigillata' },
    container: {
      card: { items: '{n} oggetti', children: '{n} annidate' },
    },
  },
}
const i18n = createI18n({ legacy: false, locale: 'it', messages })

const baseContainer: ContainerSummary = {
  id: 'abc-123',
  code: 'T-001',
  status: 'open',
  destination_location: null,
  current_location: null,
  item_count: 3,
  volume_liters: 60.0,
  cover_photo_url: null,
  nesting_level: 0,
  children_count: 0,
}

function mountCard(container: Partial<ContainerSummary> = {}) {
  return mount(ContainerCard, {
    props: { container: { ...baseContainer, ...container } },
    global: { plugins: [createPinia(), i18n] },
  })
}

describe('ContainerCard', () => {
  it('renders code', () => {
    const wrapper = mountCard()
    expect(wrapper.text()).toContain('T-001')
  })

  it('shows open status badge', () => {
    const wrapper = mountCard({ status: 'open' })
    expect(wrapper.text()).toContain('Aperta')
  })

  it('shows closed status badge', () => {
    const wrapper = mountCard({ status: 'closed' })
    expect(wrapper.text()).toContain('Chiusa')
  })

  it('shows sealed status badge', () => {
    const wrapper = mountCard({ status: 'sealed' })
    expect(wrapper.text()).toContain('Sigillata')
  })

  it('shows destination location chip', () => {
    const wrapper = mountCard({
      destination_location: { id: 'd1', name: 'Soggiorno', house_id: 'h1', house_name: 'Casa Nuova' },
    })
    expect(wrapper.text()).toContain('Casa Nuova')
    expect(wrapper.text()).toContain('Soggiorno')
  })

  it('shows volume', () => {
    const wrapper = mountCard({ volume_liters: 60.0 })
    expect(wrapper.text()).toContain('60L')
  })

  it('emits click with container on click', async () => {
    const wrapper = mountCard()
    await wrapper.trigger('click')
    const emitted = wrapper.emitted('click')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toMatchObject({ id: 'abc-123', code: 'T-001' })
  })

  it('hides children count when zero', () => {
    const wrapper = mountCard({ children_count: 0 })
    expect(wrapper.text()).not.toContain('annidate')
  })

  it('shows children count when nonzero', () => {
    const wrapper = mountCard({ children_count: 2 })
    expect(wrapper.text()).toContain('ann.')
  })
})
