<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <Teleport to="body">
    <div class="modal-overlay" @click.self="emit('close')">
      <div class="modal-card">
        <div class="modal-header">
          <h3 class="modal-title">{{ $t('transfer.add_dialog.title') }}</h3>
          <button class="modal-close" @click="emit('close')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <p class="selected-summary">{{ $t('transfer.add_dialog.container_count', { n: containerIds.length }) }}</p>

        <div v-if="loading" class="transfer-pick-list">
          <div v-for="i in 3" :key="i" class="skeleton"></div>
        </div>
        <div v-else-if="plannedTransfers.length === 0" class="empty">
          {{ $t('transfer.add_dialog.no_planned') }}
        </div>
        <div v-else class="transfer-pick-list">
          <label
            v-for="t in plannedTransfers"
            :key="t.id"
            class="transfer-pick-row"
            :class="{ selected: selectedTransferId === t.id }"
          >
            <input v-model="selectedTransferId" type="radio" name="pick-transfer" :value="t.id" />
            <span class="pick-name">{{ t.name }}</span>
            <span v-if="t.destination_location" class="pick-dest">{{ t.destination_location.name }}</span>
            <span class="pick-count num">{{ t.container_count }}</span>
          </label>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <div class="modal-actions">
          <Btn kind="ghost" @click="emit('close')">{{ $t('container.edit.cancel') }}</Btn>
          <Btn :disabled="!selectedTransferId || saving" @click="confirm">
            {{ saving ? $t('container.edit.saving') : $t('transfer.add_dialog.confirm') }}
          </Btn>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTransfersStore, type TransferSummary } from '@/stores/transfers'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string; containerIds: string[] }>()
const emit = defineEmits<{ close: []; added: [] }>()

const store = useTransfersStore()
const plannedTransfers = ref<TransferSummary[]>([])
const selectedTransferId = ref<string | null>(null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

onMounted(async () => {
  loading.value = true
  try {
    plannedTransfers.value = await store.fetchTransfers(props.houseId, { status: 'planned' })
  } finally {
    loading.value = false
  }
})

async function confirm(): Promise<void> {
  if (!selectedTransferId.value) return
  saving.value = true
  error.value = ''
  try {
    await store.addContainers(props.houseId, selectedTransferId.value, props.containerIds)
    emit('added')
  } catch (err: unknown) {
    const e = err as { response?: { data?: { detail?: string } } }
    error.value = e.response?.data?.detail ?? String(err)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(20,18,28,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 300;
  backdrop-filter: blur(2px);
}
.modal-card {
  background: var(--oco-surface); border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-xl); padding: var(--oco-s-6);
  width: min(420px, 90vw); display: flex; flex-direction: column; gap: var(--oco-s-4);
  box-shadow: var(--oco-shadow-lg);
}
.modal-header { display: flex; align-items: center; justify-content: space-between; }
.modal-title { font-size: 16px; font-weight: 600; margin: 0; }
.modal-close {
  width: 28px; height: 28px; border: none; background: var(--oco-surface-2);
  border-radius: 50%; color: var(--oco-ink-3); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.modal-actions { display: flex; justify-content: flex-end; gap: var(--oco-s-2); }
.error-msg { color: var(--oco-danger); font-size: 13px; margin: 0; }

.selected-summary { font-size: 13px; color: var(--oco-ink-3); margin: 0; }

.transfer-pick-list { display: flex; flex-direction: column; gap: 2px; max-height: 280px; overflow-y: auto; }
.transfer-pick-row {
  display: flex; align-items: center; gap: var(--oco-s-2);
  padding: var(--oco-s-2) var(--oco-s-2); border-radius: var(--oco-r-md);
  font-size: 13px; cursor: pointer; transition: background 0.1s;
}
.transfer-pick-row:hover { background: var(--oco-surface-2); }
.transfer-pick-row.selected { background: var(--oco-primary-soft); }
.pick-name { font-weight: 500; flex: 1; }
.pick-dest { font-size: 12px; color: var(--oco-ink-4); }
.pick-count { font-size: 12px; color: var(--oco-ink-4); }

.empty { color: var(--oco-ink-4); font-size: 13px; text-align: center; padding: var(--oco-s-4); }
.skeleton { height: 36px; background: var(--oco-surface-2); border-radius: var(--oco-r-md); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
