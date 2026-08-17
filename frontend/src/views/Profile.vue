<template>
  <div class="space-y-6">
    <div class="border-b border-gray-700 pb-4">
      <h1 class="text-2xl font-bold text-white">Account</h1>
      <p class="text-gray-400 mt-1">Manage your account and preferences</p>
    </div>

    <!-- Profile -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Profile</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Email</label>
          <div class="flex gap-2">
            <input v-model="email" type="email"
              class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white" />
            <button @click="saveEmail" :disabled="savingEmail || email === me.email"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-md">
              {{ savingEmail ? 'Saving…' : 'Save' }}
            </button>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300 mb-1">Role</label>
          <input type="text" :value="me.role" disabled
            class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-gray-400 cursor-not-allowed" />
          <p class="text-xs text-gray-500 mt-1">Role is assigned by administrators</p>
        </div>
      </div>
    </div>

    <!-- Notification preferences -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Notifications</h2>
      <label class="inline-flex items-center text-sm text-gray-300">
        <input type="checkbox" v-model="notifyOnAvailable" @change="saveNotify" class="mr-2" />
        Email me when a request becomes available
      </label>
    </div>

    <!-- Change password -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Change Password</h2>
      <div class="space-y-3 max-w-md">
        <input v-model="pw.current" type="password" placeholder="Current password"
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        <input v-model="pw.next" type="password" placeholder="New password (min 8 chars)"
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        <input v-model="pw.confirm" type="password" placeholder="Confirm new password"
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        <div class="flex justify-end">
          <button @click="changePassword" :disabled="changingPw"
            class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-md">
            {{ changingPw ? 'Updating…' : 'Update Password' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Request stats -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Your Requests</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center"><div class="text-2xl font-bold text-white">{{ userRequests.length }}</div><div class="text-sm text-gray-400">Total</div></div>
        <div class="text-center"><div class="text-2xl font-bold text-yellow-400">{{ count('PENDING') }}</div><div class="text-sm text-gray-400">Pending</div></div>
        <div class="text-center"><div class="text-2xl font-bold text-green-400">{{ count('APPROVED') }}</div><div class="text-sm text-gray-400">Approved</div></div>
        <div class="text-center"><div class="text-2xl font-bold text-blue-400">{{ count('FULFILLED') }}</div><div class="text-sm text-gray-400">Fulfilled</div></div>
      </div>
    </div>

    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <button @click="authStore.logout" class="w-full bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md">Sign Out</button>
    </div>

    <div v-if="message" class="p-4 rounded-lg" :class="messageOk ? 'bg-green-900 text-green-100' : 'bg-red-900 text-red-100'">{{ message }}</div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useRequestsStore } from '../stores/requests'
import { API_URL } from '../utils/api'

export default {
  name: 'Profile',
  setup() {
    const authStore = useAuthStore()
    const requestsStore = useRequestsStore()

    const me = ref({ email: '', role: '', notify_on_available: true })
    const email = ref('')
    const notifyOnAvailable = ref(true)
    const pw = reactive({ current: '', next: '', confirm: '' })
    const savingEmail = ref(false)
    const changingPw = ref(false)
    const message = ref('')
    const messageOk = ref(true)

    const flash = (t, ok = true) => { message.value = t; messageOk.value = ok; setTimeout(() => message.value = '', 3000) }

    const userRequests = computed(() => requestsStore.requests.filter(r => r.user_id === authStore.user?.id))
    const count = (s) => userRequests.value.filter(r => r.status === s).length

    const loadMe = async () => {
      const { data } = await axios.get(`${API_URL}/users/me`)
      me.value = data
      email.value = data.email
      notifyOnAvailable.value = data.notify_on_available
    }

    const saveEmail = async () => {
      savingEmail.value = true
      try {
        await axios.patch(`${API_URL}/users/me`, { email: email.value })
        await loadMe(); await authStore.fetchUser()
        flash('Email updated')
      } catch (e) { flash(e.response?.data?.detail || 'Failed to update email', false) }
      finally { savingEmail.value = false }
    }

    const saveNotify = async () => {
      try {
        await axios.patch(`${API_URL}/users/me`, { notify_on_available: notifyOnAvailable.value })
        flash('Preferences saved')
      } catch (e) {
        notifyOnAvailable.value = !notifyOnAvailable.value  // revert on failure
        flash('Failed to save preference', false)
      }
    }

    const changePassword = async () => {
      if (pw.next !== pw.confirm) return flash('New passwords do not match', false)
      changingPw.value = true
      try {
        await axios.post(`${API_URL}/users/me/password`, { current_password: pw.current, new_password: pw.next })
        pw.current = pw.next = pw.confirm = ''
        flash('Password updated')
      } catch (e) { flash(e.response?.data?.detail || 'Failed to change password', false) }
      finally { changingPw.value = false }
    }

    onMounted(async () => {
      await Promise.all([loadMe(), requestsStore.fetchRequests()])
    })

    return { authStore, me, email, notifyOnAvailable, pw, savingEmail, changingPw, message, messageOk,
      userRequests, count, saveEmail, saveNotify, changePassword }
  }
}
</script>
