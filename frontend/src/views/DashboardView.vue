<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
<!-- Copyright 2026 Lorenzo Benfenati -->
<template>
  <div class="dashboard-view">
    <!-- Greeting -->
    <div class="greeting">
      <h1 class="greeting-text">{{ greeting }}</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="skeleton" v-for="i in 4" :key="i"></div>
    </div>

    <template v-else-if="data">
      <!-- Stats -->
      <div class="stats-grid">
        <Stat :value="data.containers.total" :label="$t('dashboard.total_containers')" />
        <Stat :value="data.items.total" :label="$t('dashboard.total_items')" />
        <Stat
          :value="(data.containers.by_status['closed'] ?? 0) + (data.containers.by_status['sealed'] ?? 0)"
          :label="$t('dashboard.packed')"
        />
        <Stat :value="data.containers.by_status['open'] ?? 0" :label="$t('status.open')" />
      </div>

      <!-- By destination house -->
      <Panel v-if="data.by_destination_house.length > 0" :title="$t('dashboard.destinations')" class="section">
        <div class="dest-grid">
          <div
            v-for="stat in data.by_destination_house"
            :key="stat.house.id"
            class="dest-card"
          >
            <div class="dest-dot-row">
              <span class="dest-name">{{ stat.house.name }}</span>
              <span v-if="stat.house.is_disposal" class="disposal-badge">{{ $t('house.disposal') }}</span>
            </div>
            <div class="dest-meta">
              <span class="num">{{ stat.container_count }}</span> scatole
              <span v-if="stat.delivered > 0" class="dest-transferred">· {{ stat.delivered }} ✓</span>
            </div>
          </div>
        </div>
      </Panel>

      <!-- Status bars -->
      <Panel :title="$t('dashboard.status_breakdown')" class="section">
        <div class="status-bars">
          <div v-for="(count, status) in data.containers.by_status" :key="status" class="status-row">
            <StatusBadge :kind="status" size="sm" class="status-row-badge" />
            <div class="bar-track">
              <div
                class="bar-fill"
                :class="`bar-${status}`"
                :style="{ width: `${data.containers.total > 0 ? (count / data.containers.total) * 100 : 0}%` }"
              ></div>
            </div>
            <span class="num bar-count">{{ count }}</span>
          </div>
        </div>
      </Panel>

      <!-- Upcoming transfers -->
      <Panel
        v-if="data.upcoming_transfers.length > 0"
        :title="$t('dashboard.upcoming_transfers')"
        class="section"
      >
        <div class="transfer-list">
          <TransferCard
            v-for="t in data.upcoming_transfers"
            :key="t.id"
            :transfer="t"
            @click="router.push(`/houses/${houseId}/transfers/${t.id}`)"
          />
        </div>
      </Panel>

      <!-- Recent containers -->
      <Panel
        v-if="data.recent_containers.length > 0"
        :title="$t('dashboard.recent_containers')"
        class="section"
      >
        <template #action>
          <Btn kind="ghost" :to="`/houses/${houseId}/containers`" style="font-size:12px;padding:4px 10px">
            {{ $t('nav.boxes') }} →
          </Btn>
        </template>
        <div class="containers-grid">
          <ContainerCard
            v-for="c in data.recent_containers"
            :key="c.id"
            :container="c"
            @click="router.push(`/houses/${houseId}/containers/${c.id}`)"
          />
        </div>
      </Panel>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useDashboardStore, type DashboardResponse } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import Stat from '@/components/primitives/Stat.vue'
import Panel from '@/components/primitives/Panel.vue'
import Btn from '@/components/primitives/Btn.vue'
import StatusBadge from '@/components/primitives/StatusBadge.vue'
import TransferCard from '@/components/transfers/TransferCard.vue'
import ContainerCard from '@/components/containers/ContainerCard.vue'

const props = defineProps<{ houseId: string }>()
const router = useRouter()
const { t } = useI18n()
const dashboardStore = useDashboardStore()
const authStore = useAuthStore()

const data = ref<DashboardResponse | null>(null)
const loading = ref(false)

const greeting = computed(() => {
  const hour = new Date().getHours()
  const name = authStore.user?.username ?? ''
  return hour < 18
    ? t('dashboard.greeting_morning', { name })
    : t('dashboard.greeting_evening', { name })
})

onMounted(async () => {
  loading.value = true
  try { data.value = await dashboardStore.fetchDashboard(props.houseId) }
  finally { loading.value = false }
})
</script>

<style scoped>
.dashboard-view { display: flex; flex-direction: column; gap: var(--oco-s-6); max-width: 960px; }

.greeting { margin-bottom: var(--oco-s-2); }
.greeting-text {
  font-size: 28px;
  font-weight: 600;
  letter-spacing: -0.6px;
  color: var(--oco-ink);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--oco-s-3);
}
@media (max-width: 600px) { .stats-grid { grid-template-columns: repeat(2, 1fr); } }

.section { /* Panel has its own spacing */ }

.dest-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--oco-s-3);
}
.dest-card {
  display: flex;
  flex-direction: column;
  gap: var(--oco-s-2);
  padding: var(--oco-s-4);
  background: var(--oco-surface-2);
  border: 1px solid var(--oco-line);
  border-radius: var(--oco-r-md);
  text-decoration: none;
  color: var(--oco-ink);
  transition: border-color 0.12s, box-shadow 0.12s;
}
.dest-card:hover { border-color: var(--oco-primary); box-shadow: var(--oco-shadow-2); text-decoration: none; }
.dest-dot-row { display: flex; align-items: center; gap: var(--oco-s-2); }
.dest-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--oco-ink-4); flex-shrink: 0; }
.dest-name { font-size: 13px; font-weight: 600; }
.dest-meta { font-size: 12px; color: var(--oco-ink-3); }
.dest-transferred { color: var(--oco-ok); }

.status-bars { display: flex; flex-direction: column; gap: var(--oco-s-3); }
.status-row { display: grid; grid-template-columns: 100px 1fr 36px; align-items: center; gap: var(--oco-s-3); }
.status-row-badge { justify-self: end; }
.bar-track { height: 6px; background: var(--oco-surface-3); border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.4s ease; }
.bar-open       { background: var(--oco-ok); }
.bar-closed     { background: var(--oco-warn); }
.bar-sealed     { background: var(--oco-info); }
.bar-in_transit { background: var(--oco-info); }
.bar-delivered  { background: var(--oco-mute); }
.bar-count { font-size: 12px; font-weight: 600; color: var(--oco-ink-3); text-align: right; }

.transfer-list { display: flex; flex-direction: column; gap: var(--oco-s-2); }

.containers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--oco-s-3);
}

.loading-state { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--oco-s-3); }
.skeleton {
  height: 80px;
  background: var(--oco-surface-2);
  border-radius: var(--oco-r-lg);
  animation: pulse 1.4s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
</style>
