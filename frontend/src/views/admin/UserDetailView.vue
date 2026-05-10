<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div v-if="user" class="user-detail-view">
    <div class="detail-header">
      <RouterLink to="/admin/users" class="back-link">← {{ $t('admin.users.title') }}</RouterLink>
      <h2 class="view-title">{{ user.username }}</h2>
    </div>

    <Panel :title="$t('admin.users.edit_title')">
      <form class="edit-form" @submit.prevent="handleUpdate">
        <div class="field">
          <label>{{ $t('admin.users.username') }}</label>
          <input v-model="editForm.username" required />
        </div>
        <div class="field">
          <label>{{ $t('admin.users.email') }}</label>
          <input v-model="editForm.email" type="email" required />
        </div>
        <label class="check-label">
          <input v-model="editForm.is_system_admin" type="checkbox" />
          {{ $t('admin.users.sysadmin') }}
        </label>
        <p v-if="editError" class="error-msg">{{ editError }}</p>
        <p v-if="editSuccess" class="success-msg">{{ $t('admin.users.update_success') }}</p>
        <div class="form-actions">
          <Btn type="submit" :disabled="editSaving">{{ $t('admin.users.save') }}</Btn>
        </div>
      </form>
    </Panel>

    <Panel :title="$t('admin.users.reset_password_title')">
      <form class="edit-form" @submit.prevent="handleResetPassword">
        <div class="field">
          <label>{{ $t('admin.users.new_password') }}</label>
          <input v-model="newPassword" type="password" required minlength="8" autocomplete="new-password" />
        </div>
        <p v-if="resetError" class="error-msg">{{ resetError }}</p>
        <p v-if="resetSuccess" class="success-msg">{{ $t('admin.users.reset_password_success') }}</p>
        <div class="form-actions">
          <Btn type="submit" :disabled="resetSaving" kind="soft">{{ $t('admin.users.reset_password') }}</Btn>
        </div>
      </form>
    </Panel>
  </div>

  <div v-else class="loading-state">
    <div v-for="i in 2" :key="i" class="skeleton"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ userId: string }>()

interface UserOut {
  id: string
  username: string
  email: string
  is_system_admin: boolean
  is_active: boolean
}

const user = ref<UserOut | null>(null)
const editForm = ref({ username: '', email: '', is_system_admin: false })
const editSaving = ref(false)
const editError = ref('')
const editSuccess = ref(false)

const newPassword = ref('')
const resetSaving = ref(false)
const resetError = ref('')
const resetSuccess = ref(false)

async function load(): Promise<void> {
  const res = await api.get(`/admin/users`)
  const found = res.data.items.find((u: UserOut) => u.id === props.userId)
  if (found) {
    user.value = found
    editForm.value = { username: found.username, email: found.email, is_system_admin: found.is_system_admin }
  }
}

async function handleUpdate(): Promise<void> {
  editError.value = ''
  editSuccess.value = false
  editSaving.value = true
  try {
    const res = await api.put(`/admin/users/${props.userId}`, editForm.value)
    user.value = res.data
    editSuccess.value = true
  } catch {
    editError.value = 'Errore durante l\'aggiornamento'
  } finally {
    editSaving.value = false
  }
}

async function handleResetPassword(): Promise<void> {
  resetError.value = ''
  resetSuccess.value = false
  resetSaving.value = true
  try {
    await api.post(`/admin/users/${props.userId}/reset-password`, { new_password: newPassword.value })
    newPassword.value = ''
    resetSuccess.value = true
  } catch {
    resetError.value = 'Errore durante il reset password'
  } finally {
    resetSaving.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.user-detail-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 560px; }
.detail-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.edit-form { display: flex; flex-direction: column; gap: var(--oco-s-4); }
.field { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field label { font-size: 12px; font-weight: 500; color: var(--oco-ink-3); }
.check-label { display: flex; align-items: center; gap: var(--oco-s-1); font-size: 13px; color: var(--oco-ink-2); cursor: pointer; }
.form-actions { display: flex; }
.error-msg { color: var(--oco-danger); font-size: 13px; margin: 0; }
.success-msg { color: var(--oco-ok); font-size: 13px; margin: 0; }

.loading-state { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.skeleton { height: 160px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
