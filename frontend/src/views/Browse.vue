<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="border-b border-gray-700 pb-4">
      <h1 class="text-2xl font-bold text-white">Browse & Discover</h1>
      <p class="text-gray-400 mt-1">Search and request new media</p>
    </div>

    <!-- Search form -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Search Media</h2>
      <div class="space-y-4">
        <div>
          <label for="search" class="block text-sm font-medium text-gray-300">Search Query</label>
          <input
            v-model="searchQuery"
            type="text"
            id="search"
            placeholder="Enter title, author, or keyword..."
            class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            @keyup.enter="performSearch"
          />
        </div>
        
        <div>
          <label for="mediaType" class="block text-sm font-medium text-gray-300">Media Type</label>
          <select
            v-model="selectedMediaType"
            id="mediaType"
            class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Types</option>
            <option value="book">Book</option>
            <option value="audiobook">Audiobook</option>
            <option value="movie">Movie</option>
            <option value="tv_show">TV Show</option>
            <option value="music">Music</option>
            <option value="comic">Comic</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div class="flex space-x-4">
          <button
            @click="performSearch"
            :disabled="!searchQuery.trim() || searching"
            class="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors"
          >
            {{ searching ? 'Searching...' : 'Search' }}
          </button>
          <button
            @click="clearSearch"
            class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors"
          >
            Clear
          </button>
        </div>
      </div>
    </div>

    <!-- Search results -->
    <div v-if="searchResults.length > 0" class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Search Results</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="result in searchResults"
          :key="result.id"
          class="border border-gray-600 rounded p-4 bg-gray-700 hover:bg-gray-600 transition-colors"
        >
          <div class="flex flex-col h-full">
            <div class="flex gap-4 flex-1">
              <div v-if="result.cover_url" class="flex-shrink-0">
                <img
                  :src="result.cover_url"
                  :alt="result.title"
                  class="w-16 h-24 object-cover rounded"
                  @error="$event.target.style.display = 'none'"
                />
              </div>
              <div class="flex-1">
                <h3 class="font-medium text-white">{{ result.title }}</h3>
                <p class="text-sm text-gray-300 mt-1">{{ result.author }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ result.year }}</p>
                <p class="text-sm text-gray-300 mt-2 line-clamp-3">{{ result.description }}</p>
                <div class="mt-2 flex gap-2">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
                    {{ result.media_type }}
                  </span>
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-900 text-green-200">
                    {{ result.provider }}
                  </span>
                </div>
              </div>
            </div>
            <div class="mt-4">
              <button
                @click="requestMedia(result)"
                class="w-full bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-md text-sm transition-colors"
              >
                Request This Item
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="error" class="bg-red-900 border border-red-700 p-4 rounded-lg">
      <div class="flex">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800">Search Error</h3>
          <p class="mt-1 text-sm text-red-700">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- No results -->
    <div v-else-if="hasSearched && !searching && searchResults.length === 0" class="bg-gray-800 border border-gray-700 p-6 rounded-lg text-center">
      <p class="text-gray-400">No results found for "{{ searchQuery }}"</p>
    </div>

    <!-- Manual request form -->
    <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg">
      <h2 class="text-lg font-medium text-white mb-4">Can't Find What You're Looking For?</h2>
      <p class="text-gray-400 mb-4">Submit a manual request with the details you have.</p>
      <RequestForm @request-created="handleRequestCreated" />
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRequestsStore } from '../stores/requests'
import { useMetadataStore } from '../stores/metadata'
import RequestForm from '../components/RequestForm.vue'

export default {
  name: 'Browse',
  components: {
    RequestForm
  },
  setup() {
    const requestsStore = useRequestsStore()
    const metadataStore = useMetadataStore()
    
    const searchQuery = ref('')
    const selectedMediaType = ref('')
    const hasSearched = ref(false)

    const performSearch = async () => {
      if (!searchQuery.value.trim()) return
      
      hasSearched.value = true
      
      const result = await metadataStore.searchMetadata(
        searchQuery.value,
        selectedMediaType.value || 'book'
      )
      
      if (!result.success) {
        console.error('Search error:', result.error)
      }
    }

    const clearSearch = () => {
      searchQuery.value = ''
      selectedMediaType.value = ''
      metadataStore.clearResults()
      hasSearched.value = false
    }

    const requestMedia = async (mediaItem) => {
      try {
        const requestDescription = `${mediaItem.description}

Author: ${mediaItem.author}
Year: ${mediaItem.year}
Genre: ${mediaItem.genre}
Source: ${mediaItem.provider}`

        await requestsStore.createRequest({
          title: mediaItem.title,
          description: requestDescription,
          media_type: mediaItem.media_type
        })
        
        // Show success message or redirect
        alert('Request submitted successfully!')
      } catch (error) {
        console.error('Request error:', error)
        alert('Failed to submit request. Please try again.')
      }
    }

    const handleRequestCreated = () => {
      // Handle successful manual request creation
      console.log('Manual request created successfully')
    }

    return {
      searchQuery,
      selectedMediaType,
      searchResults: computed(() => metadataStore.searchResults),
      searching: computed(() => metadataStore.isLoading),
      hasSearched,
      error: computed(() => metadataStore.error),
      performSearch,
      clearSearch,
      requestMedia,
      handleRequestCreated
    }
  }
}
</script>