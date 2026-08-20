<template>
  <teleport to="body">
    <transition name="sheet-fade">
      <div v-if="req" class="fixed inset-0 z-50" @keydown.esc="close">
        <!-- Backdrop: the list stays behind so tapping through requests never
             loses scroll position. -->
        <div class="absolute inset-0 bg-slate-950/70 backdrop-blur-[2px]" @click="close"></div>

        <transition :name="sheetTransition" appear>
          <div
            class="absolute bg-slate-900 flex flex-col
                   inset-x-0 bottom-0 max-h-[88vh] rounded-t-2xl border-t border-slate-700 shadow-sheet
                   lg:inset-y-0 lg:right-0 lg:left-auto lg:bottom-auto lg:w-[420px] lg:max-h-none lg:rounded-none lg:border-t-0 lg:border-l"
          >
            <!-- drag handle (mobile) -->
            <div class="lg:hidden pt-2.5 flex-none flex justify-center">
              <div class="w-9 h-1 rounded-full bg-slate-700"></div>
            </div>

            <div class="flex-1 overflow-y-auto">
              <!-- Header -->
              <div class="px-[18px] pt-3 pb-4 flex gap-3.5 items-start">
                <MediaThumb :cover="req.cover_url" :type="mediaKey" :w="72" :h="104" radius="md" />
                <div class="flex-1 min-w-0 flex flex-col gap-1.5">
                  <div class="text-[19px] font-bold leading-tight tracking-tight text-slate-100">{{ req.title }}</div>
                  <div class="text-[13px] text-slate-400">{{ metaLine }}</div>
                  <div class="flex flex-wrap gap-1.5 pt-0.5">
                    <TypeBadge :type="mediaKey" />
                    <span
                      v-if="req.provider"
                      class="inline-flex items-center px-2 py-1 rounded-md bg-slate-800 font-mono text-[10px] font-medium uppercase text-slate-400"
                    >{{ req.provider }}</span>
                  </div>
                </div>
                <button class="p-2 -mr-2 text-slate-500 hover:text-slate-300 flex-none" @click="close" aria-label="Close">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                    <line x1="6" y1="6" x2="18" y2="18" /><line x1="18" y1="6" x2="6" y2="18" />
                  </svg>
                </button>
              </div>

              <div class="px-[18px]"><div class="h-px bg-slate-800"></div></div>

              <!-- Progress -->
              <div class="px-[18px] py-4 flex flex-col gap-3.5">
                <div class="flex items-center justify-between">
                  <div class="eyebrow">Progress</div>
                  <StatusPill :status="statusKey" :label="statusLabel" />
                </div>

                <div class="flex flex-col">
                  <div v-for="(step, i) in timeline" :key="i" class="flex gap-3">
                    <div class="flex flex-col items-center flex-none">
                      <span
                        class="w-[11px] h-[11px] rounded-full mt-1 border-2"
                        :class="dotClass(step.state)"
                      ></span>
                      <span v-if="i < timeline.length - 1" class="w-0.5 flex-1" :class="step.state === 'done' ? 'bg-emerald-500/60' : 'bg-slate-800'"></span>
                    </div>
                    <div class="flex flex-col gap-0.5" :class="i < timeline.length - 1 ? 'pb-3.5' : ''">
                      <div class="text-sm font-semibold" :class="step.state === 'future' ? 'text-slate-500' : 'text-slate-200'">{{ step.title }}</div>
                      <div v-if="step.sub" class="text-xs" :class="step.state === 'future' ? 'text-slate-600' : 'text-slate-500'">{{ step.sub }}</div>
                    </div>
                  </div>
                </div>

                <p v-if="req.fulfillment_detail" class="text-xs text-slate-500 bg-slate-800/50 rounded-lg px-3 py-2">{{ req.fulfillment_detail }}</p>
              </div>

              <!-- Issues (available media only) -->
              <div v-if="statusKey === 'FULFILLED'" class="px-[18px] pb-4 flex flex-col gap-3">
                <div class="h-px bg-slate-800"></div>
                <div class="eyebrow">Issues</div>

                <div v-for="issue in issues" :key="issue.id" class="rounded-lg bg-slate-800/70 border border-slate-700 p-3 flex flex-col gap-1.5">
                  <div class="flex items-center justify-between gap-2">
                    <span class="text-sm font-medium text-slate-200">{{ categoryLabel(issue.category) }}</span>
                    <StatusPill :status="issue.status === 'RESOLVED' ? 'FULFILLED' : 'ISSUE'" :label="issue.status === 'RESOLVED' ? 'Resolved' : 'Open'" small />
                  </div>
                  <p class="text-[13px] text-slate-400">{{ issue.description }}</p>
                  <p v-if="issue.admin_response" class="text-[13px] text-indigo-300">Admin: {{ issue.admin_response }}</p>
                </div>

                <!-- Report form -->
                <div v-if="reporting" class="rounded-lg bg-slate-800/70 border border-slate-700 p-3 flex flex-col gap-2">
                  <select v-model="form.category" class="input">
                    <option v-for="c in CATEGORIES" :key="c.value" :value="c.value">{{ c.label }}</option>
                  </select>
                  <textarea v-model="form.description" rows="2" placeholder="What's wrong?" class="input"></textarea>
                  <div class="flex justify-end gap-2">
                    <button class="btn-ghost btn-sm" @click="reporting = false">Cancel</button>
                    <button class="btn-primary btn-sm" :disabled="submitting || !form.description.trim()" @click="submitReport">
                      {{ submitting ? 'Sending…' : 'Submit' }}
                    </button>
                  </div>
                </div>
                <button v-else class="btn-secondary w-full" @click="startReport">Report an issue</button>
              </div>

              <!-- Cancel / delete -->
              <div v-if="canDelete" class="px-[18px] pb-4 flex flex-col gap-3">
                <div class="h-px bg-slate-800"></div>
                <button class="btn-deny w-full" @click="confirmOpen = true">{{ deleteLabel }}</button>
              </div>

              <div class="h-4"></div>
            </div>
          </div>
        </transition>

        <ConfirmModal
          :open="confirmOpen"
          :title="deleteLabel + '?'"
          :message="confirmMessage"
          :confirm-label="deleteLabel"
          :busy="deleting"
          @confirm="doDelete"
          @cancel="confirmOpen = false"
        />
      </div>
    </transition>
  </teleport>
</template>

<script>
import { ref, reactive, computed, watch } from 'vue'
import axios from 'axios'
import MediaThumb from './ui/MediaThumb.vue'
import TypeBadge from './ui/TypeBadge.vue'
import StatusPill from './ui/StatusPill.vue'
import ConfirmModal from './ui/ConfirmModal.vue'
import { useUiStore } from '../stores/ui'
import { useAuthStore } from '../stores/auth'
import { useRequestsStore } from '../stores/requests'
import { statusMeta, formatDateTime, formatRelative } from '../utils/requestUtils'
import { API_URL } from '../utils/api'

const CATEGORIES = [
  { value: 'WRONG_CONTENT', label: 'Wrong content (edition/version)' },
  { value: 'QUALITY', label: 'Quality problem' },
  { value: 'PLAYBACK', label: "Won't play / open" },
  { value: 'INCOMPLETE', label: 'Incomplete (missing parts)' },
  { value: 'OTHER', label: 'Other' },
]

// Backend media_type values arrive lowercase ("tv_show"); the icon/label maps
// key on those directly.
export default {
  name: 'RequestDetailSheet',
  components: { MediaThumb, TypeBadge, StatusPill, ConfirmModal },
  setup() {
    const ui = useUiStore()
    const auth = useAuthStore()
    const requestsStore = useRequestsStore()
    const req = computed(() => ui.sheetRequest)
    const issues = ref([])
    const reporting = ref(false)
    const submitting = ref(false)
    const form = reactive({ category: 'WRONG_CONTENT', description: '' })
    const confirmOpen = ref(false)
    const deleting = ref(false)

    const mediaKey = computed(() => (req.value?.media_type || 'other'))
    const statusKey = computed(() => req.value?.status || 'PENDING')

    const isAdmin = computed(() => auth.isAdmin)
    const isOwn = computed(() => req.value?.user_id === auth.user?.id)
    // A user can cancel their own request while it's pending; an admin can remove
    // any request in any status.
    const canCancel = computed(() => statusKey.value === 'PENDING' && (isOwn.value || isAdmin.value))
    const canDelete = computed(() => canCancel.value || isAdmin.value)
    const deleteLabel = computed(() => (canCancel.value ? 'Cancel request' : 'Delete request'))
    const confirmMessage = computed(() =>
      canCancel.value
        ? 'This removes your pending request. It has not been sent to a media manager yet.'
        : 'This removes the request from the list. It does not delete any downloaded media.'
    )

    const doDelete = async () => {
      deleting.value = true
      const res = await requestsStore.deleteRequest(req.value.id)
      deleting.value = false
      confirmOpen.value = false
      if (res.success) {
        ui.toast(canCancel.value ? 'Request cancelled' : 'Request deleted')
        ui.closeSheet()
      } else {
        ui.toast(res.error || 'Could not delete the request', { type: 'error' })
      }
    }

    const metaLine = computed(() => {
      if (!req.value) return ''
      return [req.value.author, req.value.year].filter(Boolean).join(' · ')
    })

    const statusLabel = computed(() => {
      const s = statusKey.value
      if (s === 'PENDING') return 'Pending review'
      if (s === 'APPROVED') return 'Downloading'
      return statusMeta(s).label
    })

    // Presentational timeline derived from status + timestamps.
    const timeline = computed(() => {
      const r = req.value
      if (!r) return []
      const s = r.status
      const requested = { title: 'Requested by you', sub: formatDateTime(r.created_at), state: 'done' }
      if (s === 'DENIED') {
        return [
          requested,
          { title: 'Request denied', sub: r.fulfillment_detail || 'An admin declined this request', state: 'denied' },
        ]
      }
      const approved = {
        title: s === 'PENDING' ? 'Waiting for approval' : 'Approved',
        sub: s === 'PENDING' ? 'Usually reviewed within a day' : (r.target_service ? `Sent to ${r.target_service}` : 'Sent to the library'),
        state: s === 'PENDING' ? 'current' : 'done',
      }
      const available = {
        title: 'Available in library',
        sub: s === 'FULFILLED' ? `Ready ${formatRelative(r.updated_at || r.created_at)}` : "You'll get a notification",
        state: s === 'FULFILLED' ? 'done' : (s === 'APPROVED' ? 'current' : 'future'),
      }
      return [requested, approved, available]
    })

    const dotClass = (state) => {
      if (state === 'done') return 'bg-emerald-400 border-emerald-400'
      if (state === 'current') return 'bg-slate-900 border-amber-400'
      if (state === 'denied') return 'bg-rose-400 border-rose-400'
      return 'bg-slate-800 border-slate-700'
    }

    const categoryLabel = (v) => (CATEGORIES.find((c) => c.value === v) || {}).label || v

    const loadIssues = async () => {
      if (!req.value || req.value.status !== 'FULFILLED') { issues.value = []; return }
      try {
        const { data } = await axios.get(`${API_URL}/issues/`)
        issues.value = data.filter((i) => i.request_id === req.value.id)
      } catch (e) { issues.value = [] }
    }

    const startReport = () => {
      reporting.value = true
      form.category = 'WRONG_CONTENT'
      form.description = ''
    }

    const submitReport = async () => {
      submitting.value = true
      try {
        await axios.post(`${API_URL}/issues/`, {
          request_id: req.value.id,
          category: form.category,
          description: form.description,
        })
        reporting.value = false
        ui.toast('Issue reported — an admin will take a look')
        await loadIssues()
      } catch (e) {
        ui.toast(e.response?.data?.detail || 'Could not report the issue', { type: 'error' })
      } finally {
        submitting.value = false
      }
    }

    const close = () => ui.closeSheet()

    // Reset per-request UI state and (re)load issues whenever the open request changes.
    watch(req, (r) => {
      reporting.value = false
      confirmOpen.value = false
      if (r) loadIssues()
    })

    // On desktop the sheet slides in from the right; on mobile it rises from the
    // bottom. matchMedia picks the transition at open time.
    const sheetTransition = computed(() =>
      typeof window !== 'undefined' && window.matchMedia('(min-width: 1024px)').matches ? 'sheet-right' : 'sheet-up'
    )

    return {
      ui, req, issues, reporting, submitting, form, CATEGORIES,
      mediaKey, statusKey, statusLabel, metaLine, timeline, dotClass,
      categoryLabel, startReport, submitReport, close, sheetTransition,
      confirmOpen, deleting, canDelete, deleteLabel, confirmMessage, doDelete,
    }
  },
}
</script>

<style scoped>
.sheet-fade-enter-active,
.sheet-fade-leave-active { transition: opacity 0.2s ease; }
.sheet-fade-enter-from,
.sheet-fade-leave-to { opacity: 0; }

.sheet-up-enter-active,
.sheet-up-leave-active { transition: transform 0.26s cubic-bezier(0.22, 1, 0.36, 1); }
.sheet-up-enter-from,
.sheet-up-leave-to { transform: translateY(100%); }

.sheet-right-enter-active,
.sheet-right-leave-active { transition: transform 0.26s cubic-bezier(0.22, 1, 0.36, 1); }
.sheet-right-enter-from,
.sheet-right-leave-to { transform: translateX(100%); }
</style>
