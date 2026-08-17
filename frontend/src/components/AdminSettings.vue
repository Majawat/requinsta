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

        <!-- Hardcover API Token -->
        <div>
          <label for="hardcover-key" class="block text-sm font-medium text-gray-300">Hardcover API Token</label>
          <div class="mt-1 flex">
            <input
              v-model="hardcoverToken"
              :type="showHardcoverKey ? 'text' : 'password'"
              id="hardcover-key"
              placeholder="Enter Hardcover API token for book metadata"
              class="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-l-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              @click="showHardcoverKey = !showHardcoverKey"
              class="px-3 py-2 bg-gray-600 border border-gray-600 border-l-0 rounded-r-md text-gray-300 hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {{ showHardcoverKey ? 'Hide' : 'Show' }}
            </button>
          </div>
          <p class="mt-1 text-xs text-gray-400">
            Get your token from <a href="https://hardcover.app/account/api" target="_blank" class="text-blue-400 hover:text-blue-300">Hardcover → Account → API</a>
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

    <!-- Email Notifications -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h3 class="text-lg font-medium text-white mb-1">Email Notifications</h3>
      <p class="text-sm text-gray-400 mb-4">SMTP server used to email requesters when their request is available.</p>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-300">SMTP Host</label>
          <input v-model="smtp.host" placeholder="smtp.example.com" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300">Port</label>
          <input v-model="smtp.port" placeholder="587" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300">From Address</label>
          <input v-model="smtp.from" placeholder="requinsta@example.com" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300">Username</label>
          <input v-model="smtp.username" placeholder="(optional)" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-300">Password</label>
          <input v-model="smtp.password" type="password" :placeholder="smtp.passwordSet ? '•••••• (unchanged)' : '(optional)'" class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400" />
        </div>
        <div class="flex items-end">
          <label class="inline-flex items-center text-sm text-gray-300">
            <input type="checkbox" v-model="smtp.useTls" class="mr-2" /> Use STARTTLS
          </label>
        </div>
      </div>

      <div class="flex justify-end gap-2 mt-4">
        <button @click="sendTestEmail" :disabled="testing" class="bg-gray-600 hover:bg-gray-500 disabled:bg-gray-700 text-white px-4 py-2 rounded-md">
          {{ testing ? 'Sending...' : 'Send Test' }}
        </button>
        <button @click="saveSmtp" :disabled="savingSmtp" class="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md">
          {{ savingSmtp ? 'Saving...' : 'Save Email Settings' }}
        </button>
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
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { API_URL } from '../utils/api'

export default {
  name: 'AdminSettings',
  setup() {
    const settings = ref([])
    const tmdbApiKey = ref('')
    const showTmdbKey = ref(false)
    const hardcoverToken = ref('')
    const showHardcoverKey = ref(false)
    const saving = ref(false)
    const loading = ref(false)
    const message = ref('')
    const messageType = ref('')

    const smtp = reactive({
      host: '', port: '', from: '', username: '', password: '',
      useTls: true, passwordSet: false,
    })
    const savingSmtp = ref(false)
    const testing = ref(false)

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

        const tmdbSetting = settings.value.find(s => s.key === 'TMDB_API_KEY')
        if (tmdbSetting) {
          tmdbApiKey.value = tmdbSetting.value === '***' ? '' : tmdbSetting.value
        }
        const hcSetting = settings.value.find(s => s.key === 'HARDCOVER_API_TOKEN')
        if (hcSetting) {
          hardcoverToken.value = hcSetting.value === '***' ? '' : hcSetting.value
        }

        const val = (key) => {
          const s = settings.value.find(x => x.key === key)
          return s ? s.value : ''
        }
        smtp.host = val('SMTP_HOST')
        smtp.port = val('SMTP_PORT')
        smtp.from = val('SMTP_FROM')
        smtp.username = val('SMTP_USERNAME')
        smtp.passwordSet = !!settings.value.find(x => x.key === 'SMTP_PASSWORD')
        const tls = val('SMTP_USE_TLS')
        smtp.useTls = tls === '' ? true : ['1', 'true', 'yes'].includes(String(tls).toLowerCase())
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
          const existingSetting = settings.value.find(s => s.key === 'TMDB_API_KEY')

          if (existingSetting) {
            const { data: updated } = await axios.put(`${API_URL}/settings/TMDB_API_KEY`, {
              value: tmdbApiKey.value.trim(),
              description: 'TMDB API key for movie and TV show metadata'
            })
            const idx = settings.value.findIndex(s => s.key === 'TMDB_API_KEY')
            if (idx !== -1) settings.value[idx] = updated
          } else {
            const { data: created } = await axios.post(`${API_URL}/settings/`, {
              key: 'TMDB_API_KEY',
              value: tmdbApiKey.value.trim(),
              description: 'TMDB API key for movie and TV show metadata',
              is_secret: true
            })
            settings.value.push(created)
          }
        }

        if (hardcoverToken.value.trim()) {
          await upsertSetting(
            'HARDCOVER_API_TOKEN',
            hardcoverToken.value.trim(),
            'Hardcover API token for book metadata',
            true
          )
        }

        await fetchSettings()
        showMessage('Settings saved successfully!')
      } catch (error) {
        console.error('Error saving settings:', error)
        showMessage('Failed to save settings', 'error')
      } finally {
        saving.value = false
      }
    }

    // Upsert a settings-table key (create if new, update if it exists).
    const upsertSetting = async (key, value, description, isSecret = false) => {
      const existing = settings.value.find(s => s.key === key)
      if (existing) {
        await axios.put(`${API_URL}/settings/${key}`, { value, description })
      } else {
        await axios.post(`${API_URL}/settings/`, { key, value, description, is_secret: isSecret })
      }
    }

    const saveSmtp = async () => {
      savingSmtp.value = true
      try {
        await upsertSetting('SMTP_HOST', smtp.host.trim(), 'SMTP server host')
        await upsertSetting('SMTP_PORT', String(smtp.port || '587').trim(), 'SMTP server port')
        await upsertSetting('SMTP_FROM', smtp.from.trim(), 'From address for notifications')
        await upsertSetting('SMTP_USERNAME', smtp.username.trim(), 'SMTP username')
        await upsertSetting('SMTP_USE_TLS', smtp.useTls ? 'true' : 'false', 'Use STARTTLS')
        // Only write the password when the admin entered a new one.
        if (smtp.password.trim()) {
          await upsertSetting('SMTP_PASSWORD', smtp.password.trim(), 'SMTP password', true)
          smtp.password = ''
        }
        await fetchSettings()
        showMessage('Email settings saved!')
      } catch (error) {
        console.error('Error saving SMTP settings:', error)
        showMessage('Failed to save email settings', 'error')
      } finally {
        savingSmtp.value = false
      }
    }

    const sendTestEmail = async () => {
      testing.value = true
      try {
        const { data } = await axios.post(`${API_URL}/notifications/test`, { service: 'email' })
        showMessage(data.ok ? `Test sent: ${data.message}` : `Test failed: ${data.message}`, data.ok ? 'success' : 'error')
      } catch (error) {
        showMessage(error.response?.data?.detail || 'Test email failed', 'error')
      } finally {
        testing.value = false
      }
    }

    const deleteSetting = async (key) => {
      if (!confirm(`Are you sure you want to delete the setting "${key}"?`)) {
        return
      }

      try {
        await axios.delete(`${API_URL}/settings/${key}`)
        settings.value = settings.value.filter(s => s.key !== key)
        showMessage('Setting deleted successfully!')
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
      hardcoverToken,
      showHardcoverKey,
      saving,
      loading,
      message,
      messageType,
      saveSettings,
      deleteSetting,
      smtp,
      savingSmtp,
      testing,
      saveSmtp,
      sendTestEmail,
    }
  }
}
</script>
