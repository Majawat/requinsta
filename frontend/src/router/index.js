import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import Search from '../views/Search.vue'
import MyRequests from '../views/MyRequests.vue'
import Admin from '../views/Admin.vue'
import Profile from '../views/Profile.vue'

const routes = [
  {
    path: '/',
    name: 'Search',
    component: Search,
    meta: { requiresAuth: true }
  },
  {
    // Legacy deep links (Dashboard used to hand off to /browse?q=…&type=…).
    path: '/browse',
    redirect: (to) => ({ path: '/', query: to.query })
  },
  {
    path: '/my-requests',
    name: 'MyRequests',
    component: MyRequests,
    meta: { requiresAuth: true }
  },
  {
    // Day-to-day admin: the requests + issues queues (staff = admin or moderator).
    path: '/admin',
    name: 'Queue',
    component: Admin,
    meta: { requiresAuth: true, requiresStaff: true, section: 'queue' }
  },
  {
    // Configuration, split off from the daily queue — admins only.
    path: '/admin/setup',
    name: 'Setup',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true, section: 'setup' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Return-style guard (the old next(false) aborted the very first navigation, so
// after logging in nothing re-triggered it → a blank screen until you navigated
// or refreshed). The whole app is gated on auth in App.vue, so it's safe to let
// routes resolve while logged out — they just render under the login overlay.
router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.initAuth()
  }

  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return { path: '/' }
  }
  if (to.meta.requiresStaff && !authStore.isStaff) {
    return { path: '/' }
  }

  return true
})

export default router
