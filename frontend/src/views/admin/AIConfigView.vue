<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="admin-view">
    <h2 class="view-title">{{ $t('admin.ai_config.title') }}</h2>

    <div v-if="loading" class="skeleton-list">
      <div v-for="i in 3" :key="i" class="skeleton"></div>
    </div>

    <form v-else class="config-form" @submit.prevent="handleSave">
      <!-- Provider selector -->
      <Panel :title="$t('admin.ai_config.active_provider')">
        <div class="provider-grid">
          <label v-for="p in providers" :key="p" class="provider-card" :class="{ active: form.active_provider === p }">
            <input v-model="form.active_provider" type="radio" :value="p" hidden />
            <span class="provider-name">{{ p }}</span>
          </label>
        </div>
      </Panel>

      <!-- Ollama -->
      <Panel title="Ollama">
        <template #action>
          <span class="status-dot" :class="config?.ollama.reachable ? 'dot--ok' : 'dot--fail'"></span>
          <span class="status-text" :class="config?.ollama.reachable ? 'text--ok' : 'text--fail'">
            {{ config?.ollama.reachable ? $t('admin.ai_config.ollama.reachable') : $t('admin.ai_config.ollama.unreachable') }}
          </span>
        </template>
        <div class="fields">
          <div class="field-group">
            <label class="field-label">{{ $t('admin.ai_config.ollama.url') }}</label>
            <input v-model="form.ollama_url" type="url" />
          </div>
          <div class="field-group">
            <label class="field-label">{{ $t('admin.ai_config.ollama.model') }}</label>
            <input v-model="form.ollama_model" />
          </div>
        </div>
      </Panel>

      <!-- Claude -->
      <Panel title="Claude API">
        <template #action>
          <span class="status-dot" :class="config?.claude.configured ? 'dot--ok' : 'dot--neutral'"></span>
          <span class="status-text" :class="config?.claude.configured ? 'text--ok' : 'text--mute'">
            {{ config?.claude.configured ? $t('admin.ai_config.claude.configured') : $t('admin.ai_config.claude.not_configured') }}
          </span>
        </template>
        <div class="field-group">
          <label class="field-label">{{ $t('admin.ai_config.claude.api_key') }}</label>
          <input v-model="form.claude_api_key" type="password" autocomplete="new-password" placeholder="sk-ant-…" />
        </div>
      </Panel>

      <!-- Mistral -->
      <Panel title="Mistral API">
        <template #action>
          <span class="status-dot" :class="config?.mistral.configured ? 'dot--ok' : 'dot--neutral'"></span>
          <span class="status-text" :class="config?.mistral.configured ? 'text--ok' : 'text--mute'">
            {{ config?.mistral.configured ? $t('admin.ai_config.mistral.configured') : $t('admin.ai_config.mistral.not_configured') }}
          </span>
        </template>
        <div class="field-group">
          <label class="field-label">{{ $t('admin.ai_config.mistral.api_key') }}</label>
          <input v-model="form.mistral_api_key" type="password" autocomplete="new-password" placeholder="…" />
        </div>
      </Panel>

      <p v-if="saveError" class="error-msg">{{ saveError }}</p>
      <p v-if="saveSuccess" class="success-msg">{{ $t('admin.ai_config.saved') }}</p>

      <!-- Test result -->
      <div v-if="testResult" class="test-result" :class="testResult.ok ? 'test--ok' : 'test--fail'">
        <span v-if="testResult.ok">
          {{ $t('admin.ai_config.test_ok') }}
          <span v-if="testResult.latency_ms" class="num"> — {{ testResult.latency_ms }}ms</span>
        </span>
        <span v-else>{{ $t('admin.ai_config.test_failed') }}: {{ testResult.error }}</span>
      </div>

      <div class="form-actions">
        <Btn type="submit" :disabled="saving">
          {{ saving ? $t('admin.ai_config.saving') : $t('admin.ai_config.save') }}
        </Btn>
        <Btn kind="soft" type="button" :disabled="testing" @click="handleTest">
          {{ testing ? $t('admin.ai_config.testing') : $t('admin.ai_config.test') }}
        </Btn>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

interface OllamaOut { url: string; model: string; reachable: boolean }
interface ProviderOut { configured: boolean }
interface AIConfigOut { active_provider: string; ollama: OllamaOut; claude: ProviderOut; mistral: ProviderOut }
interface AITestOut { ok: boolean; latency_ms?: number; provider: string; error?: string }

const providers = ['ollama', 'claude', 'mistral']
const loading = ref(true)
const saving = ref(false)
const testing = ref(false)
const saveError = ref('')
const saveSuccess = ref(false)
const config = ref<AIConfigOut | null>(null)
const testResult = ref<AITestOut | null>(null)

const form = ref({ active_provider: 'ollama', ollama_url: '', ollama_model: '', claude_api_key: '', mistral_api_key: '' })

onMounted(async () => {
  const { data } = await api.get<AIConfigOut>('/admin/config/ai')
  config.value = data
  form.value.active_provider = data.active_provider
  form.value.ollama_url = data.ollama.url
  form.value.ollama_model = data.ollama.model
  loading.value = false
})

async function handleSave(): Promise<void> {
  saving.value = true
  saveError.value = ''
  saveSuccess.value = false
  try {
    const payload: Record<string, string> = {
      active_provider: form.value.active_provider,
      ollama_url: form.value.ollama_url,
      ollama_model: form.value.ollama_model,
    }
    if (form.value.claude_api_key) payload.claude_api_key = form.value.claude_api_key
    if (form.value.mistral_api_key) payload.mistral_api_key = form.value.mistral_api_key
    const { data } = await api.put<AIConfigOut>('/admin/config/ai', payload)
    config.value = data
    form.value.claude_api_key = ''
    form.value.mistral_api_key = ''
    saveSuccess.value = true
  } catch (e: unknown) {
    saveError.value = String(e)
  } finally {
    saving.value = false
  }
}

async function handleTest(): Promise<void> {
  testing.value = true
  testResult.value = null
  try {
    const { data } = await api.post<AITestOut>('/admin/config/ai/test')
    testResult.value = data
  } finally {
    testing.value = false
  }
}
</script>

<style scoped>
.admin-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 640px; }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.config-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }

.provider-grid { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; }
.provider-card {
  flex: 1;
  min-width: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--oco-s-3) var(--oco-s-4);
  border: 1.5px solid var(--oco-line);
  border-radius: var(--oco-r-lg);
  cursor: pointer;
  transition: border-color 0.12s, background 0.12s;
}
.provider-card.active { border-color: var(--oco-primary); background: var(--oco-primary-soft); }
.provider-name { font-size: 14px; font-weight: 600; text-transform: capitalize; color: var(--oco-ink-2); }
.provider-card.active .provider-name { color: var(--oco-primary); }

.fields { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.field-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }

/* Status indicators in panel header */
.status-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.status-text { font-size: 12px; font-weight: 600; }
.dot--ok    { background: var(--oco-ok); }
.dot--fail  { background: var(--oco-danger); }
.dot--neutral { background: var(--oco-ink-4); }
.text--ok   { color: var(--oco-ok); }
.text--fail { color: var(--oco-danger); }
.text--mute { color: var(--oco-ink-4); }

.error-msg   { color: var(--oco-danger); font-size: 13px; }
.success-msg { color: var(--oco-ok); font-size: 13px; font-weight: 600; }

.test-result {
  padding: var(--oco-s-3) var(--oco-s-4);
  border-radius: var(--oco-r-lg);
  font-size: 13px;
  font-weight: 500;
}
.test--ok   { background: var(--oco-ok-soft); color: var(--oco-ok); }
.test--fail { background: var(--oco-danger-soft); color: var(--oco-danger); }

.form-actions { display: flex; gap: var(--oco-s-3); }

.skeleton-list { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.skeleton { height: 120px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
