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
          <option v-for="role in ROLES" :key="role.value" :value="role.value">{{ role.label }}</option>
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
        class="border border-gray-600 rounded p-3 bg-gray-700 space-y-3">
        <div class="flex justify-between items-center">
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
              <option v-for="role in ROLES" :key="role.value" :value="role.value">{{ role.label }}</option>
            </select>
            <button
              @click="deleteUser(user.id)"
              class="px-2 py-1 bg-red-600 text-white rounded text-xs hover:bg-red-700">
              Delete
            </button>
          </div>
        </div>

        <!-- Per-user media-type access -->
        <div class="border-t border-gray-600 pt-2">
          <div class="flex items-center justify-between mb-1">
            <span class="text-xs font-medium text-gray-300">Can request</span>
            <span v-if="user.role === 'ADMIN'" class="text-xs text-gray-400">All types (admin)</span>
            <span v-else-if="!user.allowed_media_types || !user.allowed_media_types.length" class="text-xs text-green-400">All types</span>
            <span v-else class="text-xs text-yellow-400">{{ user.allowed_media_types.length }} type(s)</span>
          </div>
          <div class="flex flex-wrap gap-2">
            <label
              v-for="mt in MEDIA_TYPES"
              :key="mt.value"
              class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded"
              :class="user.role === 'ADMIN' ? 'text-gray-500 cursor-not-allowed' : 'text-gray-200 bg-gray-800 cursor-pointer'">
              <input
                type="checkbox"
                :disabled="user.role === 'ADMIN' || savingAccess === user.id"
                :checked="isAllowed(user, mt.value)"
                @change="toggleType(user, mt.value, $event.target.checked)" />
              {{ mt.label }}
            </label>
          </div>
          <p class="text-xs text-gray-500 mt-1">None checked = all types allowed.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { API_URL } from "../utils/api";

const ROLES = [
  { value: "READ_ONLY", label: "Read Only" },
  { value: "USER", label: "User" },
  { value: "POWER_USER", label: "Power User" },
  { value: "MODERATOR", label: "Moderator" },
  { value: "ADMIN", label: "Admin" },
]

const MEDIA_TYPES = [
  { value: "book", label: "Book" },
  { value: "audiobook", label: "Audiobook" },
  { value: "movie", label: "Movie" },
  { value: "tv_show", label: "TV" },
  { value: "music", label: "Music" },
  { value: "comic", label: "Comic" },
  { value: "podcast", label: "Podcast" },
]

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
      savingAccess: null,
      ROLES,
      MEDIA_TYPES,
    };
  },
  async mounted() {
    await this.fetchUsers();
  },
  methods: {
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await axios.get(`${API_URL}/admin/users`);
        this.users = response.data;
      } catch (error) {
        console.error("Failed to fetch users:", error);
      } finally {
        this.loading = false;
      }
    },

    async addUser() {
      this.adding = true;
      try {
        const { data: newUser } = await axios.post(`${API_URL}/admin/users`, this.newUser);
        this.users.push(newUser);
        this.newUser = { email: "", password: "", role: "USER" };
      } catch (error) {
        console.error("Failed to add user:", error);
        alert(error.response?.data?.detail || "Failed to add user");
      } finally {
        this.adding = false;
      }
    },

    async updateUserRole(userId, newRole) {
      try {
        const { data: updated } = await axios.patch(
          `${API_URL}/admin/users/${userId}/role`,
          { role: newRole }
        );
        const idx = this.users.findIndex(u => u.id === userId);
        if (idx !== -1) this.users[idx] = updated;
      } catch (error) {
        console.error("Failed to update user role:", error);
      }
    },

    isAllowed(user, type) {
      return Array.isArray(user.allowed_media_types) && user.allowed_media_types.includes(type);
    },

    async toggleType(user, type, checked) {
      const current = Array.isArray(user.allowed_media_types) ? [...user.allowed_media_types] : [];
      const next = checked ? [...new Set([...current, type])] : current.filter((t) => t !== type);
      this.savingAccess = user.id;
      try {
        const { data: updated } = await axios.patch(
          `${API_URL}/admin/users/${user.id}/media-types`,
          { allowed_media_types: next }
        );
        const idx = this.users.findIndex((u) => u.id === user.id);
        if (idx !== -1) this.users[idx] = updated;
      } catch (error) {
        console.error("Failed to update access:", error);
        alert(error.response?.data?.detail || "Failed to update access");
      } finally {
        this.savingAccess = null;
      }
    },

    async deleteUser(userId) {
      if (!confirm("Are you sure you want to delete this user?")) return;

      try {
        await axios.delete(`${API_URL}/admin/users/${userId}`);
        this.users = this.users.filter(u => u.id !== userId);
      } catch (error) {
        console.error("Failed to delete user:", error);
        alert(error.response?.data?.detail || "Failed to delete user");
      }
    },
  },
};
</script>
