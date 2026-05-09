<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="qr-display">
    <img :src="qrSrc" :alt="`QR ${code}`" class="qr-img" />
    <a :href="qrSrc" :download="`${code}-qr.png`" class="download-btn">
      {{ $t('container.qr.download') }}
    </a>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useContainersStore } from '@/stores/containers'

const props = defineProps<{ houseId: string; containerId: string; code: string }>()
const store = useContainersStore()
const qrSrc = computed(() => store.qrUrl(props.houseId, props.containerId))
</script>

<style scoped>
.qr-display { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; }
.qr-img { width: 200px; height: 200px; border: 1px solid #eee; border-radius: 4px; }
.download-btn {
  font-size: 0.875rem;
  color: #4a90e2;
  text-decoration: none;
  padding: 0.3rem 0.75rem;
  border: 1px solid #4a90e2;
  border-radius: 4px;
}
.download-btn:hover { background: #4a90e2; color: #fff; }
</style>
