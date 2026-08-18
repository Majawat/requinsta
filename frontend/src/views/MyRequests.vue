<template>
  <div>
    <!-- Header -->
    <div class="flex items-center justify-between mb-3">
      <h1 class="text-[22px] font-bold tracking-tight">My Requests</h1>
      <button class="p-2 -mr-2 text-slate-400 hover:text-slate-200" @click="showFilter = !showFilter" aria-label="Filter by title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="21" y2="21" /></svg>
      </button>
    </div>

    <input
      v-if="showFilter"
      v-model="titleFilter"
      class="input mb-3"
      placeholder="Filter by title…"
      autofocus
    />

    <!-- Filter chips -->
    <div class="flex gap-2 overflow-x-auto pb-3 -mx-1 px-1 scrollbar-none">
      <button
        v-for="f in filters"
        :key="f.key"
        class="flex-none"
        :class="activeFilter === f.key ? 'chip-active' : 'chip-idle'"
        @click="activeFilter = f.key"
      >
        <span v-if="f.dot" class="w-[5px] h-[5px] rounded-full" :class="f.dot"></span>
        <span>{{ f.label }}</span>
        <span v-if="f.count !== null" class="tabular-nums opacity-70">{{ f.count }}</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="requestsStore.loading && requestsStore.requests.length === 0" class="border-t border-slate-800">
      <SkeletonRow /><SkeletonRow title-width="55%" /><SkeletonRow title-width="62%" />
    </div>

    <!-- Empty -->
    <EmptyState
      v-else-if="filtered.length === 0"
      :title="activeFilter === 'all' ? 'Nothing requested yet' : `No ${activeLabel.toLowerCase()} requests`"
      :body="activeFilter === 'all' ? 'Find a book, album or film and tap Request — it shows up here.' : 'Try a different filter.'"
      :action-label="activeFilter === 'all' ? 'Start searching' : ''"
      :action-primary="false"
      @action="$router.push('/')"
    />

    <!-- Rows -->
    <div v-else class="border-t border-slate-800">
      <button
        v-for="r in filtered"
        :key="r.id"
        class="w-full text-left flex items-center gap-3 px-1 py-3 border-b border-slate-800 hover:bg-slate-900/50"
        :class="rowTint(r)"
        @click="ui.openSheet(r)"
      >
        <MediaThumb :cover="r.cover_url" :type="r.media_type" :w="40" :h="56" />
        <div class="flex-1 min-w-0 flex flex-col gap-1">
          <div class="text-[15px] font-semibold text-slate-100 truncate">{{ r.title }}</div>
          <div class="text-[13px] text-slate-400 truncate">{{ rowMeta(r) }}</div>
          <div class="flex items-center gap-2 min-w-0">
            <StatusPill :status="rowState(r).status" :label="rowState(r).label" small class="flex-none" />
            <span v-if="rowState(r).note" class="text-xs text-slate-500 truncate">{{ rowState(r).note }}</span>
          </div>
        </div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="2.2" stroke-linecap="round" class="flex-none"><polyline points="9 6 15 12 9 18" /></svg>
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRequestsStore } from '../stores/requests'
import { useUiStore } from '../stores/ui'
import { useAuthStore } from '../stores/auth'
import { mediaTypeLabel, formatRelative } from '../utils/requestUtils'
import { API_URL } from '../utils/api'
import MediaThumb from '../components/ui/MediaThumb.vue'
import StatusPill from '../components/ui/StatusPill.vue'
import SkeletonRow from '../components/ui/SkeletonRow.vue'
import EmptyState from '../components/ui/EmptyState.vue'

export default {
  name: 'MyRequests',
  components: { MediaThumb, StatusPill, SkeletonRow, EmptyState },
  setup() {
    const requestsStore = useRequestsStore()
    const ui = useUiStore()
    const authStore = useAuthStore()
    // MyRequests is personal; admins see all of theirs here, the admin Queue is separate.
    const mine = computed(() => requestsStore.requests.filter((r) => r.user_id === authStore.user?.id))
    const activeFilter = ref('all')
    const showFilter = ref(false)
    const titleFilter = ref('')
    const issues = ref([])

    const openIssueFor = (id) => issues.value.find((i) => i.request_id === id && i.status !== 'RESOLVED')
    const anyIssueFor = (id) => issues.value.find((i) => i.request_id === id)

    const counts = computed(() => {
      const c = { PENDING: 0, APPROVED: 0, FULFILLED: 0, DENIED: 0 }
      for (const r of mine.value) c[r.status] = (c[r.status] || 0) + 1
      return c
    })

    const filters = computed(() => [
      { key: 'all', label: 'All', count: mine.value.length, dot: null },
      { key: 'PENDING', label: 'Pending', count: counts.value.PENDING, dot: 'bg-amber-400' },
      { key: 'APPROVED', label: 'Approved', count: counts.value.APPROVED, dot: 'bg-sky-400' },
      { key: 'FULFILLED', label: 'Ready', count: counts.value.FULFILLED, dot: 'bg-emerald-400' },
      { key: 'DENIED', label: 'Denied', count: counts.value.DENIED, dot: 'bg-rose-400' },
    ])

    const activeLabel = computed(() => (filters.value.find((f) => f.key === activeFilter.value) || {}).label || 'all')

    const filtered = computed(() => {
      let list = mine.value
      if (activeFilter.value !== 'all') list = list.filter((r) => r.status === activeFilter.value)
      const q = titleFilter.value.trim().toLowerCase()
      if (q) list = list.filter((r) => r.title.toLowerCase().includes(q))
      return list.slice().sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    })

    const rowMeta = (r) => {
      const who = r.author || mediaTypeLabel(r.media_type)
      return [who, formatRelative(r.created_at)].filter(Boolean).join(' · ')
    }

    // Plain-language status label + a one-line "next thing you care about".
    const rowState = (r) => {
      if (r.status === 'FULFILLED') {
        const open = openIssueFor(r.id)
        if (open) {
          return { status: 'ISSUE', label: 'Issue open', note: open.admin_response ? 'Admin replied' : 'Awaiting admin' }
        }
        return { status: 'FULFILLED', label: 'Available', note: 'Report an issue' }
      }
      if (r.status === 'PENDING') return { status: 'PENDING', label: 'Pending review', note: '' }
      if (r.status === 'APPROVED') return { status: 'APPROVED', label: 'Downloading', note: '' }
      if (r.status === 'DENIED') return { status: 'DENIED', label: 'Denied', note: r.fulfillment_detail || '' }
      return { status: r.status, label: r.status, note: '' }
    }

    const rowTint = (r) => (r.status === 'FULFILLED' && !openIssueFor(r.id) ? 'bg-emerald-400/[0.035]' : '')

    const loadIssues = async () => {
      try {
        const { data } = await axios.get(`${API_URL}/issues/`)
        issues.value = data
      } catch (e) { /* non-fatal */ }
    }

    onMounted(() => {
      requestsStore.fetchRequests()
      loadIssues()
    })

    return {
      requestsStore, ui, activeFilter, showFilter, titleFilter,
      filters, activeLabel, filtered, rowMeta, rowState, rowTint,
    }
  },
}
</script>

<style scoped>
.scrollbar-none::-webkit-scrollbar { display: none; }
.scrollbar-none { -ms-overflow-style: none; scrollbar-width: none; }
</style>
