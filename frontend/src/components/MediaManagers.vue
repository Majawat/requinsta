<template>
  <div class="space-y-6">
    <div class="border-b border-gray-700 pb-4">
      <h2 class="text-xl font-bold text-white">Media Managers</h2>
      <p class="text-gray-400 mt-1">
        Connect Readarr/Radarr/etc. instances. Approved requests for a matching
        media type can be pushed here automatically. With none configured,
        requests still work as a manual approval queue.
      </p>
    </div>

    <!-- Existing instances -->
    <div class="space-y-3">
      <div
        v-for="inst in instances"
        :key="inst.id"
        class="bg-gray-800 border border-gray-700 p-4 rounded-lg"
      >
        <div class="flex justify-between items-start">
          <div>
            <h3 class="font-medium text-white">
              {{ inst.name }}
              <span class="text-xs text-gray-400">({{ inst.service }})</span>
              <span v-if="!inst.enabled" class="ml-2 text-xs text-yellow-400">disabled</span>
            </h3>
            <p class="text-sm text-gray-400">{{ inst.base_url }}</p>
            <div class="mt-2 flex flex-wrap gap-1">
              <span
                v-for="mt in inst.media_types"
                :key="mt"
                class="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-blue-900 text-blue-200"
              >{{ mt }}</span>
            </div>
          </div>
          <div class="flex gap-2">
            <button @click="testInstance(inst)" class="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-500">Test</button>
            <button @click="beginConfigure(inst)" class="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">Configure</button>
            <button @click="deleteInstance(inst)" class="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700">Delete</button>
          </div>
        </div>

        <p v-if="testResults[inst.id]" :class="['mt-2 text-sm', testResults[inst.id].ok ? 'text-green-400' : 'text-red-400']">
          {{ testResults[inst.id].message }}
        </p>

        <!-- Configure: root folder + profiles pulled live from the instance -->
        <div v-if="configuringId === inst.id" class="mt-4 border-t border-gray-700 pt-4 space-y-3">
          <p v-if="optionsError" class="text-sm text-red-400">{{ optionsError }}</p>
          <template v-else>
            <div>
              <label class="block text-sm text-gray-300">Root Folder</label>
              <select v-model="cfg.root_folder_path" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white">
                <option :value="null">— select —</option>
                <option v-for="r in options.root_folders" :key="r.id" :value="r.path">{{ r.path }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-300">Quality Profile</label>
              <select v-model="cfg.quality_profile_id" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white">
                <option :value="null">— select —</option>
                <option v-for="p in options.quality_profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div v-if="options.metadata_profiles.length">
              <label class="block text-sm text-gray-300">Metadata Profile</label>
              <select v-model="cfg.metadata_profile_id" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white">
                <option :value="null">— select —</option>
                <option v-for="p in options.metadata_profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </div>
            <div class="flex gap-2 justify-end">
              <button @click="configuringId = null" class="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-500">Cancel</button>
              <button @click="saveConfigure(inst)" class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">Save</button>
            </div>
          </template>
        </div>
      </div>

      <div v-if="instances.length === 0" class="text-center text-gray-400 py-6">
        No media managers configured yet.
      </div>
    </div>

    <!-- Add new instance -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h3 class="text-lg font-medium text-white mb-4">Add Media Manager</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-300">Service</label>
          <select v-model="form.service" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white">
            <option v-for="s in services" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm text-gray-300">Name</label>
          <input v-model="form.name" placeholder="e.g. Readarr - Audiobooks" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        </div>
        <div>
          <label class="block text-sm text-gray-300">Base URL</label>
          <input v-model="form.base_url" placeholder="http://192.168.1.10:8787" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        </div>
        <div>
          <label class="block text-sm text-gray-300">API Key</label>
          <input v-model="form.api_key" type="password" placeholder="Instance API key" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        </div>
        <div>
          <label class="block text-sm text-gray-300 mb-1">Media Types</label>
          <div class="flex flex-wrap gap-3">
            <label v-for="mt in MEDIA_TYPES" :key="mt.value" class="inline-flex items-center text-sm text-gray-300">
              <input type="checkbox" :value="mt.value" v-model="form.media_types" class="mr-1" />
              {{ mt.label }}
            </label>
          </div>
        </div>
        <div class="flex justify-end">
          <button @click="createInstance" :disabled="!canCreate || saving" class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md">
            {{ saving ? 'Adding...' : 'Add Manager' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="message" class="p-4 rounded-lg" :class="messageOk ? 'bg-green-900 text-green-100' : 'bg-red-900 text-red-100'">
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
  { value: 'other', label: 'Other' },
]

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
    const cfg = reactive({ root_folder_path: null, quality_profile_id: null, metadata_profile_id: null })

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
    }
  },
}
</script>
