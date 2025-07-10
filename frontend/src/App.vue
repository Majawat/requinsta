<template>
  <div id="app">
    <div v-if="!authStore.isAuthenticated" class="min-h-screen bg-gray-900 text-white flex items-center justify-center">
      <div class="max-w-md w-full space-y-8 p-8">
        <div class="text-center">
          <h1 class="text-3xl font-bold text-white mb-6">Requinsta</h1>
          <p class="text-gray-400 mb-8">Sign in to access your media requests</p>
        </div>
        <LoginForm />
      </div>
    </div>

    <Layout v-else />
  </div>
</template>

<script>
import { onMounted } from "vue";
import { useAuthStore } from "./stores/auth";
import LoginForm from "./components/LoginForm.vue";
import Layout from "./components/layout/Layout.vue";

export default {
  name: "App",
  components: {
    LoginForm,
    Layout,
  },
  setup() {
    const authStore = useAuthStore();

    onMounted(async () => {
      await authStore.initAuth();
    });

    return {
      authStore,
    };
  },
};
</script>
