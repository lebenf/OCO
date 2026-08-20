// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { describe, it, expect, beforeAll, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import ItemCaptureView from '../ItemCaptureView.vue'

const i18n = createI18n({ legacy: false, locale: 'it', missingWarn: false, fallbackWarn: false, messages: { it: {} } })

beforeAll(() => {
  let n = 0
  URL.createObjectURL = vi.fn(() => `blob:preview-${n++}`)
  URL.revokeObjectURL = vi.fn()
})

function mountView() {
  return mount(ItemCaptureView, {
    props: { houseId: 'house-1', containerId: 'container-1' },
    global: {
      plugins: [createPinia(), i18n],
      stubs: { RouterLink: true, HintTypeSelector: true, Photo: true, Btn: true },
    },
  })
}

async function pick(wrapper: ReturnType<typeof mountView>, names: string[]) {
  const input = wrapper.find('input[type="file"]')
  const files = names.map((name) => new File(['x'], name, { type: 'image/jpeg' }))
  Object.defineProperty(input.element, 'files', { value: files, configurable: true })
  await input.trigger('change')
}

describe('ItemCaptureView photo selection', () => {
  it('keeps earlier shots when another photo is taken', async () => {
    const wrapper = mountView()
    await pick(wrapper, ['first.jpg'])
    expect(wrapper.findAll('.preview-thumb')).toHaveLength(1)

    // Tapping "+" reopens the same picker: the second shot must be added, not swap out the first.
    await pick(wrapper, ['second.jpg'])
    expect(wrapper.findAll('.preview-thumb')).toHaveLength(2)
  })

  it('accepts several photos from one selection', async () => {
    const wrapper = mountView()
    await pick(wrapper, ['a.jpg', 'b.jpg', 'c.jpg'])
    expect(wrapper.findAll('.preview-thumb')).toHaveLength(3)
  })

  it('ignores a cancelled picker without dropping the selection', async () => {
    const wrapper = mountView()
    await pick(wrapper, ['first.jpg'])
    await pick(wrapper, [])
    expect(wrapper.findAll('.preview-thumb')).toHaveLength(1)
  })
})
