<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="border-b border-gray-700 pb-4">
      <h1 class="text-2xl font-bold text-white">Profile & Settings</h1>
      <p class="text-gray-400 mt-1">Manage your account and preferences</p>
    </div>

    <!-- Profile Information -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Profile Information</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Email</label>
          <input
            type="email"
            :value="authStore.user?.email"
            disabled
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-400 cursor-not-allowed"
          />
          <p class="text-xs text-gray-500 mt-1">Email cannot be changed</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Role</label>
          <input
            type="text"
            :value="authStore.user?.role"
            disabled
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-400 cursor-not-allowed"
          />
          <p class="text-xs text-gray-500 mt-1">Role is assigned by administrators</p>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">Member Since</label>
          <input
            type="text"
            :value="formatDate(authStore.user?.created_at)"
            disabled
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-400 cursor-not-allowed"
          />
        </div>
      </div>
    </div>

    <!-- Request Statistics -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Your Request Statistics</h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="text-center">
          <div class="text-2xl font-bold text-white">{{ userRequests.length }}</div>
          <div class="text-sm text-gray-400">Total Requests</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-yellow-400">{{ pendingCount }}</div>
          <div class="text-sm text-gray-400">Pending</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-green-400">{{ approvedCount }}</div>
          <div class="text-sm text-gray-400">Approved</div>
        </div>
        <div class="text-center">
          <div class="text-2xl font-bold text-blue-400">{{ fulfilledCount }}</div>
          <div class="text-sm text-gray-400">Fulfilled</div>
        </div>
      </div>
    </div>

    <!-- Security -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Security</h2>
      <p class="text-gray-400 text-sm">Password change and additional security features are coming soon.</p>
    </div>

    <!-- Account Actions -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Account Actions</h2>
      <div class="space-y-4">
        <button
          @click="authStore.logout"
          class="w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md transition-colors"
        >
          Sign Out
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRequestsStore } from '../stores/requests'
import { formatDate } from '../utils/requestUtils'

export default {
  name: 'Profile',
  setup() {
    const authStore = useAuthStore()
    const requestsStore = useRequestsStore()

    const userRequests = computed(() =>
      requestsStore.requests.filter(req => req.user_id === authStore.user?.id)
    )

    const pendingCount = computed(() =>
      userRequests.value.filter(req => req.status === 'PENDING').length
    )

    const approvedCount = computed(() =>
      userRequests.value.filter(req => req.status === 'APPROVED').length
    )

    const fulfilledCount = computed(() =>
      userRequests.value.filter(req => req.status === 'FULFILLED').length
    )

    onMounted(async () => {
      await requestsStore.fetchRequests()
    })

    return {
      authStore,
      userRequests,
      pendingCount,
      approvedCount,
      fulfilledCount,
      formatDate,
    }
  }
}
</script>
