<template>
  <div id="app" class="min-h-screen bg-gray-900 text-white">
    <nav class="bg-gray-800 shadow-sm border-b border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-white">Requinsta</h1>
          </div>
          <div class="flex items-center space-x-4" v-if="authStore.isAuthenticated">
            <span class="text-sm text-gray-300">{{ authStore.user?.email }}</span>
            <button @click="authStore.logout" class="text-sm text-gray-400 hover:text-gray-200">
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
          class="bg-yellow-900 border border-yellow-700 p-4 rounded-lg">
          <p class="text-yellow-200 font-medium">Admin Mode</p>
        </div>

        <!-- Admin Layout -->
        <div
          v-if="authStore.user?.role.toLowerCase() === 'admin'"
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <RequestForm @request-created="loadRequests" />
          <AdminPanel :requests="requestsStore.requests" />
          <UserManagement />
        </div>

        <!-- Regular User Layout -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <RequestForm @request-created="loadRequests" />
          <div class="bg-gray-800 border border-gray-700 p-6 rounded-lg shadow-md">
            <h2 class="text-xl font-bold mb-4 text-white">All Requests</h2>
            <div v-if="requestsStore.loading" class="text-gray-400">Loading...</div>
            <div v-else-if="requestsStore.requests.length === 0" class="text-gray-400">
              No requests yet
            </div>
            <div v-else class="space-y-3">
              <div
                v-for="request in requestsStore.requests"
                :key="request.id"
                class="border border-gray-600 rounded p-3 bg-gray-700">
                <h3 class="font-medium text-white">{{ request.title }}</h3>
                <p class="text-sm text-gray-300">{{ request.description }}</p>
                <div class="flex justify-between items-center mt-2">
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-900 text-blue-200">
                    {{ request.media_type }}
                  </span>
                  <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-600 text-gray-200">
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

    /**
     * Loads requests from the store if user is authenticated
     * @async
     * @returns {Promise<void>}
     */
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
