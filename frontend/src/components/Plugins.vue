<template>
  <div class="space-y-5">
    <div>
      <h2 class="text-base font-semibold">Plugins</h2>
      <p class="text-sm text-slate-400 mt-0.5">
        Installed connectors. Built-ins ship with Requinsta; drop a <code class="text-slate-300 font-mono text-xs">.py</code>
        file into the mounted <code class="text-slate-300 font-mono text-xs">/plugins</code> folder to add your own.
      </p>
    </div>

    <!-- Search source per media type -->
    <div class="card p-5" v-if="Object.keys(selection.options).length">
      <h3 class="text-base font-semibold mb-1">Search source per media type</h3>
      <p class="text-sm text-slate-400 mb-3">
        By default each type searches its media manager directly — so results are
        exactly what can be added, with accurate availability. Optionally override
        with a standalone metadata provider.
      </p>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div v-for="(opts, mt) in selection.options" :key="mt">
          <label class="label capitalize">{{ mt.replace('_', ' ') }}</label>
          <select v-model="selection.active[mt]" @change="saveSelection" class="input">
            <option value="">Media manager (default)</option>
            <option v-for="o in opts" :key="o.id" :value="o.id">{{ o.label }}</option>
          </select>
        </div>
      </div>
    </div>

    <div v-for="group in groups" :key="group.type" v-show="group.items.length">
      <h3 class="eyebrow mb-2.5">{{ group.label }}</h3>
      <div class="space-y-3">
        <div v-for="p in group.items" :key="p.id" class="card p-4">
          <div class="flex justify-between items-start gap-3">
            <div class="min-w-0">
              <h4 class="font-semibold text-slate-100">
                {{ p.display_name }} <span class="text-xs font-normal text-slate-500">v{{ p.version }}</span>
              </h4>
              <p v-if="p.media_types" class="mt-1.5 flex flex-wrap gap-1">
                <span v-for="mt in p.media_types" :key="mt" class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-medium bg-slate-800 text-slate-300">{{ mt }}</span>
              </p>
            </div>
            <div class="flex items-center gap-2 flex-none">
              <span class="pill" :class="p.configured ? 'bg-emerald-400/15 text-emerald-300 ring-1 ring-emerald-400/25' : 'bg-slate-700/40 text-slate-300 ring-1 ring-slate-600/40'">
                {{ p.configured ? 'Configured' : 'Not configured' }}
              </span>
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-mono uppercase" :class="p.source === 'builtin' ? 'bg-slate-800 text-slate-400' : 'bg-indigo-500/15 text-indigo-300'">{{ p.source }}</span>
              <button
                v-if="p.config_scope === 'global'"
                @click="openId === p.id ? closeConfig() : openConfig(p)"
                class="btn-secondary btn-sm"
              >{{ openId === p.id ? 'Close' : 'Configure' }}</button>
            </div>
          </div>

          <p v-if="p.config_scope === 'instance'" class="mt-2 text-xs text-slate-400">
            Managed under the <span class="text-slate-300">Media Managers</span> tab
            <template v-if="p.instance_count"> — {{ p.instance_count }} instance{{ p.instance_count === 1 ? '' : 's' }}</template>.
          </p>
          <p v-else-if="p.config_scope === 'none'" class="mt-2 text-xs text-slate-400">No configuration needed.</p>

          <!-- Schema-driven config form -->
          <div v-if="openId === p.id && cfg" class="mt-4 border-t border-slate-800 pt-4 space-y-3">
            <div v-for="f in cfg.fields" :key="f.key">
              <label class="label">
                {{ f.label }} <span v-if="f.required" class="text-rose-400">*</span>
              </label>

              <input v-if="['string'].includes(f.type)" v-model="form[f.key]" type="text" class="input" />
              <input v-else-if="f.type === 'number'" v-model="form[f.key]" type="number" class="input" />
              <input
                v-else-if="f.type === 'password'"
                v-model="form[f.key]" type="password"
                :placeholder="f.is_set ? '•••••• (unchanged)' : ''"
                class="input" />

              <label v-else-if="f.type === 'boolean'" class="inline-flex items-center gap-2 text-sm text-slate-300">
                <input type="checkbox" v-model="form[f.key]" class="accent-indigo-600 w-4 h-4" /> Enabled
              </label>

              <select v-else-if="f.type === 'select'" v-model="form[f.key]" class="input">
                <option v-for="o in (f.options || [])" :key="o" :value="o">{{ o }}</option>
              </select>

              <div v-else-if="f.type === 'multiselect'" class="flex flex-wrap gap-3">
                <label v-for="o in (f.options || [])" :key="o" class="inline-flex items-center gap-1.5 text-sm text-slate-300">
                  <input type="checkbox" :value="o" v-model="form[f.key]" class="accent-indigo-600 w-4 h-4" /> {{ o }}
                </label>
              </div>

              <input v-else v-model="form[f.key]" type="text" class="input" />

              <p v-if="f.help" class="mt-1 text-xs text-slate-500">{{ f.help }}</p>
            </div>

            <p v-if="testResult" :class="['text-sm', testResult.ok ? 'text-emerald-300' : 'text-rose-300']">{{ testResult.message }}</p>

            <div class="flex justify-end gap-2">
              <button v-if="cfg.testable" @click="testPlugin(p)" :disabled="testing" class="btn-secondary btn-sm">
                {{ testing ? 'Testing…' : 'Test' }}
              </button>
              <button @click="saveConfig(p)" :disabled="saving" class="btn-primary btn-sm">
                {{ saving ? 'Saving…' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="message" class="p-4 rounded-lg text-sm" :class="messageOk ? 'bg-emerald-500/10 text-emerald-200 border border-emerald-400/30' : 'bg-rose-500/10 text-rose-200 border border-rose-400/30'">{{ message }}</div>
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
    const selection = reactive({ options: {}, active: {} })

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

    const loadSelection = async () => {
      try {
        const { data } = await axios.get(`${API_URL}/plugins/metadata-selection`)
        selection.options = data.options
        const active = { ...data.active }
        for (const mt of Object.keys(data.options)) if (!(mt in active)) active[mt] = ''
        selection.active = active
      } catch (e) { /* non-fatal */ }
    }

    const saveSelection = async () => {
      try {
        await axios.put(`${API_URL}/plugins/metadata-selection`, { active: selection.active })
        flash('Search providers updated')
      } catch (e) { flash('Failed to update providers', false) }
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

    onMounted(() => { load(); loadSelection() })
    return { groups, message, messageOk, openId, cfg, form, saving, testing, testResult,
      selection, saveSelection, openConfig, closeConfig, saveConfig, testPlugin }
  },
}
</script>
