// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { createI18n } from 'vue-i18n'
import it from './locales/it.json'
import en from './locales/en.json'
import fr from './locales/fr.json'
import de from './locales/de.json'
import es from './locales/es.json'
import pt from './locales/pt.json'

export default createI18n({
  legacy: false,
  locale: 'it',
  fallbackLocale: 'en',
  messages: { it, en, fr, de, es, pt },
})
