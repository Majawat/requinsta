<template>
  <div id="app" class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold">Requinsta</h1>
          </div>
          <div class="flex items-center space-x-4" v-if="authStore.isAuthenticated">
            <span class="text-sm text-gray-700">{{ authStore.user?.email }}</span>
            <button @click="authStore.logout" class="text-sm text-gray-500 hover:text-gray-700">
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div v-if="!authStore.isAuthenticated">
        <LoginForm />
      </div>

      <div v-else class="space-y-6">
        <div
          v-if="authStore.user?.role.toLowerCase() === 'admin'"
          class="bg-yellow-100 p-4 rounded-lg">
          <p class="text-yellow-800 font-medium">Admin Mode</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <RequestForm @request-created="loadRequests" />

          <AdminPanel
            v-if="authStore.user?.role.toLowerCase() === 'admin'"
            :requests="requestsStore.requests" />

          <UserManagement v-if="authStore.user?.role.toLowerCase() === 'admin'" />

          <div
            v-if="authStore.user?.role.toLowerCase() !== 'admin'"
            class="bg-white p-6 rounded-lg shadow-md">
            <h2 class="text-xl font-bold mb-4">All Requests</h2>
            <div v-if="requestsStore.loading" class="text-gray-500">Loading...</div>
            <div v-else-if="requestsStore.requests.length === 0" class="text-gray-500">
              No requests yet
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="request in requestsStore.requests"
                :key="request.id"
                class="border border-gray-200 rounded p-3">
                <h3 class="font-medium">{{ request.title }}</h3>
                <p class="text-sm text-gray-600">{{ request.description }}</p>
                <div class="flex justify-between items-center mt-2">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {{ request.media_type }}
                  </span>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {{ request.status }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { onMounted } from "vue";
import { useAuthStore } from "./stores/auth";
import { useRequestsStore } from "./stores/requests";
import LoginForm from "./components/LoginForm.vue";
import RequestForm from "./components/RequestForm.vue";
import AdminPanel from "./components/AdminPanel.vue";
import UserManagement from "./components/UserManagement.vue";

export default {
  name: "App",
  components: {
    LoginForm,
    RequestForm,
    AdminPanel,
    UserManagement,
  },
  setup() {
    const authStore = useAuthStore();
    const requestsStore = useRequestsStore();

    const loadRequests = async () => {
      if (authStore.isAuthenticated) {
        await requestsStore.fetchRequests();
      }
    };

    onMounted(async () => {
      await authStore.initAuth();
      await loadRequests();
    });

    return {
      authStore,
      requestsStore,
      loadRequests,
    };
  },
};
</script>
