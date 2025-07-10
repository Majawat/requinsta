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
      <div class="sticky top-0 z-10 flex-shrink-0 flex h-16 bg-gray-800 shadow-sm border-b border-gray-700">
        <button
          @click="sidebarOpen = true"
          class="px-4 border-r border-gray-700 text-gray-400 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 lg:hidden"
        >
          <span class="sr-only">Open sidebar</span>
          <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <div class="flex-1 px-4 flex justify-between">
          <div class="flex-1 flex items-center">
            <h1 class="text-xl font-semibold text-white lg:hidden">Requinsta</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-sm text-gray-300">{{ authStore.user?.email }}</span>
            <button 
              @click="authStore.logout" 
              class="text-sm text-gray-400 hover:text-gray-200 transition-colors"
            >
              Logout
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