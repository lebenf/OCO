<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div v-if="transfer" class="transfer-detail-view">
    <div class="detail-header">
      <RouterLink :to="`/houses/${houseId}/transfers`" class="back-link">← {{ $t('transfer.list.title') }}</RouterLink>
      <h2 class="view-title">{{ transfer.name }}</h2>
    </div>

    <div class="meta-row">
      <StatusBadge :kind="transfer.status" />
      <span v-if="transfer.destination_location" class="dest-chip">
        {{ transfer.destination_location.house_name }} · {{ transfer.destination_location.name }}
      </span>
      <span v-if="transfer.scheduled_date" class="date-chip num">{{ transfer.scheduled_date }}</span>
    </div>

    <VolumeIndicator
      v-if="transfer.vehicle_volume_liters"
      :used="transfer.total_volume_liters"
      :total="transfer.vehicle_volume_liters"
    />

    <Panel v-if="transfer.notes">
      <p class="notes-text">{{ transfer.notes }}</p>
    </Panel>

    <Panel>
      <template #action>
        <span class="section-title">{{ $t('transfer.detail.containers') }} <span class="num count">{{ transfer.containers.length }}</span></span>
        <div class="panel-actions">
          <Btn
            v-if="transfer.status === 'planned'"
            kind="soft"
            style="font-size:12px;padding:4px 10px"
            @click="showAddModal = true"
          >
            + {{ $t('transfer.detail.add_container') }}
          </Btn>
          <Btn v-if="transfer.status === 'planned'" @click="handleStart">
            {{ $t('transfer.detail.start') }}
          </Btn>
          <Btn v-if="transfer.status === 'in_progress'" @click="handleComplete">
            {{ $t('transfer.detail.complete') }}
          </Btn>
        </div>
      </template>
      <ContainerTransferList
        :containers="transfer.containers"
        :removable="transfer.status === 'planned'"
        @remove="handleRemoveContainer"
      />
    </Panel>

    <!-- Add container modal -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal-card">
          <div class="modal-header">
            <h3 class="modal-title">{{ $t('transfer.detail.add_container') }}</h3>
            <button class="modal-close" @click="showAddModal = false">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="16" height="16">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <ContainerCombobox
            :house-id="houseId"
            :placeholder="$t('transfer.detail.container_code_placeholder')"
            @select="onComboboxSelect"
          />

          <button class="qr-btn" @click="showQRScanner = true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
              <rect x="3" y="14" width="7" height="7"/>
              <path d="M14 14h2v2h-2zM18 14v2M14 18h4v2h-4M20 18v2"/>
            </svg>
            {{ $t('transfer.qr_scan.scan_btn') }}
          </button>

          <p v-if="addError" class="error-msg">{{ addError }}</p>
          <div class="modal-actions">
            <Btn kind="ghost" @click="showAddModal = false">{{ $t('container.edit.cancel') }}</Btn>
          </div>
        </div>
      </div>
    </Teleport>

    <QRScannerOverlay
      v-if="showQRScanner"
      @close="showQRScanner = false"
      @scanned="onQRScanned"
    />
  </div>

  <div v-else class="loading-state">
    <div v-for="i in 3" :key="i" class="skeleton"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useTransfersStore, type TransferDetail } from '@/stores/transfers'
import { useContainersStore, type ContainerSummary } from '@/stores/containers'
import VolumeIndicator from '@/components/transfers/VolumeIndicator.vue'
import ContainerTransferList from '@/components/transfers/ContainerTransferList.vue'
import ContainerCombobox from '@/components/containers/ContainerCombobox.vue'
import QRScannerOverlay from '@/components/containers/QRScannerOverlay.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'

const props = defineProps<{ houseId: string; transferId: string }>()
const store = useTransfersStore()
const containersStore = useContainersStore()

const transfer = ref<TransferDetail | null>(null)
const showAddModal = ref(false)
const showQRScanner = ref(false)
const addError = ref('')

async function load(): Promise<void> {
  transfer.value = await store.fetchTransfer(props.houseId, props.transferId)
}

async function handleStart(): Promise<void> {
  transfer.value = await store.startTransfer(props.houseId, props.transferId)
}

async function handleComplete(): Promise<void> {
  transfer.value = await store.completeTransfer(props.houseId, props.transferId)
}

async function handleRemoveContainer(containerId: string): Promise<void> {
  transfer.value = await store.removeContainer(props.houseId, props.transferId, containerId)
}

async function addContainerById(id: string): Promise<void> {
  addError.value = ''
  try {
    transfer.value = await store.addContainers(props.houseId, props.transferId, [id])
    showAddModal.value = false
  } catch {
    addError.value = 'Errore durante l\'aggiunta'
  }
}

async function onComboboxSelect(c: ContainerSummary): Promise<void> {
  await addContainerById(c.id)
}

async function onQRScanned(code: string): Promise<void> {
  showQRScanner.value = false
  addError.value = ''
  try {
    const container = await containersStore.fetchContainer(props.houseId, code)
    await addContainerById(container.id)
  } catch {
    addError.value = `Scatola "${code}" non trovata`
    showAddModal.value = true
  }
}

onMounted(load)
</script>

<style scoped>
.transfer-detail-view { display: flex; flex-direction: column; gap: var(--oco-s-4); max-width: 800px; }

.detail-header { display: flex; flex-direction: column; gap: var(--oco-s-2); }
.back-link { font-size: 13px; color: var(--oco-ink-3); font-weight: 500; }
.back-link:hover { text-decoration: none; color: var(--oco-ink); }
.view-title { font-size: 22px; font-weight: 600; letter-spacing: -0.4px; }

.meta-row { display: flex; align-items: center; gap: var(--oco-s-2); flex-wrap: wrap; }
.dest-chip {
  font-size: 13px; font-weight: 500; color: var(--oco-ink-2);
  background: var(--oco-surface-2); padding: 3px 10px; border-radius: var(--oco-r-xl);
}
.date-chip {
  font-size: 12px; color: var(--oco-ink-3);
  background: var(--oco-surface-2); padding: 3px 8px; border-radius: var(--oco-r-xl);
}

.section-title { font-size: 14px; font-weight: 600; color: var(--oco-ink); flex: 1; }
.count { font-size: 12px; color: var(--oco-ink-4); margin-left: var(--oco-s-1); }
.panel-actions { display: flex; gap: var(--oco-s-2); }

.notes-text { font-size: 14px; color: var(--oco-ink-3); margin: 0; }

.modal-overlay {
  position: fixed; inset: 0; background: rgba(20,18,28,0.4);
  display: flex; align-items: center; justify-content: center; z-index: 300;
  backdrop-filter: blur(2px);
}
.modal-card {
  background: var(--oco-surface); border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-xl); padding: var(--oco-s-6);
  width: min(400px, 90vw); display: flex; flex-direction: column; gap: var(--oco-s-4);
  box-shadow: var(--oco-shadow-lg);
}
.modal-header { display: flex; align-items: center; justify-content: space-between; }
.modal-title { font-size: 16px; font-weight: 600; margin: 0; }
.modal-close {
  width: 28px; height: 28px; border: none; background: var(--oco-surface-2);
  border-radius: 50%; color: var(--oco-ink-3); cursor: pointer;
  display: flex; align-items: center; justify-content: center;
}
.modal-actions { display: flex; gap: var(--oco-s-2); }
.error-msg { color: var(--oco-danger); font-size: 13px; margin: 0; }

.qr-btn {
  display: flex; align-items: center; gap: 8px;
  width: 100%; padding: 10px 12px;
  border: 1px dashed var(--oco-line-strong); border-radius: var(--oco-r-md);
  background: var(--oco-surface-2); color: var(--oco-ink-3);
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: all 0.12s;
}
.qr-btn:hover { border-color: var(--oco-primary); color: var(--oco-primary-ink); background: var(--oco-primary-soft); }
@media (min-width: 1024px) { .qr-btn { display: none; } }

.loading-state { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.skeleton { height: 72px; background: var(--oco-surface); border-radius: var(--oco-r-lg); animation: pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
