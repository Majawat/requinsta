<template>
  <div class="space-y-6">
    <div class="border-b border-gray-700 pb-4">
      <h2 class="text-xl font-bold text-white">Plugins</h2>
      <p class="text-gray-400 mt-1">
        Installed connectors. Built-ins ship with Requinsta; drop a <code class="text-gray-300">.py</code>
        file into the mounted <code class="text-gray-300">/plugins</code> folder to add your own.
      </p>
    </div>

    <div v-for="group in groups" :key="group.type" v-show="group.items.length">
      <h3 class="text-lg font-medium text-white mb-3">{{ group.label }}</h3>
      <div class="space-y-3">
        <div
          v-for="p in group.items"
          :key="p.id"
          class="bg-gray-800 border border-gray-700 p-4 rounded-lg"
        >
          <div class="flex justify-between items-start">
            <div>
              <h4 class="font-medium text-white">
                {{ p.display_name }} <span class="text-xs text-gray-500">v{{ p.version }}</span>
              </h4>
              <p v-if="p.media_types" class="mt-1 flex flex-wrap gap-1">
                <span v-for="mt in p.media_types" :key="mt" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-blue-900 text-blue-200">{{ mt }}</span>
              </p>
            </div>
            <div class="flex items-center gap-2">
              <span :class="['px-2 py-0.5 rounded-full text-xs font-medium', p.configured ? 'bg-green-900 text-green-200' : 'bg-gray-600 text-gray-300']">
                {{ p.configured ? 'Configured' : 'Not configured' }}
              </span>
              <span :class="['px-2 py-0.5 rounded-full text-xs', p.source === 'builtin' ? 'bg-gray-700 text-gray-300' : 'bg-purple-900 text-purple-200']">{{ p.source }}</span>
              <button
                v-if="p.config_scope === 'global'"
                @click="openId === p.id ? closeConfig() : openConfig(p)"
                class="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
              >{{ openId === p.id ? 'Close' : 'Configure' }}</button>
            </div>
          </div>

          <p v-if="p.config_scope === 'instance'" class="mt-2 text-xs text-gray-400">
            Managed under the <span class="text-gray-300">Media Managers</span> tab
            <template v-if="p.instance_count"> — {{ p.instance_count }} instance{{ p.instance_count === 1 ? '' : 's' }}</template>.
          </p>
          <p v-else-if="p.config_scope === 'none'" class="mt-2 text-xs text-gray-400">No configuration needed.</p>

          <!-- Schema-driven config form -->
          <div v-if="openId === p.id && cfg" class="mt-4 border-t border-gray-700 pt-4 space-y-3">
            <div v-for="f in cfg.fields" :key="f.key">
              <label class="block text-sm text-gray-300">
                {{ f.label }} <span v-if="f.required" class="text-red-400">*</span>
              </label>

              <input
                v-if="['string'].includes(f.type)"
                v-model="form[f.key]" type="text"
                class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white" />

              <input
                v-else-if="f.type === 'number'"
                v-model="form[f.key]" type="number"
                class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white" />

              <input
                v-else-if="f.type === 'password'"
                v-model="form[f.key]" type="password"
                :placeholder="f.is_set ? '•••••• (unchanged)' : ''"
                class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />

              <label v-else-if="f.type === 'boolean'" class="mt-1 inline-flex items-center text-sm text-gray-300">
                <input type="checkbox" v-model="form[f.key]" class="mr-2" /> Enabled
              </label>

              <select
                v-else-if="f.type === 'select'"
                v-model="form[f.key]"
                class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white">
                <option v-for="o in (f.options || [])" :key="o" :value="o">{{ o }}</option>
              </select>

              <div v-else-if="f.type === 'multiselect'" class="mt-1 flex flex-wrap gap-3">
                <label v-for="o in (f.options || [])" :key="o" class="inline-flex items-center text-sm text-gray-300">
                  <input type="checkbox" :value="o" v-model="form[f.key]" class="mr-1" /> {{ o }}
                </label>
              </div>

              <input
                v-else
                v-model="form[f.key]" type="text"
                class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white" />

              <p v-if="f.help" class="mt-1 text-xs text-gray-400">{{ f.help }}</p>
            </div>

            <p v-if="testResult" :class="['text-sm', testResult.ok ? 'text-green-400' : 'text-red-400']">{{ testResult.message }}</p>

            <div class="flex justify-end gap-2">
              <button
                v-if="cfg.testable"
                @click="testPlugin(p)" :disabled="testing"
                class="px-3 py-1 text-sm bg-gray-600 text-white rounded hover:bg-gray-500 disabled:opacity-50"
              >{{ testing ? 'Testing…' : 'Test' }}</button>
              <button
                @click="saveConfig(p)" :disabled="saving"
                class="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >{{ saving ? 'Saving…' : 'Save' }}</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="message" class="p-4 rounded-lg" :class="messageOk ? 'bg-green-900 text-green-100' : 'bg-red-900 text-red-100'">{{ message }}</div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import axios from 'axios'
import { API_URL } from '../utils/api'

const TYPE_LABELS = {
  metadata_provider: 'Metadata Providers',
  media_manager: 'Media Managers',
  library: 'Libraries',
  notifier: 'Notifiers',
}

export default {
  name: 'Plugins',
  setup() {
    const plugins = ref([])
    const message = ref('')
    const messageOk = ref(true)
    const openId = ref(null)
    const cfg = ref(null)
    const form = reactive({})
    const saving = ref(false)
    const testing = ref(false)
    const testResult = ref(null)

    const groups = computed(() =>
      Object.entries(TYPE_LABELS).map(([type, label]) => ({
        type, label,
        items: plugins.value.filter(p => p.plugin_type === type),
      }))
    )

    const flash = (text, ok = true) => {
      message.value = text; messageOk.value = ok
      setTimeout(() => { message.value = '' }, 3000)
    }

    const load = async () => {
      try {
        const { data } = await axios.get(`${API_URL}/plugins/`)
        plugins.value = data
      } catch (e) {
        flash('Failed to load plugins', false)
      }
    }

    const openConfig = async (p) => {
      testResult.value = null
      try {
        const { data } = await axios.get(`${API_URL}/plugins/${p.plugin_type}/${p.key}/config`)
        cfg.value = data
        // seed the form from current values
        Object.keys(form).forEach(k => delete form[k])
        for (const f of data.fields) {
          if (f.type === 'boolean') form[f.key] = f.value === true || f.value === 'true'
          else if (f.type === 'multiselect') form[f.key] = Array.isArray(f.value) ? f.value : []
          else form[f.key] = f.secret ? '' : (f.value ?? '')
        }
        openId.value = p.id
      } catch (e) {
        flash(e.response?.data?.detail || 'Could not load config', false)
      }
    }

    const closeConfig = () => { openId.value = null; cfg.value = null; testResult.value = null }

    const saveConfig = async (p) => {
      saving.value = true
      try {
        await axios.put(`${API_URL}/plugins/${p.plugin_type}/${p.key}/config`, { values: { ...form } })
        await load()
        flash('Saved')
      } catch (e) {
        flash(e.response?.data?.detail || 'Failed to save', false)
      } finally {
        saving.value = false
      }
    }

    const testPlugin = async (p) => {
      testing.value = true
      testResult.value = null
      try {
        const { data } = await axios.post(`${API_URL}/plugins/${p.plugin_type}/${p.key}/test`)
        testResult.value = data
      } catch (e) {
        testResult.value = { ok: false, message: e.response?.data?.detail || 'Test failed' }
      } finally {
        testing.value = false
      }
    }

    onMounted(load)
    return { groups, message, messageOk, openId, cfg, form, saving, testing, testResult, openConfig, closeConfig, saveConfig, testPlugin }
  },
}
</script>
