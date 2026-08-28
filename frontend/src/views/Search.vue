<template>
  <div>
    <!-- ============================ RESULTS MODE ============================ -->
    <template v-if="hasSearched">
      <!-- Scoped search bar -->
      <div class="flex items-center gap-2 mb-1">
        <button class="p-2 -ml-2 text-slate-300 hover:text-white flex-none" @click="backToIdle" aria-label="Back">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 5 8 12 15 19" />
          </svg>
        </button>
        <div class="flex-1 flex items-center gap-2 h-11 rounded-lg bg-slate-800 border border-slate-700 px-2.5 min-w-0 focus-within:border-indigo-500 focus-within:ring-[3px] focus-within:ring-indigo-500/20">
          <span v-if="typeScope" class="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-slate-900 flex-none">
            <MediaIcon :type="typeScope" :size="12" />
            <span class="text-[11px] font-semibold text-slate-300">{{ scopeLabel }}</span>
          </span>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" class="flex-none">
            <circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="21" y2="21" />
          </svg>
          <input
            ref="resultInput"
            v-model="query"
            @keyup.enter="runSearch()"
            type="text"
            class="flex-1 min-w-0 bg-transparent text-[15px] text-slate-100 placeholder-slate-500 focus:outline-none"
            placeholder="Search…"
          />
          <button v-if="query" class="text-slate-500 hover:text-slate-300 flex-none" @click="backToIdle" aria-label="Clear">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
              <line x1="6" y1="6" x2="18" y2="18" /><line x1="18" y1="6" x2="6" y2="18" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Result count + source -->
      <div class="flex items-center justify-between px-1 py-2.5 text-xs text-slate-500 border-b border-slate-800">
        <span>{{ searching ? 'Searching…' : `${results.length} result${results.length === 1 ? '' : 's'}` }}</span>
        <span v-if="source">via <span class="font-mono text-[11px] text-slate-400 uppercase">{{ source }}</span></span>
      </div>

      <!-- Loading skeletons -->
      <div v-if="searching">
        <SkeletonRow />
        <SkeletonRow title-width="55%" meta-width="35%" />
        <SkeletonRow title-width="62%" meta-width="30%" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="mx-1 my-4 rounded-lg border border-rose-400/30 bg-rose-500/5 px-4 py-3 text-sm text-rose-300">
        {{ error }}
      </div>

      <!-- Empty -->
      <EmptyState
        v-else-if="results.length === 0"
        :title="`No ${scopeLabel.toLowerCase()} match “${lastQuery}”`"
        body="Check the spelling, or send it as a manual request and an admin will find it."
        action-label="Request manually"
        @action="openManual"
      />

      <!-- Results -->
      <div v-else>
        <div
          v-for="r in results"
          :key="resultKey(r)"
          class="flex items-center gap-3 px-1 py-3 border-b border-slate-800"
        >
          <MediaThumb :cover="r.cover_url" :type="r.media_type || typeScope" :w="44" :h="62" />
          <div class="flex-1 min-w-0 flex flex-col gap-0.5">
            <div class="text-[15px] font-semibold leading-snug truncate" :class="isAvailable(r) ? 'text-slate-300' : 'text-slate-100'">{{ r.title }}</div>
            <div class="text-[13px] text-slate-400 truncate">{{ resultMeta(r) }}</div>
          </div>

          <!-- one action per row -->
          <div v-if="isAvailable(r)" class="flex items-center gap-1.5 pr-1 flex-none">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 12.5 9.5 18 20 6" /></svg>
            <span class="text-[13px] font-semibold text-emerald-300">In library</span>
          </div>
          <StatusPill v-else-if="isRequested(r)" status="PENDING" label="Requested" class="flex-none" />
          <button v-else-if="canRequest" class="btn-primary btn-sm flex-none" :disabled="pendingIds.has(resultKey(r))" @click="requestItem(r)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
            Request
          </button>
        </div>

        <!-- Not here? -->
        <button v-if="canRequest" class="w-full text-left m-1 mt-4 p-3.5 rounded-[10px] border border-dashed border-slate-700 hover:border-slate-600 flex items-center gap-3" @click="openManual">
          <span class="grid place-items-center w-[34px] h-[34px] rounded-lg bg-slate-800 flex-none">
            <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" /></svg>
          </span>
          <span class="flex-1">
            <span class="block text-sm font-semibold text-slate-200">Not here?</span>
            <span class="block text-xs text-slate-400">Send a manual request instead</span>
          </span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2.2" stroke-linecap="round"><polyline points="9 6 15 12 9 18" /></svg>
        </button>
      </div>
    </template>

    <!-- ============================= IDLE MODE ============================= -->
    <template v-else>
      <h1 class="text-[22px] font-bold tracking-tight leading-tight mb-3.5">What do you want to add?</h1>

      <div class="flex items-center gap-2.5 h-[46px] rounded-lg bg-slate-800 border border-slate-700 px-3 focus-within:border-indigo-500 focus-within:ring-[3px] focus-within:ring-indigo-500/20">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" class="flex-none"><circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="21" y2="21" /></svg>
        <input
          ref="idleInput"
          v-model="query"
          @keyup.enter="runSearch()"
          type="text"
          placeholder="Search everything"
          class="flex-1 min-w-0 bg-transparent text-[15px] text-slate-100 placeholder-slate-500 focus:outline-none"
        />
      </div>

      <div class="eyebrow mt-5 mb-2.5">Or pick a type</div>
      <div class="grid grid-cols-2 gap-2.5">
        <button
          v-for="t in visibleTypeCards"
          :key="t.value"
          class="h-[54px] rounded-[10px] bg-slate-900 border border-slate-800 hover:border-slate-700 flex items-center gap-2.5 px-3.5 transition-colors"
          :class="typeScope === t.value ? 'ring-1 ring-indigo-500/50 border-indigo-500/40' : ''"
          @click="pickType(t.value)"
        >
          <MediaIcon :type="t.value" :size="18" />
          <span class="text-sm font-semibold text-slate-200">{{ t.label }}</span>
        </button>
      </div>

      <!-- Your requests -->
      <div class="flex items-center justify-between mt-6 mb-1">
        <div class="eyebrow">Your requests</div>
        <router-link to="/my-requests" class="text-[13px] font-semibold text-indigo-300 hover:text-indigo-200">See all</router-link>
      </div>
      <div class="flex items-center gap-3.5 text-xs text-slate-400 pb-2.5">
        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>{{ counts.pending }} pending</span>
        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-sky-400"></span>{{ counts.approved }} approved</span>
        <span class="flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>{{ counts.ready }} ready</span>
      </div>

      <div v-if="requestsStore.loading && recent.length === 0" class="border-t border-slate-800">
        <SkeletonRow /><SkeletonRow title-width="50%" />
      </div>
      <EmptyState
        v-else-if="recent.length === 0"
        title="Nothing requested yet"
        body="Find a book, album or film and tap Request — it shows up here."
        action-label="Start searching"
        :action-primary="false"
        @action="focusIdle"
      />
      <div v-else class="border-t border-slate-800">
        <button
          v-for="r in recent"
          :key="r.id"
          class="w-full text-left flex items-center gap-3 px-1 py-2.5 border-b border-slate-800 hover:bg-slate-900/50"
          @click="ui.openSheet(r)"
        >
          <MediaThumb :cover="r.cover_url" :type="r.media_type" :w="40" :h="56" />
          <div class="flex-1 min-w-0 flex flex-col gap-0.5">
            <div class="text-[15px] font-semibold text-slate-100 truncate">{{ r.title }}</div>
            <div class="text-[13px] text-slate-400 truncate">{{ recentMeta(r) }}</div>
          </div>
          <StatusPill :status="r.status" small class="flex-none" />
        </button>
      </div>
    </template>

    <!-- ======================= MANUAL REQUEST MODAL ======================= -->
    <teleport to="body">
      <transition name="sheet-fade">
        <div v-if="showManual" class="fixed inset-0 z-50 flex items-end lg:items-center justify-center p-0 lg:p-4">
          <div class="absolute inset-0 bg-slate-950/70 backdrop-blur-[2px]" @click="showManual = false"></div>
          <div class="relative w-full lg:max-w-md bg-slate-900 border-t lg:border border-slate-700 rounded-t-2xl lg:rounded-2xl p-5 shadow-sheet">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-bold">Manual request</h2>
              <button class="text-slate-500 hover:text-slate-300" @click="showManual = false" aria-label="Close">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18" /><line x1="18" y1="6" x2="6" y2="18" /></svg>
              </button>
            </div>
            <div class="flex flex-col gap-3">
              <div>
                <label class="label">Title</label>
                <input v-model="manual.title" class="input" placeholder="Title" />
              </div>
              <div>
                <label class="label">Type</label>
                <select v-model="manual.media_type" class="input">
                  <option v-for="t in visibleTypeCards" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>
              <div>
                <label class="label">Details <span class="text-slate-500 font-normal">(optional)</span></label>
                <textarea v-model="manual.description" rows="3" class="input" placeholder="Author, edition, year, anything that helps find it"></textarea>
              </div>
              <button class="btn-primary w-full" :disabled="manualSubmitting || !manual.title.trim()" @click="submitManual">
                {{ manualSubmitting ? 'Sending…' : 'Send request' }}
              </button>
            </div>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRequestsStore } from '../stores/requests'
import { useMetadataStore } from '../stores/metadata'
import { useUiStore } from '../stores/ui'
import { useAuthStore } from '../stores/auth'
import { TYPE_CARDS, mediaTypeLabel, formatRelative } from '../utils/requestUtils'
import MediaIcon from '../components/ui/MediaIcon.vue'
import MediaThumb from '../components/ui/MediaThumb.vue'
import StatusPill from '../components/ui/StatusPill.vue'
import SkeletonRow from '../components/ui/SkeletonRow.vue'
import EmptyState from '../components/ui/EmptyState.vue'

const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

export default {
  name: 'Search',
  components: { MediaIcon, MediaThumb, StatusPill, SkeletonRow, EmptyState },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const requestsStore = useRequestsStore()
    const metadataStore = useMetadataStore()
    const ui = useUiStore()
    const authStore = useAuthStore()

    // Admins receive ALL requests from /requests/; the personal "your requests"
    // sections must narrow to the signed-in user.
    const mine = computed(() => requestsStore.requests.filter((r) => r.user_id === authStore.user?.id))

    // Per-user media-type access. null => unrestricted (admins, or no list set).
    const canRequest = computed(() => authStore.canRequest)
    const allowedTypes = computed(() => {
      const a = authStore.user?.allowed_media_types
      if (authStore.isAdmin || !a || !a.length) return null
      return a
    })
    const visibleTypeCards = computed(() =>
      allowedTypes.value ? TYPE_CARDS.filter((t) => allowedTypes.value.includes(t.value)) : TYPE_CARDS
    )
    const defaultType = computed(() => {
      if (!allowedTypes.value) return 'book'
      return allowedTypes.value.includes('book') ? 'book' : (visibleTypeCards.value[0]?.value || 'book')
    })

    const query = ref('')
    const typeScope = ref('')
    const hasSearched = ref(false)
    const lastQuery = ref('')
    const idleInput = ref(null)
    const resultInput = ref(null)
    const pendingIds = ref(new Set())     // in-flight request creations
    const requestedKeys = ref(new Set())  // optimistically requested this session

    const results = computed(() => metadataStore.searchResults)
    const searching = computed(() => metadataStore.isLoading)
    const error = computed(() => metadataStore.error)
    const scopeLabel = computed(() => (typeScope.value ? mediaTypeLabel(typeScope.value) : 'All'))
    const source = computed(() => (results.value[0]?.provider ? String(results.value[0].provider).toUpperCase() : ''))

    const recent = computed(() =>
      mine.value.slice().sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5)
    )
    const counts = computed(() => {
      const r = mine.value
      return {
        pending: r.filter((x) => x.status === 'PENDING').length,
        approved: r.filter((x) => x.status === 'APPROVED').length,
        ready: r.filter((x) => x.status === 'FULFILLED').length,
      }
    })

    const resultKey = (r) => `${r.media_type || typeScope.value}:${r.id ?? r.external_id ?? r.title}`
    const isAvailable = (r) => r.availability === 'available'
    const isRequested = (r) => r.availability === 'requested' || requestedKeys.value.has(resultKey(r))
    const resultMeta = (r) => [r.author, r.year].filter(Boolean).join(' · ')
    const recentMeta = (r) => {
      const who = r.author || mediaTypeLabel(r.media_type)
      return [who, formatRelative(r.created_at)].filter(Boolean).join(' · ')
    }

    const runSearch = async (t) => {
      if (t !== undefined) typeScope.value = t
      if (!query.value.trim()) return
      // Clamp an out-of-policy scope (e.g. a shared ?type= link) to an allowed type.
      if (allowedTypes.value && typeScope.value && !allowedTypes.value.includes(typeScope.value)) {
        typeScope.value = ''
      }
      hasSearched.value = true
      lastQuery.value = query.value.trim()
      // keep the URL shareable / back-friendly
      router.replace({ query: { q: lastQuery.value, ...(typeScope.value ? { type: typeScope.value } : {}) } })
      await metadataStore.searchMetadata(lastQuery.value, typeScope.value || defaultType.value)
      await nextTick()
      resultInput.value?.focus?.()
    }

    const pickType = (t) => {
      typeScope.value = t
      if (query.value.trim()) runSearch(t)
      else nextTick(() => idleInput.value?.focus?.())
    }

    const backToIdle = () => {
      hasSearched.value = false
      metadataStore.clearResults()
      router.replace({ query: {} })
      nextTick(() => idleInput.value?.focus?.())
    }

    const focusIdle = () => nextTick(() => idleInput.value?.focus?.())

    const requestItem = async (r) => {
      const key = resultKey(r)
      pendingIds.value = new Set(pendingIds.value).add(key)
      const res = await requestsStore.createRequest({
        title: r.title,
        description: r.description || null,
        media_type: r.media_type || typeScope.value || 'book',
        external_id: r.id ?? r.external_id ?? null,
        provider: r.provider || null,
        cover_url: r.cover_url || null,
        author: r.author || null,
        year: r.year || null,
      })
      const next = new Set(pendingIds.value); next.delete(key); pendingIds.value = next
      if (res.success) {
        requestedKeys.value.add(key)
        requestedKeys.value = new Set(requestedKeys.value) // trigger reactivity
        const newId = res.request?.id
        const autoApproved = res.request?.status && res.request.status !== 'PENDING'
        const label = autoApproved
          ? `Requested <strong>${escapeHtml(r.title)}</strong> — auto-approved`
          : `Requested <strong>${escapeHtml(r.title)}</strong>`
        ui.toast(label, {
          actionLabel: 'Undo',
          onAction: async () => {
            if (newId) await requestsStore.deleteRequest(newId)
            const s = new Set(requestedKeys.value); s.delete(key); requestedKeys.value = s
          },
        })
      } else {
        ui.toast(res.error || `Couldn't request ${r.title}`, { type: 'error' })
      }
    }

    // Manual request modal
    const showManual = ref(false)
    const manual = reactive({ title: '', media_type: 'book', description: '' })
    const manualSubmitting = ref(false)
    const openManual = () => {
      manual.title = lastQuery.value || query.value
      manual.media_type = typeScope.value || defaultType.value
      manual.description = ''
      showManual.value = true
    }
    const submitManual = async () => {
      manualSubmitting.value = true
      const res = await requestsStore.createRequest({
        title: manual.title.trim(),
        media_type: manual.media_type,
        description: manual.description.trim() || null,
      })
      manualSubmitting.value = false
      if (res.success) {
        showManual.value = false
        ui.toast(`Requested <strong>${escapeHtml(manual.title.trim())}</strong>`)
      } else {
        ui.toast(res.error || 'Could not send the request', { type: 'error' })
      }
    }

    onMounted(async () => {
      requestsStore.fetchRequests()
      if (route.query.q) {
        query.value = String(route.query.q)
        if (route.query.type) typeScope.value = String(route.query.type)
        runSearch()
      } else {
        focusIdle()
      }
    })

    return {
      TYPE_CARDS, visibleTypeCards, canRequest, query, typeScope, hasSearched, lastQuery, idleInput, resultInput,
      results, searching, error, scopeLabel, source, recent, counts, pendingIds,
      resultKey, isAvailable, isRequested, resultMeta, recentMeta,
      runSearch, pickType, backToIdle, focusIdle, requestItem,
      requestsStore, ui,
      showManual, manual, manualSubmitting, openManual, submitManual,
    }
  },
}
</script>

<style scoped>
.sheet-fade-enter-active,
.sheet-fade-leave-active { transition: opacity 0.2s ease; }
.sheet-fade-enter-from,
.sheet-fade-leave-to { opacity: 0; }
</style>
