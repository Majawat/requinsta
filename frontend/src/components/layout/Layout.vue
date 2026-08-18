<template>
  <div class="min-h-screen bg-slate-950 text-slate-100">
    <Sidebar />

    <div class="lg:pl-64 flex flex-col min-h-screen">
      <!-- Top bar -->
      <header class="sticky top-0 z-30 flex h-14 lg:h-16 flex-shrink-0 items-center gap-3 border-b border-slate-800 bg-slate-900/85 backdrop-blur px-4 lg:px-6">
        <!-- Mobile brand -->
        <div class="flex items-center gap-2 lg:hidden">
          <div class="h-[22px] w-[22px] rounded-md bg-indigo-600 grid place-items-center">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="21" y2="21" /></svg>
          </div>
          <span class="text-[15px] font-bold tracking-tight">Requinsta</span>
        </div>

        <div class="flex-1"></div>

        <span class="hidden sm:block text-sm text-slate-400">{{ authStore.user?.email }}</span>
        <div class="h-8 w-8 rounded-full bg-slate-800 border border-slate-700 grid place-items-center text-[11px] font-bold text-slate-300">
          {{ initials }}
        </div>
        <button @click="authStore.logout" class="hidden lg:inline text-slate-400 hover:text-white" title="Sign out">
          <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" /></svg>
        </button>
      </header>

      <!-- Page content: 16px mobile gutter, wider on desktop; bottom padding clears the tab bar -->
      <main class="flex-1 px-4 sm:px-6 lg:px-8 py-5 pb-24 lg:pb-8">
        <div class="max-w-3xl mx-auto">
          <router-view />
        </div>
      </main>
    </div>

    <BottomNav />
    <RequestDetailSheet />
    <ToastHost />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import Sidebar from './Sidebar.vue'
import BottomNav from './BottomNav.vue'
import RequestDetailSheet from '../RequestDetailSheet.vue'
import ToastHost from '../ui/ToastHost.vue'

export default {
  name: 'Layout',
  components: { Sidebar, BottomNav, RequestDetailSheet, ToastHost },
  setup() {
    const authStore = useAuthStore()
    const initials = computed(() => (authStore.user?.email || '?').slice(0, 1).toUpperCase())
    return { authStore, initials }
  },
}
</script>
