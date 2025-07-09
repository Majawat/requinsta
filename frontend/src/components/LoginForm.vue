<template>
  <div class="max-w-md mx-auto bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-4 text-white">{{ isLogin ? "Login" : "Register" }}</h2>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-300">Email</label>
        <input
          v-model="email"
          type="email"
          required
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-300">Password</label>
        <input
          v-model="password"
          type="password"
          required
          class="mt-1 block w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md shadow-sm text-white placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
      </div>

      <div v-if="error" class="text-red-400 text-sm">
        {{ error }}
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
        {{ loading ? "Loading..." : isLogin ? "Login" : "Register" }}
      </button>
    </form>

    <p class="mt-4 text-center text-sm text-gray-400">
      {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
      <button @click="toggleMode" class="font-medium text-indigo-400 hover:text-indigo-300">
        {{ isLogin ? "Register" : "Login" }}
      </button>
    </p>
  </div>
</template>

<script>
import { useAuthStore } from "../stores/auth";

export default {
  name: "LoginForm",
  data() {
    return {
      email: "",
      password: "",
      isLogin: true,
      loading: false,
      error: "",
    };
  },
  methods: {
    /**
     * Handles form submission for login or registration based on current mode
     * @async
     * @returns {Promise<void>}
     */
    async handleSubmit() {
      this.loading = true;
      this.error = "";

      const authStore = useAuthStore();

      try {
        let result;
        if (this.isLogin) {
          result = await authStore.login(this.email, this.password);
        } else {
          result = await authStore.register(this.email, this.password);
          if (result.success) {
            result = await authStore.login(this.email, this.password);
          }
        }

        if (!result.success) {
          this.error = result.error;
        }
      } finally {
        this.loading = false;
      }
    },

    /**
     * Toggles between login and registration modes, clears error messages
     * @returns {void}
     */
    toggleMode() {
      this.isLogin = !this.isLogin;
      this.error = "";
    },
  },
};
</script>
