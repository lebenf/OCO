<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="admin-view">
    <h2 class="view-title">{{ $t('admin.users.title') }}</h2>

    <Panel :title="$t('admin.create')">
      <form class="row-form" @submit.prevent="handleCreate">
        <input v-model="form.username" :placeholder="$t('admin.users.username')" required />
        <input v-model="form.email" type="email" :placeholder="$t('admin.users.email')" required />
        <input v-model="form.password" type="password" :placeholder="$t('admin.users.password')" required />
        <label class="check-label">
          <input v-model="form.is_system_admin" type="checkbox" />
          {{ $t('admin.users.sysadmin') }}
        </label>
        <Btn type="submit" :disabled="saving">{{ $t('admin.create') }}</Btn>
      </form>
      <p v-if="error" class="error-msg">{{ error }}</p>
    </Panel>

    <Panel v-if="users.length">
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{{ $t('admin.users.username') }}</th>
              <th>{{ $t('admin.users.email') }}</th>
              <th>Admin</th>
              <th>{{ $t('admin.users.active') }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id" :class="{ 'row-inactive': !u.is_active }">
              <td class="mono">{{ u.username }}</td>
              <td>{{ u.email }}</td>
              <td>
                <span v-if="u.is_system_admin" class="badge badge--admin">admin</span>
              </td>
              <td>
                <span class="badge" :class="u.is_active ? 'badge--ok' : 'badge--mute'">
                  {{ u.is_active ? $t('admin.users.active') : $t('admin.users.inactive') }}
                </span>
              </td>
              <td>
                <div style="display:flex;gap:4px">
                  <Btn kind="ghost" style="font-size:12px;padding:3px 8px" :to="`/admin/users/${u.id}`">
                    {{ $t('admin.users.edit') }}
                  </Btn>
                  <Btn v-if="u.is_active" kind="ghost" style="font-size:12px;padding:3px 8px" @click="handleDeactivate(u.id)">
                    {{ $t('admin.users.deactivate') }}
                  </Btn>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </Panel>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

interface UserOut {
  id: string
  username: string
  email: string
  is_system_admin: boolean
  is_active: boolean
}

const users = ref<UserOut[]>([])
const error = ref('')
const saving = ref(false)
const form = ref({ username: '', email: '', password: '', is_system_admin: false })

async function loadUsers(): Promise<void> {
  const res = await api.get('/admin/users')
  users.value = res.data.items
}

async function handleCreate(): Promise<void> {
  error.value = ''
  saving.value = true
  try {
    await api.post('/admin/users', form.value)
    form.value = { username: '', email: '', password: '', is_system_admin: false }
    await loadUsers()
  } catch {
    error.value = 'Errore nella creazione utente'
  } finally {
    saving.value = false
  }
}

async function handleDeactivate(id: string): Promise<void> {
  await api.delete(`/admin/users/${id}`)
  await loadUsers()
}

onMounted(loadUsers)
</script>

<style scoped>
.admin-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 900px; }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.row-form { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; align-items: center; }
.row-form input { min-width: 140px; }
.check-label { display: flex; align-items: center; gap: var(--oco-s-1); font-size: 13px; color: var(--oco-ink-2); cursor: pointer; white-space: nowrap; }

.error-msg { color: var(--oco-danger); font-size: 13px; margin-top: var(--oco-s-2); }

.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--oco-ink-4);
  padding: var(--oco-s-2) var(--oco-s-3);
  text-align: left;
  border-bottom: 1px solid var(--oco-line);
}
td { padding: var(--oco-s-2) var(--oco-s-3); font-size: 14px; color: var(--oco-ink); border-bottom: 1px solid var(--oco-line); }
tr:last-child td { border-bottom: none; }
tr.row-inactive td { color: var(--oco-ink-4); }

.badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: var(--oco-r-xl);
}
.badge--ok    { background: var(--oco-ok-soft); color: var(--oco-ok); }
.badge--mute  { background: var(--oco-mute-soft); color: var(--oco-mute); }
.badge--admin { background: var(--oco-primary-soft); color: var(--oco-primary); }
</style>
