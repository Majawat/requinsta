<template>
  <div class="space-y-4">
    <div>
      <h2 class="text-base font-semibold">Reported issues</h2>
      <p class="text-sm text-slate-400 mt-0.5">Problems users reported on available media.</p>
    </div>

    <div class="flex gap-2">
      <button
        v-for="f in ['open', 'all', 'resolved']"
        :key="f"
        @click="filter = f"
        :class="filter === f ? 'chip-active' : 'chip-idle'"
      >
        {{ f[0].toUpperCase() + f.slice(1) }}
      </button>
    </div>

    <div v-if="filtered.length === 0" class="card p-6 text-center text-slate-400 text-sm">
      No {{ filter === 'all' ? '' : filter }} issues.
    </div>

    <div v-for="issue in filtered" :key="issue.id" class="card p-4">
      <div class="flex justify-between items-start gap-3">
        <div class="min-w-0">
          <h3 class="font-semibold text-slate-100 truncate">{{ issue.request_title }}</h3>
          <p class="text-xs text-slate-400">
            {{ categoryLabel(issue.category) }} · reported by {{ issue.reporter_email || 'user #' + issue.user_id }}
          </p>
        </div>
        <StatusPill
          :status="issue.status === 'RESOLVED' ? 'FULFILLED' : 'ISSUE'"
          :label="issue.status === 'RESOLVED' ? 'Resolved' : 'Open'"
          small
          class="flex-none"
        />
      </div>

      <p class="text-sm text-slate-300 mt-2">{{ issue.description }}</p>

      <div class="mt-3 space-y-2">
        <textarea v-model="responses[issue.id]" rows="2" placeholder="Response to the user (optional)" class="input"></textarea>
        <div class="flex justify-end gap-2">
          <button @click="save(issue, null)" class="btn-secondary btn-sm">Save response</button>
          <button v-if="issue.status !== 'RESOLVED'" @click="save(issue, 'RESOLVED')" class="btn-primary btn-sm">Save &amp; resolve</button>
          <button v-else @click="save(issue, 'OPEN')" class="btn-secondary btn-sm">Reopen</button>
        </div>
      </div>
    </div>

    <div v-if="message" class="p-3 rounded-lg bg-emerald-500/10 text-emerald-200 border border-emerald-400/30 text-sm">{{ message }}</div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { API_URL } from '../utils/api'
import StatusPill from './ui/StatusPill.vue'

const CATEGORY_LABELS = {
  WRONG_CONTENT: 'Wrong content', QUALITY: 'Quality', PLAYBACK: "Won't play",
  INCOMPLETE: 'Incomplete', OTHER: 'Other',
}

export default {
  name: 'AdminIssues',
  components: { StatusPill },
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
