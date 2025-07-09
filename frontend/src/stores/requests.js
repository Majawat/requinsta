import { defineStore } from "pinia";
import axios from "axios";

const API_URL = `http://${window.location.hostname}:8000/api/v1`;

export const useRequestsStore = defineStore("requests", {
  state: () => ({
    requests: [],
    loading: false,
  }),

  actions: {
    /**
     * Fetches all requests from the API and updates the store state
     * @async
     * @returns {Promise<void>}
     * @throws {Error} If the API request fails
     */
    async fetchRequests() {
      this.loading = true;
      try {
        const response = await axios.get(`${API_URL}/requests/`);
        this.requests = response.data;
      } catch (error) {
        console.error("Failed to fetch requests:", error);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Creates a new request with the provided data and adds it to the store
     * @async
     * @param {Object} requestData - The request data to create
     * @param {string} requestData.title - The title of the requested media
     * @param {string} requestData.media_type - The type of media (book, movie, etc.)
     * @param {string} [requestData.description] - Optional description
     * @returns {Promise<Object>} Result object with success status and data or error
     * @throws {Error} If the API request fails
     */
    async createRequest(requestData) {
      try {
        const response = await axios.post(`${API_URL}/requests/`, requestData);
        this.requests.push(response.data);
        return { success: true, request: response.data };
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || "Request creation failed" };
      }
    },
  },
});
