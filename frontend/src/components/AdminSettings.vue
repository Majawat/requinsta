<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="border-b border-gray-700 pb-4">
      <h2 class="text-xl font-bold text-white">System Settings</h2>
      <p class="text-gray-400 mt-1">Configure API keys and system settings</p>
    </div>

    <!-- Settings form -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h3 class="text-lg font-medium text-white mb-4">API Configuration</h3>
      
      <div class="space-y-4">
        <!-- TMDB API Key -->
        <div>
          <label for="tmdb-key" class="block text-sm font-medium text-gray-300">TMDB API Key</label>
          <div class="mt-1 flex">
            <input
              v-model="tmdbApiKey"
              :type="showTmdbKey ? 'text' : 'password'"
              id="tmdb-key"
              placeholder="Enter TMDB API key for movies/TV shows"
              class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-l-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              @click="showTmdbKey = !showTmdbKey"
              class="px-3 py-2 bg-gray-600 border border-gray-600 border-l-0 rounded-r-md text-gray-300 hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {{ showTmdbKey ? 'Hide' : 'Show' }}
            </button>
          </div>
          <p class="mt-1 text-xs text-gray-400">
            Get your API key from <a href="https://www.themoviedb.org/settings/api" target="_blank" class="text-blue-400 hover:text-blue-300">TMDB API Settings</a>
          </p>
        </div>

        <!-- Save button -->
        <div class="flex justify-end">
          <button
            @click="saveSettings"
            :disabled="saving"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
          >
            {{ saving ? 'Saving...' : 'Save Settings' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Current Settings -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h3 class="text-lg font-medium text-white mb-4">Current Settings</h3>
      
      <div class="space-y-3">
        <div v-for="setting in settings" :key="setting.key" class="flex justify-between items-center p-3 bg-gray-700 rounded">
          <div>
            <h4 class="font-medium text-white">{{ setting.key }}</h4>
            <p class="text-sm text-gray-400">{{ setting.description || 'No description' }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-300">{{ setting.value }}</span>
            <button
              @click="deleteSetting(setting.key)"
              class="text-red-400 hover:text-red-300 p-1"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <div v-if="settings.length === 0" class="text-center text-gray-400 py-8">
          No settings configured yet.
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div v-if="message" class="p-4 rounded-lg" :class="messageType === 'success' ? 'bg-green-900 text-green-100' : 'bg-red-900 text-red-100'">
      {{ message }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

export default {
  name: 'AdminSettings',
  setup() {
    const authStore = useAuthStore()
    const settings = ref([])
    const tmdbApiKey = ref('')
    const showTmdbKey = ref(false)
    const saving = ref(false)
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('')

    const API_URL = `http://${window.location.hostname}:8000/api/v1`

    const showMessage = (text, type = 'success') => {
      message.value = text
      messageType.value = type
      setTimeout(() => {
        message.value = ''
      }, 3000)
    }

    const fetchSettings = async () => {
      try {
        loading.value = true
        const response = await axios.get(`${API_URL}/settings/`)
        settings.value = response.data
        
        // Pre-fill TMDB key if it exists
        const tmdbSetting = settings.value.find(s => s.key === 'TMDB_API_KEY')
        if (tmdbSetting) {
          tmdbApiKey.value = tmdbSetting.value === '***' ? '' : tmdbSetting.value
        }
      } catch (error) {
        console.error('Error fetching settings:', error)
        showMessage('Failed to load settings', 'error')
      } finally {
        loading.value = false
      }
    }

    const saveSettings = async () => {
      try {
        saving.value = true
        
        if (tmdbApiKey.value.trim()) {
          // Check if TMDB setting exists
          const existingSetting = settings.value.find(s => s.key === 'TMDB_API_KEY')
          
          if (existingSetting) {
            // Update existing setting
            await axios.put(`${API_URL}/settings/TMDB_API_KEY`, {
              value: tmdbApiKey.value.trim(),
              description: 'TMDB API key for movie and TV show metadata'
            })
          } else {
            // Create new setting
            await axios.post(`${API_URL}/settings/`, {
              key: 'TMDB_API_KEY',
              value: tmdbApiKey.value.trim(),
              description: 'TMDB API key for movie and TV show metadata',
              is_secret: true
            })
          }
        }
        
        showMessage('Settings saved successfully!')
        await fetchSettings()
      } catch (error) {
        console.error('Error saving settings:', error)
        showMessage('Failed to save settings', 'error')
      } finally {
        saving.value = false
      }
    }

    const deleteSetting = async (key) => {
      if (!confirm(`Are you sure you want to delete the setting "${key}"?`)) {
        return
      }
      
      try {
        await axios.delete(`${API_URL}/settings/${key}`)
        showMessage('Setting deleted successfully!')
        await fetchSettings()
      } catch (error) {
        console.error('Error deleting setting:', error)
        showMessage('Failed to delete setting', 'error')
      }
    }

    onMounted(() => {
      fetchSettings()
    })

    return {
      settings,
      tmdbApiKey,
      showTmdbKey,
      saving,
      loading,
      message,
      messageType,
      saveSettings,
      deleteSetting
    }
  }
}
</script>