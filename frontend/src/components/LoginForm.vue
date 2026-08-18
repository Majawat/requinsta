<template>
  <div class="card p-6 shadow-xl shadow-black/20">
    <h2 class="text-xl font-semibold mb-5 text-white">{{ isLogin ? "Welcome back" : "Create your account" }}</h2>

    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label class="label">Email</label>
        <input v-model="email" type="email" required placeholder="you@example.com" class="input" />
      </div>

      <div>
        <label class="label">Password</label>
        <input v-model="password" type="password" required placeholder="••••••••" class="input" />
      </div>

      <div v-if="error" class="flex items-start gap-2 text-rose-300 text-sm bg-rose-500/10 ring-1 ring-rose-400/30 rounded-lg px-3 py-2">
        <svg class="h-4 w-4 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" /></svg>
        {{ error }}
      </div>

      <button type="submit" :disabled="loading" class="btn-primary w-full py-2.5">
        {{ loading ? "Please wait…" : isLogin ? "Sign in" : "Create account" }}
      </button>
    </form>

    <p class="mt-5 text-center text-sm text-slate-400">
      {{ isLogin ? "Don't have an account?" : "Already have an account?" }}
      <button @click="toggleMode" class="font-semibold text-indigo-300 hover:text-indigo-200">
        {{ isLogin ? "Register" : "Sign in" }}
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
