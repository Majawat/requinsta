<template>
  <!-- Desktop-only persistent sidebar. Mobile uses the bottom tab bar. -->
  <div class="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0 bg-slate-900 border-r border-slate-800">
    <!-- Brand -->
    <div class="flex items-center h-16 flex-shrink-0 px-5">
      <div class="h-8 w-8 rounded-lg bg-indigo-600 grid place-items-center">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round">
          <circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="21" y2="21" />
        </svg>
      </div>
      <h1 class="ml-3 text-lg font-bold tracking-tight text-white">Requinsta</h1>
    </div>

    <nav class="mt-4 px-3 space-y-1">
      <router-link
        v-for="item in navigation"
        :key="item.name"
        :to="item.href"
        :class="[
          'group relative flex items-center gap-3 px-3 py-2.5 text-sm font-semibold rounded-lg transition-colors',
          isActive(item) ? 'bg-indigo-500/10 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white',
        ]"
      >
        <span v-if="isActive(item)" class="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r bg-indigo-500"></span>
        <svg
          class="h-5 w-5 flex-shrink-0"
          viewBox="0 0 24 24" fill="none"
          :stroke="isActive(item) ? '#a5b4fc' : 'currentColor'"
          stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"
          v-html="item.svg"
        />
        <span class="flex-1">{{ item.name }}</span>
        <span
          v-if="item.badge"
          class="min-w-[18px] h-[18px] px-1 grid place-items-center rounded-full bg-amber-400 text-[10px] font-bold text-slate-900"
        >{{ item.badge }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useRequestsStore } from '../../stores/requests'

const ICON = {
  search: '<circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="21" y2="21" />',
  requests: '<line x1="9" y1="6" x2="20" y2="6" /><line x1="9" y1="12" x2="20" y2="12" /><line x1="9" y1="18" x2="20" y2="18" /><circle cx="4.5" cy="6" r="1.2" /><circle cx="4.5" cy="12" r="1.2" /><circle cx="4.5" cy="18" r="1.2" />',
  queue: '<path d="M4 13h4l1.5 2.5h5L16 13h4" /><path d="M4 13V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v7" />',
  setup: '<circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />',
  profile: '<circle cx="12" cy="8" r="3.6" /><path d="M5 20c0-3.6 3.1-5.5 7-5.5s7 1.9 7 5.5" />',
}

export default {
  name: 'Sidebar',
  setup() {
    const route = useRoute()
    const auth = useAuthStore()
    const requests = useRequestsStore()

    const queuePending = computed(
      () => (auth.isAdmin ? requests.requests.filter((r) => r.status === 'PENDING').length : 0)
    )

    const navigation = computed(() => {
      const nav = [
        { name: 'Search', href: '/', svg: ICON.search, exact: true },
        { name: 'My Requests', href: '/my-requests', svg: ICON.requests },
      ]
      if (auth.isAdmin) {
        // Queue = requests + issues (day-to-day); Setup = configuration.
        nav.push({ name: 'Queue', href: '/admin', svg: ICON.queue, badge: queuePending.value || null, exact: true })
        nav.push({ name: 'Setup', href: '/admin/setup', svg: ICON.setup })
      }
      nav.push({ name: 'Profile', href: '/profile', svg: ICON.profile })
      return nav
    })

    const isActive = (item) => (item.exact ? route.path === item.href : route.path.startsWith(item.href))

    return { navigation, isActive }
  },
}
</script>
