<template>
  <div class="space-y-5">
    <div>
      <h2 class="text-base font-semibold">Media managers</h2>
      <p class="text-sm text-slate-400 mt-0.5">
        Connect Readarr/Radarr/etc. instances. Approved requests for a matching
        media type can be pushed here automatically. With none configured,
        requests still work as a manual approval queue.
      </p>
    </div>

    <!-- Existing instances -->
    <div class="space-y-3">
      <div v-for="inst in instances" :key="inst.id" class="card p-4">
        <div class="flex justify-between items-start gap-3">
          <div class="min-w-0">
            <h3 class="font-semibold text-slate-100">
              {{ inst.name }}
              <span class="text-xs font-normal text-slate-400">({{ inst.service }})</span>
              <span v-if="!inst.enabled" class="ml-2 text-xs text-amber-300">disabled</span>
            </h3>
            <p class="text-sm text-slate-400 truncate">{{ inst.base_url }}</p>
            <p v-if="scopeApplies(inst.service)" class="text-xs text-slate-500 mt-1">
              Monitors: <span class="text-slate-300">{{ scopeLabel(inst) }}</span>
            </p>
            <div class="mt-2 flex flex-wrap gap-1">
              <span
                v-for="mt in inst.media_types"
                :key="mt"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-300"
              >{{ mt }}</span>
            </div>
          </div>
          <div class="flex gap-2 flex-none">
            <button @click="testInstance(inst)" class="btn-secondary btn-sm">Test</button>
            <button @click="beginConfigure(inst)" class="btn-primary btn-sm">Configure</button>
            <button @click="deleteInstance(inst)" class="btn-deny btn-sm">Delete</button>
          </div>
        </div>

        <p v-if="testResults[inst.id]" :class="['mt-2 text-sm', testResults[inst.id].ok ? 'text-emerald-300' : 'text-rose-300']">
          {{ testResults[inst.id].message }}
        </p>

        <!-- Configure: root folder + profiles pulled live from the instance -->
        <div v-if="configuringId === inst.id" class="mt-4 border-t border-slate-800 pt-4 space-y-3">
          <p v-if="optionsError" class="text-sm text-rose-300">{{ optionsError }}</p>
          <template v-else>
            <div>
              <label class="label">Root folder</label>
              <select v-model="cfg.root_folder_path" class="input">
                <option :value="null">— select —</option>
                <option v-for="r in options.root_folders" :key="r.id" :value="r.path">{{ r.path }}</option>
              </select>
            </div>
            <div>
              <label class="label">Quality profile</label>
              <select v-model="cfg.quality_profile_id" class="input">
                <option :value="null">— select —</option>
                <option v-for="p in options.quality_profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div v-if="options.metadata_profiles.length">
              <label class="label">Metadata profile</label>
              <select v-model="cfg.metadata_profile_id" class="input">
                <option :value="null">— select —</option>
                <option v-for="p in options.metadata_profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div v-if="scopeApplies(inst.service)">
              <label class="label">Monitor scope</label>
              <select v-model="cfg.monitor_scope" class="input">
                <option value="item">{{ scopeOpts(inst.service).item }}</option>
                <option value="collection">{{ scopeOpts(inst.service).collection }}</option>
              </select>
              <p class="text-xs text-slate-500 mt-1">
                What {{ inst.service }} monitors &amp; searches when a request is approved. "{{ scopeOpts(inst.service).item }}" avoids pulling in the whole {{ inst.service === 'lidarr' ? 'artist' : 'author' }}.
              </p>
            </div>
            <div class="flex gap-2 justify-end">
              <button @click="configuringId = null" class="btn-ghost btn-sm">Cancel</button>
              <button @click="saveConfigure(inst)" class="btn-primary btn-sm">Save</button>
            </div>
          </template>
        </div>
      </div>

      <div v-if="instances.length === 0" class="card p-6 text-center text-slate-400 text-sm">
        No media managers configured yet.
      </div>
    </div>

    <!-- Add new instance -->
    <div class="card p-5">
      <h3 class="text-base font-semibold mb-4">Add media manager</h3>
      <div class="space-y-4">
        <div>
          <label class="label">Service</label>
          <select v-model="form.service" class="input">
            <option v-for="s in services" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div>
          <label class="label">Name</label>
          <input v-model="form.name" placeholder="e.g. Readarr - Audiobooks" class="input" />
        </div>
        <div>
          <label class="label">Base URL</label>
          <input v-model="form.base_url" placeholder="http://192.168.1.10:8787" class="input" />
        </div>
        <div>
          <label class="label">API key</label>
          <input v-model="form.api_key" type="password" placeholder="Instance API key" class="input" />
        </div>
        <div>
          <label class="label">Media types</label>
          <div class="flex flex-wrap gap-3">
            <label v-for="mt in MEDIA_TYPES" :key="mt.value" class="inline-flex items-center gap-1.5 text-sm text-slate-300">
              <input type="checkbox" :value="mt.value" v-model="form.media_types" class="accent-indigo-600 w-4 h-4" />
              {{ mt.label }}
            </label>
          </div>
        </div>
        <div class="flex justify-end">
          <button @click="createInstance" :disabled="!canCreate || saving" class="btn-primary">
            {{ saving ? 'Adding…' : 'Add manager' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="message" class="p-4 rounded-lg text-sm" :class="messageOk ? 'bg-emerald-500/10 text-emerald-200 border border-emerald-400/30' : 'bg-rose-500/10 text-rose-200 border border-rose-400/30'">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { API_URL } from '../utils/api'

const MEDIA_TYPES = [
  { value: 'book', label: 'Book' },
  { value: 'audiobook', label: 'Audiobook' },
  { value: 'movie', label: 'Movie' },
  { value: 'tv_show', label: 'TV Show' },
  { value: 'music', label: 'Music' },
  { value: 'comic', label: 'Comic' },
  { value: 'podcast', label: 'Podcast' },
  { value: 'other', label: 'Other' },
]

// Monitor scope only applies to the arr adapters that add an item under a parent
// (book→author, album→artist). Labels are service-aware.
const SCOPE_LABELS = {
  readarr: { item: 'Just this book', collection: 'Whole author' },
  lidarr: { item: 'Just this album', collection: 'Whole artist' },
  _default: { item: 'Just this item', collection: 'Whole collection' },
}
const scopeApplies = (service) => service === 'readarr' || service === 'lidarr'
const scopeOpts = (service) => SCOPE_LABELS[service] || SCOPE_LABELS._default
const scopeLabel = (inst) => scopeOpts(inst.service)[inst.monitor_scope || 'item']

export default {
  name: 'MediaManagers',
  setup() {
    const instances = ref([])
    const services = ref([])
    const testResults = reactive({})
    const saving = ref(false)
    const message = ref('')
    const messageOk = ref(true)

    const form = reactive({ service: 'readarr', name: '', base_url: '', api_key: '', media_types: [] })

    const configuringId = ref(null)
    const options = reactive({ root_folders: [], quality_profiles: [], metadata_profiles: [] })
    const optionsError = ref('')
    const cfg = reactive({ root_folder_path: null, quality_profile_id: null, metadata_profile_id: null, monitor_scope: 'item' })

    const canCreate = computed(() =>
      form.service && form.name.trim() && form.base_url.trim() && form.media_types.length > 0
    )

    const flash = (text, ok = true) => {
      message.value = text; messageOk.value = ok
      setTimeout(() => { message.value = '' }, 3000)
    }

    const load = async () => {
      try {
        const [inst, svc] = await Promise.all([
          axios.get(`${API_URL}/media-managers/`),
          axios.get(`${API_URL}/media-managers/services`),
        ])
        instances.value = inst.data
        services.value = svc.data
        if (svc.data.length && !svc.data.includes(form.service)) form.service = svc.data[0]
      } catch (e) {
        flash('Failed to load media managers', false)
      }
    }

    const createInstance = async () => {
      saving.value = true
      try {
        await axios.post(`${API_URL}/media-managers/`, { ...form })
        Object.assign(form, { name: '', base_url: '', api_key: '', media_types: [] })
        await load()
        flash('Media manager added')
      } catch (e) {
        flash(e.response?.data?.detail || 'Failed to add', false)
      } finally {
        saving.value = false
      }
    }

    const testInstance = async (inst) => {
      try {
        const { data } = await axios.post(`${API_URL}/media-managers/${inst.id}/test`)
        testResults[inst.id] = data
      } catch (e) {
        testResults[inst.id] = { ok: false, message: 'Test request failed' }
      }
    }

    const beginConfigure = async (inst) => {
      configuringId.value = inst.id
      optionsError.value = ''
      Object.assign(cfg, {
        root_folder_path: inst.root_folder_path,
        quality_profile_id: inst.quality_profile_id,
        metadata_profile_id: inst.metadata_profile_id,
        monitor_scope: inst.monitor_scope || 'item',
      })
      try {
        const { data } = await axios.get(`${API_URL}/media-managers/${inst.id}/options`)
        Object.assign(options, data)
      } catch (e) {
        optionsError.value = 'Could not reach the instance to load folders/profiles. Check URL, API key, then Test.'
      }
    }

    const saveConfigure = async (inst) => {
      try {
        await axios.put(`${API_URL}/media-managers/${inst.id}`, {
          root_folder_path: cfg.root_folder_path,
          quality_profile_id: cfg.quality_profile_id,
          metadata_profile_id: cfg.metadata_profile_id,
          monitor_scope: cfg.monitor_scope,
        })
        configuringId.value = null
        await load()
        flash('Configuration saved')
      } catch (e) {
        flash('Failed to save configuration', false)
      }
    }

    const deleteInstance = async (inst) => {
      if (!confirm(`Delete media manager "${inst.name}"?`)) return
      try {
        await axios.delete(`${API_URL}/media-managers/${inst.id}`)
        await load()
        flash('Media manager deleted')
      } catch (e) {
        flash('Failed to delete', false)
      }
    }

    onMounted(load)

    return {
      MEDIA_TYPES, instances, services, testResults, form, saving, message, messageOk,
      canCreate, createInstance, testInstance, deleteInstance,
      configuringId, options, optionsError, cfg, beginConfigure, saveConfigure,
      scopeApplies, scopeOpts, scopeLabel,
    }
  },
}
</script>
