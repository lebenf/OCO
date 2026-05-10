// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright 2026 Lorenzo Benfenati
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView, meta: { public: true } },
    { path: '/', component: () => import('@/views/HomeView.vue') },
    {
      path: '/houses/:houseId',
      component: () => import('@/views/DashboardView.vue'),
      props: true,
    },
    {
      path: '/account',
      component: () => import('@/views/AccountView.vue'),
    },
    {
      path: '/admin/users',
      component: () => import('@/views/admin/UsersView.vue'),
      meta: { adminOnly: true },
    },
    {
      path: '/admin/users/:userId',
      component: () => import('@/views/admin/UserDetailView.vue'),
      props: true,
      meta: { adminOnly: true },
    },
    {
      path: '/admin/houses',
      component: () => import('@/views/admin/HousesView.vue'),
      meta: { adminOnly: true },
    },
    {
      path: '/admin/houses/:id',
      component: () => import('@/views/admin/HouseDetailView.vue'),
      meta: { adminOnly: true },
    },
    {
      path: '/houses/:houseId/containers',
      component: () => import('@/views/containers/ContainerListView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/containers/create',
      component: () => import('@/views/containers/ContainerCreateView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/containers/:containerId/edit',
      component: () => import('@/views/containers/ContainerEditView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/containers/:containerId',
      component: () => import('@/views/containers/ContainerDetailView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/containers/:containerId/capture',
      component: () => import('@/views/items/ItemCaptureView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/inbox',
      component: () => import('@/views/items/InboxView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/items/search',
      component: () => import('@/views/items/ItemSearchView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/items/:itemId/edit',
      component: () => import('@/views/items/ItemEditView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/items/:itemId',
      component: () => import('@/views/items/ItemDetailView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/transfers',
      component: () => import('@/views/transfers/TransferListView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/transfers/create',
      component: () => import('@/views/transfers/TransferCreateView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/transfers/plan',
      component: () => import('@/views/transfers/TransferPlanView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/transfers/:transferId',
      component: () => import('@/views/transfers/TransferDetailView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/locations/:locationId/summary',
      component: () => import('@/views/transfers/DestinationSummaryView.vue'),
      props: true,
    },
    {
      path: '/houses/:houseId/search',
      component: () => import('@/views/SearchView.vue'),
      props: true,
    },
    {
      path: '/admin/ai-config',
      component: () => import('@/views/admin/AIConfigView.vue'),
      meta: { adminOnly: true },
    },
    {
      path: '/print/:houseId/container/:code',
      component: () => import('@/views/print/ContainerPrintView.vue'),
      props: true,
      meta: { public: false, noShell: true },
    },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.public) return true

  const auth = useAuthStore()
  if (!auth.user) {
    try {
      await auth.fetchMe()
    } catch {
      return { path: '/login', query: { redirect: to.fullPath } }
    }
  }

  if (to.meta.adminOnly && !auth.user?.is_system_admin) {
    return { path: '/' }
  }

  return true
})

export default router
