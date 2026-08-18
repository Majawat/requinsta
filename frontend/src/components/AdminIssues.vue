<template>
  <div class="space-y-4">
    <div class="border-b border-gray-700 pb-4">
      <h2 class="text-xl font-bold text-white">Reported Issues</h2>
      <p class="text-gray-400 mt-1">Problems users reported on available media.</p>
    </div>

    <div class="flex gap-2">
      <button v-for="f in ['open', 'all', 'resolved']" :key="f" @click="filter = f"
        :class="['px-3 py-1 text-sm rounded-md', filter === f ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600']">
        {{ f[0].toUpperCase() + f.slice(1) }}
      </button>
    </div>

    <div v-if="filtered.length === 0" class="bg-gray-800 border border-gray-700 p-6 rounded-lg text-center text-gray-400">
      No {{ filter === 'all' ? '' : filter }} issues.
    </div>

    <div v-for="issue in filtered" :key="issue.id" class="bg-gray-800 border border-gray-700 p-4 rounded-lg">
      <div class="flex justify-between items-start">
        <div>
          <h3 class="font-medium text-white">{{ issue.request_title }}</h3>
          <p class="text-xs text-gray-400">
            {{ categoryLabel(issue.category) }} · reported by {{ issue.reporter_email || 'user #' + issue.user_id }}
          </p>
        </div>
        <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', issue.status === 'RESOLVED' ? 'bg-green-900 text-green-200' : 'bg-yellow-900 text-yellow-200']">{{ issue.status }}</span>
      </div>

      <p class="text-sm text-gray-300 mt-2">{{ issue.description }}</p>

      <div class="mt-3 space-y-2">
        <textarea v-model="responses[issue.id]" rows="2" placeholder="Response to the user (optional)"
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white text-sm placeholder-gray-400"></textarea>
        <div class="flex justify-end gap-2">
          <button @click="save(issue, null)" class="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500">Save response</button>
          <button v-if="issue.status !== 'RESOLVED'" @click="save(issue, 'RESOLVED')" class="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700">Save &amp; resolve</button>
          <button v-else @click="save(issue, 'OPEN')" class="px-3 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700">Reopen</button>
        </div>
      </div>
    </div>

    <div v-if="message" class="p-3 rounded-lg bg-green-900 text-green-100 text-sm">{{ message }}</div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { API_URL } from '../utils/api'

const CATEGORY_LABELS = {
  WRONG_CONTENT: 'Wrong content', QUALITY: 'Quality', PLAYBACK: "Won't play",
  INCOMPLETE: 'Incomplete', OTHER: 'Other',
}

export default {
  name: 'AdminIssues',
  setup() {
    const issues = ref([])
    const responses = reactive({})
    const filter = ref('open')
    const message = ref('')

    const filtered = computed(() => {
      if (filter.value === 'all') return issues.value
      return issues.value.filter(i => i.status === filter.value.toUpperCase())
    })
    const categoryLabel = (v) => CATEGORY_LABELS[v] || v

    const load = async () => {
      const { data } = await axios.get(`${API_URL}/issues/`)
      issues.value = data
      for (const i of data) if (!(i.id in responses)) responses[i.id] = i.admin_response || ''
    }

    const save = async (issue, status) => {
      try {
        const body = { admin_response: responses[issue.id] }
        if (status) body.status = status
        await axios.patch(`${API_URL}/issues/${issue.id}`, body)
        await load()
        message.value = 'Saved'; setTimeout(() => message.value = '', 2500)
      } catch (e) { /* ignore */ }
    }

    onMounted(load)
    return { issues, responses, filter, filtered, categoryLabel, save, message }
  }
}
</script>
