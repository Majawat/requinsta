<template>
  <div id="app">
    <div v-if="!authStore.isAuthenticated"
      class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-slate-950">
      <!-- ambient glow -->
      <div class="pointer-events-none absolute -top-40 -left-40 h-96 w-96 rounded-full bg-indigo-600/20 blur-3xl"></div>
      <div class="pointer-events-none absolute -bottom-40 -right-40 h-96 w-96 rounded-full bg-indigo-500/10 blur-3xl"></div>

      <div class="relative w-full max-w-md">
        <div class="text-center mb-8">
          <div class="mx-auto h-14 w-14 rounded-2xl bg-indigo-600 grid place-items-center shadow-lg shadow-indigo-900/50">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="21" y2="21" /></svg>
          </div>
          <h1 class="mt-4 text-3xl font-bold tracking-tight text-white">Requinsta</h1>
          <p class="text-slate-400 mt-1">Search, request, done.</p>
        </div>
        <LoginForm />
      </div>
    </div>

    <Layout v-else />
  </div>
</template>

<script>
import { useAuthStore } from "./stores/auth";
import LoginForm from "./components/LoginForm.vue";
import Layout from "./components/layout/Layout.vue";

export default {
  name: "App",
  components: { LoginForm, Layout },
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
};
</script>
