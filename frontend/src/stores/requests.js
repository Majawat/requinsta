import { defineStore } from "pinia";
import axios from "axios";

const API_URL = "http://localhost:8000/api/v1";

export const useRequestsStore = defineStore("requests", {
  state: () => ({
    requests: [],
    loading: false,
  }),

  actions: {
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
