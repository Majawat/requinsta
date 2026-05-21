import { defineStore } from "pinia";
import axios from "axios";
import { API_URL } from "../utils/api";

export const useMetadataStore = defineStore("metadata", {
  state: () => ({
    searchResults: [],
    isLoading: false,
    error: null,
  }),

  actions: {
    async searchMetadata(query, mediaType = "book") {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await axios.get(`${API_URL}/metadata/search`, {
          params: { query, media_type: mediaType },
        });

        this.searchResults = response.data;
        return { success: true, data: response.data };
      } catch (error) {
        this.error = error.response?.data?.detail || "Search failed";
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    async getMetadataById(id, mediaType = "book") {
      this.isLoading = true;
      this.error = null;

      try {
        const response = await axios.get(`${API_URL}/metadata/${id}`, {
          params: { media_type: mediaType },
        });

        return { success: true, data: response.data };
      } catch (error) {
        this.error = error.response?.data?.detail || "Failed to fetch metadata";
        return { success: false, error: this.error };
      } finally {
        this.isLoading = false;
      }
    },

    clearResults() {
      this.searchResults = [];
      this.error = null;
    },
  },
});
