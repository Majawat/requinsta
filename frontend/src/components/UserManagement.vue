<template>
  <div class="space-y-5">
    <h2 class="text-base font-semibold">User management</h2>

    <!-- Add User Form -->
    <div class="card p-5">
      <h3 class="text-base font-semibold mb-3">Add new user</h3>
      <form @submit.prevent="addUser" class="space-y-2">
        <input v-model="newUser.email" type="email" placeholder="Email" required class="input" />
        <input v-model="newUser.password" type="password" placeholder="Password" required class="input" />
        <select v-model="newUser.role" class="input">
          <option v-for="role in ROLES" :key="role.value" :value="role.value">{{ role.label }}</option>
        </select>
        <button type="submit" :disabled="adding" class="btn-primary w-full">
          {{ adding ? "Adding…" : "Add user" }}
        </button>
      </form>
    </div>

    <!-- Users List -->
    <div v-if="loading" class="text-slate-400 text-sm">Loading users…</div>
    <div v-else class="space-y-3">
      <div v-for="user in users" :key="user.id" class="card p-4 space-y-3">
        <div class="flex justify-between items-center gap-3">
          <div class="min-w-0">
            <h3 class="font-semibold text-slate-100 truncate">{{ user.email }}</h3>
            <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold bg-indigo-500/15 text-indigo-300">
              {{ user.role }}
            </span>
          </div>
          <div class="flex gap-2 flex-none">
            <select
              :value="user.role"
              @change="updateUserRole(user.id, $event.target.value)"
              class="text-xs bg-slate-800 border border-slate-700 rounded-md px-2 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500">
              <option v-for="role in ROLES" :key="role.value" :value="role.value">{{ role.label }}</option>
            </select>
            <button @click="deleteUser(user.id)" class="btn-deny btn-sm">Delete</button>
          </div>
        </div>

        <!-- Per-user media-type access -->
        <div class="border-t border-slate-800 pt-3">
          <div class="flex items-center justify-between mb-1.5">
            <span class="eyebrow">Can request</span>
            <span v-if="user.role === 'ADMIN'" class="text-xs text-slate-400">All types (admin)</span>
            <span v-else-if="!user.allowed_media_types || !user.allowed_media_types.length" class="text-xs text-emerald-300">All types</span>
            <span v-else class="text-xs text-amber-300">{{ user.allowed_media_types.length }} type(s)</span>
          </div>
          <div class="flex flex-wrap gap-2">
            <label
              v-for="mt in MEDIA_TYPES"
              :key="mt.value"
              class="inline-flex items-center gap-1.5 text-xs px-2 py-1 rounded-md"
              :class="user.role === 'ADMIN' ? 'text-slate-600 cursor-not-allowed' : 'text-slate-200 bg-slate-800 cursor-pointer'">
              <input
                type="checkbox"
                class="accent-indigo-600 w-3.5 h-3.5"
                :disabled="user.role === 'ADMIN' || savingAccess === user.id"
                :checked="isAllowed(user, mt.value)"
                @change="toggleType(user, mt.value, $event.target.checked)" />
              {{ mt.label }}
            </label>
          </div>
          <p class="text-xs text-slate-500 mt-1">None checked = all types allowed.</p>
        </div>

        <!-- Per-user auto-approval -->
        <div class="border-t border-slate-800 pt-3">
          <div class="flex items-center justify-between mb-1.5">
            <span class="eyebrow">Auto-approve</span>
            <span v-if="user.role === 'ADMIN'" class="text-xs text-slate-400">Own requests (admin)</span>
            <span v-else-if="!user.auto_approve_media_types || !user.auto_approve_media_types.length" class="text-xs text-slate-400">Off</span>
            <span v-else class="text-xs text-sky-300">{{ user.auto_approve_media_types.length }} type(s)</span>
          </div>
          <div class="flex flex-wrap gap-2">
            <label
              v-for="mt in MEDIA_TYPES"
              :key="mt.value"
              class="inline-flex items-center gap-1.5 text-xs px-2 py-1 rounded-md"
              :class="user.role === 'ADMIN' ? 'text-slate-600 cursor-not-allowed' : 'text-slate-200 bg-slate-800 cursor-pointer'">
              <input
                type="checkbox"
                class="accent-indigo-600 w-3.5 h-3.5"
                :disabled="user.role === 'ADMIN' || savingAuto === user.id"
                :checked="isAutoApprove(user, mt.value)"
                @change="toggleAutoApprove(user, mt.value, $event.target.checked)" />
              {{ mt.label }}
            </label>
          </div>
          <p class="text-xs text-slate-500 mt-1">Checked types skip the approval queue and push immediately.</p>
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
      savingAuto: null,
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

    isAutoApprove(user, type) {
      return Array.isArray(user.auto_approve_media_types) && user.auto_approve_media_types.includes(type);
    },

    async toggleAutoApprove(user, type, checked) {
      const current = Array.isArray(user.auto_approve_media_types) ? [...user.auto_approve_media_types] : [];
      const next = checked ? [...new Set([...current, type])] : current.filter((t) => t !== type);
      this.savingAuto = user.id;
      try {
        const { data: updated } = await axios.patch(
          `${API_URL}/admin/users/${user.id}/auto-approve`,
          { auto_approve_media_types: next }
        );
        const idx = this.users.findIndex((u) => u.id === user.id);
        if (idx !== -1) this.users[idx] = updated;
      } catch (error) {
        console.error("Failed to update auto-approve:", error);
        alert(error.response?.data?.detail || "Failed to update auto-approve");
      } finally {
        this.savingAuto = null;
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
