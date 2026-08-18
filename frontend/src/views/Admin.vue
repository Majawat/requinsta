<template>
  <div class="space-y-5">
    <!-- Header: Queue (day-to-day) vs Setup (configuration) -->
    <div class="flex items-center justify-between">
      <h1 class="text-[22px] font-bold tracking-tight">{{ isSetup ? 'Setup' : 'Queue' }}</h1>
      <router-link
        :to="isSetup ? '/admin' : '/admin/setup'"
        class="btn-secondary btn-sm"
      >
        <svg v-if="!isSetup" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" /></svg>
        <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 5 8 12 15 19" /></svg>
        {{ isSetup ? 'Back to queue' : 'Setup' }}
      </router-link>
    </div>

    <!-- Tabs (scoped to the active section) -->
    <div class="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1 scrollbar-none">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="flex-none"
        :class="activeTab === tab.key ? 'chip-active' : 'chip-idle'"
      >
        {{ tab.label }}
        <span v-if="tab.badge" class="min-w-[16px] h-4 px-1 grid place-items-center rounded-full bg-amber-400 text-[10px] font-bold text-slate-900">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- Requests queue -->
    <div v-if="activeTab === 'requests'">
      <AdminPanel :requests="requestsStore.requests" />
    </div>

    <!-- Issues queue -->
    <div v-else-if="activeTab === 'issues'">
      <AdminIssues />
    </div>

    <!-- Users -->
    <div v-else-if="activeTab === 'users'">
      <UserManagement />
    </div>

    <!-- Media managers -->
    <div v-else-if="activeTab === 'managers'">
      <MediaManagers />
    </div>

    <!-- Plugins -->
    <div v-else-if="activeTab === 'plugins'">
      <Plugins />
    </div>

    <!-- Settings -->
    <div v-else-if="activeTab === 'settings'">
      <AdminSettings />
    </div>

    <!-- Statistics -->
    <div v-else-if="activeTab === 'stats'" class="space-y-4">
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div class="card p-4"><div class="text-2xl font-bold">{{ totalUsers }}</div><div class="text-xs text-slate-400 mt-0.5">Total users</div></div>
        <div class="card p-4"><div class="text-2xl font-bold">{{ requestsStore.requests.length }}</div><div class="text-xs text-slate-400 mt-0.5">Total requests</div></div>
        <div class="card p-4"><div class="text-2xl font-bold text-amber-300">{{ pendingRequests }}</div><div class="text-xs text-slate-400 mt-0.5">Pending</div></div>
        <div class="card p-4"><div class="text-2xl font-bold text-emerald-300">{{ fulfilledRequests }}</div><div class="text-xs text-slate-400 mt-0.5">Fulfilled</div></div>
      </div>

      <div class="card p-5">
        <h2 class="text-base font-semibold mb-3">Recent activity</h2>
        <div class="divide-y divide-slate-800">
          <div v-for="request in requestsStore.recentRequests" :key="request.id" class="flex items-center justify-between gap-3 py-2.5">
            <div class="min-w-0">
              <p class="font-semibold text-slate-100 truncate">{{ request.title }}</p>
              <p class="text-sm text-slate-500 line-clamp-1">{{ request.description }}</p>
            </div>
            <div class="text-right flex-none">
              <StatusPill :status="request.status" small />
              <p class="text-xs text-slate-500 mt-1">{{ formatDate(request.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { useRequestsStore } from '../stores/requests'
import { formatDate } from '../utils/requestUtils'
import { API_URL } from '../utils/api'
import AdminPanel from '../components/AdminPanel.vue'
import UserManagement from '../components/UserManagement.vue'
import AdminSettings from '../components/AdminSettings.vue'
import MediaManagers from '../components/MediaManagers.vue'
import Plugins from '../components/Plugins.vue'
import AdminIssues from '../components/AdminIssues.vue'
import StatusPill from '../components/ui/StatusPill.vue'

export default {
  name: 'Admin',
  components: { AdminPanel, UserManagement, AdminSettings, MediaManagers, Plugins, AdminIssues, StatusPill },
  setup() {
    const route = useRoute()
    const requestsStore = useRequestsStore()
    const totalUsers = ref(0)

    const isSetup = computed(() => route.meta.section === 'setup')

    const pendingRequests = computed(() => requestsStore.requests.filter((r) => r.status === 'PENDING').length)
    const openIssues = ref(0)

    const queueTabs = computed(() => [
      { key: 'requests', label: 'Requests', badge: pendingRequests.value || null },
      { key: 'issues', label: 'Issues', badge: openIssues.value || null },
    ])
    const setupTabs = [
      { key: 'users', label: 'Users' },
      { key: 'managers', label: 'Media managers' },
      { key: 'plugins', label: 'Plugins' },
      { key: 'settings', label: 'Settings' },
      { key: 'stats', label: 'Statistics' },
    ]
    const tabs = computed(() => (isSetup.value ? setupTabs : queueTabs.value))

    const activeTab = ref('requests')
    // Reset to the first tab of the active section when the route section changes.
    watch(
      () => route.meta.section,
      (section) => { activeTab.value = section === 'setup' ? 'users' : 'requests' },
      { immediate: true }
    )

    const fulfilledRequests = computed(() => requestsStore.requests.filter((r) => r.status === 'FULFILLED').length)

    onMounted(async () => {
      await requestsStore.fetchRequests()
      try {
        const { data } = await axios.get(`${API_URL}/admin/users`)
        totalUsers.value = data.length
      } catch (e) { /* non-fatal */ }
      try {
        const { data } = await axios.get(`${API_URL}/issues/`)
        openIssues.value = data.filter((i) => i.status !== 'RESOLVED').length
      } catch (e) { /* non-fatal */ }
    })

    return { requestsStore, isSetup, tabs, activeTab, totalUsers, pendingRequests, fulfilledRequests, formatDate }
  },
}
</script>

<style scoped>
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }
</style>
