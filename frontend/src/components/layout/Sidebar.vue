<template>
  <div class="lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
    <div
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 border-r border-gray-800 transition-transform transform lg:translate-x-0',
        open ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <!-- Brand -->
      <div class="flex items-center h-16 flex-shrink-0 px-5">
        <div class="h-9 w-9 rounded-lg bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center shadow-lg shadow-indigo-900/40">
          <span class="text-white font-bold text-lg">R</span>
        </div>
        <h1 class="ml-3 text-lg font-semibold tracking-tight text-white">Requinsta</h1>
      </div>

      <nav class="mt-4 px-3 space-y-1">
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.href"
          @click="$emit('close')"
          :class="[
            'group relative flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-colors',
            isActive(item)
              ? 'bg-indigo-500/10 text-white'
              : 'text-gray-400 hover:bg-gray-800 hover:text-white'
          ]"
        >
          <span v-if="isActive(item)" class="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r bg-indigo-500"></span>
          <svg class="h-5 w-5 flex-shrink-0" :class="isActive(item) ? 'text-indigo-400' : 'text-gray-500 group-hover:text-gray-300'"
               fill="none" viewBox="0 0 24 24" stroke-width="1.7" stroke="currentColor">
            <path v-for="(d, i) in item.paths" :key="i" stroke-linecap="round" stroke-linejoin="round" :d="d" />
          </svg>
          {{ item.name }}
        </router-link>
      </nav>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const ICONS = {
  dashboard: ['M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75'],
  browse: ['M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z'],
  requests: ['M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25z'],
  admin: [
    'M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.004.827c-.292.24-.437.613-.43.992a6.759 6.759 0 010 .255c-.007.378.138.75.43.99l1.005.828c.424.35.534.955.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.57 6.57 0 01-.22.128c-.331.183-.581.495-.644.869l-.213 1.281c-.09.542-.56.94-1.11.94h-2.594c-.55 0-1.02-.398-1.11-.94l-.213-1.281c-.062-.374-.312-.686-.644-.87a6.52 6.52 0 01-.22-.127c-.325-.196-.72-.257-1.076-.124l-1.217.456a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.26-1.431l1.004-.827c.292-.24.437-.613.43-.992a6.932 6.932 0 010-.255c.007-.378-.138-.75-.43-.99l-1.004-.828a1.125 1.125 0 01-.26-1.43l1.297-2.247a1.125 1.125 0 011.37-.491l1.216.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z',
    'M15 12a3 3 0 11-6 0 3 3 0 016 0z',
  ],
  profile: ['M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z'],
}

export default {
  name: 'Sidebar',
  props: { open: { type: Boolean, default: false } },
  emits: ['close'],
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()

    const navigation = computed(() => {
      const nav = [
        { name: 'Dashboard', href: '/', paths: ICONS.dashboard },
        { name: 'Browse', href: '/browse', paths: ICONS.browse },
        { name: 'My Requests', href: '/my-requests', paths: ICONS.requests },
      ]
      if (authStore.isAdmin) nav.push({ name: 'Admin', href: '/admin', paths: ICONS.admin })
      nav.push({ name: 'Profile', href: '/profile', paths: ICONS.profile })
      return nav
    })

    const isActive = (item) => route.path === item.href

    return { navigation, isActive }
  }
}
</script>
