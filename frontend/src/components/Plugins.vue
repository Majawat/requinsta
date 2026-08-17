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
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="p in group.items"
          :key="p.id"
          class="bg-gray-800 border border-gray-700 p-4 rounded-lg"
        >
          <div class="flex justify-between items-start">
            <div>
              <h4 class="font-medium text-white">
                {{ p.display_name }}
                <span class="text-xs text-gray-500">v{{ p.version }}</span>
              </h4>
              <p v-if="p.media_types" class="mt-1 flex flex-wrap gap-1">
                <span v-for="mt in p.media_types" :key="mt" class="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-blue-900 text-blue-200">{{ mt }}</span>
              </p>
            </div>
            <div class="flex flex-col items-end gap-1">
              <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium', p.configured ? 'bg-green-900 text-green-200' : 'bg-gray-600 text-gray-300']">
                {{ p.configured ? 'Configured' : 'Not configured' }}
              </span>
              <span :class="['inline-flex items-center px-2 py-0.5 rounded-full text-xs', p.source === 'builtin' ? 'bg-gray-700 text-gray-300' : 'bg-purple-900 text-purple-200']">
                {{ p.source }}
              </span>
            </div>
          </div>
          <p v-if="p.config_scope === 'instance' && p.instance_count" class="mt-2 text-xs text-gray-400">
            {{ p.instance_count }} instance{{ p.instance_count === 1 ? '' : 's' }} configured
          </p>
        </div>
      </div>
    </div>

    <div v-if="message" class="p-4 rounded-lg bg-red-900 text-red-100">{{ message }}</div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
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

    const groups = computed(() =>
      Object.entries(TYPE_LABELS).map(([type, label]) => ({
        type,
        label,
        items: plugins.value.filter(p => p.plugin_type === type),
      }))
    )

    const load = async () => {
      try {
        const { data } = await axios.get(`${API_URL}/plugins/`)
        plugins.value = data
      } catch (e) {
        message.value = 'Failed to load plugins'
      }
    }

    onMounted(load)
    return { groups, message }
  },
}
</script>
