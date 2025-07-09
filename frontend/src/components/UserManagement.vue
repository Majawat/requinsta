<template>
  <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4 text-white">User Management</h2>

    <!-- Add User Form -->
    <div class="border-b border-gray-600 pb-4 mb-4">
      <h3 class="text-lg font-medium mb-2 text-white">Add New User</h3>
      <form @submit.prevent="addUser" class="space-y-2">
        <input
          v-model="newUser.email"
          type="email"
          placeholder="Email"
          required
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
        <input
          v-model="newUser.password"
          type="password"
          placeholder="Password"
          required
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-sm text-white placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
        <select
          v-model="newUser.role"
          class="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-sm text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500">
          <option value="READ_ONLY">Read Only</option>
          <option value="USER">User</option>
          <option value="POWER_USER">Power User</option>
          <option value="MODERATOR">Moderator</option>
          <option value="ADMIN">Admin</option>
        </select>
        <button
          type="submit"
          :disabled="adding"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md text-sm hover:bg-blue-700 disabled:opacity-50">
          {{ adding ? "Adding..." : "Add User" }}
        </button>
      </form>
    </div>

    <!-- Users List -->
    <div v-if="loading" class="text-gray-400">Loading users...</div>
    <div v-else class="space-y-3">
      <div
        v-for="user in users"
        :key="user.id"
        class="border border-gray-600 rounded p-3 flex justify-between items-center bg-gray-700">
        <div>
          <h3 class="font-medium text-white">{{ user.email }}</h3>
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
            {{ user.role }}
          </span>
        </div>
        <div class="flex space-x-2">
          <select
            :value="user.role"
            @change="updateUserRole(user.id, $event.target.value)"
            class="text-xs bg-gray-600 border border-gray-500 rounded px-2 py-1 text-white">
            <option value="READ_ONLY">Read Only</option>
            <option value="USER">User</option>
            <option value="POWER_USER">Power User</option>
            <option value="MODERATOR">Moderator</option>
            <option value="ADMIN">Admin</option>
          </select>
          <button
            @click="deleteUser(user.id)"
            class="px-2 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "UserManagement",
  data() {
    return {
      users: [],
      loading: false,
      adding: false,
      newUser: {
        email: "",
        password: "",
        role: "USER",
      },
    };
  },
  async mounted() {
    await this.fetchUsers();
  },
  methods: {
    /**
     * Fetches all users from admin API and updates component state
     * @async
     * @returns {Promise<void>}
     */
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await axios.get(`http://${window.location.hostname}:8000/api/v1/admin/users`);
        this.users = response.data;
      } catch (error) {
        console.error("Failed to fetch users:", error);
      } finally {
        this.loading = false;
      }
    },

    /**
     * Creates a new user with provided form data and refreshes users list
     * @async
     * @returns {Promise<void>}
     */
    async addUser() {
      this.adding = true;
      try {
        await axios.post(`http://${window.location.hostname}:8000/api/v1/admin/users`, this.newUser);
        this.newUser = { email: "", password: "", role: "USER" };
        await this.fetchUsers();
      } catch (error) {
        console.error("Failed to add user:", error);
        alert(error.response?.data?.detail || "Failed to add user");
      } finally {
        this.adding = false;
      }
    },

    /**
     * Updates user role via API and refreshes users list
     * @async
     * @param {number|string} userId - The ID of the user to update
     * @param {string} newRole - The new role to assign
     * @returns {Promise<void>}
     */
    async updateUserRole(userId, newRole) {
      try {
        await axios.patch(`http://${window.location.hostname}:8000/api/v1/admin/users/${userId}/role`, {
          role: newRole,
        });
        await this.fetchUsers();
      } catch (error) {
        console.error("Failed to update user role:", error);
      }
    },

    /**
     * Deletes user after confirmation prompt and refreshes users list
     * @async
     * @param {number|string} userId - The ID of the user to delete
     * @returns {Promise<void>}
     */
    async deleteUser(userId) {
      if (!confirm("Are you sure you want to delete this user?")) return;

      try {
        await axios.delete(`http://${window.location.hostname}:8000/api/v1/admin/users/${userId}`);
        await this.fetchUsers();
      } catch (error) {
        console.error("Failed to delete user:", error);
        alert(error.response?.data?.detail || "Failed to delete user");
      }
    },
  },
};
</script>
