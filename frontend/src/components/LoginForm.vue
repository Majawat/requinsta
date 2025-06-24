<template>
  <div class="max-w-md mx-auto bg-white p-6 rounded-lg shadow-md">
    <h2 class="text-2xl font-bold mb-4">{{ isLogin ? "Login" : "Register" }}</h2>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700">Email</label>
        <input
          v-model="email"
          type="email"
          required
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700">Password</label>
        <input
          v-model="password"
          type="password"
          required
          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500" />
      </div>

      <div v-if="error" class="text-red-600 text-sm">
        {{ error }}
      </div>

      <button
        type="submit"
        :disabled="loading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
        {{ loading ? "Loading..." : isLogin ? "Login" : "Register" }}
      </button>
    </form>

    <p class="mt-4 text-center text-sm text-gray-600">
      {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
      <button @click="toggleMode" class="font-medium text-indigo-600 hover:text-indigo-500">
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

    toggleMode() {
      this.isLogin = !this.isLogin;
      this.error = "";
    },
  },
};
</script>
