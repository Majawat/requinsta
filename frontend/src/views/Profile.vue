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

    <!-- Preferences -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Preferences</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Email Notifications
          </label>
          <div class="space-y-2">
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="preferences.emailOnApproval"
                class="rounded bg-gray-700 border-gray-600 text-blue-600"
              />
              <span class="ml-2 text-sm text-gray-300">Request approval notifications</span>
            </label>
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="preferences.emailOnFulfillment"
                class="rounded bg-gray-700 border-gray-600 text-blue-600"
              />
              <span class="ml-2 text-sm text-gray-300">Request fulfillment notifications</span>
            </label>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Default Media Type
          </label>
          <select
            v-model="preferences.defaultMediaType"
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
          >
            <option value="">No preference</option>
            <option value="book">Book</option>
            <option value="audiobook">Audiobook</option>
            <option value="movie">Movie</option>
            <option value="tv_show">TV Show</option>
            <option value="music">Music</option>
            <option value="comic">Comic</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div class="pt-4">
          <button
            @click="savePreferences"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
          >
            Save Preferences
          </button>
        </div>
      </div>
    </div>

    <!-- Security -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Security</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-2">
            Change Password
          </label>
          <div class="space-y-3">
            <input
              type="password"
              v-model="passwordForm.currentPassword"
              placeholder="Current password"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400"
            />
            <input
              type="password"
              v-model="passwordForm.newPassword"
              placeholder="New password"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400"
            />
            <input
              type="password"
              v-model="passwordForm.confirmPassword"
              placeholder="Confirm new password"
              class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400"
            />
            <button
              @click="changePassword"
              :disabled="!isPasswordFormValid"
              class="bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
            >
              Change Password
            </button>
          </div>
        </div>
      </div>
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
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRequestsStore } from '../stores/requests'

export default {
  name: 'Profile',
  setup() {
    const authStore = useAuthStore()
    const requestsStore = useRequestsStore()

    const preferences = reactive({
      emailOnApproval: true,
      emailOnFulfillment: true,
      defaultMediaType: ''
    })

    const passwordForm = reactive({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

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

    const isPasswordFormValid = computed(() => {
      return passwordForm.currentPassword && 
             passwordForm.newPassword && 
             passwordForm.confirmPassword &&
             passwordForm.newPassword === passwordForm.confirmPassword &&
             passwordForm.newPassword.length >= 8
    })

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const savePreferences = async () => {
      try {
        // In a real app, this would save to backend
        console.log('Saving preferences:', preferences)
        alert('Preferences saved successfully!')
      } catch (error) {
        console.error('Error saving preferences:', error)
        alert('Failed to save preferences. Please try again.')
      }
    }

    const changePassword = async () => {
      try {
        // In a real app, this would call the backend API
        console.log('Changing password...')
        alert('Password changed successfully!')
        
        // Clear form
        passwordForm.currentPassword = ''
        passwordForm.newPassword = ''
        passwordForm.confirmPassword = ''
      } catch (error) {
        console.error('Error changing password:', error)
        alert('Failed to change password. Please try again.')
      }
    }

    onMounted(async () => {
      await requestsStore.fetchRequests()
      
      // In a real app, load user preferences from backend
      // For now, use defaults
    })

    return {
      authStore,
      requestsStore,
      preferences,
      passwordForm,
      userRequests,
      pendingCount,
      approvedCount,
      fulfilledCount,
      isPasswordFormValid,
      formatDate,
      savePreferences,
      changePassword
    }
  }
}
</script>