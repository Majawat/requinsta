import { defineStore } from "pinia";
import axios from "axios";

const API_URL = `http://${window.location.hostname}:8000/api/v1`;

export const useMetadataStore = defineStore("metadata", {
  state: () => ({
    searchResults: [],
    isLoading: false,
    error: null,
  }),

  actions: {
    /**
     * Searches for metadata using the backend plugin system
     * @async
     * @param {string} query - Search query
     * @param {string} mediaType - Type of media to search for
     * @returns {Promise<Object>} Result object with success status and data or error
     */
    async searchMetadata(query, mediaType = "book") {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`${API_URL}/metadata/search`, {
          params: { query, media_type: mediaType }
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

    /**
     * Gets detailed metadata by ID
     * @async
     * @param {string} id - Metadata ID
     * @param {string} mediaType - Type of media
     * @returns {Promise<Object>} Result object with success status and data or error
     */
    async getMetadataById(id, mediaType = "book") {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.get(`${API_URL}/metadata/${id}`, {
          params: { media_type: mediaType }
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