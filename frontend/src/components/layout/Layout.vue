<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Mobile menu backdrop -->
    <div 
      v-if="sidebarOpen" 
      class="fixed inset-0 z-40 lg:hidden"
      @click="sidebarOpen = false"
    >
      <div class="fixed inset-0 bg-gray-600 bg-opacity-75"></div>
    </div>

    <!-- Sidebar -->
    <Sidebar 
      :open="sidebarOpen" 
      @close="sidebarOpen = false" 
    />

    <!-- Main content area -->
    <div class="lg:pl-64 flex flex-col flex-1">
      <!-- Top navigation -->
      <div class="sticky top-0 z-10 flex-shrink-0 flex h-16 bg-gray-900/80 backdrop-blur border-b border-gray-800">
        <button
          @click="sidebarOpen = true"
          class="px-4 text-gray-400 hover:text-white focus:outline-none lg:hidden"
        >
          <span class="sr-only">Open sidebar</span>
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
          </svg>
        </button>
        <div class="flex-1 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <h1 class="text-lg font-semibold text-white lg:hidden">Requinsta</h1>
          <div class="flex-1"></div>
          <div class="flex items-center gap-3">
            <span class="hidden sm:block text-sm text-gray-400">{{ authStore.user?.email }}</span>
            <div class="h-8 w-8 rounded-full bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-white text-sm font-semibold">
              {{ (authStore.user?.email || '?')[0].toUpperCase() }}
            </div>
            <button @click="authStore.logout" class="text-sm text-gray-400 hover:text-white transition-colors" title="Sign out">
              <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15M12 9l-3 3m0 0l3 3m-3-3h12.75" /></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Page content -->
      <main class="flex-1">
        <div class="py-6">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <router-view />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import Sidebar from './Sidebar.vue'

export default {
  name: 'Layout',
  components: {
    Sidebar
  },
  setup() {
    const authStore = useAuthStore()
    const sidebarOpen = ref(false)

    return {
      authStore,
      sidebarOpen
    }
  }
}
</script>