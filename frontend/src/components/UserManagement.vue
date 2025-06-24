<template>
  <div class="bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-xl font-bold mb-4">User Management</h2>

    <!-- Add User Form -->
    <div class="border-b pb-4 mb-4">
      <h3 class="text-lg font-medium mb-2">Add New User</h3>
      <form @submit.prevent="addUser" class="space-y-2">
        <input
          v-model="newUser.email"
          type="email"
          placeholder="Email"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm" />
        <input
          v-model="newUser.password"
          type="password"
          placeholder="Password"
          required
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm" />
        <select
          v-model="newUser.role"
          class="w-full px-3 py-2 border border-gray-300 rounded-md text-sm">
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
    <div v-if="loading" class="text-gray-500">Loading users...</div>
    <div v-else class="space-y-3">
      <div
        v-for="user in users"
        :key="user.id"
        class="border border-gray-200 rounded p-3 flex justify-between items-center">
        <div>
          <h3 class="font-medium">{{ user.email }}</h3>
          <span
            class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {{ user.role }}
          </span>
        </div>
        <div class="flex space-x-2">
          <select
            :value="user.role"
            @change="updateUserRole(user.id, $event.target.value)"
            class="text-xs border border-gray-300 rounded px-2 py-1">
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
    async fetchUsers() {
      this.loading = true;
      try {
        const response = await axios.get("http://localhost:8000/api/v1/admin/users");
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
        await axios.post("http://localhost:8000/api/v1/admin/users", this.newUser);
        this.newUser = { email: "", password: "", role: "USER" };
        await this.fetchUsers();
      } catch (error) {
        console.error("Failed to add user:", error);
        alert(error.response?.data?.detail || "Failed to add user");
      } finally {
        this.adding = false;
      }
    },

    async updateUserRole(userId, newRole) {
      try {
        await axios.patch(`http://localhost:8000/api/v1/admin/users/${userId}/role`, {
          role: newRole,
        });
        await this.fetchUsers();
      } catch (error) {
        console.error("Failed to update user role:", error);
      }
    },

    async deleteUser(userId) {
      if (!confirm("Are you sure you want to delete this user?")) return;

      try {
        await axios.delete(`http://localhost:8000/api/v1/admin/users/${userId}`);
        await this.fetchUsers();
      } catch (error) {
        console.error("Failed to delete user:", error);
        alert(error.response?.data?.detail || "Failed to delete user");
      }
    },
  },
};
</script>
