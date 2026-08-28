<template>
  <nav
    class="lg:hidden fixed inset-x-0 bottom-0 z-40 bg-slate-900 border-t border-slate-800 pb-[env(safe-area-inset-bottom)]"
  >
    <div class="grid" :style="{ gridTemplateColumns: `repeat(${tabs.length}, minmax(0, 1fr))` }">
      <router-link
        v-for="tab in tabs"
        :key="tab.name"
        :to="tab.href"
        class="relative flex flex-col items-center gap-1 pt-2.5 pb-2"
      >
        <span class="relative">
          <svg
            width="22" height="22" viewBox="0 0 24 24" fill="none"
            :stroke="isActive(tab) ? '#a5b4fc' : '#64748b'"
            stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"
            v-html="tab.svg"
          />
          <span
            v-if="tab.badge"
            class="absolute -top-1.5 left-[calc(50%+6px)] min-w-[16px] h-4 px-1 grid place-items-center rounded-full bg-amber-400 text-[10px] font-bold text-slate-900"
          >{{ tab.badge }}</span>
        </span>
        <span class="text-[11px] font-semibold" :class="isActive(tab) ? 'text-indigo-300' : 'text-slate-500'">{{ tab.name }}</span>
      </router-link>
    </div>
  </nav>
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
  profile: '<circle cx="12" cy="8" r="3.6" /><path d="M5 20c0-3.6 3.1-5.5 7-5.5s7 1.9 7 5.5" />',
}

export default {
  name: 'BottomNav',
  setup() {
    const route = useRoute()
    const auth = useAuthStore()
    const requests = useRequestsStore()

    const myPending = computed(
      () => requests.requests.filter((r) => r.user_id === auth.user?.id && r.status === 'PENDING').length
    )
    const queuePending = computed(
      () => (auth.isStaff ? requests.requests.filter((r) => r.status === 'PENDING').length : 0)
    )

    const tabs = computed(() => {
      const list = [
        { name: 'Search', href: '/', svg: ICON.search },
        { name: 'Requests', href: '/my-requests', svg: ICON.requests, badge: myPending.value || null },
      ]
      if (auth.isStaff) list.push({ name: 'Queue', href: '/admin', svg: ICON.queue, badge: queuePending.value || null })
      list.push({ name: 'Profile', href: '/profile', svg: ICON.profile })
      return list
    })

    const isActive = (tab) => (tab.href === '/' ? route.path === '/' : route.path.startsWith(tab.href))

    return { tabs, isActive }
  },
}
</script>
