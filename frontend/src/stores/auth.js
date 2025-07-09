import { defineStore } from "pinia";
import axios from "axios";

const API_URL = "http://localhost:8000/api/v1";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    token: localStorage.getItem("token"),
    isAuthenticated: false,
  }),

  actions: {
    /**
     * Registers a new user with email and password
     * @async
     * @param {string} email - User's email address
     * @param {string} password - User's password
     * @returns {Promise<Object>} Result object with success status and user data or error
     * @throws {Error} If the API request fails
     */
    async register(email, password) {
      try {
        const response = await axios.post(`${API_URL}/auth/register`, {
          email,
          password,
        });
        return { success: true, user: response.data };
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || "Registration failed" };
      }
    },

    /**
     * Authenticates user with email and password, sets token and fetches user data
     * @async
     * @param {string} email - User's email address
     * @param {string} password - User's password
     * @returns {Promise<Object>} Result object with success status and error if applicable
     * @throws {Error} If the API request fails
     */
    async login(email, password) {
      try {
        const response = await axios.post(`${API_URL}/auth/login`, {
          email,
          password,
        });

        this.token = response.data.access_token;
        localStorage.setItem("token", this.token);
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;

        await this.fetchUser();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.response?.data?.detail || "Login failed" };
      }
    },

    /**
     * Fetches current user data from API using stored token
     * @async
     * @returns {Promise<void>}
     * @throws {Error} If the API request fails, triggers logout
     */
    async fetchUser() {
      try {
        const response = await axios.get(`${API_URL}/auth/me`);
        this.user = response.data;
        this.isAuthenticated = true;
      } catch (error) {
        this.logout();
      }
    },

    logout() {
      this.user = null;
      this.token = null;
      this.isAuthenticated = false;
      localStorage.removeItem("token");
      delete axios.defaults.headers.common["Authorization"];
    },

    /**
     * Initializes authentication by setting token header and fetching user data if token exists
     * @async
     * @returns {Promise<void>}
     */
    async initAuth() {
      if (this.token) {
        axios.defaults.headers.common["Authorization"] = `Bearer ${this.token}`;
        await this.fetchUser();
      }
    },
  },
});
