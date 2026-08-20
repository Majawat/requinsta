<template>
  <div class="space-y-5">
    <div>
      <h2 class="text-base font-semibold">System settings</h2>
      <p class="text-sm text-slate-400 mt-0.5">
        Low-level configuration values. Connect metadata providers, media managers,
        and notifiers under the <span class="text-slate-300">Plugins</span> tab.
      </p>
    </div>

    <div class="card p-5">
      <h3 class="text-base font-semibold mb-3">Stored settings</h3>

      <div class="space-y-2">
        <div v-for="setting in settings" :key="setting.key" class="flex justify-between items-center gap-3 rounded-lg border border-slate-800 bg-slate-800/40 p-3">
          <div class="min-w-0">
            <h4 class="font-semibold text-slate-100 font-mono text-[13px] truncate">{{ setting.key }}</h4>
            <p class="text-sm text-slate-400">{{ setting.description || 'No description' }}</p>
          </div>
          <div class="flex items-center gap-2 flex-none">
            <span class="text-sm text-slate-300 font-mono text-[13px]">{{ setting.value }}</span>
            <button @click="deleteSetting(setting.key)" class="text-slate-500 hover:text-rose-300 p-1" title="Delete">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="settings.length === 0" class="text-center text-slate-400 text-sm py-8">
          No settings stored yet. Configure plugins under the Plugins tab.
        </div>
      </div>
    </div>

    <div v-if="message" class="p-4 rounded-lg text-sm" :class="messageType === 'success' ? 'bg-emerald-500/10 text-emerald-200 border border-emerald-400/30' : 'bg-rose-500/10 text-rose-200 border border-rose-400/30'">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { API_URL } from '../utils/api'

export default {
  name: 'AdminSettings',
  setup() {
    const settings = ref([])
    const message = ref('')
    const messageType = ref('')

    const showMessage = (text, type = 'success') => {
      message.value = text
      messageType.value = type
      setTimeout(() => { message.value = '' }, 3000)
    }

    const fetchSettings = async () => {
      try {
        const response = await axios.get(`${API_URL}/settings/`)
        settings.value = response.data
      } catch (error) {
        showMessage('Failed to load settings', 'error')
      }
    }

    const deleteSetting = async (key) => {
      if (!confirm(`Delete the setting "${key}"?`)) return
      try {
        await axios.delete(`${API_URL}/settings/${key}`)
        settings.value = settings.value.filter(s => s.key !== key)
        showMessage('Setting deleted')
      } catch (error) {
        showMessage('Failed to delete setting', 'error')
      }
    }

    onMounted(fetchSettings)
    return { settings, message, messageType, deleteSetting }
  }
}
</script>
