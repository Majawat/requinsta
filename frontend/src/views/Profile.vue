<template>
  <div class="space-y-5">
    <h1 class="text-[22px] font-bold tracking-tight">Account</h1>

    <!-- Profile -->
    <section class="card p-5">
      <h2 class="text-base font-semibold mb-4">Profile</h2>
      <div class="space-y-4">
        <div>
          <label class="label">Email</label>
          <div class="flex gap-2">
            <input v-model="email" type="email" class="input flex-1" />
            <button @click="saveEmail" :disabled="savingEmail || email === me.email" class="btn-primary flex-none">
              {{ savingEmail ? 'Saving…' : 'Save' }}
            </button>
          </div>
        </div>
        <div>
          <label class="label">Role</label>
          <input type="text" :value="me.role" disabled class="input text-slate-400 cursor-not-allowed" />
          <p class="text-xs text-slate-500 mt-1">Role is assigned by administrators</p>
        </div>
      </div>
    </section>

    <!-- Notification preferences -->
    <section class="card p-5">
      <h2 class="text-base font-semibold mb-3">Notifications</h2>
      <label class="inline-flex items-center gap-2 text-sm text-slate-300">
        <input type="checkbox" v-model="notifyOnAvailable" @change="saveNotify" class="accent-indigo-600 w-4 h-4" />
        Email me when a request becomes available
      </label>
    </section>

    <!-- Change password -->
    <section class="card p-5">
      <h2 class="text-base font-semibold mb-4">Change password</h2>
      <div class="space-y-3 max-w-md">
        <input v-model="pw.current" type="password" placeholder="Current password" class="input" />
        <input v-model="pw.next" type="password" placeholder="New password (min 8 chars)" class="input" />
        <input v-model="pw.confirm" type="password" placeholder="Confirm new password" class="input" />
        <div class="flex justify-end">
          <button @click="changePassword" :disabled="changingPw" class="btn-primary">
            {{ changingPw ? 'Updating…' : 'Update password' }}
          </button>
        </div>
      </div>
    </section>

    <!-- Request stats -->
    <section class="card p-5">
      <h2 class="text-base font-semibold mb-4">Your requests</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="text-center"><div class="text-2xl font-bold text-slate-100">{{ userRequests.length }}</div><div class="text-xs text-slate-400 mt-0.5">Total</div></div>
        <div class="text-center"><div class="text-2xl font-bold text-amber-300">{{ count('PENDING') }}</div><div class="text-xs text-slate-400 mt-0.5">Pending</div></div>
        <div class="text-center"><div class="text-2xl font-bold text-sky-300">{{ count('APPROVED') }}</div><div class="text-xs text-slate-400 mt-0.5">Approved</div></div>
        <div class="text-center"><div class="text-2xl font-bold text-emerald-300">{{ count('FULFILLED') }}</div><div class="text-xs text-slate-400 mt-0.5">Available</div></div>
      </div>
    </section>

    <button @click="authStore.logout" class="btn-secondary w-full">Sign out</button>

    <div v-if="message" class="p-4 rounded-lg text-sm" :class="messageOk ? 'bg-emerald-500/10 text-emerald-200 border border-emerald-400/30' : 'bg-rose-500/10 text-rose-200 border border-rose-400/30'">{{ message }}</div>
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
