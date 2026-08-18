<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="border-b border-gray-700 pb-4">
      <h1 class="text-2xl font-bold text-white">My Requests</h1>
      <p class="text-gray-400 mt-1">Track your media requests and their status</p>
    </div>

    <!-- Filter tabs -->
    <div class="bg-gray-800 border border-gray-700 rounded-lg">
      <div class="flex border-b border-gray-700">
        <button
          v-for="filter in filters"
          :key="filter.key"
          @click="activeFilter = filter.key"
          :class="[
            'px-4 py-3 text-sm font-medium transition-colors',
            activeFilter === filter.key
              ? 'border-b-2 border-blue-500 text-blue-400'
              : 'text-gray-400 hover:text-gray-200'
          ]"
        >
          {{ filter.label }}
          <span
            v-if="filter.count > 0"
            class="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-gray-200"
          >
            {{ filter.count }}
          </span>
        </button>
      </div>
    </div>

    <!-- Requests list -->
    <div v-if="requestsStore.loading" class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <div class="text-gray-400">Loading your requests...</div>
    </div>

    <div v-else-if="filteredRequests.length === 0" class="bg-gray-800 border border-gray-700 p-6 rounded-lg text-center">
      <div class="text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        <p class="text-lg font-medium">No {{ activeFilter === 'all' ? '' : activeFilter.toLowerCase() }} requests found</p>
        <p class="text-sm mt-1">
          {{ activeFilter === 'all' ? 'Start by browsing and requesting some media!' : `You don't have any ${activeFilter.toLowerCase()} requests.` }}
        </p>
      </div>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="request in filteredRequests"
        :key="request.id"
        class="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <h3 class="text-lg font-medium text-white">{{ request.title }}</h3>
              <span
                :class="[
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                  getStatusClasses(request.status)
                ]"
              >
                {{ request.status }}
              </span>
            </div>

            <p class="text-gray-300 mt-2">{{ request.description }}</p>

            <div class="flex items-center mt-4 space-x-4">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
                {{ request.media_type }}
              </span>
              <span class="text-sm text-gray-400">
                Requested on {{ formatDate(request.created_at) }}
              </span>
            </div>

            <!-- Status-specific information -->
            <div v-if="request.status === 'APPROVED'" class="mt-4 p-3 bg-green-900 bg-opacity-50 border border-green-700 rounded-md">
              <p class="text-green-200 text-sm">
                <svg class="inline h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Your request has been approved and is being processed.
              </p>
            </div>

            <div v-if="request.status === 'FULFILLED'" class="mt-4 p-3 bg-blue-900 bg-opacity-50 border border-blue-700 rounded-md">
              <p class="text-blue-200 text-sm">
                <svg class="inline h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                Your request has been fulfilled! The media should be available now.
              </p>
            </div>

            <!-- Issues on this (fulfilled) media -->
            <div v-if="request.status === 'FULFILLED'" class="mt-3">
              <div v-for="issue in issuesFor(request.id)" :key="issue.id" class="mb-2 p-3 bg-gray-700 border border-gray-600 rounded-md">
                <div class="flex items-center justify-between">
                  <span class="text-sm text-gray-200">{{ categoryLabel(issue.category) }}</span>
                  <span :class="['px-2 py-0.5 rounded-full text-xs', issue.status === 'RESOLVED' ? 'bg-green-900 text-green-200' : 'bg-yellow-900 text-yellow-200']">{{ issue.status }}</span>
                </div>
                <p class="text-sm text-gray-400 mt-1">{{ issue.description }}</p>
                <p v-if="issue.admin_response" class="text-sm text-blue-300 mt-2">Admin: {{ issue.admin_response }}</p>
              </div>

              <button v-if="reportingId !== request.id" @click="startReport(request.id)"
                class="text-sm text-red-400 hover:text-red-300">Report an issue</button>

              <div v-else class="mt-2 p-3 bg-gray-700 border border-gray-600 rounded-md space-y-2">
                <select v-model="reportForm.category" class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white text-sm">
                  <option v-for="c in CATEGORIES" :key="c.value" :value="c.value">{{ c.label }}</option>
                </select>
                <textarea v-model="reportForm.description" rows="2" placeholder="What's wrong?"
                  class="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-md text-white text-sm placeholder-gray-400"></textarea>
                <div class="flex justify-end gap-2">
                  <button @click="reportingId = null" class="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500">Cancel</button>
                  <button @click="submitReport(request.id)" :disabled="submitting || !reportForm.description.trim()"
                    class="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50">{{ submitting ? 'Sending…' : 'Submit' }}</button>
                </div>
              </div>
            </div>

            <div v-if="request.status === 'DENIED'" class="mt-4 p-3 bg-red-900 bg-opacity-50 border border-red-700 rounded-md">
              <p class="text-red-200 text-sm">
                <svg class="inline h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
                Your request was denied. Please contact an administrator for more information.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { useRequestsStore } from '../stores/requests'
import { getStatusClasses, formatDate } from '../utils/requestUtils'
import { API_URL } from '../utils/api'

const CATEGORIES = [
  { value: 'WRONG_CONTENT', label: 'Wrong content (edition/version)' },
  { value: 'QUALITY', label: 'Quality problem' },
  { value: 'PLAYBACK', label: "Won't play / open" },
  { value: 'INCOMPLETE', label: 'Incomplete (missing parts)' },
  { value: 'OTHER', label: 'Other' },
]

export default {
  name: 'MyRequests',
  setup() {
    const requestsStore = useRequestsStore()
    const activeFilter = ref('all')

    const issues = ref([])
    const reportingId = ref(null)
    const reportForm = reactive({ category: 'WRONG_CONTENT', description: '' })
    const submitting = ref(false)

    const issuesFor = (requestId) => issues.value.filter(i => i.request_id === requestId)
    const categoryLabel = (v) => (CATEGORIES.find(c => c.value === v) || {}).label || v

    const loadIssues = async () => {
      try {
        const { data } = await axios.get(`${API_URL}/issues/`)
        issues.value = data
      } catch (e) { /* non-fatal */ }
    }

    const startReport = (requestId) => {
      reportingId.value = requestId
      reportForm.category = 'WRONG_CONTENT'
      reportForm.description = ''
    }

    const submitReport = async (requestId) => {
      submitting.value = true
      try {
        await axios.post(`${API_URL}/issues/`, {
          request_id: requestId,
          category: reportForm.category,
          description: reportForm.description,
        })
        reportingId.value = null
        await loadIssues()
      } catch (e) { /* surfaced via disabled state; keep simple */ }
      finally { submitting.value = false }
    }

    const filters = computed(() => {
      const counts = requestsStore.requests.reduce((acc, r) => {
        acc[r.status] = (acc[r.status] || 0) + 1
        return acc
      }, {})
      return [
        { key: 'all',       label: 'All Requests', count: requestsStore.requests.length },
        { key: 'pending',   label: 'Pending',      count: counts.PENDING   || 0 },
        { key: 'approved',  label: 'Approved',     count: counts.APPROVED  || 0 },
        { key: 'fulfilled', label: 'Fulfilled',    count: counts.FULFILLED || 0 },
        { key: 'denied',    label: 'Denied',       count: counts.DENIED    || 0 },
      ]
    })

    const filteredRequests = computed(() => {
      if (activeFilter.value === 'all') return requestsStore.requests
      return requestsStore.requests.filter(
        request => request.status === activeFilter.value.toUpperCase()
      )
    })

    onMounted(async () => {
      await Promise.all([requestsStore.fetchRequests(), loadIssues()])
    })

    return {
      requestsStore,
      activeFilter,
      filters,
      filteredRequests,
      getStatusClasses,
      formatDate,
      CATEGORIES,
      issuesFor,
      categoryLabel,
      reportingId,
      reportForm,
      submitting,
      startReport,
      submitReport,
    }
  }
}
</script>
