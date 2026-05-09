<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <span class="brand-logo">OCO</span>
        <p class="brand-sub">{{ $t('auth.login.subtitle') }}</p>
      </div>

      <form class="login-form" @submit.prevent="handleLogin">
        <div class="field-group">
          <label class="field-label" for="username">{{ $t('auth.login.username') }}</label>
          <input id="username" v-model="username" type="text" autocomplete="username" :disabled="loading" required />
        </div>

        <div class="field-group">
          <label class="field-label" for="password">{{ $t('auth.login.password') }}</label>
          <input id="password" v-model="password" type="password" autocomplete="current-password" :disabled="loading" required />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? $t('auth.login.loading') : $t('auth.login.submit') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin(): Promise<void> {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(username.value, password.value)
    await router.push('/')
  } catch {
    error.value = t('auth.login.error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--oco-surface-2);
  padding: var(--oco-s-4);
}

.login-card {
  background: var(--oco-surface);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-xl);
  box-shadow: var(--oco-shadow-lg);
  padding: var(--oco-s-8);
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: var(--oco-s-6);
}

.login-brand { text-align: center; }
.brand-logo {
  display: inline-block;
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -1.5px;
  color: var(--oco-primary);
  font-family: var(--oco-font-sans);
}
.brand-sub { margin: var(--oco-s-1) 0 0; font-size: 14px; color: var(--oco-ink-3); }

.login-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.field-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }

.submit-btn {
  width: 100%;
  padding: 11px;
  background: var(--oco-primary);
  color: white;
  border: none;
  border-radius: var(--oco-r-lg);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  font-family: var(--oco-font-sans);
  transition: background 0.12s;
  margin-top: var(--oco-s-1);
}
.submit-btn:hover { background: var(--oco-primary-2); }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.error-msg {
  color: var(--oco-danger);
  font-size: 13px;
  background: var(--oco-danger-soft);
  padding: var(--oco-s-3);
  border-radius: var(--oco-r-md);
  margin: 0;
}
</style>
