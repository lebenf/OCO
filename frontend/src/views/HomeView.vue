<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="home">
    <h1>OCO</h1>
    <p>{{ $t('app.tagline') }}</p>
    <div class="health-status">
      <span v-if="healthStatus === 'ok'" class="ok">Backend: OK</span>
      <span v-else-if="healthStatus === 'error'" class="error">Backend: unreachable</span>
      <span v-else>Checking backend...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'

const healthStatus = ref<'loading' | 'ok' | 'error'>('loading')

onMounted(async () => {
  try {
    const res = await axios.get('/health', { validateStatus: () => true })
    healthStatus.value = res.status < 500 ? 'ok' : 'error'
  } catch {
    healthStatus.value = 'error'
  }
})
</script>

<style scoped>
.home { padding: 2rem; text-align: center; }
.ok { color: green; }
.error { color: red; }
</style>
