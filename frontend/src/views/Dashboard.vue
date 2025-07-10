<template>
  <div class="space-y-6">
    <!-- Welcome header -->
    <div class="border-b border-gray-700 pb-4">
      <h1 class="text-2xl font-bold text-white">Dashboard</h1>
      <p class="text-gray-400 mt-1">Welcome back, {{ authStore.user?.email }}</p>
    </div>

    <!-- Admin notification -->
    <div
      v-if="authStore.user?.role.toLowerCase() === 'admin'"
      class="bg-yellow-900 border border-yellow-700 p-4 rounded-lg"
    >
      <p class="text-yellow-200 font-medium">Admin Mode Active</p>
    </div>

    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-8 w-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-400 truncate">Total Requests</dt>
              <dd class="text-lg font-medium text-white">{{ totalRequests }}</dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-8 w-8 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-400 truncate">Pending</dt>
              <dd class="text-lg font-medium text-white">{{ pendingRequests }}</dd>
            </dl>
          </div>
        </div>
      </div>

      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <svg class="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div class="ml-5 w-0 flex-1">
            <dl>
              <dt class="text-sm font-medium text-gray-400 truncate">Approved</dt>
              <dd class="text-lg font-medium text-white">{{ approvedRequests }}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Quick Actions</h2>
      <div class="space-y-3">
        <router-link
          to="/browse"
          class="flex items-center p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <svg class="h-5 w-5 text-gray-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span class="text-gray-200">Browse & Search Media</span>
        </router-link>
        
        <router-link
          to="/my-requests"
          class="flex items-center p-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
        >
          <svg class="h-5 w-5 text-gray-400 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <span class="text-gray-200">View My Requests</span>
        </router-link>
      </div>
    </div>

    <!-- Recent requests -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Recent Requests</h2>
      <div v-if="requestsStore.loading" class="text-gray-400">Loading...</div>
      <div v-else-if="recentRequests.length === 0" class="text-gray-400">
        No recent requests
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="request in recentRequests"
          :key="request.id"
          class="border border-gray-600 rounded p-4 bg-gray-700"
        >
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="font-medium text-white">{{ request.title }}</h3>
              <p class="text-sm text-gray-300 mt-1">{{ request.description }}</p>
              <div class="flex items-center mt-2 space-x-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
                  {{ request.media_type }}
                </span>
                <span class="text-xs text-gray-400">
                  {{ formatDate(request.created_at) }}
                </span>
              </div>
            </div>
            <span
              :class="[
                'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                getStatusClasses(request.status)
              ]"
            >
              {{ request.status }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRequestsStore } from '../stores/requests'

export default {
  name: 'Dashboard',
  setup() {
    const authStore = useAuthStore()
    const requestsStore = useRequestsStore()

    const totalRequests = computed(() => requestsStore.requests.length)
    const pendingRequests = computed(() => 
      requestsStore.requests.filter(req => req.status === 'PENDING').length
    )
    const approvedRequests = computed(() => 
      requestsStore.requests.filter(req => req.status === 'APPROVED').length
    )

    const recentRequests = computed(() => 
      requestsStore.requests
        .slice()
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 5)
    )

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const getStatusClasses = (status) => {
      const classes = {
        'PENDING': 'bg-yellow-900 text-yellow-200',
        'APPROVED': 'bg-green-900 text-green-200',
        'FULFILLED': 'bg-blue-900 text-blue-200',
        'DENIED': 'bg-red-900 text-red-200'
      }
      return classes[status] || 'bg-gray-600 text-gray-200'
    }

    onMounted(async () => {
      if (authStore.isAuthenticated) {
        await requestsStore.fetchRequests()
      }
    })

    return {
      authStore,
      requestsStore,
      totalRequests,
      pendingRequests,
      approvedRequests,
      recentRequests,
      formatDate,
      getStatusClasses
    }
  }
}
</script>