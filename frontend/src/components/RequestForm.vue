<template>
  <div class="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-4">New Request</h2>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">Title</label>
        <input
          v-model="title"
          type="text"
          required
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Media Type</label>
        <select
          v-model="mediaType"
          required
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
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
        <label class="block text-sm font-medium text-gray-700">Description</label>
        <textarea
          v-model="description"
          rows="3"
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"></textarea>
      </div>

      <div v-if="error" class="text-red-600 text-sm">
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

export default {
  name: "RequestForm",
  data() {
    return {
      title: "",
      description: "",
      mediaType: "book",
      loading: false,
      error: "",
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
          this.$emit("request-created");
        } else {
          this.error = result.error;
        }
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
