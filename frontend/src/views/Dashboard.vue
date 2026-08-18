<template>
  <div class="space-y-6">
    <!-- Search-first hero -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h1 class="text-2xl font-bold text-white">What do you want to add?</h1>
      <p class="text-gray-400 mt-1">Search books, movies, music, comics and more — then request it.</p>
      <div class="mt-4 flex flex-col sm:flex-row gap-2">
        <select v-model="mediaType" class="px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white">
          <option v-for="t in MEDIA_TYPES" :key="t.value" :value="t.value">{{ t.label }}</option>
        </select>
        <input
          v-model="query"
          @keyup.enter="search"
          type="text"
          placeholder="Title, author, keyword…"
          class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button @click="search" :disabled="!query.trim()"
          class="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-md">
          Search
        </button>
      </div>
    </div>

    <!-- Compact stats -->
    <div class="grid grid-cols-3 gap-4">
      <div class="bg-gray-800 border border-gray-700 p-4 rounded-lg text-center">
        <div class="text-2xl font-bold text-white">{{ totalRequests }}</div>
        <div class="text-sm text-gray-400">Your Requests</div>
      </div>
      <div class="bg-gray-800 border border-gray-700 p-4 rounded-lg text-center">
        <div class="text-2xl font-bold text-yellow-400">{{ pendingRequests }}</div>
        <div class="text-sm text-gray-400">Pending</div>
      </div>
      <div class="bg-gray-800 border border-gray-700 p-4 rounded-lg text-center">
        <div class="text-2xl font-bold text-blue-400">{{ fulfilledRequests }}</div>
        <div class="text-sm text-gray-400">Available</div>
      </div>
    </div>

    <!-- Recent requests strip -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-lg font-medium text-white">Your Recent Requests</h2>
        <router-link to="/my-requests" class="text-sm text-blue-400 hover:text-blue-300">View all →</router-link>
      </div>
      <div v-if="requestsStore.loading" class="text-gray-400">Loading…</div>
      <div v-else-if="requestsStore.recentRequests.length === 0" class="text-gray-400">
        No requests yet — search above to make your first.
      </div>
      <div v-else class="space-y-3">
        <div v-for="request in requestsStore.recentRequests" :key="request.id"
          class="border border-gray-600 rounded p-4 bg-gray-700">
          <div class="flex justify-between items-start">
            <div class="flex-1">
              <h3 class="font-medium text-white">{{ request.title }}</h3>
              <p v-if="request.author" class="text-xs text-gray-400">{{ request.author }}</p>
              <div class="flex items-center mt-2 space-x-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200">{{ request.media_type }}</span>
                <span class="text-xs text-gray-400">{{ formatDate(request.created_at) }}</span>
              </div>
            </div>
            <span :class="['inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium', getStatusClasses(request.status)]">{{ request.status }}</span>
          </div>
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
import { getStatusClasses, formatDate } from '../utils/requestUtils'

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
      totalRequests, pendingRequests, fulfilledRequests, search, getStatusClasses, formatDate }
  }
}
</script>
