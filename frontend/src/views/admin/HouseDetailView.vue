<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="admin-view">
    <div class="admin-header">
      <RouterLink to="/admin/houses" class="back-link">← {{ $t('admin.back') }}</RouterLink>
      <h2 class="view-title">{{ house?.name }}</h2>
    </div>

    <div class="sections-grid">
      <!-- General info -->
      <Panel :title="$t('admin.house.general')">
        <form class="edit-form" @submit.prevent="saveHouse">
          <div class="form-group">
            <label class="field-label">{{ $t('admin.house.name') }}</label>
            <input v-model="editForm.name" required />
          </div>
          <div class="form-group">
            <label class="field-label">{{ $t('admin.house.description') }}</label>
            <input v-model="editForm.description" />
          </div>
          <div class="form-group">
            <label class="field-label">{{ $t('admin.house.code_prefix') }}</label>
            <input v-model="editForm.code_prefix" maxlength="1" style="width:60px" required />
          </div>
          <div class="form-actions">
            <Btn type="submit" :disabled="savingHouse" style="padding:6px 12px;font-size:13px">
              {{ savingHouse ? $t('container.edit.saving') : $t('admin.save') }}
            </Btn>
            <span v-if="saveOk" class="save-ok">✓</span>
          </div>
        </form>
      </Panel>

      <!-- Members -->
      <Panel :title="$t('admin.house.members')">
        <form class="row-form" @submit.prevent="addMember">
          <select v-model="memberForm.user_id" required>
            <option value="" disabled>{{ $t('admin.house.select_user') }}</option>
            <option v-for="u in availableUsers" :key="u.id" :value="u.id">{{ u.username }} ({{ u.email }})</option>
          </select>
          <select v-model="memberForm.role">
            <option value="member">member</option>
            <option value="admin">admin</option>
          </select>
          <Btn type="submit" :disabled="!memberForm.user_id" style="padding:6px 12px;font-size:13px">{{ $t('admin.add') }}</Btn>
        </form>
        <ul class="item-list">
          <li v-for="m in members" :key="m.user_id" class="list-row">
            <div class="list-info">
              <span class="mono list-name">{{ m.username }}</span>
              <span class="list-sub">{{ m.email }}</span>
            </div>
            <span class="role-badge">{{ m.role }}</span>
            <button class="remove-btn" @click="removeMember(m.user_id)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </li>
        </ul>
      </Panel>

      <!-- Locations -->
      <Panel :title="$t('admin.house.locations')">
        <form class="row-form" @submit.prevent="addLocation">
          <input v-model="locForm.name" :placeholder="$t('admin.house.location_name')" required />
          <Btn type="submit" style="padding:6px 12px;font-size:13px">{{ $t('admin.add') }}</Btn>
        </form>
        <ul class="item-list">
          <li v-for="l in locations" :key="l.id" class="list-row">
            <span class="list-name">{{ l.name }}</span>
            <button class="remove-btn" @click="deleteLocation(l.id)">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </li>
        </ul>
      </Panel>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'
import type { LocationOut } from '@/stores/houses'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

interface MemberOut { user_id: string; username: string; email: string; role: string }
interface HouseOut { id: string; name: string; description: string | null; code_prefix: string }
interface UserOut { id: string; username: string; email: string }

const route = useRoute()
const houseId = route.params.id as string

const house = ref<HouseOut | null>(null)
const members = ref<MemberOut[]>([])
const locations = ref<LocationOut[]>([])
const allUsers = ref<UserOut[]>([])

const memberIds = computed(() => new Set(members.value.map((m) => m.user_id)))
const availableUsers = computed(() => allUsers.value.filter((u) => !memberIds.value.has(u.id)))

const memberForm = ref({ user_id: '', role: 'member' })
const locForm = ref({ name: '' })
const editForm = ref({ name: '', description: '', code_prefix: '' })
const savingHouse = ref(false)
const saveOk = ref(false)

async function load(): Promise<void> {
  const [hRes, mRes, lRes, uRes] = await Promise.all([
    api.get(`/admin/houses`),
    api.get(`/admin/houses/${houseId}/members`),
    api.get(`/houses/${houseId}/locations`),
    api.get(`/admin/users`),
  ])
  house.value = hRes.data.items.find((h: HouseOut) => h.id === houseId) ?? null
  members.value = mRes.data
  locations.value = lRes.data
  allUsers.value = uRes.data.items
  if (house.value) {
    editForm.value.name = house.value.name
    editForm.value.description = house.value.description ?? ''
    editForm.value.code_prefix = house.value.code_prefix
  }
}

async function saveHouse(): Promise<void> {
  savingHouse.value = true
  saveOk.value = false
  try {
    await api.put(`/admin/houses/${houseId}`, {
      name: editForm.value.name,
      description: editForm.value.description || null,
      code_prefix: editForm.value.code_prefix,
    })
    await load()
    saveOk.value = true
    setTimeout(() => { saveOk.value = false }, 2000)
  } finally {
    savingHouse.value = false
  }
}

async function addMember(): Promise<void> {
  await api.post(`/admin/houses/${houseId}/members`, { user_id: memberForm.value.user_id, role: memberForm.value.role })
  memberForm.value.user_id = ''
  await load()
}

async function removeMember(userId: string): Promise<void> {
  await api.delete(`/admin/houses/${houseId}/members/${userId}`)
  await load()
}

async function addLocation(): Promise<void> {
  await api.post(`/houses/${houseId}/locations`, { name: locForm.value.name })
  locForm.value.name = ''
  await load()
}

async function deleteLocation(id: string): Promise<void> {
  await api.delete(`/houses/${houseId}/locations/${id}`)
  await load()
}

onMounted(load)
</script>

<style scoped>
.admin-view { display: flex; flex-direction: column; gap: var(--oco-s-5); max-width: 900px; }
.admin-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.sections-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: var(--oco-s-4); }

.edit-form { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.form-group { display: flex; flex-direction: column; gap: var(--oco-s-1); }
.field-label { font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase; color: var(--oco-ink-3); }
.form-actions { display: flex; align-items: center; gap: var(--oco-s-3); }
.save-ok { font-size: 13px; color: var(--oco-ok); font-weight: 600; }

.row-form { display: flex; gap: var(--oco-s-2); flex-wrap: wrap; align-items: center; margin-bottom: var(--oco-s-3); }
.row-form input { flex: 1; min-width: 100px; }
.color-input { width: 40px; height: 36px; border: 1px solid var(--oco-line); border-radius: var(--oco-r-md); padding: 2px; cursor: pointer; }

.item-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 1px; }
.list-row {
  display: flex; align-items: center; gap: var(--oco-s-2);
  padding: var(--oco-s-2) 0;
  border-bottom: 1px solid var(--oco-line);
}
.list-row:last-child { border-bottom: none; }
.list-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px; }
.list-name { font-size: 13px; font-weight: 500; color: var(--oco-ink); }
.list-sub { font-size: 11px; color: var(--oco-ink-4); }
.role-badge {
  font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px;
  padding: 2px 6px; border-radius: var(--oco-r-sm);
  background: var(--oco-surface-2); color: var(--oco-ink-3);
}
.dest-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.remove-btn {
  flex-shrink: 0; width: 24px; height: 24px; border: none;
  background: transparent; color: var(--oco-ink-4); cursor: pointer;
  border-radius: var(--oco-r-sm); display: flex; align-items: center; justify-content: center;
  transition: background 0.12s, color 0.12s;
}
.remove-btn:hover { background: var(--oco-danger-soft); color: var(--oco-danger); }
</style>
