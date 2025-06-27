<template>
  <div class="max-w-md mx-auto bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-4 text-white">New Request</h2>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-300">Title</label>
        <input
          v-model="title"
          @input="searchMetadata"
          type="text"
          required
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />

        <!-- Metadata suggestions -->
        <div
          v-if="metadataResults.length > 0"
          class="mt-2 bg-gray-700 border border-gray-600 rounded-md max-h-48 overflow-y-auto">
          <div
            v-for="(result, index) in metadataResults"
            :key="index"
            @click="selectMetadata(result)"
            class="p-2 hover:bg-gray-600 cursor-pointer border-b border-gray-600 last:border-b-0">
            <div class="text-white text-sm font-medium">{{ result.title }}</div>
            <div v-if="result.author" class="text-gray-300 text-xs">by {{ result.author }}</div>
            <div v-if="result.year" class="text-gray-400 text-xs">{{ result.year }}</div>
          </div>
        </div>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300">Media Type</label>
        <select
          v-model="mediaType"
          @change="searchMetadata"
          required
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          <option value="book">Book</option>
          <option value="audiobook">Audiobook</option>
          <option value="movie">Movie</option>
          <option value="tv_show">TV Show</option>
          <option value="music">Music</option>
          <option value="comic">Comic</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300">Description</label>
        <textarea
          v-model="description"
          rows="3"
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"></textarea>
      </div>

      <div v-if="error" class="text-red-400 text-sm">
        {{ error }}
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
        {{ loading ? "Creating..." : "Create Request" }}
      </button>
    </form>
  </div>
</template>

<script>
import { useRequestsStore } from "../stores/requests";
import axios from "axios";

export default {
  name: "RequestForm",
  data() {
    return {
      title: "",
      description: "",
      mediaType: "book",
      loading: false,
      error: "",
      metadataResults: [],
      searchTimeout: null,
    };
  },
  methods: {
    async handleSubmit() {
      this.loading = true;
      this.error = "";

      const requestsStore = useRequestsStore();

      try {
        const result = await requestsStore.createRequest({
          title: this.title,
          description: this.description,
          media_type: this.mediaType,
        });

        if (result.success) {
          this.title = "";
          this.description = "";
          this.mediaType = "book";
          this.metadataResults = [];
          this.$emit("request-created");
        } else {
          this.error = result.error;
        }
      } finally {
        this.loading = false;
      }
    },

    searchMetadata() {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }

      this.searchTimeout = setTimeout(async () => {
        if (this.title.length < 3) {
          this.metadataResults = [];
          return;
        }

        try {
          const response = await axios.get(`http://localhost:8000/api/v1/metadata/search`, {
            params: { query: this.title, media_type: this.mediaType },
          });

          // Flatten results from all providers
          this.metadataResults = [];
          Object.values(response.data).forEach((providerResults) => {
            this.metadataResults.push(...providerResults.slice(0, 3)); // Limit per provider
          });
        } catch (error) {
          console.error("Metadata search error:", error);
          this.metadataResults = [];
        }
      }, 300);
    },

    selectMetadata(metadata) {
      this.title = metadata.title;
      if (metadata.description && !this.description) {
        this.description = metadata.description;
      }
      this.metadataResults = [];
    },
  },
};
</script>
