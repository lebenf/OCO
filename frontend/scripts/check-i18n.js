#!/usr/bin/env node
/**
 * Checks that all locale files have the same keys as the reference (it.json).
 * Usage: node scripts/check-i18n.js
 */

import { readFileSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const localesDir = resolve(__dirname, '../src/i18n/locales')

const LOCALES = ['en', 'fr', 'de', 'es', 'pt']
const REFERENCE = 'it'

function flattenKeys(obj, prefix = '') {
  return Object.entries(obj).flatMap(([k, v]) => {
    const key = prefix ? `${prefix}.${k}` : k
    return typeof v === 'object' && v !== null ? flattenKeys(v, key) : [key]
  })
}

function loadLocale(locale) {
  const path = resolve(localesDir, `${locale}.json`)
  return JSON.parse(readFileSync(path, 'utf8'))
}

const reference = loadLocale(REFERENCE)
const refKeys = new Set(flattenKeys(reference))

let hasError = false

for (const locale of LOCALES) {
  let data
  try {
    data = loadLocale(locale)
  } catch {
    console.error(`ERROR: could not load ${locale}.json`)
    hasError = true
    continue
  }

  const keys = new Set(flattenKeys(data))

  const missing = [...refKeys].filter(k => !keys.has(k))
  const extra = [...keys].filter(k => !refKeys.has(k))

  if (missing.length === 0 && extra.length === 0) {
    console.log(`✓ ${locale}.json — ${keys.size} keys OK`)
  } else {
    if (missing.length) {
      console.error(`✗ ${locale}.json — missing keys (${missing.length}):`)
      missing.forEach(k => console.error(`    - ${k}`))
    }
    if (extra.length) {
      console.warn(`  ${locale}.json — extra keys (${extra.length}):`)
      extra.forEach(k => console.warn(`    + ${k}`))
    }
    hasError = true
  }
}

process.exit(hasError ? 1 : 0)
