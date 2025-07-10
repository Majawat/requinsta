<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="border-b border-gray-700 pb-4">
      <h1 class="text-2xl font-bold text-white">Admin Panel</h1>
      <p class="text-gray-400 mt-1">Manage requests and users</p>
    </div>

    <!-- Admin tabs -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg">
      <div class="flex border-b border-gray-700">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'px-4 py-3 text-sm font-medium transition-colors',
            activeTab === tab.key
              ? 'border-b-2 border-blue-500 text-blue-400'
              : 'text-gray-400 hover:text-gray-200'
          ]"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- Request Management Tab -->
    <div v-if="activeTab === 'requests'" class="space-y-4">
      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
        <h2 class="text-lg font-medium text-white mb-4">Request Management</h2>
        <AdminPanel :requests="requestsStore.requests" />
      </div>
    </div>

    <!-- User Management Tab -->
    <div v-if="activeTab === 'users'" class="space-y-4">
      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
        <h2 class="text-lg font-medium text-white mb-4">User Management</h2>
        <UserManagement />
      </div>
    </div>

    <!-- Settings Tab -->
    <div v-if="activeTab === 'settings'" class="space-y-4">
      <AdminSettings />
    </div>

    <!-- Statistics Tab -->
    <div v-if="activeTab === 'stats'" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-8 w-8 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            <div class="ml-5">
              <p class="text-sm font-medium text-gray-400">Total Users</p>
              <p class="text-2xl font-semibold text-white">{{ totalUsers }}</p>
            </div>
          </div>
        </div>

        <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-8 w-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div class="ml-5">
              <p class="text-sm font-medium text-gray-400">Total Requests</p>
              <p class="text-2xl font-semibold text-white">{{ requestsStore.requests.length }}</p>
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
            <div class="ml-5">
              <p class="text-sm font-medium text-gray-400">Pending</p>
              <p class="text-2xl font-semibold text-white">{{ pendingRequests }}</p>
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
            <div class="ml-5">
              <p class="text-sm font-medium text-gray-400">Fulfilled</p>
              <p class="text-2xl font-semibold text-white">{{ fulfilledRequests }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
        <h2 class="text-lg font-medium text-white mb-4">Recent Activity</h2>
        <div class="space-y-3">
          <div v-for="request in recentRequests" :key="request.id" class="flex items-center justify-between p-3 bg-gray-700 rounded">
            <div>
              <p class="text-white font-medium">{{ request.title }}</p>
              <p class="text-sm text-gray-400">{{ request.description }}</p>
            </div>
            <div class="text-right">
              <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', getStatusClasses(request.status)]">
                {{ request.status }}
              </span>
              <p class="text-xs text-gray-400 mt-1">{{ formatDate(request.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRequestsStore } from '../stores/requests'
import AdminPanel from '../components/AdminPanel.vue'
import UserManagement from '../components/UserManagement.vue'
import AdminSettings from '../components/AdminSettings.vue'

export default {
  name: 'Admin',
  components: {
    AdminPanel,
    UserManagement,
    AdminSettings
  },
  setup() {
    const requestsStore = useRequestsStore()
    const activeTab = ref('requests')
    const totalUsers = ref(0) // This would come from a users store

    const tabs = [
      { key: 'requests', label: 'Requests' },
      { key: 'users', label: 'Users' },
      { key: 'settings', label: 'Settings' },
      { key: 'stats', label: 'Statistics' }
    ]

    const pendingRequests = computed(() => 
      requestsStore.requests.filter(req => req.status === 'PENDING').length
    )

    const fulfilledRequests = computed(() => 
      requestsStore.requests.filter(req => req.status === 'FULFILLED').length
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
      await requestsStore.fetchRequests()
      // In a real app, also fetch user count
      totalUsers.value = 42 // Mock data
    })

    return {
      requestsStore,
      activeTab,
      tabs,
      totalUsers,
      pendingRequests,
      fulfilledRequests,
      recentRequests,
      formatDate,
      getStatusClasses
    }
  }
}
</script>