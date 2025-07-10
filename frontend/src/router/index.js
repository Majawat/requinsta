import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Views
import Dashboard from '../views/Dashboard.vue'
import Browse from '../views/Browse.vue'
import MyRequests from '../views/MyRequests.vue'
import Admin from '../views/Admin.vue'
import Profile from '../views/Profile.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/browse',
    name: 'Browse',
    component: Browse,
    meta: { requiresAuth: true }
  },
  {
    path: '/my-requests',
    name: 'MyRequests',
    component: MyRequests,
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: Admin,
    meta: { requiresAuth: true, requiresAdmin: true }
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

// Navigation guard for authentication
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Initialize auth if not done yet
  if (!authStore.initialized) {
    await authStore.initAuth()
  }
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/')
    return
  }
  
  // Check if route requires admin access
  if (to.meta.requiresAdmin && authStore.user?.role.toLowerCase() !== 'admin') {
    next('/')
    return
  }
  
  next()
})

export default router