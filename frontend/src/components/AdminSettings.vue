<template>
  <div class="space-y-6">
    <div class="border-b border-gray-700 pb-4">
      <h2 class="text-xl font-bold text-white">System Settings</h2>
      <p class="text-gray-400 mt-1">
        Low-level configuration values. Connect metadata providers, media managers,
        and notifiers under the <span class="text-gray-300">Plugins</span> tab.
      </p>
    </div>

    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h3 class="text-lg font-medium text-white mb-4">Stored Settings</h3>

      <div class="space-y-3">
        <div v-for="setting in settings" :key="setting.key" class="flex justify-between items-center p-3 bg-gray-700 rounded">
          <div>
            <h4 class="font-medium text-white">{{ setting.key }}</h4>
            <p class="text-sm text-gray-400">{{ setting.description || 'No description' }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-300">{{ setting.value }}</span>
            <button @click="deleteSetting(setting.key)" class="text-red-400 hover:text-red-300 p-1" title="Delete">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="settings.length === 0" class="text-center text-gray-400 py-8">
          No settings stored yet. Configure plugins under the Plugins tab.
        </div>
      </div>
    </div>

    <div v-if="message" class="p-4 rounded-lg" :class="messageType === 'success' ? 'bg-green-900 text-green-100' : 'bg-red-900 text-red-100'">
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
