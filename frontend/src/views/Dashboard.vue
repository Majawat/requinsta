<template>
  <div class="space-y-6">
    <!-- Search-first hero -->
    <div class="card p-6 bg-gradient-to-br from-gray-800/90 to-gray-800/60">
      <h1 class="text-2xl font-bold text-white">What do you want to add?</h1>
      <p class="text-gray-400 mt-1">Search books, movies, music, comics and more — then request it.</p>
      <div class="mt-4 flex flex-col sm:flex-row gap-2">
        <select v-model="mediaType" class="input sm:w-40">
          <option v-for="t in MEDIA_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>
        <input v-model="query" @keyup.enter="search" type="text" placeholder="Title, author, keyword…" class="input flex-1" />
        <button @click="search" :disabled="!query.trim()" class="btn-primary px-6">
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" /></svg>
          Search
        </button>
      </div>
    </div>

    <!-- Compact stats -->
    <div class="grid grid-cols-3 gap-4">
      <div class="card p-4 text-center">
        <div class="text-2xl font-bold text-white">{{ totalRequests }}</div>
        <div class="text-sm text-gray-400">Your Requests</div>
      </div>
      <div class="card p-4 text-center">
        <div class="text-2xl font-bold text-yellow-400">{{ pendingRequests }}</div>
        <div class="text-sm text-gray-400">Pending</div>
      </div>
      <div class="card p-4 text-center">
        <div class="text-2xl font-bold text-indigo-400">{{ fulfilledRequests }}</div>
        <div class="text-sm text-gray-400">Available</div>
      </div>
    </div>

    <!-- Recent requests strip -->
    <div class="card p-6">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-white">Your Recent Requests</h2>
        <router-link to="/my-requests" class="text-sm text-blue-400 hover:text-blue-300">View all →</router-link>
      </div>
      <div v-if="requestsStore.loading" class="text-gray-400">Loading…</div>
      <div v-else-if="requestsStore.recentRequests.length === 0" class="text-gray-400">
        No requests yet — search above to make your first.
      </div>
      <div v-else class="space-y-2">
        <div v-for="request in requestsStore.recentRequests" :key="request.id"
          class="flex gap-3 p-3 rounded-lg bg-gray-900/40 ring-1 ring-gray-700/50 hover:ring-gray-600 transition">
          <img v-if="request.cover_url" :src="request.cover_url" :alt="request.title"
            class="w-11 h-16 rounded object-cover flex-shrink-0 bg-gray-700" @error="$event.target.style.display='none'" />
          <div v-else class="w-11 h-16 rounded flex-shrink-0 bg-gray-700 flex items-center justify-center text-gray-500">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-medium text-white truncate">{{ request.title }}</h3>
            <p v-if="request.author" class="text-xs text-gray-400 truncate">{{ request.author }}</p>
            <div class="flex items-center gap-3 mt-1.5">
              <span class="text-xs text-gray-400">{{ mediaTypeLabel(request.media_type) }}</span>
              <span class="text-xs text-gray-600">·</span>
              <span class="text-xs text-gray-500">{{ formatDate(request.created_at) }}</span>
            </div>
          </div>
          <span :class="['badge self-start', statusMeta(request.status).classes]">
            <span :class="['h-1.5 w-1.5 rounded-full', statusMeta(request.status).dot]"></span>
            {{ statusMeta(request.status).label }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useRequestsStore } from '../stores/requests'
import { statusMeta, mediaTypeLabel, formatDate } from '../utils/requestUtils'

const MEDIA_TYPES = [
  { value: 'book', label: 'Book' },
  { value: 'audiobook', label: 'Audiobook' },
  { value: 'movie', label: 'Movie' },
  { value: 'tv_show', label: 'TV Show' },
  { value: 'music', label: 'Music' },
  { value: 'comic', label: 'Comic' },
  { value: 'other', label: 'Other' },
]

export default {
  name: 'Dashboard',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const requestsStore = useRequestsStore()

    const query = ref('')
    const mediaType = ref('book')

    const totalRequests = computed(() => requestsStore.requests.length)
    const pendingRequests = computed(() => requestsStore.requests.filter(r => r.status === 'PENDING').length)
    const fulfilledRequests = computed(() => requestsStore.requests.filter(r => r.status === 'FULFILLED').length)

    const search = () => {
      if (!query.value.trim()) return
      router.push({ path: '/browse', query: { q: query.value.trim(), type: mediaType.value } })
    }

    onMounted(async () => {
      if (authStore.isAuthenticated) await requestsStore.fetchRequests()
    })

    return { MEDIA_TYPES, query, mediaType, authStore, requestsStore,
      totalRequests, pendingRequests, fulfilledRequests, search, statusMeta, mediaTypeLabel, formatDate }
  }
}
</script>
