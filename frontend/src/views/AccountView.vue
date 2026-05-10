<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="account-view">
    <h2 class="view-title">{{ $t('account.title') }}</h2>

    <Panel :title="$t('account.profile.title')">
      <div class="profile-info">
        <div class="info-row">
          <span class="info-label">{{ $t('account.profile.username') }}</span>
          <span class="info-value mono">{{ authStore.user?.username }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">{{ $t('account.profile.email') }}</span>
          <span class="info-value">{{ authStore.user?.email }}</span>
        </div>
      </div>
    </Panel>

    <Panel :title="$t('account.change_password.title')">
      <form class="pw-form" @submit.prevent="handleChangePassword">
        <div class="field">
          <label>{{ $t('account.change_password.current') }}</label>
          <input
            v-model="pwForm.current_password"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>
        <div class="field">
          <label>{{ $t('account.change_password.new') }}</label>
          <input
            v-model="pwForm.new_password"
            type="password"
            autocomplete="new-password"
            required
            minlength="8"
          />
        </div>
        <div class="field">
          <label>{{ $t('account.change_password.confirm') }}</label>
          <input
            v-model="pwForm.confirm_password"
            type="password"
            autocomplete="new-password"
            required
          />
        </div>
        <p v-if="pwError" class="error-msg">{{ pwError }}</p>
        <p v-if="pwSuccess" class="success-msg">{{ $t('account.change_password.success') }}</p>
        <div class="form-actions">
          <Btn type="submit" :disabled="pwSaving">{{ $t('account.change_password.submit') }}</Btn>
        </div>
      </form>
    </Panel>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

const { t } = useI18n()
const authStore = useAuthStore()

const pwForm = ref({ current_password: '', new_password: '', confirm_password: '' })
const pwSaving = ref(false)
const pwError = ref('')
const pwSuccess = ref(false)

async function handleChangePassword(): Promise<void> {
  pwError.value = ''
  pwSuccess.value = false
  if (pwForm.value.new_password !== pwForm.value.confirm_password) {
    pwError.value = t('account.change_password.mismatch')
    return
  }
  pwSaving.value = true
  try {
    await api.post('/auth/me/change-password', {
      current_password: pwForm.value.current_password,
      new_password: pwForm.value.new_password,
    })
    pwForm.value = { current_password: '', new_password: '', confirm_password: '' }
    pwSuccess.value = true
  } catch (e: any) {
    const code = e?.response?.data?.detail?.code
    if (code === 'WRONG_PASSWORD') {
      pwError.value = t('account.change_password.wrong_current')
    } else {
      pwError.value = t('account.change_password.error')
    }
  } finally {
    pwSaving.value = false
  }
}
</script>

<style scoped>
.account-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 560px; }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.profile-info { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.info-row { display: flex; gap: var(--oco-s-4); align-items: baseline; }
.info-label { font-size: 12px; color: var(--oco-ink-4); font-weight: 500; width: 80px; flex-shrink: 0; }
.info-value { font-size: 14px; color: var(--oco-ink); }

.pw-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.field { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field label { font-size: 12px; font-weight: 500; color: var(--oco-ink-3); }
.form-actions { display: flex; }
.error-msg { color: var(--oco-danger); font-size: 13px; margin: 0; }
.success-msg { color: var(--oco-ok); font-size: 13px; margin: 0; }
</style>
