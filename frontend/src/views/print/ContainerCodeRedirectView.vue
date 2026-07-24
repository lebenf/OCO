<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="redirect-page">
    <p v-if="error">{{ error }}</p>
    <p v-else>{{ $t('container.redirect.loading') }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

const props = defineProps<{ code: string }>()

const router = useRouter()
const { t } = useI18n()
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get<{ house_id: string; container_id: string }>(
      `/containers/by-code/${props.code}`,
    )
    router.replace(`/houses/${data.house_id}/containers/${data.container_id}`)
  } catch (e: any) {
    error.value =
      e?.response?.status === 404
        ? t('container.redirect.not_found')
        : t('container.redirect.error')
  }
})
</script>

<style scoped>
.redirect-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--oco-s-5);
  text-align: center;
}
</style>
