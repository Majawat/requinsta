<template>
  <div class="lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
    <!-- Sidebar component for mobile -->
    <div
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-gray-800 transition-transform transform lg:translate-x-0',
        open ? 'translate-x-0' : '-translate-x-full'
      ]"
    >
      <div class="flex items-center h-16 flex-shrink-0 px-4 bg-gray-900">
        <div class="h-8 w-8 bg-blue-600 rounded-md flex items-center justify-center">
          <span class="text-white font-bold text-lg">R</span>
        </div>
        <h1 class="ml-3 text-xl font-semibold text-white">Requinsta</h1>
      </div>
      
      <div class="mt-5 flex-1 flex flex-col">
        <nav class="flex-1 px-2 pb-4 space-y-1">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            :class="[
              $route.name === item.name
                ? 'bg-gray-900 text-white'
                : 'text-gray-300 hover:bg-gray-700 hover:text-white',
              'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors'
            ]"
            @click="$emit('close')"
          >
            <component 
              :is="item.icon" 
              :class="[
                $route.name === item.name ? 'text-gray-300' : 'text-gray-400 group-hover:text-gray-300',
                'mr-3 flex-shrink-0 h-6 w-6'
              ]"
            />
            {{ item.name }}
          </router-link>
        </nav>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

// Icons as inline SVG components
const DashboardIcon = {
  template: `
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v10a2 2 0 01-2 2H10a2 2 0 01-2-2V5z" />
    </svg>
  `
}

const BrowseIcon = {
  template: `
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  `
}

const RequestsIcon = {
  template: `
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
    </svg>
  `
}

const AdminIcon = {
  template: `
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  `
}

const ProfileIcon = {
  template: `
    <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
    </svg>
  `
}

export default {
  name: 'Sidebar',
  components: {
    DashboardIcon,
    BrowseIcon,
    RequestsIcon,
    AdminIcon,
    ProfileIcon
  },
  props: {
    open: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup() {
    const authStore = useAuthStore()

    const navigation = computed(() => {
      const baseNavigation = [
        { name: 'Dashboard', href: '/', icon: 'DashboardIcon' },
        { name: 'Browse', href: '/browse', icon: 'BrowseIcon' },
        { name: 'My Requests', href: '/my-requests', icon: 'RequestsIcon' },
      ]

      // Add admin navigation if user is admin
      if (authStore.user?.role.toLowerCase() === 'admin') {
        baseNavigation.push(
          { name: 'Admin', href: '/admin', icon: 'AdminIcon' }
        )
      }

      baseNavigation.push(
        { name: 'Profile', href: '/profile', icon: 'ProfileIcon' }
      )

      return baseNavigation
    })

    return {
      navigation
    }
  }
}
</script>