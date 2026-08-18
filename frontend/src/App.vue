<template>
  <div id="app">
    <div v-if="!authStore.isAuthenticated"
      class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden bg-gray-900">
      <!-- ambient glow -->
      <div class="pointer-events-none absolute -top-40 -left-40 h-96 w-96 rounded-full bg-indigo-600/20 blur-3xl"></div>
      <div class="pointer-events-none absolute -bottom-40 -right-40 h-96 w-96 rounded-full bg-blue-600/20 blur-3xl"></div>

      <div class="relative w-full max-w-md">
        <div class="text-center mb-8">
          <div class="mx-auto h-14 w-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center shadow-lg shadow-indigo-900/50">
            <span class="text-white font-bold text-2xl">R</span>
          </div>
          <h1 class="mt-4 text-3xl font-bold tracking-tight text-white">Requinsta</h1>
          <p class="text-gray-400 mt-1">Request any media, all in one place.</p>
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
